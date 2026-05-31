import os
import mysql.connector
from mysql.connector import Error

def get_db():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='db',
            database='sos_golpes',
            user='root',
            password=os.getenv('MYSQL_ROOT_PASSWORD')
        )
        if connection.is_connected():
            yield connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise e
    finally:
        if connection and connection.is_connected():
            connection.close()