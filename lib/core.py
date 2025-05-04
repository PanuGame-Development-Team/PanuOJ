from constances import *
from uuid import uuid4 as _uuid
from datetime import datetime
from model import *
def lin(ls1,ls2):
    for i in ls1:
        if not i in ls2:
            return False
    return True
def split_access(user):
    l = {"admin":False,"view":False,"submit":False,"publish":False}
    if user.access & ACCESS["ADMIN"]:
        l["admin"] = True
    if user.access & ACCESS["VIEW"]:
        l["view"] = True
    if user.access & ACCESS["SUBMIT"]:
        l["submit"] = True
    if user.access & ACCESS["PUBLISH"]:
        l["publish"] = True
    return l
def syslog(message,category,uid=-1):
    log = Logging()
    log.uid = uid
    log.describe = message
    log.category = category
    log.date = datetime.now()
    db.session.add(log)
    db.session.commit()
def uuidgen():
    return _uuid().hex