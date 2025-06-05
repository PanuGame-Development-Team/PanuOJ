from lib import *
from settings import *
from constances import *
from model import *
from json import loads as _loads
from markdown import markdown as _markdown
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
    if user:
        if not user.verified:
            flash("您的账号尚未通过验证，请前往主页进行验证。","warning")
        user.latest_login_time = datetime.now()
        db.session.add(user)
        db.session.commit()
    
    dic["split_access"] = split_access
    dic["jsonload"] = _loads
    dic["max"] = max
    dic["min"] = min
    
    dic["uquery"] = User.query
    dic["proquery"] = Problem.query
    dic["dquery"] = Discussion.query
    dic["recquery"] = Record.query
    dic["dcquery"] = DiscussionComment.query
    dic["annoquery"] = Announcement.query
    
    return dic
def render_markdown(md):
    mdmodules = ["markdown.extensions.extra","markdown.extensions.codehilite","markdown.extensions.tables","markdown.extensions.toc"]
    mdconfigs = {}
    return _markdown(md,extensions=mdmodules,extension_configs=mdconfigs)