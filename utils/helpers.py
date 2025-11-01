import sqlite3
import os
import pandas as pd
import hashlib

DB_PATH = "database/keuangan.db"

def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            kategori_pengguna TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            tanggal TEXT,
            kategori_pengguna TEXT,
            jenis TEXT,
            item TEXT,
            jumlah REAL,
            catatan TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(nama, email, password, kategori_pengguna):
    """Create a new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (nama, email, password_hash, kategori_pengguna)
            VALUES (?, ?, ?, ?)
        """, (nama, email, password_hash, kategori_pengguna))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Email already exists

def verify_user(email, password):
    """Verify user credentials"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute("""
        SELECT nama, kategori_pengguna FROM users 
        WHERE email = ? AND password_hash = ?
    """, (email, password_hash))
    result = cursor.fetchone()
    conn.close()
    return result  # Returns (nama, kategori_pengguna) if valid, None otherwise

def get_user_info(email):
    """Get user information"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nama, kategori_pengguna FROM users WHERE email = ?
    """, (email,))
    result = cursor.fetchone()
    conn.close()
    return result

def save_transaction(email, tanggal, kategori_pengguna, jenis, item, jumlah, catatan):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (email, tanggal, kategori_pengguna, jenis, item, jumlah, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, str(tanggal), kategori_pengguna, jenis, item, jumlah, catatan))
    conn.commit()
    conn.close()

def get_transactions(email):
    import pandas as pd
    conn = sqlite3.connect(DB_PATH)
    df = None
    try:
        df = pd.read_sql_query("SELECT tanggal AS Tanggal, jenis AS Jenis, item AS Item, jumlah AS Jumlah, catatan AS Catatan FROM transactions WHERE email = ?", conn, params=(email,))
    except Exception as e:
        print("Error membaca data:", e)
        df = pd.DataFrame(columns=["Tanggal", "Jenis", "Item", "Jumlah", "Catatan"])
    conn.close()
    return df
