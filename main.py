from judge5 import judge
from settings import *
from lib import *
from model import *
from forms import *
from ui import *
from flask import *
from flask_bootstrap import Bootstrap
from multiprocessing import Process
app = Flask(APP_NAME)
app.secret_key = SECRET_KEY
for config in APP_CONFIG:
    app.config[config] = APP_CONFIG[config]
app.add_template_filter(bs4_render_table,"render_table")
app.add_template_filter(render_markdown,"render_markdown")
for mod in mods:
    if mod.use_route:
        app.register_blueprint(mod.app,url_prefix=f"/mod/{mod.name}")
bs = Bootstrap(app)
db.init_app(app)
@app.route("/",methods=["GET","POST"])
def index():
    sesdic,currentuser = readsession(session)
    if request.method == "GET":
        return render_template("index.html",sesdic=sesdic,mods=mods,**sesdic)
    else:
        forms = {mod.name:{} for mod in mods}
        for i in request.form:
            for mod in mods:
                if mod.use_mainpage and mod.mainpage_allowpost and i.startswith(mod.name + "-"):
                    forms[mod.name][i.replace(mod.name + "-","",1)] = request.form[i]
        for mod in mods:
            if forms[mod.name] != {}:
                return mod.handle_mainpagepost(forms[mod.name])
@app.route("/problems",methods=["GET"])
@app.route("/problems/",methods=["GET"])
def problems():
    sesdic,currentuser = readsession(session)
    table = [["PID","题目名称","是否通过"]]
    for problem in Problem.query.all():
        table.append([f"""<a href="/problems/{problem.id}"><font color="{BLACK}">{problem.id}</font></a>""",f"""<a href="/problems/{problem.id}"><font color="{BLACK}">{problem.title}</font></a>"""])
        if check_login(sesdic):
            up = UserProblem.query.filter(UserProblem.user_id == currentuser.id).filter(UserProblem.problem_id == problem.id).first()
        else:
            up = None
        if up and up.score == 100:
            table[-1].append(f"""<font color="{PRIMARYCOLOR}">通过</font>""")
        elif up:
            table[-1].append(f"""<font color="{SECONDARYCOLOR}">未通过</font>""")
        else:
            table[-1].append("未做")
    return render_template("problems.html",table=table,mods=mods,**sesdic)
@app.route("/problems/<int:pid>",methods=["GET","POST"])
@app.route("/problems/<int:pid>/",methods=["GET","POST"])
def problemshow(pid):
    sesdic,currentuser = readsession(session)
    if not check_login(sesdic):
        flash("请先登录","danger")
        return redirect("/login")
    problem = Problem.query.get(pid)
    if request.method == "GET":
        if problem:
            return render_template("problem_show.html",problem=problem,mods=mods,**sesdic)
        else:
            abort(404)
    else:
        if "code" in request.form:
            code = request.form["code"]
            rid = Record.query.count()
            Process(target=judge,args=(app,code,problem,currentuser)).start()
            return redirect(f"/record/{rid+1}")
        abort(400)
@app.route("/login",methods=["GET","POST"])
@app.route("/login/",methods=["GET","POST"])
def login():
    if check_login(session):
        return redirect("/logout")
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter(User.username == username).first()
        if user:
            if check_password_hash(user.password,password):
                session["logged_in"] = True
                session["id"] = user.id
                flash("登录成功","success")
                return redirect("/")
            else:
                flash("密码错误","danger")
                return redirect("/login")
        else:
            user = User()
            user.username = username
            user.password = generate_password_hash(password)
            db.session.add(user)
            db.session.commit()
            flash("注册成功，请重新登录","success")
            return redirect("/login")
    return render_template("login.html",mods=mods,form=form)
@app.route("/record/<int:rid>",methods=["GET"])
@app.route("/record/<int:rid>/",methods=["GET"])
def get_record(rid):
    sesdic,currentuser = readsession(session)
    record = Record.query.get(rid)
    table = [["测试点","评测结果","得分","占用内存","时间"]]
    if record:
        detail = eval(record.detail)
        i = 1
        for task in detail:
            if task[0] == "AC":
                table.append([f"Test {i}",f"""<font color="{PRIMARYCOLOR}">答案正确</font>""",round(100/len(detail),2),task[1],task[2]])       
            elif task[0] == "WA":
                table.append([f"Test {i}",f"""<font color="{SECONDARYCOLOR}">答案错误</font>""",0,task[1],task[2]])
            elif task[0] == "MLE":
                table.append([f"Test {i}",f"""<font color="{SECONDARYCOLOR}">内存超限</font>""",0,task[1],task[2]])
            elif task[0] == "TLE":
                table.append([f"Test {i}",f"""<font color="{SECONDARYCOLOR}">时间超限</font>""",0,task[1],task[2]])
            elif task[0] == "IE":
                table.append([f"Test {i}",f"""<font color="{SECONDARYCOLOR}">内部错误</font>""",0,task[1],task[2]])
            elif task[0] == "CE":
                table.append([f"Test {i}",f"""<font color="{SECONDARYCOLOR}">编译错误</font>""",0,task[1],task[2]])
            elif task[0] == "UKE":
                table.append([f"Test {i}",f"""<font color="{SECONDARYCOLOR}">未知错误</font>""",0,task[1],task[2]])
            i += 1
        juser = User.query.get(record.user_id)
        jproblem = Problem.query.get(record.problem_id)
        score = record.score
        string = f"""<p>提交者：{juser.username}&nbsp;&nbsp;&nbsp;题目：<a href="/problems/{jproblem.id}">{jproblem.title}</a>&nbsp;&nbsp;&nbsp;得分：{score}</p>"""
        return render_template("record.html",status="accepted" if score == 100 else "unaccepted",table=table,mods=mods,**sesdic)
    else:
        table = [["测试点","评测结果","得分","占用内存","时间"]]
        table.append(["Test 1","未知（可能原因：程序未完成评测，记录不存在）","0","0B","0.0s"])
        string = f"""<p>提交者：未知&nbsp;&nbsp;&nbsp;题目：未知&nbsp;&nbsp;&nbsp;得分：未知</p>"""
        return render_template("default.html",htmltext=string,mods=mods,**sesdic)
@app.route("/logout",methods=["GET"])
@app.route("/logout/",methods=["GET"])
def logout():
    session.clear()
    return redirect("/")
@app.errorhandler(404)
def not_found(*args):
    sesdic,currentuser = readsession(session)
    return render_template("404.html",fluid=True,mods=mods,**sesdic),404
@app.errorhandler(500)
def othererror(*args):
    sesdic,currentuser = readsession(session)
    string = """# <center>哦，你遇到了未知错误，PanuOJ出现了问题...</center>
<center>[尝试联系作者](mailto:23599488@qq.com)也许会有用</center>"""
    content = render_markdown(string)
    return render_template("default.html",htmltext=content,mods=mods,**sesdic),500
if __name__ == "__main__":
    app.run(host=HOST,port=PORT,debug=DEBUG)
