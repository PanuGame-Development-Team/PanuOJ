from smtplib import SMTP_SSL
from email.message import EmailMessage
def send_SMTP(message,From,to,passwd,service,subject):
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = "PanuOJ Verification <%s>" % From
        msg["To"] = to
        s = SMTP_SSL(service)
        s.login(From,passwd)
        s.send_message(msg)
        s.quit()
        return True
    except:
        return False