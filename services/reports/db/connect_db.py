import mysql.connector
import os

def get_db():
    db = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'db'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('MYSQL_ROOT_PASSWORD', 'root_password'),
        database=os.getenv('MYSQL_DATABASE', 'sos_golpes')
    )
    try:
        yield db
    finally:
        db.close()
