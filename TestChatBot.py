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