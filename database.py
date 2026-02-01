import sqlite3

conn = sqlite3.connect("support.db", check_same_thread=False)
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    uid TEXT,
    email TEXT,
    active_case_id TEXT
)
""")

# Agents table
cursor.execute("""
CREATE TABLE IF NOT EXISTS agents(
    agent_id INTEGER PRIMARY KEY,
    name TEXT
)
""")

# Cases table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cases(
    case_id TEXT PRIMARY KEY,
    user_id INTEGER,
    agent_id INTEGER,
    description TEXT,
    status TEXT,
    created_at TEXT,
    updated_at TEXT
)
""")

conn.commit()
