import sqlite3

# Connect to your database file (creates it if it doesn't exist)
conn = sqlite3.connect("finance.db")
c = conn.cursor()

# Create a new table
c.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    category TEXT,
    amount REAL
)
""")

conn.commit()
conn.close()

print("Table created successfully!")
