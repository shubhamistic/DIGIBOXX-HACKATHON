import mysql.connector
import json


# Function to establish a database connection
def connect_to_database():
    with open("configs/mysql_config.json", 'r') as mysql_config_file:
        mysql_config = json.load(mysql_config_file)
        try:
            # Replace these values with your MySQL database credentials
            connection = mysql.connector.connect(
                host=mysql_config["host"],
                user=mysql_config["user"],
                password=mysql_config["password"],
                database=mysql_config["database"]
            )
            print("Connected to MySQL database")
            return connection
        except mysql.connector.Error as error:
            print("Error connecting to MySQL database:", error)
            return None


# Exporting the database connection
db_connection = connect_to_database()
