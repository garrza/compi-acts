import sqlite3
from contextlib import contextmanager

import pandas as pd

from pipeline.config import DB_PATH, SCHEMA_PATH


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema() -> None:
    sql = SCHEMA_PATH.read_text()
    with get_connection() as conn:
        conn.executescript(sql)


def read_table(name: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql(f"SELECT * FROM {name}", conn)


def write_table(df: pd.DataFrame, name: str, if_exists: str = "append") -> None:
    with get_connection() as conn:
        df.to_sql(name, conn, if_exists=if_exists, index=False)
