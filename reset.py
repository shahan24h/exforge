import sqlite3

conn = sqlite3.connect('data/leads.db')
conn.execute("UPDATE leads SET status='new' WHERE status='rejected'")
conn.commit()
conn.close()
print('Reset done')