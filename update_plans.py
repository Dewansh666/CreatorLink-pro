import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'")
cur.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT 'blue'")

cur.execute("""
CREATE TABLE IF NOT EXISTS clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id INTEGER
)
""")

conn.commit()
conn.close()
