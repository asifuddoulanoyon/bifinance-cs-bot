import sqlite3
from config import DB_FILE

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
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_FILE)def add_user(user_id, name, uid, email):
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
