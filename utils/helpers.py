import streamlit as st
import pandas as pd
import hashlib

@st.cache_resource
def init_connection():
    return st.connection('sqlite', type='sql')

def init_db():
    conn = init_connection()
    # Create users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            kategori_pengguna TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Create transactions table
    conn.execute("""
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

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(nama, email, password, kategori_pengguna):
    """Create a new user"""
    conn = init_connection()
    try:
        password_hash = hash_password(password)
        conn.execute("""
            INSERT INTO users (nama, email, password_hash, kategori_pengguna)
            VALUES (?, ?, ?, ?)
        """, (nama, email, password_hash, kategori_pengguna))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False  # Email already exists or other error

def verify_user(email, password):
    """Verify user credentials"""
    conn = init_connection()
    password_hash = hash_password(password)
    result = conn.query(
        """
        SELECT nama, kategori_pengguna FROM users 
        WHERE email = ? AND password_hash = ?
        """, 
        params={"email": email, "password_hash": password_hash}
    )
    
    if not result.empty and len(result) > 0:
        row = result.iloc[0]
        return (row['nama'], row['kategori_pengguna'])
    return None  # Returns (nama, kategori_pengguna) if valid, None otherwise

def get_user_info(email):
    """Get user information"""
    conn = init_connection()
    result = conn.query(
        """
        SELECT nama, kategori_pengguna FROM users WHERE email = ?
        """, 
        params={"email": email}
    )
    
    if not result.empty and len(result) > 0:
        row = result.iloc[0]
        return (row['nama'], row['kategori_pengguna'])
    return None

def save_transaction(email, tanggal, kategori_pengguna, jenis, item, jumlah, catatan):
    """Save transaction to database"""
    conn = init_connection()
    conn.execute("""
        INSERT INTO transactions (email, tanggal, kategori_pengguna, jenis, item, jumlah, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, str(tanggal), kategori_pengguna, jenis, item, jumlah, catatan))
    conn.commit()

def get_transactions(email):
    """Get all transactions for a user"""
    conn = init_connection()
    df = None
    try:
        df = conn.query(
            """
            SELECT tanggal AS Tanggal, jenis AS Jenis, item AS Item, jumlah AS Jumlah, catatan AS Catatan 
            FROM transactions 
            WHERE email = ?
            """, 
            params={"email": email}
        )
    except Exception as e:
        print("Error membaca data:", e)
        df = pd.DataFrame(columns=["Tanggal", "Jenis", "Item", "Jumlah", "Catatan"])
    return df

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
