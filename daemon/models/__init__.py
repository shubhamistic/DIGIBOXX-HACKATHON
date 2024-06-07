import mysql.connector
from os import environ


# Function to establish a database connection
def connect_to_database():
    try:
        # Replace these values with your MySQL database credentials
        connection = mysql.connector.connect(
            host="localhost",
            user=environ.get('DB_USER'),
            password=environ.get('DB_PASS'),
            database="digiboxx",
        )
        print("Connected to MySQL database")
        return connection
    except mysql.connector.Error as error:
        print("Error connecting to MySQL database:", error)
        return None


# get the connection
connection = connect_to_database()
