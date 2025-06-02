import random
import redis
import smtplib
from email.message import EmailMessage

r = redis.Redis(host="localhost", port=6379, db=0)

def generate_otp():
    return str(random.randint(100000, 999999))

# def send_otp_email(email: str, otp: str):
#     msg = EmailMessage()
#     msg.set_content(f"Your OTP code is: {otp}")
#     msg["Subject"] = "Verify your email"
#     msg["From"] = "your@email.com"
#     msg["To"] = email

#     with smtplib.SMTP("localhost") as server:
#         server.send_message(msg)

def store_otp(email: str, otp: str, expiration=120):
    r.setex(f"otp:{email}", expiration, otp)

def verify_otp(email: str, otp: str):
    saved = r.get(f"otp:{email}")
    return saved and saved.decode() == otp

import smtplib
from email.mime.text import MIMEText

def send_otp_email(email: str, otp: str):
    msg = MIMEText(f"Your OTP code is: {otp}")
    msg["Subject"] = "OTP Verification"
    msg["From"] = "your_email@gmail.com"
    msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("mahdirahimi1250@gmail.com", "skjhpalrywdqjxek")
        server.send_message(msg)