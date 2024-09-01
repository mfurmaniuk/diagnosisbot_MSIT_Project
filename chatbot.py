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
context = {}
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

model = tf.keras.Sequential()

model.add(tf.keras.layers.InputLayer(shape=(len(training[0]),)))
model.add(tf.keras.layers.Dense(8))
model.add(tf.keras.layers.Dense(8))
model.add(tf.keras.layers.Dense(8))
model.add(tf.keras.layers.Dense(len(output[0]), activation="softmax"))

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

def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bag_of_words(sentence, words)])[0]
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((labels[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list

def response(sentence, userID='123', show_details=False):
    results = classify(sentence)
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in data['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        # a random response from the intent
                        return print(random.choice(i['responses']))
            results.pop(0)
    else:	                
        print("Sorry, I don't understand that!")
    try:	                    
        with open('exceptions.txt') as f:	                        
            if sentence not in f.read():	                            
                with open('exceptions.txt', 'a') as f:	                             
                    f.write(f'{sentence}  Predicted category: {i["tag"]}\n')	                                
    except:	                  
        file = open('exceptions.txt', 'x')                        
        with open('exceptions.txt') as f:	                        
            if sentence not in f.read():	                            
                with open('exceptions.txt', 'a') as f:	                            
                    f.write(f'{sentence}  (Predicted category: {i["tag"]})\n')
         	  
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
                chat()	 
                
            else:
                response(inp)         

chat()                	
