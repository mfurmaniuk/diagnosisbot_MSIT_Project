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
import pandas as pd
import random
import tensorflow as tf
from tensorflow import keras
from keras.api import layers
import mysql.connector
from mysql.connector import Error

# Settings needed to run TensorFlow without warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Initialize the stemmer
stemmer = LancasterStemmer()

# Vectorization settings
max_tokens = 100  # Vocabulary size
sequence_length = 20  # Max length of each sequence

# Create a TextVectorization layer as an alternative to Tokenizer
vectorize_layer = tf.keras.layers.TextVectorization(
    max_tokens=max_tokens, 
    output_mode='int', 
    output_sequence_length=sequence_length
)
    
# Intialize the conversation history
conversation_history = []
    
# Load data
def load_data():
    """Loads data from intents.json and MySQL Database for Disease and Symptoms."""
    with open("intents.json") as file:	
        data = json.load(file)
    disease_data = get_disease_data()
    symptom_data = get_symptom_data()
    return data, disease_data, symptom_data
    
# Preprocess data from inputs
def preprocess_data(data):
    """Tokenize the intents.json data for the model."""
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

def preprocess_disease_data(disease_data):
    """Tokenize the Disease data for addition to the model."""
    # Combine disease names and descriptions into one list for tokenizing
    all_texts = [' '.join(nltk.word_tokenize(disease) + nltk.word_tokenize(description))
             for disease, description in disease_data]

    # Adapt the layer to the dataset (fit it to the text data)
    vectorize_layer.adapt(all_texts)

    # Use the layer to transform the texts into integer sequences
    sequences = vectorize_layer(all_texts)

    # Convert the sequences to numpy array for further processing
    padded_sequences = sequences.numpy()

    # Display the tokenized and padded sequences
    print(padded_sequences)
    return padded_sequences

# Create training data
def create_training_data(words, labels, docs_x, docs_y):
    """Create the data for training the model."""
    training = []	
    output = []	
    out_empty = [0 for _ in range(len(labels))]	
    for doc in docs_x:	
        bag = [0] * len(words)	   
        wrds = [stemmer.stem(w.lower()) for w in doc]	
        for i,w in enumerate(words):	    
            if w in wrds:	        
                bag[i] = 1
        output_row = out_empty[:]	    
        output_row[labels.index(docs_y[docs_x.index(doc)])] = 1	 
        training.append(bag)	 
        output.append(output_row)	
    return np.array(training), np.array(output)	

# Create the model
def create_model(input_shape, output_shape):
    """Create model for the AI."""
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(shape=(input_shape,)))
    model.add(keras.layers.Dense(128, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(32, activation='relu'))
    model.add(keras.layers.Dense(output_shape, activation="softmax"))
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])	      
    # Uncomment and run this command to get the summary of the model	
    # model.summary()
    return model

