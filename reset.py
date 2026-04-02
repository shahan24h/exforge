import sqlite3

conn = sqlite3.connect('data/leads.db')
conn.execute("UPDATE leads SET status='audited' WHERE status='report_ready'")
conn.commit()

cursor = conn.cursor()
cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
for row in cursor.fetchall():
    print(f"  {row[0]:12} : {row[1]}")

conn.close()
print('Reset done')