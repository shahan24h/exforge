import sqlite3

conn = sqlite3.connect('data/leads.db')
conn.execute("UPDATE leads SET status='approved' WHERE status IN ('no_email', 'email_failed', 'audited', 'report_ready', 'email_drafted', 'approved_to_send')")
conn.commit()

cursor = conn.cursor()
cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
for row in cursor.fetchall():
    print(f"  {row[0]:20} : {row[1]}")

conn.close()
print('Reset done')