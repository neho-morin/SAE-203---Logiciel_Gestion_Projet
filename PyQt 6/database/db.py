import sqlite3
from config.settings import DATABASE_PATH
from database.models import SCHEMA


_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row  # accès aux colonnes par nom
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


def init_db() -> None:
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()


def close_db() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
