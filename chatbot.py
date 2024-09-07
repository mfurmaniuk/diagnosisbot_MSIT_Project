#------------------------#
# Tensorflow 2.0 chatbot #
#   by VISHANK           #
#------------------------#

import os
import json	
import random
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
import tensorflow as tf
from tensorflow import keras
import mysql.connector
from mysql.connector import Error

# Settings needed to run TensorFlow without warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Initialize the stemmer
stemmer = LancasterStemmer()

# Add to existing intents data, but needs formatting
# data["intents"].extend(disease_data)

# Add to existing intents data, but needs formatting
# data["intents"].extend(symptom_data)
    
# Load data
def load_data():
    with open("intents.json") as file:	
        data = json.load(file)
    with open("diagnosebot.disease.json") as file:
        disease_data = json.load(file)
    with open("diagnosebot.symptom.json") as file:
        symptom_data = json.load(file)
    return data, disease_data, symptom_data

# Preprocess data
def preprocess_data(data):
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
        
conversation_history = []
ERROR_THRESHOLD = 0.25

# Create training data
def create_training_data(words, labels, docs_x, docs_y):
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

# Create and train the model
def create_model(input_shape, output_shape):
    # Creating the neural net	
    model = keras.Sequential()
    model.add(keras.layers.InputLayer(shape=(input_shape,)))
    model.add(keras.layers.Dense(8))
    model.add(keras.layers.Dense(8))
    model.add(keras.layers.Dense(8))
    model.add(keras.layers.Dropout(0.1))
    model.add(keras.layers.Dense(output_shape, activation="softmax"))
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])	      
    # Uncomment and run this command to get the summary of the model	
    #model.summary()
    return model

def train_model(model, training, output):
    model.fit(training, output, epochs=500, batch_size=256)	  
    model.save('model.h5')

def load_or_train_model(training, output):
    try:	
        model = keras.models.load_model('model.h5')	   
    except:
        model = create_model(len(training[0]), len(output[0]))
        train_model(model, training, output)
    return model

# Utility functions	    
def bag_of_words(s, words):	
    bag = [0] * len(words)
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        if se in words:
            bag[words.index(se)] = 1
    return np.array([bag])

def get_disease_info(disease_data, disease_name):
    """Look up disease information from the data source."""
    for disease in disease_data:
        if disease_name.lower() in disease["DiseaseName"].lower():
            return disease["Description"]
    return "Disease information not found."

def get_symptom_info(symptom_data, symptom_name):
    """Look up symptom information from the data source."""
    for symptom in symptom_data:
        if symptom_name.lower() in symptom["SymptomName"].lower():
            return symptom["SymDesc"]
    return "Symptom information not found."

def update_history(conversation_history, user_input, bot_response):
    conversation_history.append({'user': user_input, 'bot': bot_response})
    # Limit history length if needed
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def get_contextual_input(conversation_history, user_input):
    # Combine conversation history into a single string (or any other way you prefer)
    history_context = " ".join([f"User: {entry['user']} Bot: {entry['bot']}" for entry in conversation_history])
    return f"{history_context} User: {user_input}"

def log_exception(user_input, predicted_tag):
    try:
        with open('exceptions.txt', 'a') as f:
            f.write(f'{user_input}  (Predicted category: {predicted_tag})\n')
    except FileNotFoundError:
        with open('exceptions.txt', 'w') as f:
            f.write(f'{user_input}  (Predicted category: {predicted_tag})\n')

def mysql_db_connection():
    try:
        connection = mysql.connector.connect(host='localhost', database='diagnosebot', user='michael', password='F0xxyH4rl0tsC00l!')
        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_info)
            cursor = connection.cursor()
            return connection, cursor
    except Error as e:
        print("Error while connecting to MySQL", e)
    return None, None

def close_db_connection(connection):
    """Closes any lingering connections"""
    try:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed.")
    except Error as e:
        print("Error while connecting to MySQL to close", e)

# Main chat function
def chat(model, words, labels, data, disease_data, symptom_data):	
    print(f"Welcome to TriageBot to help you with your health needs.")
    print("Please let us know how you are feeling (type /bye to stop or /retrain to train again)!")
    connection, cursor = mysql_db_connection()  	       
    while True:	       
        inp = input("Patient: ")	
        
        if inp.lower() == "/bye":
            close_db_connection(connection)
            print("Goodbye!")
            break	             	 
        elif inp.lower() == "/retrain":	          
            training, output = create_training_data(words, labels, docs_x, docs_y)
            model = load_or_train_model(training, output)
            continue
        else:
            contextual_input = get_contextual_input(conversation_history, inp)           
            results = model.predict([bag_of_words(contextual_input, words)])[0]
            results_index = np.argmax(results)	                
            tag = labels[results_index]
            
            if results[results_index] > 0.9:
                response = ""
                if tag == "disease_info":
                    # Extract disease name from user input
                    disease_name = inp.split("about")[-1].strip().capitalize()
                    response = get_disease_info(disease_data, disease_name)
                elif tag == "symptom_info":
                    # Extract symptom name from user input
                    symptom_name = inp.split("about")[-1].strip().lower()
                    response = get_symptom_info(symptom_data, symptom_name)
                else:
                    for tg in data["intents"]:
                        if tg["tag"] == tag:
                            responses = tg["responses"]
                            response = random.choice(responses)
                print(f"{response} (Category: {tag})")
                update_history(conversation_history, inp, response)
            else:	                
                print("Sorry, I didn't understand you!")
                log_exception(inp, tag)

    if cursor:
        cursor.close()
    close_db_connection(connection)

# Main execution
if __name__ == "__main__":
    data, disease_data, symptom_data = load_data()
    words, labels, docs_x, docs_y = preprocess_data(data)
    training, output = create_training_data(words, labels, docs_x, docs_y)
    model = load_or_train_model(training, output)
    chat(model, words, labels, data, disease_data, symptom_data)              	
