import psycopg
import logging

log = logging.getLogger("office_visits_etl")

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

        log.info('Connection successful')

        return cursor
    except Exception as e:
        log.exception(f"Error with database connection : {e}")
