#------------------------#
# Based off
# Tensorflow 2.0 chatbot #
#   by VISHANK           #
#------------------------#

import json
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import os
from dotenv import load_dotenv
import pandas as pd
import random
import tensorflow as tf
from tensorflow import keras
import mysql.connector
from mysql.connector import Error

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

stemmer = LancasterStemmer()
load_dotenv()

conversation_history = []

# Configuration settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "db", "intents.json")
EXCEPTIONS_PATH = os.path.join(BASE_DIR, "db", "exceptions.txt")
TRAINING_CSV = os.path.join(BASE_DIR, "db", "source_data", "chatbot-symptom-checker", "Training.csv")
DESCRIPTION_CSV = os.path.join(BASE_DIR, "db", "source_data", "chatbot-symptom-description", "symptom_Description.csv")
PRECAUTION_CSV = os.path.join(BASE_DIR, "db", "source_data", "chatbot-symptom-description", "symptom_precaution.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.h5")
SYMPTOM_MODEL_PATH = os.path.join(BASE_DIR, "symptom_model.h5")

def load_data():
    """Loads data from intents.json and CSV files for disease and symptom lookups."""
    with open(INTENTS_PATH) as file:
        data = json.load(file)
    disease_data = get_disease_data()
    symptom_data = get_symptom_data()
    return data, disease_data, symptom_data

def preprocess_data(data):
    """Tokenize the intents.json data for the intent model."""
    words, labels, docs_x, docs_y = [], [], [], []
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])
        if intent["tag"] not in labels:
            labels.append(intent["tag"])
    words = [stemmer.stem(w.lower()) for w in words if w != ("?" or "!")]
    words = sorted(list(set(words)))
    labels = sorted(labels)
    return words, labels, docs_x, docs_y

def load_symptom_training_data():
    """Load binary symptom features and disease labels from Training.csv."""
    df = pd.read_csv(TRAINING_CSV)
    symptom_cols = [c for c in df.columns if c != 'prognosis']
    X = df[symptom_cols].values.astype(np.float32)
    prognosis_labels = sorted(df['prognosis'].unique().tolist())
    y_idx = np.array([prognosis_labels.index(p) for p in df['prognosis']])
    y = np.zeros((len(y_idx), len(prognosis_labels)), dtype=np.float32)
    y[np.arange(len(y_idx)), y_idx] = 1
    return X, y, symptom_cols, prognosis_labels

