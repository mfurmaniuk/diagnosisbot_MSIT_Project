# TriageBot
A Triage AI Chatbot that uses Disease and Symptom data to help diagnose what a User may be suffering from, and provide some treatment options.

This is a chatbot which works with tensorflow 2.1 and higher.<br>
It uses disease data from Kaggle.com on Diseases and Symptoms, which is contained in MySQL and MongoDB versions.<br>
The intents.json contains the intitial patterns and responses for the chatbot to interact with the User.<br>
It also saves wrong answers with predicted category in a text file named as 'exceptions.txt'

Requirements:<br>
-Tensorflow 2.0 or higher, built upon 2.17.0<br>
-Keras 3.4.1<br>
-MySQL Connector 9.0.0<br>
-Nltk 3.8.1<br>
-Numpy 1.26.4<br>
-Pandas 2.2.2<br>
-Punkt from nltk 
<path_to_local_python>>/python3.10.exe -c 'import nltk; nltk.download("punkt")'

Dataset is from: https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset
The source_data folder contains the original datasets in CSV format as well as the testing and training data files.

## Load the data
The current Chatbot runs off a MySQL database.
From a MySQL Workbench run the files in the sql_scripts directory
- Create Table Script
- Insert the necessary data

There is a MongoDB version of all data in the mongodb directory.
This could be used for a local, lightweight version but is not implemented.

## Running the Chatbot
Run the Chatbot using the Python script, which will build the data model from MySQL and the Patterns and Responses from the intents.json file
From a Workbench run the chatbot.py script
Or from the command line, in the Python venv
<path>/.venv/Scripts/python.exe chatbot.py

## Interactions
Feel free to check on the chatbot, ask about diseases, or tell it how you are feeling.