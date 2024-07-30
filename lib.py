from model import *
from werkzeug.security import check_password_hash,generate_password_hash
from importlib import import_module
from settings import *
def check_login(session):
    return session.get("logged_in")
def readsession(session):
    dic = dict(session)
    if dic.get("logged_in"):
        user = User.query.get(dic["id"])
    else:
        user = None
    dic["user"] = user
    return dic,user
def load_mods(modlist):
    mods = []
    for modname in modlist:
        mods.append(import_module(modname))
    for i in range(len(mods)):
        mods[i].init(mods)
    return mods
mods = load_mods(INSTALLED_MODS)