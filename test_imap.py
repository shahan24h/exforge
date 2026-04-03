import imaplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# Create a test email message
msg = MIMEMultipart()
msg["From"]    = f"Test <{SMTP_USER}>"
msg["To"]      = SMTP_USER
msg["Subject"] = "Test - IMAP Sent folder save"
msg.attach(MIMEText("This is a test email to verify Sent folder saving works.", "plain", "utf-8"))

# Try saving to Sent folder
print(f"Connecting to IMAP: {SMTP_HOST}")
imap = imaplib.IMAP4_SSL(SMTP_HOST)
imap.login(SMTP_USER, SMTP_PASS)
print("Login successful")

result = imap.append(
    "Sent",
    "\\Seen",
    imaplib.Time2Internaldate(datetime.now(timezone.utc)),
    msg.as_bytes()
)
print(f"Append result: {result}")
imap.logout()
print("Done — check your Sent folder now")