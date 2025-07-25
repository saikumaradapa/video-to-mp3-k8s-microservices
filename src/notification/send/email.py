import smtplib
import os
import json
import logging
from email.message import EmailMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def notification(message):
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        receiver_address = message["username"]

        sender_address = os.getenv("SENDER_EMAIL", "no-reply@mp3video.com")  # dummy sender
        mailhog_host = os.getenv("MAILHOG_HOST", "mailhog")
        mailhog_port = int(os.getenv("MAILHOG_PORT", 1025))

        logging.info(f"📥 New task received for MP3 email notification")
        logging.info(f"Preparing email for user: {receiver_address}")

        msg = EmailMessage()
        msg.set_content(f"🎧 Your MP3 file is ready!\n\nFile ID: {mp3_fid}")
        msg["Subject"] = "✅ MP3 Ready for Download"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session = smtplib.SMTP(mailhog_host, mailhog_port)
        session.send_message(msg)
        session.quit()

        logging.info(f"📧 Email sent to {receiver_address}")
        return None

    except Exception as err:
        logging.error(f"❌ Error while sending email: {err}")
        return err
