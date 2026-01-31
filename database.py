import sqlite3
from datetime import datetime

conn = sqlite3.connect("support.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    uid TEXT,
    email TEXT,
    problem TEXT,
    status TEXT,
    assigned_agent INTEGER,
    conversation TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    user_rating INTEGER,
    agent_rating INTEGER
)
''')
conn.commit()

def create_case(user_id, name, uid, email, problem):
    from random import randint
    case_id = f"BF-{randint(100000, 999999)}"
    now = datetime.now()
    c.execute(
        "INSERT INTO cases (case_id, user_id, name, uid, email, problem, status, conversation, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (case_id, user_id, name, uid, email, problem, "OPEN", problem, now, now)
    )
    conn.commit()
    return case_id

def append_message(case_id, sender, message):
    c.execute("SELECT conversation FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    if row:
        conv = row[0] + f"\n[{sender}] {message}"
        c.execute("UPDATE cases SET conversation=?, updated_at=? WHERE case_id=?", (conv, datetime.now(), case_id))
        conn.commit()

def get_user_active_case(user_id):
    c.execute("SELECT case_id FROM cases WHERE user_id=? AND status IN ('OPEN','IN_PROGRESS')", (user_id,))
    row = c.fetchone()
    return row[0] if row else None

def assign_agent(case_id, agent_id):
    c.execute("UPDATE cases SET assigned_agent=?, status='IN_PROGRESS' WHERE case_id=?", (agent_id, case_id))
    conn.commit()

def close_case(case_id):
    c.execute("UPDATE cases SET status='CLOSED' WHERE case_id=?", (case_id,))
    conn.commit()
