import judge4
import flask,os
from flask import session,request
import markdown
from multiprocessing import Process
mdmodules = ["markdown.extensions.extra","markdown.extensions.codehilite","markdown.extensions.tables","markdown.extensions.toc"]#,"markdown_katex"
mdconfigs = {}
app = flask.Flask("PanuOJ")
app.secret_key = "PanuGame-Online-Judge"
def judge(code,rid,pid,username):
    judge4.sandbox(code,"R%07d"%rid,pid,"""g++ {name}.cpp -o test -lm -O2 -std=c++14 -w""")
    with open("R%07d.ans"%rid) as file:
        if eval(file.read().split("\n")[1]) == 100:
            if not pid in eval(getuserinfo(username)["aclist"]):
                temp = getuserinfo(username)
                dic = {i:eval(temp[i]) for i in temp}
                dic["accnt"] += 1
                dic["aclist"].append(pid)
                if pid in dic["uaclist"]:
                    dic["uaclist"].remove(pid)
                    dic["uaccnt"] -= 1
                save_conf(dic["uid"],dic)
        else:
            if not pid in eval(getuserinfo(username)["aclist"]):
                if not pid in eval(getuserinfo(username)["uaclist"]):
                    temp = getuserinfo(username)
                    dic = {i:eval(temp[i]) for i in temp}
                    dic["uaccnt"] += 1
                    dic["uaclist"].append(pid)
                    save_conf(dic["uid"],dic)
def getuserinfo(username):
    with open(f"usermapping/{username}.map") as file:
        uid = file.read()
    with open(f"users/{uid}.conf") as file:
        cont = file.read()
    dic = {}
    for i in cont.strip("\n").split("\n"):
        temp = i.strip(" ").split(" = ")
        dic[temp[0]] = temp[1]
    return dic
def getuserinfo_id(uid):
    with open(f"users/{uid}.conf") as file:
        cont = file.read()
    dic = {}
    for i in cont.strip("\n").split("\n"):
        temp = i.strip(" ").split(" = ")
        dic[temp[0]] = temp[1]
    return dic
def save_conf(uid,dic):
    with open(f"users/{uid}.conf","w") as file:
        for i in dic:
            if type(dic[i]) == str:
                file.write(f"""{i} = "{dic[i]}"\n""")
            else:
                file.write(f"""{i} = {dic[i]}\n""")
@app.route("/")
def mainpage():
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
        main = f"""<center><h3>你好，{username}，您已经通过了{getuserinfo(username)["accnt"]}题</h3>"""
        aclist = eval(getuserinfo(username)["aclist"])
        uaclist = eval(getuserinfo(username)["uaclist"])
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
        main = "<center>"
        aclist = []
        uaclist = []
    md = "| PID | 题目名称 | 是否通过 |\n| :---: | :---: | :---: |\n"
    i = 0
    while os.path.isfile("problem/%04d.title"%i):
        with open("problem/%04d.title"%i,encoding="UTF-8") as file:
            title = file.read().strip("\n")
        md += f"""| <a href="/problem/{"%04d"%i}"><font color=#000000>{"%04d"%i}</font></a> | {title} | """
        if "%04d"%i in aclist:
            md += "<font color=#0080FF>通过</font> |\n"
        elif "%04d"%i in uaclist:
            md += "<font color=#FF8000>未通过</font> |\n"
        else:
            md += "未做 |\n"
        i += 1
    main += markdown.markdown(md,extensions=mdmodules,extension_configs=mdconfigs) + "</center>"
    return flask.render_template("default.html",title="Welcome to PanuOJ",header="欢迎来到PanuOJ评测系统",userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc,main=main)
@app.route("/user/<uid>/")
def userpage(uid):
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    if os.path.isfile(f"users/{uid}.conf"):
        conf = getuserinfo_id(uid)
    else:
        conf = None
    main = ""
    if conf:
        if username == eval(conf["username"]):
            main += """<p><a href="/edit/conf">修改我的信息</a>&nbsp;&nbsp;&nbsp;<a href="/edit/mainpage">修改我的主页</a></p>"""
        main += f"""<p>{eval(conf["username"])}是{"男" if eval(conf["sex"]) == "male" else "女"}孩，提交过{eval(conf["accnt"])+eval(conf["uaccnt"])}题，通过{eval(conf["accnt"])}题</p>"""
        with open(f"""userpage/{eval(conf["username"])}.md""") as file:
            main += markdown.markdown(file.read(),extensions=mdmodules,extension_configs=mdconfigs)
        return flask.render_template("default.html",title="用户信息",header=eval(conf["username"]) + "的信息",userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc,main=main)
    else:
        return flask.render_template("default.html",title="用户信息",header="该用户不存在",userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc,main="<p>该用户不存在</p>")
