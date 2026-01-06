import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    name TEXT,
    bio TEXT,
    avatar TEXT
)
""")

cur.execute("""
INSERT OR IGNORE INTO users (username, name, bio, avatar)
VALUES (
    'dewansh',
    'Dewansh',
    'Student | Creator | Building my first SaaS 🚀',
    'avatar.png'
)
""")

conn.commit()
conn.close()
