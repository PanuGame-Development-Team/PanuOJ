from flask import *
from ui import *
from model import *
from lib import *
from constances import *
from settings import *
from api import app as api_blueprint
from admin import app as admin_blueprint
from discuss import app as discuss_blueprint
from sys import modules as sysmodules
from rmj import remotejudges,rmjqueue
app = Flask(APP_NAME)
app.secret_key = SECRET_KEY
for conf in CONFIG:
    app.config[conf] = CONFIG[conf]
db.init_app(app)
app.register_blueprint(api_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(discuss_blueprint)
app.add_template_filter(render_markdown,"render_markdown")
app.add_template_filter(combine,"combine")
if __name__ == "__main__" or "gunicorn" in sysmodules:
    for i in judgers:
        judgers[i].init_app(app)
        judgers[i].start()
    for i in userrecycler.pool:
        userrecycler.pool[i].app = app
    for i in rmjqueue.pool:
        rmjqueue.pool[i].app = app
@app.route("/",methods=["GET"])
def index():
    ses = readSession(request.cookies)
    if ses[0] == -1:
        return redirect("/login/")
    user = User.query.get(ses[0])
    if not user.access & ACCESS["VIEW"]:
        abort(403)
    announcements = Announcement.query.all()
    discussions = Discussion.query.order_by(Discussion.top.desc(),Discussion.id.desc()).limit(6).all()
    fortunes = [get_fortune() for i in range(5)]
    return render_template("index.html",fortunes=fortunes,announcements=announcements,discussions=discussions,**default_dict(ses[1],request,user))
@app.route("/login",methods=["GET","POST"])
@app.route("/login/",methods=["GET","POST"])
def login():
    ses = readSession(request.cookies)
    if ses[0] != -1:
        return redirect("/")
    if request.method == "GET":
        return render_template("login.html",**default_dict(ses[1],request,None,True))
    else:
        if lin(["username","password"],request.form):
            user = User.query.filter_by(username=request.form["username"]).first()
            if user:
                if check_password_hash(user.password,request.form["password"]):
                    db.session.add(user)
                    db.session.commit()
                    res = redirect("/")
                    res.set_cookie("sessionid",createSession(user.id,{}),max_age=8640000,samesite="Strict")
                    return res
                else:
                    flash("密码错误，请重新输入。","danger")
                    return redirect("/login/")
            elif len(request.form["username"]) >= 4 and len(request.form["username"]) <= 32:
                if len(request.form["password"]) >= 8:
                    user = User()
                    user.username = request.form["username"]
                    user.password = generate_password_hash(request.form["password"])
                    user.access = ACCESS["VIEW"]
                    user.verified = 0
                    user.verify_expireation = datetime.now() + timedelta(hours=3)
                    db.session.add(user)
                    db.session.commit()
                    flash("注册成功，请重新登录","success")
                    userrecycler.put(str(user.id))
                    syslog("用户%s注册"%user.username,S2NCATEGORY["SUSPICIOUS"],user.id)
                    return redirect("/login/")
                else:
                    flash("密码长度必须大于8位。","danger")
                    return redirect("/login/")
            else:
                flash("用户名长度必须在4-32位之间。","danger")
                return redirect("/login/")
        else:
            flash("表单信息不全，请重新输入。","danger")
            return redirect("/login/")
@app.route("/problems",methods=["GET"])
@app.route("/problems/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def problems(ses,user):
    curpage = int(request.args.get("page",1))
    problemset = request.args.get("problemset","PanuOJ.local")
    search = request.args.get("search","")
    if problemset in remotejudges:
        problems,pagecnt = remotejudges[problemset].getproblemlist(curpage,searchtext=search)
    else:
        problemset = "PanuOJ.local"
        paginate = Problem.query.filter(Problem.deleted==0)
        if search:
            for i in search.split(" "):
                if not i:
                    continue
                paginate = paginate.filter(Problem.title.like(f"%{i}%"))
        paginate = paginate.paginate(page=curpage,per_page=30,max_per_page=30)
        pagecnt = paginate.pages
        problems = paginate.items
    problemsets = ["PanuOJ.local"] + list(remotejudges.keys())
    suffix = {"problemset":problemset,"search":search}
    return render_template("problems.html",suffix=suffix,curpage=curpage,pagecnt=pagecnt,problems=problems,problemsets=problemsets,**default_dict(ses[1],request,user))
@app.route("/problems/<int:pid>",methods=["GET"])
@app.route("/problems/<int:pid>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def problem_show(ses,user,pid):
    problemset = request.args.get("problemset","PanuOJ.local")
    if problemset in remotejudges:
        problem,allow_submit = remotejudges[problemset].getproblem(pid)
        languages = list(remotejudges[problemset].languages)
    else:
        problemset = "PanuOJ.local"
        problem = Problem.query.get(pid)
        allow_submit = True
        languages = LANGUAGES
    if problem and (problem.deleted == 0 or user.access & ACCESS["ADMIN"]):
        discussions = Discussion.query.filter(Discussion.pid==pid).order_by(Discussion.id.desc()).limit(20).all()
        return render_template("problem_show.html",languages=languages,problemset=problemset,allow_submit=allow_submit,problem=problem,discussions=discussions,**default_dict(ses[1],request,user))
    else:
        abort(404)
@app.route("/problems/random",methods=["GET"])
@app.route("/problems/random/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def random_problem(ses,user):
    problem = Problem.query.filter(Problem.deleted==0).order_by(func.random()).first()
    return redirect("/problems/%d/"%problem.id)
@app.route("/submit/<pid>",methods=["POST"])
@app.route("/submit/<pid>/",methods=["POST"])
@ACCESS_REQUIRE_HTML(["SUBMIT"])
def submit(ses,user,pid):
    problemset = request.args.get("problemset","PanuOJ.local")
    if problemset in remotejudges:
        rec = Record()
        rec.code = request.form["code"]
        rec.O2 = 0
        rec.language = request.form["language"]
        rec.pid = None
        rec.rmjname = problemset
        rec.rmjpid = pid
        rec.uid = user.id
        rec.submit_time = datetime.now()
        rec.result = "WAITING"
        db.session.add(rec)
        db.session.commit()
        rmjqueue.put(dumps({"name":problemset,"record":rec.id,"user":user.id,"problem_id":pid}))
        return redirect("/record/%d"%rec.id)
    else:
        try:
            pid = int(pid)
        except:
            flash("题目不存在。","danger")
            return redirect("/")
        problem:Problem = Problem.query.get(pid)
        problem.submit += 1
        db.session.add(problem)
        db.session.commit()
        if not lin(["code","language"],request.form):
            flash("表单信息不全。","danger")
            return redirect("/problems/%d/"%pid)
        if not problem:
            flash("题目不存在。","danger")
            return redirect("/problems/")
        if user.access & ACCESS["SUBMIT"]:
            rec = Record()
            rec.code = request.form["code"]
            rec.O2 = 1 if request.form.get("O2") else 0
            rec.language = request.form["language"]
            rec.pid = pid
            rec.uid = user.id
            rec.submit_time = datetime.now()
            rec.result = "WAITING"
            db.session.add(rec)
            db.session.commit()
            judgequeue.put(str(rec.id))
            return redirect("/record/%d/"%rec.id)
        else:
            flash("权限不足。","danger")
            return redirect("/problems/%d/"%pid)
@app.route("/record/<int:rid>",methods=["GET"])
@app.route("/record/<int:rid>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["SUBMIT"])
def record(ses,user,rid):
    record:Record = Record.query.get(rid)
    if record:
        if record.uid == user.id or user.access & ACCESS["ADMIN"]:
            return render_template("record.html",record=record,**default_dict(ses[1],request,user))
        else:
            flash("权限不足。","danger")
            return redirect("/problems/")
    else:
        abort(404)
@app.route("/judgerstatus",methods=["GET"])
@app.route("/judgerstatus/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def judgerstatus(ses,user):
    stat = {}
    for judger in judgers:
        if judgers[judger].error:
            stat[judger] = "error"
        elif not judgers[judger].available:
            stat[judger] = "offline"
        elif judgers[judger].busy:
            stat[judger] = "busy"
        else:
            stat[judger] = "idle"
    return render_template("judgerstatus.html",stat=stat,**default_dict(ses[1],request,user))
@app.route("/logout",methods=["GET"])
@app.route("/logout/",methods=["GET"])
def logout():
    res = redirect("/")
    res.delete_cookie("sessionid")
    return res
@app.route("/user/<int:uid>",methods=["GET"])
@app.route("/user/<int:uid>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def user_show(ses,user,uid):
    showuser = User.query.get(uid)
    if not showuser:
        abort(404)
    discussions = Discussion.query.filter(Discussion.uid==uid).order_by(Discussion.id.desc()).limit(20).all()
    return render_template("user_show.html",showuser=showuser,discussions=discussions,**default_dict(ses[1],request,user))
@app.route("/user/<int:uid>/edit",methods=["GET","POST"])
@app.route("/user/<int:uid>/edit/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def user_edit(ses,user,uid):
    showuser = User.query.get(uid)
    if not showuser:
        abort(404)
    if not showuser.verified:
        flash("用户未验证。","danger")
        return redirect("/user/%d/"%uid)
    if user != showuser:
        flash("权限不足。","danger")
        return redirect("/user/%d/"%uid)
    if request.method == "POST":
        logoutrequired = False
        if lin(["icon"],request.files) and lin(["mainpage","oldpassword","password"],request.form):
            icon = request.files["icon"]
            if icon:
                filename = "static/icons/" + uuidgen() + "." + icon.filename.split(".")[-1]
                icon.save(filename)
                showuser.icon = "/" + filename
            showuser.mainpage = request.form["mainpage"]
            if request.form["oldpassword"] and request.form["password"]:
                if check_password_hash(showuser.password,request.form["oldpassword"]):
                    if len(request.form["password"]) >= 8:
                        showuser.password = generate_password_hash(request.form["password"])
                        logoutrequired = True
                    else:
                        flash("新密码长度必须大于8位。","danger")
                        return redirect("/user/%d/edit/"%uid)
                else:
                    flash("旧密码错误。","danger")
                    return redirect("/user/%d/edit/"%uid)
        else:
            flash("表单信息不全。","danger")
            return redirect("/user/%d/edit/"%uid)
        rmjuser = {}
        for i in remotejudges:
            if request.form.get("username-" + i) and request.form.get("password-" + i):
                rmjuser[i] = {"username":request.form.get("username-" + i),"password":request.form.get("password-" + i)}
        showuser.rmjuser = dumps(rmjuser)
        db.session.add(showuser)
        db.session.commit()
        flash("修改成功。","success")
        if not logoutrequired:
            return redirect("/user/%d/"%uid)
        else:
            return logout()
    return render_template("user_edit.html",remotejudges=remotejudges,showuser=showuser,**default_dict(ses[1],request,user))
@app.route("/verify",methods=["GET","POST"])
@app.route("/verify/",methods=["GET","POST"])
@app.route("/verify/<token>",methods=["GET"])
@app.route("/verify/<token>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def verify(ses,user,token=None):
    if not user.verified:
        if request.method == "POST":
            if not lin(["email"],request.form):
                flash("表单信息不全。","danger")
                return redirect("/verify/")
            if User.query.filter_by(email=request.form["email"]).first():
                flash("该邮箱已被注册。","danger")
                return redirect("/verify/")
            ses[1]["email"] = request.form["email"]
            ses[1]["emailexpireation"] = (datetime.now() + timedelta(minutes=5)).strftime("%Y/%m/%d %H:%M:%S")
            gentoken = uuidgen()
            ses[1]["token"] = gentoken
            mailqueue.put(dumps({"email":ses[1]["email"],"gentoken":gentoken}))
            saveSession(request.cookies.get("sessionid"),ses[1])
            return redirect("/verify/")
        if not "email" in ses[1] or datetime.now() > datetime.strptime(ses[1]["emailexpireation"],"%Y/%m/%d %H:%M:%S"):
            return render_template("verify.html",formtype="email",**default_dict(ses[1],request,user))
        if token:
            if token == ses[1]["token"]:
                user.verified = 1
                user.email = ses[1]["email"]
                user.access |= ACCESS["SUBMIT"]
                db.session.add(user)
                db.session.commit()
                flash("验证成功","success")
                syslog("用户%s验证成功，自动授予提交权限。"%user.username,S2NCATEGORY["INFO"],user.id)
                return redirect("/user/%d/"%user.id)
            else:
                flash("验证失败。","danger")
                syslog("用户%s验证失败"%user.username,S2NCATEGORY["SUSPICIOUS"],user.id)
                return redirect("/verify/")
        return render_template("verify.html",formtype="token",**default_dict(ses[1],request,user))
    else:
        flash("用户已验证。","danger")
        return redirect("/user/%d/"%user.id)
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(ospath.join(app.root_path,'static'),'favicon.ico',mimetype='image/jpeg')
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html",APP_VERSYM=APP_VERSYM,headertype="error"),404
@app.errorhandler(500)
def internal_server_error(e):
    err = traceback.format_exc()
    syslog("服务器错误：%s"%err.strip("\n").split("\n")[-1],S2NCATEGORY["ERROR"])
    return render_template("500.html",error=err,APP_VERSYM=APP_VERSYM,headertype="error"),500
if __name__ == "__main__":
    app.run(host=HOST,port=PORT,debug=False)