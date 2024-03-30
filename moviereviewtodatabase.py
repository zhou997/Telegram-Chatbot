import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ysql-zy.mysql.database.azure.com;UID=comp7940db;PWD=Cloud7940!,=')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INT PRIMARY KEY,
                    movie_name NVARCHAR(255),
                    rating INT,
                    review NVARCHAR(MAX)
                 )''')


#movie_name = 'Inception'
#rating = 5
#review = 'A mind-bending masterpiece!' (the example of the reply function)

cursor.execute("INSERT INTO reviews (movie_name, rating, review) VALUES (?, ?, ?)", (movie_name, rating, review))
conn.commit()

conn.close()