def create_symptom_model(input_shape, output_shape):
    """Build a classifier: binary symptom vector → disease label."""
    model = keras.Sequential([
        keras.layers.InputLayer(shape=(input_shape,)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(output_shape, activation='softmax'),
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def load_or_train_symptom_model(X, y, output_shape):
    """Load symptom_model.h5 if it exists, otherwise train and save it."""
    try:
        return keras.models.load_model(SYMPTOM_MODEL_PATH)
    except Exception:
        model = create_symptom_model(X.shape[1], output_shape)
        model.fit(X, y, epochs=100, batch_size=32, validation_split=0.1)
        model.save(SYMPTOM_MODEL_PATH)
        return model

def extract_symptoms(user_input, symptom_cols):
    """Match words in user text against known symptom column names."""
    col_lookup = {c.replace('_', ' ').strip().lower(): c for c in symptom_cols}
    text = user_input.lower()
    for filler in ("i have", "i am", "i'm", "i feel", "feeling", "experiencing",
                   "suffering from", "my symptoms are", "symptoms include"):
        text = text.replace(filler, ' ')
    found = []
    # Longer phrases first to avoid partial overlaps
    for display, col in sorted(col_lookup.items(), key=lambda x: -len(x[0])):
        if display in text:
            found.append(col)
            text = text.replace(display, ' ')
    return found

def build_symptom_vector(symptoms_found, symptom_cols):
    """Convert matched symptom column names into a binary feature vector."""
    vec = np.zeros((1, len(symptom_cols)), dtype=np.float32)
    for sym in symptoms_found:
        if sym in symptom_cols:
            vec[0, symptom_cols.index(sym)] = 1
    return vec

def predict_disease_from_symptoms(symptom_model, symptom_vector, prognosis_labels):
    """Return (disease_name, confidence) for the top prediction."""
    results = symptom_model.predict(symptom_vector, verbose=0)[0]
    idx = int(np.argmax(results))
    return prognosis_labels[idx], float(results[idx])

def create_training_data(words, labels, docs_x, docs_y):
    """Create bag-of-words training matrix for the intent model."""
    training = []
    output = []
    out_empty = [0 for _ in range(len(labels))]
    for doc in docs_x:
        bag = [0] * len(words)
        wrds = [stemmer.stem(w.lower()) for w in doc]
        for i, w in enumerate(words):
            if w in wrds:
                bag[i] = 1
        output_row = out_empty[:]
        output_row[labels.index(docs_y[docs_x.index(doc)])] = 1
        training.append(bag)
        output.append(output_row)
    return np.array(training), np.array(output)

def create_model(input_shape, output_shape):
    """Create the intent classifier model."""
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(shape=(input_shape,)))
    model.add(keras.layers.Dense(128, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(32, activation='relu'))
    model.add(keras.layers.Dense(output_shape, activation="softmax"))
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model

def train_model(model, training, output):
    """Train and save the intent model."""
    model.fit(training, output, epochs=500, batch_size=256, validation_split=0.1)
    model.save(MODEL_PATH)

def load_or_train_model(training, output):
    """Load model.h5 if it exists, otherwise train and save it."""
    try:
        return keras.models.load_model(MODEL_PATH)
    except Exception:
        model = create_model(len(training[0]), len(output[0]))
        train_model(model, training, output)
        return model

def bag_of_words(s, words):
    """Convert input string to a bag-of-words feature vector."""
    bag = [0] * len(words)
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        if se in words:
            bag[words.index(se)] = 1
    return np.array([bag])

def extract_entity_from_input(inp):
    """Extract a disease or symptom name from user input by scanning for trigger words."""
    lower = inp.lower().rstrip('?').strip()
    for trigger in ("precautions for", "treatment for", "treat", "about", "explain", "what is", "is"):
        if trigger in lower:
            candidate = lower.split(trigger, 1)[-1].strip()
            if candidate:
                return candidate.title()
    return inp.strip().title()

def check_disease_info(disease_data, disease_name):
    """Look up disease description from the loaded CSV data."""
    for name, description in disease_data:
        if disease_name.lower() in name.lower():
            return description
    return "Disease information not found."

def check_symptom_info(symptom_data, symptom_name):
    """Look up treatment precautions from the loaded CSV data."""
    for treatment, immediate, second, third, longterm in symptom_data:
        if symptom_name.lower() in treatment.lower():
            return f"Immediate: {immediate}. Next steps: {second}. Then: {third}. Long-term: {longterm}."
    return "Symptom information not found."

def update_history(conversation_history, user_input, bot_response):
    """Append an exchange to conversation history, capping at 10 entries."""
    conversation_history.append({'user': user_input, 'bot': bot_response})
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def get_contextual_input(conversation_history, user_input):
    """Prepend conversation history to the current input for context-aware prediction."""
    history_context = " ".join([f"User: {entry['user']} Bot: {entry['bot']}" for entry in conversation_history])
    return f"{history_context} User: {user_input}"

def log_exception(user_input, predicted_tag):
    """Append unrecognised inputs to exceptions.txt for review."""
    mode = 'a' if os.path.exists('exceptions.txt') else 'w'
    with open('exceptions.txt', mode) as f:
        f.write(f'{user_input}  (Predicted category: {predicted_tag})\n')

def mysql_db_connection():
    """Connect to the MySQL database using credentials from environment variables."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_SERVER'),
            database=os.getenv('MYSQL_DB'),
            user=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD'),
        )
        if connection.is_connected():
            cursor = connection.cursor(buffered=True)
            return connection, cursor
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None, None

def close_db_connection(connection, cursor):
    """Close the MySQL connection and cursor."""
    try:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    except Error as e:
        print("Error while closing MySQL connection", e)

def get_disease_data():
    """Get disease descriptions (CSV mode; MySQL block left for reference)."""
    df = pd.read_csv(DESCRIPTION_CSV)
    return list(df[['DiseaseName', 'DiseaseDescription']].itertuples(index=False, name=None))

def get_symptom_data():
    """Get treatment precaution data (CSV mode; MySQL block left for reference)."""
    df = pd.read_csv(PRECAUTION_CSV)
    return list(df[['treatment', 'immediate', 'secondstep', 'thirdstep', 'longterm']].itertuples(index=False, name=None))

def add_disease(disease, description):
    """Add a new disease to the MySQL database."""
    connection, cursor = mysql_db_connection()
    if connection is None:
        print("Add disease error: no database connection")
        return
    try:
        if connection.is_connected():
            print("Adding new disease: ", disease)
            cursor.execute(
                "insert into disease(DiseaseName, Description) values(%s, %s)",
                (disease, description),
            )
            connection.commit()
            print(f"Added new disease: {disease}")
    except Error as e:
        print("Add disease error: ", e)
    close_db_connection(connection, cursor)

def remove_disease(disease):
    """Remove a disease from the MySQL database."""
    connection, cursor = mysql_db_connection()
    if connection is None:
        print("Remove disease error: no database connection")
        return
    try:
        if connection.is_connected():
            print("Removing disease: ", disease)
            cursor.execute("delete from disease where DiseaseName = %s", (disease,))
            connection.commit()
            print(f"Removed disease: {disease}")
    except Error as e:
        print("Remove disease error: ", e)
    close_db_connection(connection, cursor)

# Main chat function
def chat(model, words, labels, data, disease_data, symptom_data,
         symptom_model, symptom_cols, prognosis_labels):
    """Main chatbot loop."""
    print("Welcome to TriageBot to help you with your health needs.")
    print("Please let us know how you are feeling (type /bye to stop or /retrain to retrain)!")
    print("You may also /add_disease or /remove_disease to update the base data.")
    while True:
        inp = input("Patient: ")
        if inp.lower() == "/bye":
            print("Goodbye!")
            break

        elif inp.lower() == "/retrain":
            data, disease_data, symptom_data = load_data()
            words, labels, docs_x, docs_y = preprocess_data(data)
            training, output = create_training_data(words, labels, docs_x, docs_y)
            for f in ('model.h5', 'symptom_model.h5'):
                if os.path.exists(f):
                    os.remove(f)
            model = load_or_train_model(training, output)
            X_sym, y_sym, symptom_cols, prognosis_labels = load_symptom_training_data()
            symptom_model = load_or_train_symptom_model(X_sym, y_sym, len(prognosis_labels))
            continue

        elif inp.lower().startswith("/add_disease"):
            parts = inp.split('|')
            if len(parts) != 3:
                print("Usage: /add_disease|disease|description")
                continue
            _, disease, description = parts
            add_disease(disease, description)
            data, disease_data, symptom_data = load_data()
            continue

        elif inp.lower().startswith("/remove_disease"):
            parts = inp.split('|')
            if len(parts) != 2:
                print("Usage: /remove_disease|disease")
                continue
            _, disease = parts
            remove_disease(disease)
            data, disease_data, symptom_data = load_data()
            continue

        else:
            contextual_input = get_contextual_input(conversation_history, inp)
            results = model.predict([bag_of_words(contextual_input, words)], verbose=0)[0]
            results_index = np.argmax(results)
            tag = labels[results_index]

            if results[results_index] > 0.75:
                response = ""
                if tag == "symptom_check":
                    symptoms_found = extract_symptoms(inp, symptom_cols)
                    if not symptoms_found:
                        response = ("I couldn't identify any symptoms in what you described. "
                                    "Try listing them, e.g. 'I have itching, skin rash, and high fever'.")
                    else:
                        vec = build_symptom_vector(symptoms_found, symptom_cols)
                        disease, confidence = predict_disease_from_symptoms(
                            symptom_model, vec, prognosis_labels)
                        readable = ', '.join(s.replace('_', ' ') for s in symptoms_found)
                        response = (f"Based on your symptoms ({readable}), "
                                    f"the closest match is: {disease} "
                                    f"(confidence: {confidence:.0%}). "
                                    "Please consult a doctor for a proper diagnosis.")
                elif tag == "disease_info":
                    disease_name = extract_entity_from_input(inp)
                    response = check_disease_info(disease_data, disease_name)
                elif tag == "symptom_info":
                    symptom_name = extract_entity_from_input(inp)
                    response = check_symptom_info(symptom_data, symptom_name)
                else:
                    for tg in data["intents"]:
                        if tg["tag"] == tag:
                            response = random.choice(tg["responses"])
                print(f"{response}")
                update_history(conversation_history, inp, response)
            else:
                print("Sorry, I didn't understand you!")
                log_exception(inp, tag)

# Main execution
if __name__ == "__main__":
    data, disease_data, symptom_data = load_data()
    words, labels, docs_x, docs_y = preprocess_data(data)
    training, output = create_training_data(words, labels, docs_x, docs_y)
    model = load_or_train_model(training, output)
    X_sym, y_sym, symptom_cols, prognosis_labels = load_symptom_training_data()
    symptom_model = load_or_train_symptom_model(X_sym, y_sym, len(prognosis_labels))
    chat(model, words, labels, data, disease_data, symptom_data,
         symptom_model, symptom_cols, prognosis_labels)
