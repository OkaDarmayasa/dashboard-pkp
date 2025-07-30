import sqlite3
import json
import pandas as pd

DB_NAME = 'pkp-dashboard.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def seed_indikators_from_excel(excel_path):
    with open('schema.sql', 'r') as f:
        conn = get_connection()
        conn.executescript(f.read())
        conn.commit()
        conn.close()
    
    df = pd.read_excel(excel_path, index_col=None)
    df = df.reset_index(drop=True)

    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    conn = get_connection()
    c = conn.cursor()

    for _, row in df.iterrows():
        try:
            indikator = str(row.get("indikator_kinerja", "")).strip()
            capaian = str(row.get("capaian", "")).strip()
            kategori = str(row.get("kategori", "")).strip()
            nilai_raw = row.get("nilai", "")
            year = int(row.get("year", 2025))
            bukti = str(row.get("bukti", "")).strip()

            try:
                nilai = json.dumps(json.loads(nilai_raw))
            except:
                try:
                    nilai = json.dumps([int(x.strip()) for x in str(nilai_raw).split(",")])
                except:
                    nilai = json.dumps([nilai_raw])

            c.execute("""
                INSERT INTO Indikator (indikator, capaian, kategori, nilai, year, bukti)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                indikator,
                capaian,
                kategori,
                nilai,
                year,
                bukti
            ))
        except Exception as e:
            print(f"❌ Error inserting '{row.get('indikator_kinerja')}': {e}")

    conn.commit()
    conn.close()
    print("✅ Seeding complete.")

# ─── USER FUNCTIONS ──────────────────────────────────────────────────────────
def add_user(username, password, unit, is_admin=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password, unit, is_admin) VALUES (?, ?, ?, ?)", 
        (username, password, unit, is_admin)
    )
    conn.commit()
    conn.close()

def get_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    return c.fetchall()

# ─── INDIKATOR FUNCTIONS ─────────────────────────────────────────────────────

def add_indikator(name, capaian, kategori, nilai, year, bukti):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO Indikator (name, capaian, kategori, nilai,  year, bukti)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, capaian, kategori, json.dumps(nilai), year, bukti))
    conn.commit()
    conn.close()

def get_all_indikators():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Indikator")
    return c.fetchall()

def get_indikator_by_id(indikator_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Indikator WHERE id = ?", (indikator_id,))
    return c.fetchone()

def update_indikator(indikator_id, name, capaian, kategori, nilai, year, bukti):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE Indikator
        SET name = ?, capaian = ?, kategori = ?, nilai = ?, year = ?, bukti = ?
        WHERE id = ?
    """, (name, capaian, kategori, json.dumps(nilai), year, bukti, indikator_id))
    conn.commit()
    conn.close()

def delete_indikator(indikator_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM Indikator WHERE id = ?", (indikator_id,))
    conn.commit()
    conn.close()