def create_db_model(padded_sequences):
    """Create the model from database data"""
    # Example labels (just for demonstration purposes, usually you'd get these from a dataset)
    labels = [0, 1, 0]  # Binary labels for disease types (e.g., viral or non-viral)

    # Build the model
    model = tf.keras.Sequential([
        # Add the TextVectorization layer directly into the model pipeline
        vectorize_layer,
        layers.Embedding(input_dim=max_tokens, output_dim=16, input_length=sequence_length),
        layers.GlobalAveragePooling1D(),
        layers.Dense(16, activation='relu'),
        layers.Dense(1, activation='sigmoid')  # Binary classification
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_model(model, training, output):
    """Train the model data for the AI and save the model."""
    model.fit(training, output, epochs=500, batch_size=256, validation_split=0.1)
    # This is from the database
    # model2.fit(padded_sequences, labels, epochs=10)  
    model.save('model.h5')

def load_or_train_model(training, output, padded_sequences):
    """Either load the existing trained model, or create it if it does not exist."""
    try:	
        model = keras.models.load_model('model.h5')	   
    except:
        model = create_model(len(training[0]), len(output[0]))
        # model_d = create_db_model(padded_sequences)
        # model = merged_model(model_j, model_d)
        train_model(model, training, output)
    return model

def merged_model(model1, model2):
    """Merge models from different source data."""
    input_layer = keras.layers.Input((20,))
    out1 = model1(input_layer)
    conc = keras.layers.Concatenate()([input_layer, out1])
    out2 = model2(conc)
    xtrainshape = 10
    output_layer = keras.layers.Dense(xtrainshape, "softmax")(out2)
    model = keras.models.Model(inputs=input_layer, outputs=output_layer)
    return model
    
# Utility functions	    
def bag_of_words(s, words):
    """Create the tokens from source data."""
    bag = [0] * len(words)
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        if se in words:
            bag[words.index(se)] = 1
    return np.array([bag])

def check_disease_info(disease_data, disease_name):
    """Look up disease information from the database."""
    for disease in disease_data:
        if disease_name.lower() in disease["DiseaseName"].lower():
            return disease["Description"]
    return "Disease information not found."

def check_symptom_info(symptom_data, symptom_name):
    """Look up symptom information from the database."""
    for symptom in symptom_data:
        if symptom_name.lower() in symptom["SymptomName"].lower():
            return symptom["SymDesc"]
    return "Symptom information not found."

def update_history(conversation_history, user_input, bot_response):
    """Add conversation to the model data to keep context."""
    conversation_history.append({'user': user_input, 'bot': bot_response})
    # Limit history length if needed
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def get_contextual_input(conversation_history, user_input):
    """Combine conversation history into a single string."""
    history_context = " ".join([f"User: {entry['user']} Bot: {entry['bot']}" for entry in conversation_history])
    return f"{history_context} User: {user_input}"

def log_exception(user_input, predicted_tag):
    """Note any tags or queries not found in source data."""
    try:
        with open('exceptions.txt', 'a') as f:
            f.write(f'{user_input}  (Predicted category: {predicted_tag})\n')
    except FileNotFoundError:
        with open('exceptions.txt', 'w') as f:
            f.write(f'{user_input}  (Predicted category: {predicted_tag})\n')

def mysql_db_connection():
    """Connect to source data in the MySQL database."""
    try:
        connection = mysql.connector.connect(host='localhost', database='diagnosebot', user='michael', password='F0xxyH4rl0tsC00l!')
        if connection.is_connected():
            db_info = connection.get_server_info()
            # Uncomment for connection checking
            # print("Connected to MySQL Server version ", db_info)
            cursor = connection.cursor(buffered=True)
            return connection, cursor
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None, None

def close_db_connection(connection,cursor):
    """Closes any lingering connections."""
    try:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed.")
    except Error as e:
        print("Error while connecting to MySQL to close", e)

def get_disease_data():
    """Get Disease data from the MySQL database."""
    connection, cursor = mysql_db_connection()
    data = []
    try:
        if connection.is_connected():
            dis_query = ("select DiseaseName,Description from disease;")
            cursor.execute(dis_query)
            disease_result = cursor.fetchall()
            return disease_result
    except Error as e:
        print("Disease query error: ", e)
    close_db_connection(connection, cursor)

def get_symptom_data():
    """Get Symptom data from the MySQL database."""
    connection, cursor = mysql_db_connection()
    try:
        if connection.is_connected():
            sym_query = ("select SymptomName,SymDesc from symptom")
            cursor.execute(sym_query)
            symptom_result = cursor.fetchall()
            return symptom_result
    except Error as e:
        print("Symptom query error: ", e)
    close_db_connection(connection, cursor)

def add_disease(disease, description):
    """Add a new Disease to the database."""
    connection, cursor = mysql_db_connection()
    try:
        if connection.is_connected():
            print("Adding new disease: ", disease)
            # Create Insert statement then execute
            disease_insert = ("""insert into disease(DiseaseName, Description) values(%s, %s)""")
            result = cursor.execute(disease_insert, (disease, description))
            connection.commit()
            print(f"Added new disease: {disease}, ", result)
    except Error as e:
        print("Symptom query error: ", e)
    close_db_connection(connection, cursor)

def remove_disease(disease):
    """Remove a Disease from the database."""
    connection, cursor = mysql_db_connection()
    try:
        if connection.is_connected():
            print("Removing disease: ", disease)
            # Create Delete statement then execute
            disease_delete = "delete from disease where DiseaseName = \"" + disease + "\""
            result = cursor.execute(disease_delete)
            connection.commit()
            print(f"Removed disease: {disease}, ", result)
    except Error as e:
        print("Symptom query error: ", e)
    close_db_connection(connection, cursor)
    
# Main chat function
def chat(model, words, labels, data, disease_data, symptom_data):
    """Main Chatbot function."""
    print(f"Welcome to TriageBot to help you with your health needs.")
    print("Please let us know how you are feeling (type /bye to stop or /retrain to train again)!")
    print("You may also /add_disease or /remove_disease to be able to update the base data.")  	       
    while True:	       
        inp = input("Patient: ")	
        if inp.lower() == "/bye":
            print("Goodbye!")
            break	             	 
        elif inp.lower() == "/retrain":
            data, disease_data, symptom_data = load_data()
            words, labels, docs_x, docs_y = preprocess_data(data)      
            training, output = create_training_data(words, labels, docs_x, docs_y)
            model = load_or_train_model(training, output)
            continue
        elif inp.lower().startswith("/add_disease"):
            parts = inp.split('|')
            if len(parts) != 3:
                print("Usage: /add_disease|disease|description")
                continue
            _, disease, description = parts
            add_disease(disease, description)
            data, disease_data, symptom_data = load_data()  # Reload data after modification
            words, labels, docs_x, docs_y = preprocess_data(data)  # Reprocess data
            training, output = create_training_data(words, labels, docs_x, docs_y)  # Recreate training data
            model = load_or_train_model(training, output)  # Reload model
            continue
        elif inp.lower().startswith("/remove_disease"):
            parts = inp.split('|')
            if len(parts) != 2:
                print("Usage: /remove_disease|disease")
                continue
            _, disease = parts
            remove_disease(disease)
            data, disease_data, symptom_data = load_data()  # Reload data after modification
            words, labels, docs_x, docs_y = preprocess_data(data)  # Reprocess data
            training, output = create_training_data(words, labels, docs_x, docs_y)  # Recreate training data
            model = load_or_train_model(training, output)  # Reload model
            continue
        else:
            contextual_input = get_contextual_input(conversation_history, inp)           
            results = model.predict([bag_of_words(contextual_input, words)])[0]
            results_index = np.argmax(results)	                
            tag = labels[results_index]
            if results[results_index] > 0.9:
                response = ""
                if tag == "disease_info":
                    print("Disease!")
                    # Extract disease name from user input
                    disease_name = inp.split("about")[-1].strip().capitalize()
                    response = check_disease_info(disease_data, disease_name)
                elif tag == "symptom_info":
                    print("Symptom")
                    # Extract symptom name from user input
                    symptom_name = inp.split("about")[-1].strip().lower()
                    response = check_symptom_info(symptom_data, symptom_name)
                else:
                    for tg in data["intents"]:
                        if tg["tag"] == tag:
                            responses = tg["responses"]
                            response = random.choice(responses)
                # print(f"{response} (Category: {tag})")
                print(f"{response}")
                update_history(conversation_history, inp, response)
            else:	                
                print("Sorry, I didn't understand you!")
                log_exception(inp, tag)

# Main execution
if __name__ == "__main__":
    data, disease_data, symptom_data = load_data()
    words, labels, docs_x, docs_y = preprocess_data(data)
    padded_sequences = preprocess_disease_data(disease_data)
    training, output = create_training_data(words, labels, docs_x, docs_y)
    model = load_or_train_model(training, output, padded_sequences)
    chat(model, words, labels, data, disease_data, symptom_data)              	
