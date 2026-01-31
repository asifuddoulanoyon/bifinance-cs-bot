import sqlite3

conn = sqlite3.connect("support.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
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
    rating INTEGER
)
''')
conn.commit()
