import sqlite3

DB_NAME = "support.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            uid TEXT,
            email TEXT,
            active_case_id TEXT
        )
    ''')
    # Cases
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            user_id INTEGER,
            description TEXT,
            status TEXT,
            assigned_agent INTEGER,
            history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Agents
    c.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()    ''', (case_id, user_id, name, uid, email, description))
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
