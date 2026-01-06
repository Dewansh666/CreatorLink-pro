import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cur = conn.cursor()

hashed = generate_password_hash("123456")

cur.execute(
    "UPDATE users SET password = ? WHERE username = ?",
    (hashed, "dewansh")
)

conn.commit()
conn.close()
