#------------------------#
# Tensorflow 2.0 chatbot #
#   by VISHANK           #
#------------------------#


#nltk.download('punkt')
#run this command in python console to download punkt

# Settings needed to run TensorFlow without warnings
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# Library imports
import numpy
import tensorflow as tf
from tensorflow import keras
import random	
import json	
import nltk
from nltk.stem.lancaster import LancasterStemmer
import random

with open("intents.json") as file:	
    data = json.load(file)	  
    
stemmer = LancasterStemmer()
    	    
words = []
labels = []	
docs_x = []
docs_y = []	
conversation_history = []
ERROR_THRESHOLD = 0.25
botName = "TriageBot"

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

training = []	
output = []	

out_empty = [0 for _ in range(len(labels))]	

for x, doc in enumerate(docs_x):	
    bag = []	   
    wrds = [stemmer.stem(w.lower()) for w in doc]	
    
    for w in words:	    
        if w in wrds:	        
            bag.append(1)	            
        else:	       
            bag.append(0)	
            
    output_row = out_empty[:]	    
    output_row[labels.index(docs_y[x])] = 1	 
    
    training.append(bag)	 
    output.append(output_row)	
    
    
training = numpy.array(training)
output = numpy.array(output)	

#----------------------------------------------------------------------	

#creating the neural net	

model = keras.Sequential()

model.add(keras.layers.InputLayer(shape=(len(training[0]),)))
model.add(keras.layers.Dense(8))
model.add(keras.layers.Dense(8))
model.add(keras.layers.Dense(8))
model.add(keras.layers.Dense(len(output[0]), activation="softmax"))

#run this command to get the summary of the model	
#model.summary()

#----------------------------------------------------------------------	

def train():	
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])	  
    model.fit(training, output, epochs=500, batch_size=256)	  
    model.save('model.h5')	
    
try:	
    model = keras.models.load_model('model.h5')	   
except:	
    train()	    
    	    
def bag_of_words(s, words):	
    bag = [0 for _ in range(len(words))]	
    
    s_words = nltk.word_tokenize(s)	    
    s_words = [stemmer.stem(word.lower()) for word in s_words]	
    
    for se in s_words:	  
        for i, w in enumerate(words):	       
            if w == se:	       
                bag[i] = 1	                
                	                
    return numpy.array([bag])	  

def update_history(user_input, bot_response):
    conversation_history.append({'user': user_input, 'bot': bot_response})
    # Limit history length if needed
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def get_contextual_input(user_input):
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
            
def chat():	
        print(f"Welcome to {botName} to help you with your health needs.")
        print("Please let us know how you are feeling (type /bye to stop or /retrain to train again)!")	   	       
        while True:	       
            inp = input("Patient: ")	
            
            if inp.lower() == "/bye":	            
                break	             
                exit()	 
                
            elif inp.lower() == "/retrain":	          
                train()	               
                continue	 
                
            else:
                contextual_input = get_contextual_input(inp)           
                results = model.predict([bag_of_words(contextual_input, words)])[0]	                
               	               
                results_index = numpy.argmax(results)	                
                tag = labels[results_index]	                
                if results[results_index] > 0.9:	               
                    for tg in data["intents"]:	                  
                        if tg["tag"] == tag:	                      
                            responses = tg["responses"]	                            
                    response = random.choice(responses)
                    print(f"{response} (Category: {tag})")
                    update_history(inp, response)
                    
                else:	                
                    print("I didn't understand you!")
                    log_exception(inp, tag)

chat()                	
