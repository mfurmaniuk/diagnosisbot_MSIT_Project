# Settings needed to run TensorFlow without warnings
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy
import tensorflow as tf
from tensorflow import keras
import random
import json
import nltk
import databaseUtil as du
from nltk.stem.lancaster import LancasterStemmer
from googletrans import Translator, LANGUAGES
 
class TriageBot:
    """Some initial settings and configurations"""
    body_areas = ["ear", "nose", "throat", "head"]
    connection = None
    potential_illnesses = {
        "ear": "The ear can have many conditions from tinnitus, ear wax build-up, or hearing loss from age.",
        "nose": "The nose can cross illnesses from runny noses, congestion, allergies, to consistent nosebleeds.",
        "throat": "The throat can cross illnesses from colds, allergies, tonsillitus, to sore throat and laryngitus.",
        "head": "A headache or fever may come with other illnesses, and be focused on pain in the temples or a fever."
    }
    
    def __init__(self, name):
        self.stemmer = LancasterStemmer()
        self.name = name
        self.bag= []
        self.docs_x = []
        self.docs_y = []
        self.labels = []
        self.model = tf.keras.Sequential()
        self.output = []
        self.training = []	
        self.words = []
        with open("intents.json") as file:
            self.data = json.load(file)

    def collect_symptoms(self):
        """Collects a Users Symptoms and returns them as a list"""
        print("Please let us know your symptoms.  Add each one so they can be checked for a diagnosis later.")
        print("Add a symptom such as fever, congestions, etc for diagnosis, use an empty line to finish.")
        new_symptom = ''
        symptom_list = []
        while True:
            new_symptom = input("Your Symptom: ")
            if new_symptom == "":
                print("Thank you for letting me know how you feel.")
                break
            else:
                symptom_list.append(new_symptom)
        return symptom_list

    def triage_trainer(self):
        """Prepares the data and model if it doesn't exist"""
        try:
            print("Trying to load the existing model.")
            self.model = keras.models.load_model('triage_model.h5')
        except:
            for intent in self.data["intents"]:
                for pattern in intent["patterns"]:	    
                    wrds = nltk.word_tokenize(pattern)	        
                    self.words.extend(wrds)
                    self.docs_x.append(wrds)	        
                    self.docs_y.append(intent["tag"])
                    
                if intent["tag"] not in self.labels:	    
                    self.labels.append(intent["tag"])
                    
            self.words = [self.stemmer.stem(w.lower()) for w in self.words if w != ("?" or "!")]
            self.words = sorted(list(set(self.words)))
            self.labels = sorted(self.labels)
            out_empty = [0 for _ in range(len(self.labels))]	

            for x, doc in enumerate(self.docs_x):	   
                wrds = [self.stemmer.stem(w.lower()) for w in doc]	
                
                for w in self.words:	    
                    if w in wrds:	        
                        self.bag.append(1)	            
                    else:	       
                        self.bag.append(0)	
                        
                output_row = out_empty[:]	    
                output_row[self.labels.index(self.docs_y[x])] = 1	 
                
                self.training.append(self.bag)	 
                self.output.append(output_row)	
                
            self.training = numpy.array(self.training)
            self.output = numpy.array(self.output)

            # creating the neural net
            self.model.add(tf.keras.layers.InputLayer(shape=(len(self.training[0]),)))
            self.model.add(tf.keras.layers.Dense(8))
            self.model.add(tf.keras.layers.Dense(8))
            self.model.add(tf.keras.layers.Dense(8))
            self.model.add(tf.keras.layers.Dense(len(self.output[0]), activation="softmax"))
            # run this command to get the summary of the model	
            print(self.model.summary())
            
            self.model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])	  
            self.model.fit(self.training, self.output, epochs=250, batch_size=256)
            self.model.save('triage_model.h5')

    def bag_of_words(self, s, words):
        """Creates the tokens for the model"""
        self.bag = [0 for _ in range(len(words))]	
        s_words = nltk.word_tokenize(s)	    
        s_words = [self.stemmer.stem(word.lower()) for word in s_words]	
        
        for se in s_words:	  
            for i, w in enumerate(words):	       
                if w == se:	       
                    self.bag[i] = 1	                
                                        
        return numpy.array([self.bag])	
        
    def patient_triage(self, inp):
        """Runs the patient interaction"""
        results = self.model.predict([self.bag_of_words(inp, self.words)])[0]
        results_index = numpy.argmax(results)	                
        tag = self.labels[results_index]	                
        if results[results_index] > 0.9:	               
            for tg in self.data["intents"]:	                  
                if tg["tag"] == tag:	                      
                    responses = tg["responses"]	                            
            print(f"{random.choice(responses)}   (Category: {tag})")
                    
        else:	                
            print("Sorry, I don't understand that.")
            try:	                    
                with open('exceptions.txt') as f:	                        
                    if inp not in f.read():	                            
                        with open('exceptions.txt', 'a') as f:	                             
                            f.write(f'{inp}  (Predicted category: {tag})\n')	                                
            except:	                  
                file = open('exceptions.txt', 'x')                        
                with open('exceptions.txt') as f:	                        
                    if inp not in f.read():	                            
                        with open('exceptions.txt', 'a') as f:	                            
                            f.write(f'{inp}  (Predicted category: {tag})\n')
        
    def triage_welcome(self):
        """Prompts for what area of the body a person is feeling sick from"""
        symptom_list = []
        print("You can check for the following illnesses:")
        print(', '.join(self.body_areas))
        body_check = input("Please enter the body area you are feeling sick in: ")
        if body_check in self.body_areas:
            symptom_list = self.collect_symptoms()
            print("We can help you with looking for illnesses affecting the " + body_check)
            self.triage_check(body_check)
            print("We'll soon get to a diagnosis with your symptoms of: " + ', '.join(symptom_list))
        else:
            print("Sorry we don't currently have a way to check for illnesses in the " + body_check)
    
    def triage_check(self,body_check):
        """Matches the body area to initial conditions we can check for."""
        print(self.potential_illnesses[body_check])

    def chat(self):
        """Main entry function"""
        # Intro and prompt for function to perform
        # du.mysql_db_connection(self)
        self.triage_trainer()
        print("TensorFlow version: ", tf.__version__)
        print(f"Welcome to {self.name} to help you with your health needs.")
        print("Type /bye to leave or let us know how you are feeling.")
        while True:
            user_input = input("Patient: ")
            if user_input.lower() == "/bye":
                # du.close_connections(self)
                print("Goodbye!")
                break
            else:
                self.patient_triage(user_input)

# Create an instance of the ChatBot class
triageBot = TriageBot("TriageBot")

# Start the chat
triageBot.chat()
