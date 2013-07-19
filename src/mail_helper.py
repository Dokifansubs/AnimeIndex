import smtplib
from email.mime.text import MIMEText

import settings

def send_email(template, header, email, **kwargs):
    fp = open("emails/%s.txt" % template, "rb")
    text = "".join(fp.readlines())
    fp.close()

    for key, value in kwargs.items():
        text = text.replace("%%%s%%" % key, "%s" % value)

    msg = MIMEText(text)
    msg["Subject"] = header
    msg["from"] = "no-reply@anime-index.org"
    msg["to"] = email

    s = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    if settings.SMTP_USE_TLS:
        s.starttls()
    if settings.SMTP_USE_AUTHENTICATION:
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    s.sendmail(msg["from"], [msg["to"]], msg.as_string())
    s.quit()
