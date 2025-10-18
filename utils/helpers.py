import sqlite3
import os
import pandas as pd

DB_PATH = "database/keuangan.db"

def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
