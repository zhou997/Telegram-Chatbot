import os
from dotenv import load_dotenv
import pyodbc
from mysqlconn import Database
load_dotenv()

azure_host = os.getenv("MYSQL_HOST")
azure_database = os.getenv("chatbot")
azure_username = os.getenv("MYSQL_USER")
azure_password = os.getenv("MYSQL_PASSWORD")

conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={azure_host};DATABASE={azure_database};UID={azure_username};PWD={azure_password}')
cursor = conn.cursor()

def handle_command(command):
    if command.startswith("/search"):
        movie_name = command.split("/search ", 1)[1]
        cursor.execute("SELECT * FROM reviews WHERE movie_name LIKE ?", ('%' + movie_name + '%',))
        rows = cursor.fetchall()

        if len(rows) == 0:
            return "Can't find the movie you searched."
        elif len(rows) == 1:
            movie_info = f"movie_name: {rows[0].movie_name}\nRate: {rows[0].rating}\nComment: {rows[0].review}"

            return f"Find one movie:\n{movie_info}\nplease choose the function you want:\n1. Watch comments\n2. Add coments\n3. Delete comments"
        else:
            movies_list = "\n".join([f"{i+1}. {row.movie_name}" for i, row in enumerate(rows)])
            return f"Find several movies, please choose one of them:\n{movies_list}"

user_command = "/search"
response = handle_command(user_command)
print(response)

conn.close()