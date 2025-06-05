from flask import *
from ui import *
from model import *
from lib import *
from constances import *
from settings import *
from zipfile import ZipFile
app = Blueprint("admin","admin",url_prefix="/admin")
@app.route("/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def index(ses,user):
    return render_template("admin/index.html",headertype="admin",**default_dict(ses[1],request,user))
@app.route("/user",methods=["GET"])
@app.route("/user/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def user(ses,user):
    curpage = int(request.args.get("page",1))
    pagination = User.query.paginate(page=curpage,per_page=30,max_per_page=30)
    pagecnt = pagination.pages
    users = pagination.items
    return render_template("admin/user.html",curpage=curpage,pagecnt=pagecnt,users=users,fluid=True,**default_dict(ses[1],request,user))
@app.route("/problem",methods=["GET"])
@app.route("/problem/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def problem(ses,user):
    curpage = int(request.args.get("page",1))
    pagination = Problem.query.filter(Problem.deleted==0).paginate(page=curpage,per_page=30,max_per_page=30)
    pagecnt = pagination.pages
    problems = pagination.items
    return render_template("admin/problem.html",curpage=curpage,pagecnt=pagecnt,problems=problems,fluid=True,**default_dict(ses[1],request,user))
@app.route("/announcement",methods=["GET"])
@app.route("/announcement/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def announcement(ses,user):
    announcements = Announcement.query.all()
    return render_template("admin/announcement.html",announcements=announcements,fluid=True,**default_dict(ses[1],request,user))
@app.route("/user/edit/<int:uid>",methods=["GET","POST"])
@app.route("/user/edit/<int:uid>/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def user_edit(ses,user,uid):
    aduser = User.query.get(uid)
    if aduser is None:
        flash("用户未找到","danger")
        return redirect("/admin/user/")
    if request.method == "POST":
        if lin(["password"],request.form):
            access = 0
            if request.form["password"]:
                aduser.password = generate_password_hash(request.form["password"])
            if request.form.get("view",None) == "on":
                access |= ACCESS["VIEW"]
            if request.form.get("submit",None) == "on":
                access |= ACCESS["SUBMIT"]
            if request.form.get("admin",None) == "on":
                access |= ACCESS["ADMIN"]
            if request.form.get("publish",None) == "on":
                access |= ACCESS["PUBLISH"]
            if not aduser.verified and aduser.access != access:
                flash("用户仍未通过验证，权限修改被驳回。","danger")
                return redirect("/admin/user/edit/" + str(uid) + "/")
            aduser.access = access
            db.session.add(aduser)
            Session.query.filter_by(uid=uid).delete()
            db.session.commit()
            syslog("管理员%s修改用户信息"%user.username,S2NCATEGORY["INFO"],aduser.id)
            flash("修改成功，修改信息将通报。","success")
            return redirect("/admin/user/")
        else:
            flash("表单信息不全","danger")
            return redirect("/admin/user/edit/" + str(uid) + "/")
    return render_template("admin/user_edit.html",aduser=aduser,**default_dict(ses[1],request,user))
@app.route("/problem/edit/<int:pid>",methods=["GET","POST"])
@app.route("/problem/edit/<int:pid>/",methods=["GET","POST"])
@app.route("/problem/add",methods=["GET","POST"])
@app.route("/problem/add/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def problem_edit(ses,user,pid=None):
    if pid is None:
        adpro = Problem()
        adpro.title = ""
        adpro.time_limit = 1000
        adpro.memory_limit = 65536
        adpro.background = ""
        adpro.description = ""
        adpro.inputformat = ""
        adpro.outputformat = ""
        adpro.sample = "[]"
        adpro.hint = ""
        adpro.testcases_zip = ""
        adpro.testcases = 0
    else:
        adpro:Problem = Problem.query.get(pid)
        if adpro is None:
            flash("题目未找到","danger")
            return redirect("/admin/problem/")
    if request.method == "POST":
        if lin(["title","time_limit","memory_limit","background","description","inputformat","outputformat","sample","hint"],request.form):
            try:
                adpro.time_limit = int(request.form["time_limit"])
                adpro.memory_limit = int(request.form["memory_limit"])
                adpro.sample = json.dumps(json.loads(request.form["sample"]))
            except:
                flash("时间限制或内存限制格式错误","danger")
                return redirect("/admin/problem/edit/" + str(pid) + "/")
            adpro.title = request.form["title"]
            adpro.background = request.form["background"]
            adpro.description = request.form["description"]
            adpro.inputformat = request.form["inputformat"]
            adpro.outputformat = request.form["outputformat"]
            adpro.hint = request.form["hint"]
            if request.files.get("testcases_zip",None):
                try:
                    filename = "testcases/" + uuidgen() + ".zip"
                    request.files["testcases_zip"].save(filename)
                    zipfile = ZipFile(filename)
                    i = 1
                    namelist = zipfile.namelist()
                    while f"test{i}.in" in namelist and f"test{i}.ans" in namelist:
                        i += 1
                    adpro.testcases = i - 1
                    adpro.testcases_zip = filename
                except:
                    flash("测试数据格式错误","danger")
                    return redirect("/admin/problem/edit/" + str(pid) + "/")
            db.session.add(adpro)
            db.session.commit()
            if pid:
                syslog("管理员%s修改题目 %d 信息"%(user.username,pid),S2NCATEGORY["INFO"])
                flash("修改成功，修改信息将通报。","success")
            else:
                syslog("管理员%s添加题目 %d"%(user.username,adpro.id),S2NCATEGORY["INFO"])
                flash("添加成功，添加信息将通报。","success")
            return redirect("/admin/problem/")
        else:
            flash("表单信息不全","danger")
            if pid:
                return redirect("/admin/problem/edit/" + str(pid) + "/")
            else:
                return redirect("/admin/problem/add/")
    return render_template("admin/problem_edit.html",adpro=adpro,**default_dict(ses[1],request,user))
@app.route("/problem/delete/<int:pid>",methods=["GET"])
@app.route("/problem/delete/<int:pid>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def problem_delete(ses,user,pid):
    adpro = Problem.query.get(pid)
    if adpro is None:
        flash("题目未找到","danger")
        return redirect("/admin/problem/")
    adpro.deleted = 1
    original_title = adpro.title
    new_title = original_title + "-deleted"
    cnt = 0
    while Problem.query.filter(Problem.title==new_title).count() != 0:
        cnt += 1
        new_title = original_title + "-deleted-" + str(cnt)
    adpro.title = new_title
    db.session.add(adpro)
    db.session.commit()
    syslog("管理员%s删除题目 %d"%(user.username,pid),S2NCATEGORY["INFO"])
    flash("删除成功，删除信息将通报。","success")
    return redirect("/admin/problem/")
@app.route("/announcement/edit/<int:annoid>",methods=["GET","POST"])
@app.route("/announcement/edit/<int:annoid>/",methods=["GET","POST"])
@app.route("/announcement/add",methods=["GET","POST"])
@app.route("/announcement/add/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def announcement_edit(ses,user,annoid=None):
    if annoid is None:
        adanno = Announcement()
        adanno.title = ""
        adanno.content = ""
        adanno.created_time = datetime.now()
    else:
        adanno:Announcement = Announcement.query.get(annoid)
        if adanno is None:
            flash("公告未找到","danger")
            return redirect("/admin/announcement/")
    if request.method == "POST":
        if lin(["title","content"],request.form):
            adanno.title = request.form["title"]
            adanno.content = request.form["content"]
            db.session.add(adanno)
            db.session.commit()
            if annoid:
                syslog("管理员%s修改公告 %d 信息"%(user.username,annoid),S2NCATEGORY["INFO"])
                flash("修改成功，修改信息将通报。","success")
            else:
                syslog("管理员%s添加公告 %d"%(user.username,adanno.id),S2NCATEGORY["INFO"])
                flash("添加成功，添加信息将通报。","success")
            return redirect("/admin/announcement/")
        else:
            flash("表单信息不全","danger")
            if annoid:
                return redirect("/admin/announcement/edit/" + str(annoid) + "/")
            else:
                return redirect("/admin/announcement/add/")
    return render_template("admin/announcement_edit.html",adanno=adanno,**default_dict(ses[1],request,user))
@app.route("/announcement/delete/<int:annoid>",methods=["GET"])
@app.route("/announcement/delete/<int:annoid>/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def announcement_delete(ses,user,annoid):
    adanno = Announcement.query.get(annoid)
    if adanno is None:
        flash("公告未找到","danger")
        return redirect("/admin/announcement/")
    db.session.delete(adanno)
    db.session.commit()
    syslog("管理员%s删除公告 %d"%(user.username,annoid),S2NCATEGORY["INFO"])
    flash("删除成功，删除信息将通报。","success")
    return redirect("/admin/announcement/")
@app.route("/discussion",methods=["GET"])
@app.route("/discussion/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def discussion(ses,user):
    curpage = int(request.args.get("page",1))
    pagination = Discussion.query.paginate(page=curpage,per_page=30,max_per_page=30)
    pagecnt = pagination.pages
    discussions = pagination.items
    return render_template("admin/discussion.html",curpage=curpage,pagecnt=pagecnt,discussions=discussions,**default_dict(ses[1],request,user))
@app.route("/discussion/edit/<int:did>",methods=["GET","POST"])
@app.route("/discussion/edit/<int:did>/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def discussion_edit(ses,user,did):
    addis = Discussion.query.get(did)
    if addis is None:
        flash("讨论未找到","danger")
        return redirect("/admin/discussion/")
    if request.method == "POST":
        if lin(["title","content"],request.form):
            addis.title = request.form["title"]
            addis.content = request.form["content"]
            try:
                addis.pid = int(request.form["pid"])
                problem = Problem.query.get(addis.pid)
                if not problem or problem.deleted:
                    raise ValueError("Problem not found.")
            except:
                flash("输入数据有误：题目编号为整数且对应题目存在。","danger")
                return redirect("/admin/discussion/edit/" + str(did) + "/")
            if request.form.get("top",None) == "on":
                addis.top = 1
            else:
                addis.top = 0
            db.session.add(addis)
            db.session.commit()
            syslog("管理员%s修改讨论 %d 信息"%(user.username,did),S2NCATEGORY["INFO"])
            flash("修改成功，修改信息将通报。","success")
            return redirect("/admin/discussion/")
        else:
            flash("表单信息不全","danger")
            return redirect("/admin/discussion/edit/" + str(did) + "/")
    return render_template("admin/discussion_edit.html",discussion=addis,**default_dict(ses[1],request,user))