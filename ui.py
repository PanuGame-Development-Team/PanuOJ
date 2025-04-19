from lib import *
from settings import *
from constances import *
from model import *
from json import loads as _loads
def default_dict(session,request,user,loginpage=False):
    dic = dict()
    dic["loginpage"] = loginpage
    if loginpage:
        dic["firstvisit"] = False
    elif session.get("onevisit"):
        dic["firstvisit"] = False
    else:
        dic["firstvisit"] = True
        session["onevisit"] = True
        saveSession(request.cookies.get("sessionid"),session)
    
    dic["APP_NAME"] = APP_NAME
    dic["APP_VERSION"] = APP_VERSION
    dic["APP_VERSYM"] = APP_VERSYM
    dic["CATEGORIES"] = CATEGORY
    dic["SHOW_COLOR"] = SHOW_COLOR
    dic["ACCESS"] = ACCESS
    dic["LANGUAGES"] = LANGUAGES
    
    dic["user"] = user
    
    dic["split_access"] = split_access
    dic["jsonload"] = _loads
    return dic
def render_markdown(content):
    return content