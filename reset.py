import sqlite3

conn = sqlite3.connect('data/leads.db')

# Reset all processed leads back to audited for report regeneration
conn.execute("UPDATE leads SET status='audited' WHERE status IN ('report_ready', 'email_drafted', 'approved_to_send')")
conn.commit()

cursor = conn.cursor()
cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
for row in cursor.fetchall():
    print(f"  {row[0]:20} : {row[1]}")

conn.close()
print('Reset done')