import sqlite3
from datetime import datetime

DB_NAME = 'pkp-dashboard.db'

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    with open('schema.sql', 'r') as f:
        conn = get_connection()
        conn.executescript(f.read())
        conn.commit()
        conn.close()

def add_user(username, password, unit, is_admin=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, unit, is_admin) VALUES (?, ?, ?, ?)", 
              (username, password, unit, is_admin))
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

def add_job(user_id, job_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO jobs (user_id, job_name, start_date) VALUES (?, ?, ?)", 
              (user_id, job_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def update_job(job_id, new_start_date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE jobs SET start_date = ? WHERE id = ?", (new_start_date, job_id))
    conn.commit()
    conn.close()

def get_user_jobs(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE user_id = ?", (user_id,))
    return c.fetchall()

def update_job_stage(job_id, new_stage):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE jobs SET current_stage = ? WHERE id = ?", (new_stage, job_id))
    conn.commit()
    conn.close()

def get_all_jobs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT jobs.id, username, unit, job_name, current_stage, start_date FROM jobs JOIN users ON jobs.user_id = users.id")
    return c.fetchall()
