import pandas as pd
import psycopg
import logging
import re
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

def flag(names, raw, mask, column, reason, new=None, level=logging.WARNING):
    for idx in raw.index[mask.fillna(False).astype(bool)]:
        msg = f"[{column}] {names[idx]}: {reason} | raw={raw[idx]!r}"
        if new is not None:
            msg += f" -> {new[idx]!r}"
        log.log(level, msg)

def parse_dates(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for fmt in DATE_FORMATS:
        todo = out.isna() & s.notna()
        if not todo.any():
            break
        out[todo] = pd.to_datetime(s[todo], format=fmt, errors="coerce")
    return out