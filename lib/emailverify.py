from smtplib import SMTP_SSL
from email.message import EmailMessage
from json import loads
from .core import *
from .queues import RedisPoolQueue,BasicActivity
from settings import *
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
class MailActivity(BasicActivity):
    def __init__(self,id,smtp_service,smtp_user,smtp_passwd):
        super().__init__(id)
        self.smtp_service = smtp_service
        self.smtp_user = smtp_user
        self.smtp_passwd = smtp_passwd
    def process(self,callback,item):
        self.busy = True
        item = loads(item.decode("utf-8"))
        if not send_SMTP("你的验证令牌为：<strong><b><i>%s</b></i></strong>"%item["gentoken"],self.smtp_user,item["email"],self.smtp_passwd,self.smtp_service,"PanuOJ Email verification"):
            # self.error = True
            syslog("用户%s验证邮件发送失败，邮箱worker%d已挂起。"%(item["email"],self.id),S2NCATEGORY["WARNING"],self.id)
        self.busy = False
        callback(self.id)
senders = {i:MailActivity(i,SMTP_SERVICE,SMTP_USER,SMTP_PASSWD) for i in range(1)}
mailqueue = RedisPoolQueue(senders,"mail_queue")