@app.route("/record/<runid>/")
def get_record(runid):
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    if os.path.isfile(f"{runid}.ans"):
        with open(f"{runid}.ans") as file:
            cont = file.read().strip("\n").split("\n")
            userprob = [eval(i) for i in cont.pop(0).split(" ")]
    else:
        flask.abort(404)
        # return flask.render_template("default.html",title=runid,header=f"{runid}评测结果",main="<center>系统正在评测中，请耐心等待</center>")
    string = "| 测试点 | 评测结果 | 得分 | 占用内存 | 时间 |\n| :---: | :---: | :---: | :---: | :---: |\n"
    if cont:
        taskcnt = len(cont) - 1
        for i in range(1,len(cont)):
            temp = cont[i].strip(" ").split(" ")
            if temp[0] == "AC":
                string += f"| Test {i} | <font color=#0080FF>答案正确</font> | {100 // taskcnt} | {temp[1]} | {temp[2]}\n"        
            elif temp[0] == "WA":
                string += f"| Test {i} | <font color=#FF8000>答案错误</font> | 0 | {temp[1]} | {temp[2]}\n"
            elif temp[0] == "MLE":
                string += f"| Test {i} | <font color=#FF8000>内存超限</font> | 0 | {temp[1]} | {temp[2]}\n"
            elif temp[0] == "TLE":
                string += f"| Test {i} | <font color=#FF8000>时间超限</font> | 0 | {temp[1]} | {temp[2]}\n"
            elif temp[0] == "NOFE":
                string += f"| Test {i} | <font color=#FF8000>IO错误</font> | 0 | {temp[1]} | {temp[2]}\n"
            elif temp[0] == "CE":
                string += f"| Test {i} | <font color=#FF8000>编译错误</font> | 0 | {temp[1]} | {temp[2]}\n"
            elif temp[0] == "UKE":
                string += f"| Test {i} | <font color=#FF8000>未知错误</font> | 0 | {temp[1]} | {temp[2]}\n"
        string += f"""<p>提交者：{userprob[0]}&nbsp;&nbsp;&nbsp;题号：<a href="/problem/{userprob[1]}">{userprob[1]}</a>&nbsp;&nbsp;&nbsp;得分：{cont[0]}</p>"""
        md = markdown.markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
        if eval(cont[0]) == 100:
            return flask.render_template("record.html",title=runid,runid=runid,poptext="Accepted!",status="accepted",main=md,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
        else:
            return flask.render_template("record.html",title=runid,runid=runid,poptext="Unaccepted!",status="unaccepted",main=md,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
    else:
        string = "| 测试点 | 评测结果 | 得分 | 占用内存 | 时间 |\n| :---: | :---: | :---: | :---: | :---: |\n"
        string += "| Test 1 | <font color=#9FF9FF>正在评测</font> | 0 | 0B | 0.0s |\n"
        string += f"""<p>提交者：{userprob[0]}&nbsp;&nbsp;&nbsp;题号：<a href="/problem/{userprob[1]}">{userprob[1]}</a>&nbsp;&nbsp;&nbsp;得分：0</p>"""
        md = "<center>" + markdown.markdown(string,extensions=mdmodules,extension_configs=mdconfigs) + "</center>"
        return flask.render_template("default.html",title=runid,header=f"{runid}评测结果",main=md,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
@app.route("/problem/<pid>")
def problemshow(pid):
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    if os.path.isfile(f"problem/{pid}.md"):
        with open(f"problem/{pid}.md",encoding="UTF-8") as file:
            md = file.read()
        with open(f"problem/{pid}.title",encoding="UTF-8") as file:
            title = file.read()
        main = markdown.markdown(md,extensions=mdmodules,extension_configs=mdconfigs)
        main += f"""<p><a href="/submit/{pid}">提交</a></p>"""
        return flask.render_template("default.html",title=title,header=title,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc,main=main)
    else:
        return flask.render_template("default.html",title="题目",header="该题不存在",userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc,main="<p>该题不存在</p>")
@app.route("/login/",methods=["GET","POST"])
def login():
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if os.path.isfile(f"usermapping/{username}.map") and eval(getuserinfo(username)["password"]) == password:
            session["logged_in"] = True
            session["username"] = username
            session["uid"] = eval(getuserinfo(username)["uid"])
            return flask.redirect("/")
        else:
            flask.flash("用户名或密码错误")
            return flask.redirect("/login")
    html = """<form action="" method="post">
    <table>
    <tr><td>用户名</td><td><input type="text" name="username"/></td></tr>
    <tr><td>密码</td><td><input type="password" name="password"/></td></tr>
    <tr><td colspan="2"><button type="submit">提交</button></td></tr>
    </table>
</form>"""
    return flask.render_template("default.html",title="登录页面",header="登录页面",main=html,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
@app.route("/signin/",methods=["GET","POST"])
def signin():
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sex = request.form["sex"]
        if username.strip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") != "":
            flask.flash("用户名包含特殊字符")
            return flask.redirect("/signin")
        if len(username) < 3 or len(username) > 20:
            flask.flash("用户名必须为3到20位")
            return flask.redirect("/signin")
        if password.strip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") != "":
            flask.flash("密码包含特殊字符")
            return flask.redirect("/signin")
        if len(username) < 6 or len(username) > 20:
            flask.flash("密码必须为6到20位")
            return flask.redirect("/signin")
        if not os.path.isfile(f"usermapping/{username}.map"):
            with open(f"uids") as file:
                uid = eval(file.read())
            with open(f"uids","w") as file:
                file.write(str(uid + 1))
            with open(f"usermapping/{username}.map","w") as file:
                file.write("%06d"%uid)
            with open(f"""users/{"%06d"%uid}.conf""","w") as file:
                file.write(f"""username = "{username}"
password = "{password}"
sex = "{sex}"
accnt = 0
aclist = []
uaccnt = 0
uaclist = []
uid = "{"%06d"%uid}\"""")
            open(f"userpage/{username}.md","w").close()
            flask.flash("注册成功")
            session["logged_in"] = True
            session["username"] = username
            session["uid"] = eval(getuserinfo(username)["uid"])
            return flask.redirect("/")
        else:
            flask.flash("用户已存在")
            return flask.redirect("/signin")
    html = """<form action="" method="post">
    <table>
    <tr><td>用户名</td><td><input type="text" name="username"/></td></tr>
    <tr><td>密码</td><td><input type="password" name="password"/></td></tr>
    <tr><td>性别</td><td><input type="radio" name="sex" value="male" checked/><span>男</span>&nbsp;&nbsp;<input type="radio" name="sex" value="female"/><span>女</span></td></tr>
    <tr><td colspan="2"><button type="submit">提交</button></td></tr>
    </table>
</form>"""
    return flask.render_template("default.html",title="注册页面",header="注册页面",main=html,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
@app.route("/logout/")
def logout():
    session["logged_in"] = False
    return flask.redirect("/")
@app.route("/edit/conf/",methods=["GET","POST"])
def edit_configure_file():
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        flask.flash("出错了，您未登录，不可以修改个人信息")
        return flask.redirect("/")
    if request.method == "POST":
        ousername = username
        ouid = session.get("uid")
        username = request.form["username"]
        password = request.form["password"]
        sex = request.form["sex"]
        if username.strip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") != "":
            flask.flash("用户名包含特殊字符")
            return flask.redirect(flask.url_for("edit_configure_file"))
        if len(username) < 3 or len(username) > 20:
            flask.flash("用户名必须为3到20位")
            return flask.redirect(flask.url_for("edit_configure_file"))
        if password.strip("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_") != "":
            flask.flash("密码包含特殊字符")
            return flask.redirect(flask.url_for("edit_configure_file"))
        if len(password) < 6 or len(password) > 20:
            flask.flash("密码必须为6到20位")
            return flask.redirect(flask.url_for("edit_configure_file"))
        if (not os.path.isfile(f"usermapping/{username}.map")) or (ousername == username):
            if ousername != username:
                with open(f"usermapping/{username}.map","w") as file:
                    file.write(ouid)
                os.remove(f"usermapping/{ousername}.map")
                with open(f"userpage/{ousername}.md",encoding="UTF-8") as file:
                    md = file.read()
                with open(f"userpage/{username}.md","w",encoding="UTF-8") as file:
                    file.write(md)
                os.remove(f"userpage/{ousername}.md")
            temp = getuserinfo(username)
            dic = {i:eval(temp[i]) for i in temp}
            dic["username"] = username
            dic["password"] = password
            dic["sex"] = sex
            save_conf(dic["uid"],dic)
            flask.flash("修改成功")
            session["username"] = username
            return flask.redirect(flask.url_for("mainpage"))
        else:
            flask.flash("用户已存在")
            return flask.redirect(flask.url_for("edit_configure_file"))
    html = """<form action="" method="post">
    <table>
    <tr><td>用户名</td><td><input type="text" name="username"/></td></tr>
    <tr><td>密码</td><td><input type="password" name="password"/></td></tr>
    <tr><td>性别</td><td><input type="radio" name="sex" value="male" checked/><span>男</span>&nbsp;&nbsp;<input type="radio" name="sex" value="female"/><span>女</span></td></tr>
    <tr><td colspan="2"><button type="submit">提交</button></td></tr>
    </table>
</form>"""
    return flask.render_template("default.html",title="修改个人信息",header="修改个人信息",main=html,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
@app.route("/edit/mainpage/",methods=["GET","POST"])
def edit_mainpage():
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        flask.flash("出错了，您未登录，不可以修改个人主页")
        return flask.redirect("/")
    if request.method == "POST":
        markdown = request.form["markdown"]
        with open(f"userpage/{username}.md","w",encoding="UTF-8") as file:
            file.write(markdown)
        flask.flash("修改成功")
        return flask.redirect("/")
    with open(f"userpage/{username}.md",encoding="UTF-8") as file:
        omd = file.read()
    html = f"""<form action="" method="post">
<center>
<textarea name="markdown" rows="30" cols="50">{omd}</textarea>
<p><button type="submit">提交</button></p></center>
</form>"""
    return flask.render_template("default.html",title="修改个人主页",header="修改个人主页",main=html,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
@app.route("/submit/<pid>/",methods=["GET","POST"])
def submit(pid):
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        flask.flash("出错了，您未登录，不可以提交评测")
        return flask.redirect("/")
    if request.method == "POST":
        code = request.form["code"]
        with open("rids") as file:
            rid = eval(file.read())
        with open("rids","w") as file:
            file.write(str(rid + 1))
        with open("R%07d.ans"%rid,"w") as file:
            file.write(f"\"{username}\" \"{pid}\"\n")
        Process(target=judge,args=(code,rid,pid,username)).start()
        return flask.redirect(f"""/record/{"R%07d"%rid}""")
    html = """<style>div#main{left:30%;width:40%;}</style>
<link href="/static/codemirror/lib/codemirror.css" rel="stylesheet">
<script src="/static/codemirror/lib/codemirror.js"></script>
<script src="/static/codemirror/mode/clike/clike.js"></script>
<form action="" method="post">
<textarea id="codespace" name="code"></textarea>
<center><p><button type="submit">提交</button></p></center>
</form>
<script>
var editor = CodeMirror.fromTextArea(document.getElementById("codespace"),{
	lineNumbers: true,
    mode: "text/clike",
    indentUnit: 4,
    indentWithTabs: true
});
</script>"""
    return flask.render_template("default.html",title="提交代码",header="提交代码",main=html,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc)
@app.errorhandler(404)
def not_found(*args):
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    string = """# <center>哦，你要的页面没了，PanuOJ找不回来...</center>
<center>[尝试联系作者](mailto:23599488@qq.com)也许会有用</center>"""
    content = markdown.markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
    return flask.render_template("default.html",title="404 not found",header="页面未找到",main=content,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc),404
@app.errorhandler(403)
@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(503)
def othererror(*args):
    if session.get("logged_in"):
        userurl = "/user/" + session.get("uid")
        username = session.get("username")
        otherurl = "/logout"
        otherfunc = "登出"
    else:
        userurl = "/login"
        username = "登录"
        otherurl = "/signin"
        otherfunc = "注册"
    string = """# <center>哦，你遇到了未知错误，PanuOJ出现了问题...</center>
<center>[尝试联系作者](mailto:23599488@qq.com)也许会有用</center>"""
    content = markdown.markdown(string,extensions=mdmodules,extension_configs=mdconfigs)
    return flask.render_template("default.html",title="Unknown Error",header="未知错误",main=content,userurl=userurl,username=username,otherurl=otherurl,otherfunc=otherfunc),500
app.run(port=8080,debug=True)
