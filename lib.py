from werkzeug.security import generate_password_hash,check_password_hash
from flask import jsonify,request,flash,redirect
from os import path as ospath
from constances import *
from settings import *
from model import *
from json import loads as _jsonloads,dumps as _jsondumps
from uuid import uuid4 as _uuid
from functools import wraps as _wraps
from sqlalchemy.sql.functions import func
from judgelib import *
import traceback
def lin(ls1,ls2):
    for i in ls1:
        if not i in ls2:
            return False
    return True
def split_access(user):
    l = {"admin":False,"view":False,"submit":False}
    if user.access & ACCESS["ADMIN"]:
        l["admin"] = True
    if user.access & ACCESS["VIEW"]:
        l["view"] = True
    if user.access & ACCESS["SUBMIT"]:
        l["submit"] = True
    return l
def readSession(cookie):
    if cookie.get("sessionid"):
        sessionid = cookie.get("sessionid")
        session = Session.query.filter_by(session_id=sessionid).first()
        if session:
            uid = session.uid
            content = _jsonloads(session.content)
            return uid,content
    return -1,{}
def saveSession(sessionid,content):
    session = Session.query.filter_by(session_id=sessionid).first()
    if session:
        session.content = _jsondumps(content)
        db.session.commit()
def createSession(uid,content):
    session = Session()
    session.uid = uid
    session.content = _jsondumps(content)
    session.session_id = _uuid().hex
    while Session.query.filter_by(session_id=session.session_id).first():
        session.session_id = _uuid().hex
    db.session.add(session)
    db.session.commit()
    return session.session_id
def syslog(message,category,uid=-1):
    log = Logging()
    log.uid = uid
    log.describe = message
    log.category = category
    log.date = datetime.now()
    db.session.add(log)
    db.session.commit()

def ACCESS_REQUIRE(access):
    def ACCESS_REQUIRE_DECORATOR(func):
        @_wraps(func)
        def ACCESS_REQUIRE_HANDLER(*args,**kwargs):
            ses = readSession(request.cookies)
            if ses[0] != -1:
                user = User.query.get(ses[0])
                if user:
                    for i in access:
                        if not user.access & ACCESS[i]:
                            return jsonify({"latestid":-1,"status":"AccessDenied"}),403
                    return func(ses,user,*args,**kwargs)
                else:
                    return jsonify({"latestid":-1,"status":"UserNotFound"}),404
            else:
                return jsonify({"latestid":-1,"status":"LoginRequired"}),402
        return ACCESS_REQUIRE_HANDLER
    return ACCESS_REQUIRE_DECORATOR
def ACCESS_REQUIRE_HTML(access):
    def ACCESS_REQUIRE_DECORATOR(func):
        @_wraps(func)
        def ACCESS_REQUIRE_HANDLER(*args,**kwargs):
            ses = readSession(request.cookies)
            if ses[0] != -1:
                user = User.query.get(ses[0])
                if user:
                    for i in access:
                        if not user.access & ACCESS[i]:
                            flash("权限不足","danger")
                            return redirect("/")
                    return func(ses,user,*args,**kwargs)
                else:
                    flash("用户不存在","danger")
                    return redirect("/")
            else:
                flash("请先登录","danger")
                return redirect("/login/")
        return ACCESS_REQUIRE_HANDLER
    return ACCESS_REQUIRE_DECORATOR