from flask import *
from ui import *
from model import *
from lib import *
from constances import *
from settings import *
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
    return render_template("admin/user.html",headertype="admin-user",curpage=curpage,pagecnt=pagecnt,users=users,**default_dict(ses[1],request,user))
@app.route("/data",methods=["GET"])
@app.route("/data/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def data(ses,user):
    curpage = int(request.args.get("page",1))
    pagination = Data.query.paginate(page=curpage,per_page=30,max_per_page=30)
    pagecnt = pagination.pages
    datas = pagination.items
    return render_template("admin/data.html",headertype="admin-data",curpage=curpage,pagecnt=pagecnt,datas=datas,**default_dict(ses[1],request))
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
            if request.form.get("read",None) == "on":
                access |= ACCESS["READ"]
            if request.form.get("update",None) == "on":
                access |= ACCESS["UPDATE"]
            if request.form.get("admin",None) == "on":
                access |= ACCESS["ADMIN"]
            aduser.access = access
            db.session.add(aduser)
            Session.query.filter_by(uid=uid).delete()
            db.session.commit()
            syslog("管理员%s修改用户信息"%user.username,S2NCATEGORY["INFO"],aduser.id)
            flash("修改成功，修改信息将通报。","success")
            return redirect("/admin/user/")
        else:
            flash("表单信息不全","danger")
            return redirect("/admin/user/edit/"+str(uid)+"/")
    return render_template("admin/user_edit.html",headertype="admin-user-edit",aduser=aduser,**default_dict(ses[1],request))
@app.route("/data/edit/<int:dataid>",methods=["GET","POST"])
@app.route("/data/edit/<int:dataid>/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["ADMIN"])
def data_edit(ses,user,dataid):
    addata = Data.query.get(dataid)
    if addata is None:
        flash("数据未找到","danger")
        return redirect("/admin/data/")
    if request.method == "POST":
        if lin(["machine_type","garage_id","error_id","detail","errdate"],request.form):
            addata.machine_type = request.form["machine_type"]
            addata.garage_id = request.form["garage_id"]
            addata.error_id = request.form["error_id"]
            addata.detail = request.form["detail"]
            addata.errdate = datetime.strptime(request.form["errdate"],"%Y-%m-%d")
            db.session.add(addata)
            db.session.commit()
            syslog("管理员%s修改数据信息"%user.username,S2NCATEGORY["INFO"],data=addata.id)
            flash("修改成功，修改信息将通报。","success")
            return redirect("/admin/data/")
        else:
            flash("表单信息不全","danger")
            return redirect("/admin/data/edit/"+str(dataid)+"/")
    return render_template("admin/data_edit.html",headertype="admin-data-edit",addata=addata,**default_dict(ses[1],request))