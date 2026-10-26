import pandas as pd
import psycopg
from pathlib import Path

def connect_to_db(): 
    try:

        conn = psycopg.connect(
            host = '127.0.0.1',
            user = 'postgres',
            password = '',
            dbname = 'office',
            port = '5432',
            autocommit=True
        )

        cursor = conn.cursor()

        print('Connection successful')

        return cursor
    except Exception as e:
        print(f"Error with database connection: {e}")
