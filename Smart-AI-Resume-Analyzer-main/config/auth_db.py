import sqlite3

DB_NAME = "users.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_user_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()


def add_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def verify_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    result = cursor.fetchone()
    conn.close()
    return result is not None