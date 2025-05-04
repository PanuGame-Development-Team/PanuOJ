from flask import *
from ui import *
from model import *
from lib import *
from constances import *
from settings import *
from api import app as api_blueprint
from admin import app as admin_blueprint
from discuss import app as discuss_blueprint
app = Flask(APP_NAME)
app.secret_key = SECRET_KEY
for conf in CONFIG:
    app.config[conf] = CONFIG[conf]
db.init_app(app)
app.register_blueprint(api_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(discuss_blueprint)
app.add_template_filter(render_markdown,"render_markdown")
for i in judgers:
    judgers[i].init_app(app)
    judgers[i].start()
Thread(target=distribute_loop).start()
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
                    user.latest_login_time = datetime.now()
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
                    db.session.add(user)
                    db.session.commit()
                    flash("注册成功，请重新登录","success")
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
    paginate = Problem.query.filter(Problem.deleted==0).paginate(page=curpage,per_page=30,max_per_page=30)
    pagecnt = paginate.pages
    problems = paginate.items
    return render_template("problems.html",curpage=curpage,pagecnt=pagecnt,problems=problems,**default_dict(ses[1],request,user))
@app.route("/problems/<int:pid>",methods=["GET"])
@app.route("/problems/<int:pid>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def problem_show(ses,user,pid):
    problem = Problem.query.get(pid)
    if problem and (problem.deleted == 0 or user.access & ACCESS["ADMIN"]):
        return render_template("problem_show.html",problem=problem,**default_dict(ses[1],request,user))
    else:
        abort(404)
@app.route("/problems/random",methods=["GET"])
@app.route("/problems/random/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def random_problem(ses,user):
    problem = Problem.query.filter(Problem.deleted==0).order_by(func.random()).first()
    return redirect("/problems/%d/"%problem.id)
@app.route("/submit/<int:pid>",methods=["POST"])
@app.route("/submit/<int:pid>/",methods=["POST"])
@ACCESS_REQUIRE_HTML(["SUBMIT"])
def submit(ses,user,pid):
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
    print(request.form)
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
        judge_queue.append(rec.id)
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
        if judgers[judger].judger_online:
            if judgers[judger].judger_busy:
                stat[judger] = "busy"
            else:
                stat[judger] = "idle"
        else:
            stat[judger] = "offline"
    return render_template("judgerstatus.html",stat=stat,**default_dict(ses[1],request,user))
@app.route("/logout",methods=["GET"])
@app.route("/logout/",methods=["GET"])
def logout():
    res = redirect("/")
    res.delete_cookie("sessionid")
    return res
@app.route("/")
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
if __name__ == '__main__':
    app.run(host=HOST,port=PORT,debug=False)