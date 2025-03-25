import sqlite3
conn = sqlite3.connect("poker.db")

c = conn.cursor()

c.execute(
    """
    SELECT * FROM users
    """
)