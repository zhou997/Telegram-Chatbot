import logging
import os

import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
load_dotenv()
# Obtain connection string information from the portal
config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': 'chatbot'
}

try:
    conn = mysql.connector.connect(**config)
    logging.info("Connection established")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        logging.info("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        logging.info("Database does not exist")
    else:
        logging.info(err)
else:
    cursor = conn.cursor()
