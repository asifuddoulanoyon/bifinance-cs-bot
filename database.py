import sqlite3
from datetime import datetime

conn = sqlite3.connect("support.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    uid TEXT,
    email TEXT,
    active_case_id TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    user_id INTEGER,
    agent_id INTEGER,
    description TEXT,
    status TEXT,
    created_at TEXT,
    updated_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS agents (
    agent_id INTEGER PRIMARY KEY
)
""")

conn.commit()

def add_user(user_id, name, uid, email):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, uid, email) VALUES (?,?,?,?)",
                   (user_id, name, uid, email))
    conn.commit()

def create_case(user_id, description):
    cursor.execute("SELECT COUNT(*) FROM cases")
    count = cursor.fetchone()[0] + 1
    case_id = f"BF-2026-{count:06d}"
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO cases (case_id, user_id, description, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (case_id, user_id, description, "OPEN", now, now)
    )
    cursor.execute("UPDATE users SET active_case_id=? WHERE user_id=?", (case_id, user_id))
    conn.commit()
    return case_id

def is_agent(user_id):
    cursor.execute("SELECT 1 FROM agents WHERE agent_id=?", (user_id,))
    return cursor.fetchone() is not None

def add_agent(agent_id):
    cursor.execute("INSERT OR IGNORE INTO agents (agent_id) VALUES (?)", (agent_id,))
    conn.commit()

def remove_agent(agent_id):
    cursor.execute("DELETE FROM agents WHERE agent_id=?", (agent_id,))
    conn.commit()
def add_agent(agent_id):
    cursor.execute("INSERT OR IGNORE INTO agents (agent_id) VALUES (?)", (agent_id,))
    conn.commit()

def remove_agent(agent_id):
    cursor.execute("DELETE FROM agents WHERE agent_id=?", (agent_id,))
    conn.commit()
conn.commit()
