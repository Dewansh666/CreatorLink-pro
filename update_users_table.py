import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
ALTER TABLE users ADD COLUMN password TEXT
""")

conn.commit()
conn.close()
