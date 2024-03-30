import asyncio
import os
from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool

load_dotenv()


class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('MYSQL_HOST'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': 'chatbot'
        }
        self.pool = MySQLConnectionPool(pool_name='myPool',
                                        pool_size=10,
                                        **self.config)

    def get_connection(self):
        return self.pool.get_connection()

    async def execute_query(self, query):
        db_conn = self.pool.get_connection()
        cursor = db_conn.cursor()
        try:
            await asyncio.get_event_loop().run_in_executor(None, cursor.execute, query)
            result = await asyncio.get_event_loop().run_in_executor(None, cursor.fetchall)
            return result
        except Exception as err:
            print(f"An error occurred: {err}")
            return None
        finally:
            cursor.close()
            db_conn.close()
