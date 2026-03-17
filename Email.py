import smtplib
from email.message import EmailMessage

EMAIL = "pricopealinw21@gmail.com"
PAROLA = "**********"

msg = EmailMessage()
msg["From"] = EMAIL
msg["To"] = EMAIL
msg["Subject"] = "TEST SIMPLU"
msg.set_content("Daca vezi acest mesaj, scriptul functioneaza.")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PAROLA)
        server.send_message(msg)

    print("EMAIL TRIMIS CU SUCCES!")
except Exception as e:
    print("EROARE:", e)
