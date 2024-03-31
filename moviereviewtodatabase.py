import os
import pyodbc
from dotenv import load_dotenv

from mysqlconn import Database
load_dotenv()

azure_host = os.getenv("MYSQL_HOST")
azure_database = os.getenv("chatbot")
azure_username = os.getenv("MYSQL_USER")
azure_password = os.getenv("MYSQL_PASSWORD")

conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={azure_host};DATABASE={azure_database};UID={azure_username};PWD={azure_password}')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INT PRIMARY KEY,
                    movie_name NVARCHAR(255),
                    rating INT,
                    review NVARCHAR(MAX)
                 )''')

cursor.execute("INSERT INTO reviews (movie_name, rating, review) VALUES (?, ?, ?)", (movie_name, rating, review))
conn.commit()

conn.close()