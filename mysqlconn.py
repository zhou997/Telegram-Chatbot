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

    async def check_if_user_exists(self, message):
        user = message.from_user
        db_conn = self.pool.get_connection()
        cursor = db_conn.cursor()
        try:
            sql = "SELECT * FROM users WHERE tg_user_id=%s"
            cursor.execute(sql, (user.id,))
            cursor.fetchall()
            if cursor.rowcount > 0:
                return True
            else:
                sql2 = "Insert Into users(tg_user_id, last_name, first_name, username, chat_id) values(%s, %s, %s, %s, %s)"
                cursor.execute(sql2, (user.id, user.last_name, user.first_name, user.name, message.chat_id))
                db_conn.commit()
                return False
        except Exception as err:
            print(f"An error occurred: {err}")
            return None
        finally:
            cursor.close()
            db_conn.close()

    async def check_if_user_reviews(self, message,title_id):
        user = message.from_user
        db_conn = self.pool.get_connection()
        cursor = db_conn.cursor()
        sql = "SELECT * FROM reviews WHERE user_id=%s and media_id=%s"
        cursor.execute(sql, (user.id,title_id))
        result = cursor.fetchall()
        if len(result) > 1:
            exists = True
        else:
            exists = False
        return exists