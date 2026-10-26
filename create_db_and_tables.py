import logging

import psycopg
from psycopg import sql

log = logging.getLogger("office_visits_etl")


def create_db():
    try:
        dbname = "office"
        with psycopg.connect(
            host="127.0.0.1", user="postgres", password="",
            dbname="postgres", port=5432, autocommit=True,
        ) as conn:
            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
            ).fetchone()

            if exists:
                log.info("Database '%s' already exists.", dbname)
            else:
                conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
                log.info("Database '%s' created.", dbname)

        conn.close()

        log.info("Connection closed")

    except Exception:
        log.exception("Error with database creation")
        raise


def create_tables():
    try:
        conn = psycopg.connect(
            host='127.0.0.1',
            user='postgres',
            password='',
            dbname='office',
            port='5432',
            autocommit=True
        )

        cursor = conn.cursor()

        log.info("Connection successful to the office database")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visits_raw (
                file_name TEXT,
                visit_date TEXT,
                visit_count TEXT
            );

            TRUNCATE TABLE visits_raw;
        """)
        log.info("Table visits_raw created and truncated")

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS visits (
                file_id TEXT,
                office_name TEXT,
                Date DATE,
                visit_count INTEGER
            );

            TRUNCATE TABLE visits;
        """)

        log.info("Table visits created and truncated")

        conn.close()

        log.info("Connection closed")

    except Exception:
        log.exception("Error with table creation")
        raise


def ddl():
    create_db()
    create_tables()