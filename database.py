import sqlite3
from config import DB_FILE
from datetime import datetime

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE,
        user_id INTEGER,
        name TEXT,
        uid TEXT,
        email TEXT,
        description TEXT,
        status TEXT,
        assigned_agent INTEGER,
        messages TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_rating INTEGER,
        agent_rating INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def create_case(user_id, name, uid, email, description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    case_id = f"BF-{timestamp}"
    c.execute('''
        INSERT INTO cases (case_id, user_id, name, uid, email, description, status, messages)
        VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?)
    ''', (case_id, user_id, name, uid, email, description))
    conn.commit()
    conn.close()
    return case_id

def get_user_active_case(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE user_id=? AND status IN ('OPEN','IN_PROGRESS')", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_active_cases_for_agent(agent_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE assigned_agent=? AND status IN ('OPEN','IN_PROGRESS')", (agent_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def assign_case(case_id, agent_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE cases SET assigned_agent=?, status='IN_PROGRESS', updated_at=CURRENT_TIMESTAMP WHERE case_id=?", (agent_id, case_id))
    conn.commit()
    conn.close()

def append_message(case_id, sender, text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT messages FROM cases WHERE case_id=?", (case_id,))
    messages = c.fetchone()[0] or ""
    new_msg = f"{sender}: {text}\n"
    messages += new_msg
    c.execute("UPDATE cases SET messages=?, updated_at=CURRENT_TIMESTAMP WHERE case_id=?", (messages, case_id))
    conn.commit()
    conn.close()

def close_case(case_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE cases SET status='CLOSED', updated_at=CURRENT_TIMESTAMP WHERE case_id=?", (case_id,))
    conn.commit()
    conn.close()
