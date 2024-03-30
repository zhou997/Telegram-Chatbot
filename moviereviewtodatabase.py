import pyodbc

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
