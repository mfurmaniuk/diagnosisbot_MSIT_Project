import mysql.connector

from mysql.connector import Error
connection = None

try:
    connection = mysql.connector.connect(host='localhost', database='this_db', user='michael', password='F0xxyH4rl0tsC00l!')
    if connection.is_connected():
        db_info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You are connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Extract DiseaseName and Description separately
disease_names = [row[0] for row in data]
descriptions = [row[1] for row in data]

# Tokenize and pad the descriptions (you can adjust the num_words and maxlen as needed)
tokenizer = Tokenizer(num_words=1000)
tokenizer.fit_on_texts(descriptions)
sequences = tokenizer.texts_to_sequences(descriptions)
padded_sequences = pad_sequences(sequences, maxlen=100)

# Convert disease names to one-hot encoding or another suitable format if needed
# Here we are simply showing sequences for descriptions
print(padded_sequences[:5])  # Display the first 5 padded sequences

# Example of using the padded_sequences in a TensorFlow model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=1000, output_dim=64, input_length=100),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(10, activation='softmax')  # Adjust the output layer to your specific task
])

# Compile and use the model with the sequences
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Example: Train the model (X would be your padded_sequences and y should be your target labels)
# model.fit(padded_sequences, y, epochs=10, batch_size=32)

from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense

# Define the first model
model1 = Sequential([
    Dense(64, activation='relu', input_shape=(20,)),
    Dense(32, activation='relu')
])

# Define the second model
model2 = Sequential([
    Dense(16, activation='relu', input_shape=(32,)),
    Dense(1, activation='sigmoid')
])

# Merge the models sequentially
combined_model = Sequential([model1, model2])

# Compile the combined model
combined_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Summary of the combined model
combined_model.summary()

from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense

# Define the first model (Model 1)
# Input shape of 20 features, with two dense layers
model1 = Sequential([
    Dense(64, activation='relu', input_shape=(20,)),  # Input layer with 20 features
    Dense(32, activation='relu')                      # Intermediate layer
])

# Define the second model (Model 2)
# The input shape here should match the output shape of model1 (32 units)
model2 = Sequential([
    Dense(16, activation='relu', input_shape=(32,)),  # Takes input from model1's output
    Dense(1, activation='sigmoid')                    # Output layer
])

# Merge the models sequentially
# The output of model1 becomes the input to model2
combined_model = Sequential([model1, model2])

# Compile the combined model
combined_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Summary of the combined model
combined_model.summary()

# Example training data (X: input data, y: labels)
# Ensure your input shape matches the first model's input shape
# X.shape should be (num_samples, 20) if input_shape of model1 is (20,)
X = ...  # Input data
y = ...  # Labels

# Train the model
combined_model.fit(X, y, epochs=10, batch_size=32)

# Make predictions
predictions = combined_model.predict(X)

for row in cursor.fetchall():
                data_dict = {column[0]: row[i] for i, column in enumerate(cursor.description)}
                data.append(data_dict)
            disease_result = json.dumps(data)
            disease_result = "{\"diseases\": " + disease_result + "}"

# To merge the existing two models
from tensorflow import keras
from tensorflow.keras import layers

# Define the first model (e.g., processing text data)
input_text = keras.Input(shape=(sequence_length,))
x1 = vectorize_layer(input_text)
x1 = layers.Embedding(input_dim=max_tokens, output_dim=16)(x1)
x1 = layers.GlobalAveragePooling1D()(x1)
x1 = layers.Dense(16, activation='relu')(x1)

# Define the second model (e.g., processing dense features)
input_dense = keras.Input(shape=(input_shape,))
x2 = layers.Dense(128, activation='relu')(input_dense)
x2 = layers.Dropout(0.5)(x2)
x2 = layers.Dense(64, activation='relu')(x2)
x2 = layers.Dropout(0.5)(x2)
x2 = layers.Dense(32, activation='relu')(x2)

# Concatenate the outputs of both models
merged = layers.concatenate([x1, x2])

# Add final output layers
output = layers.Dense(output_shape, activation="softmax")(merged)

# Create a combined model
model = keras.Model(inputs=[input_text, input_dense], outputs=output)

# Compile the combined model
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Summary
model.summary()
