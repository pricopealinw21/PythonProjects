import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime


EMAIL_EMITENT = "pricopealinw21@gmail.com"
EMAIL_DESTINATAR = "pricopealinw21@gmail.com"
PAROLA_APLICATIE = "******************"

SURSE = ["https://stirileprotv.ro/"]

DICTIONAR_RISC = {
    "CRITIC": ["atentat", "explozie", "atac"],
    "INALT": ["sri", "guvern"],
    "MEDIU": ["protest"]
}

PRAG_ALERTA = 10
# ==========================================


def trimite_mail_alerta(subiect, mesaj):
    try:
        msg = MIMEText(mesaj, "plain", "utf-8")
        msg["Subject"] = subiect
        msg["From"] = EMAIL_EMITENT
        msg["To"] = EMAIL_DESTINATAR

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_EMITENT, PAROLA_APLICATIE)
            server.send_message(msg)

        print(">>> EMAIL TRIMIS CU SUCCES!")
        return True

    except Exception as e:
        print("EROARE TRIMITERE MAIL:", e)
        return False


def calculeaza_scor(text):
    scor = 0
    cuvinte_gasite = []

    for nivel, cuvinte in DICTIONAR_RISC.items():
        for cuvant in cuvinte:
            if cuvant.lower() in text.lower():
                cuvinte_gasite.append(cuvant.upper())

                if nivel == "CRITIC":
                    scor += 10
                elif nivel == "INALT":
                    scor += 5
                elif nivel == "MEDIU":
                    scor += 2

    return scor, cuvinte_gasite


def analizeaza_site(url):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Se scanează: {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        raspuns = requests.get(url, headers=headers, timeout=10)

        if raspuns.status_code != 200:
            print("Eroare acces site.")
            return

        soup = BeautifulSoup(raspuns.text, "html.parser")

        titluri = set()


        for tag in soup.find_all(["h2", "h3"]):
            text = tag.get_text(strip=True)

            if len(text) > 20:
                titluri.add(text)

        print(f"Am găsit {len(titluri)} titluri unice.\n")

        for titlu in titluri:
            scor, cuvinte = calculeaza_scor(titlu)

            if scor >= PRAG_ALERTA:
                print(f"!!! ALERTĂ: {titlu}")
                print(f"Scor: {scor} | Cuvinte: {cuvinte}")

                subiect = f"ALERTĂ SECURITATE - Scor {scor}"
                mesaj = f"""
Titlu: {titlu}

Sursă: {url}

Scor: {scor}
Cuvinte detectate: {', '.join(cuvinte)}

Ora detectării: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                trimite_mail_alerta(subiect, mesaj)
                return

        print("Nu s-au găsit alerte peste prag.")

    except Exception as e:
        print("EROARE GENERALĂ:", e)




print("Sistem pornit...\n")

for site in SURSE:
    analizeaza_site(site)