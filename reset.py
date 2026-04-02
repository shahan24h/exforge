import sqlite3

conn = sqlite3.connect('data/leads.db')

# Fix malformed email and reset status
conn.execute("""
    UPDATE leads 
    SET email = 'manhattancleaningsolutions@gmail.com',
        status = 'approved_to_send'
    WHERE name = 'Manhattan Cleaning Solutions'
""")
conn.commit()

cursor = conn.cursor()
cursor.execute("SELECT name, email, status FROM leads WHERE name = 'Manhattan Cleaning Solutions'")
row = cursor.fetchone()
print(f"Fixed: {row[0]} | {row[1]} | {row[2]}")

conn.close()