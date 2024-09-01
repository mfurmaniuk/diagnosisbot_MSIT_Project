import mysql.connector
from mysql.connector import Error

# My database utilities
def __init__(self,name):
    self.name = name
    
def mysql_db_connection(self):
    try:
        self.connection = mysql.connector.connect(host='localhost', database='diagnosebot', user='michael', password='F0xxyH4rl0tsC00l!')
        if self.connection.is_connected():
            db_info = self.connection.get_server_info()
            print("Connected to MySQL Server version ", db_info)
            cursor = self.connection.cursor()
            cursor.execute("select SymptomName from symptom;")
            records = cursor.fetchall()
            for name in records:
                print("You may use: ", name)

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if self.connection.is_connected():
            print("MySQL connection is connected.")
            cursor.close()
    
def close_connections(self):
    """Closes any lingering connections"""
    try:
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed.")
    except Error as e:
        print("Error while connecting to MySQL to close", e)