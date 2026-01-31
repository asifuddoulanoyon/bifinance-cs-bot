import sqlite3

conn = sqlite3.connect("support.db", check_same_thread=False)
c = conn.cursor()

# Create cases table if not exists
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_rating INTEGER,
    agent_rating INTEGER
)
''')
conn.commit()
