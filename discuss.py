from flask import *
from ui import *
from model import *
from lib import *
from constances import *
from settings import *
app = Blueprint("discuss","discuss",url_prefix="/discuss")
@app.route("/",methods=["GET"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def index(ses,user):
    curpage = int(request.args.get("page",1))
    pagination = Discussion.query.order_by(Discussion.id.desc()).paginate(page=curpage,per_page=30,max_per_page=30)
    pagecnt = pagination.pages
    discussions = pagination.items
    return render_template("discuss/index.html",curpage=curpage,pagecnt=pagecnt,discussions=discussions,**default_dict(ses[1],request,user))
@app.route("/<int:did>",methods=["GET","POST"])
@app.route("/<int:did>/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["VIEW"])
def discuss(ses,user,did):
    discussion = Discussion.query.get(did)
    if discussion is None:
        abort(404)
    if request.method == "POST":
        if not lin(["comment"],request.form) or not request.form["comment"]:
            flash("请填写评论内容","warning")
            return redirect("/discuss/%d/"%did)
        comment = DiscussionComment()
        comment.content = request.form["comment"]
        comment.uid = ses[0]
        comment.did = did
        if "cid" in request.form:
            comment.cid = int(request.form["cid"])
        comment.created_time = datetime.now()
        db.session.add(comment)
        db.session.commit()
        flash("评论成功","success")
        return redirect("/discuss/%d/"%did)
    comments = {i.id:i for i in DiscussionComment.query.filter(DiscussionComment.did==did).all()}
    child,start = subtree(comments.values())
    return render_template("discuss/discuss.html",discussion=discussion,comments=comments,child=child,start=start,**default_dict(ses[1],request,user))
def subtree(ls):
    child = {}
    start = []
    for i in ls:
        if i.id not in child:
            child[i.id] = []
        if i.cid:
            child[i.cid].append(i.id)
    for i in ls:
        if not i.cid:
            start.append(i.id)
    return child,start
@app.route("/new",methods=["GET","POST"])
@app.route("/new/",methods=["GET","POST"])
@app.route("/edit/<int:did>",methods=["GET","POST"])
@app.route("/edit/<int:did>/",methods=["GET","POST"])
@ACCESS_REQUIRE_HTML(["VIEW","PUBLISH"])
def new(ses,user,did=None):
    if did is None:
        discussion = Discussion()
        discussion.title = ""
        discussion.content = ""
        discussion.uid = ses[0]
        discussion.created_time = datetime.now()
    else:
        discussion = Discussion.query.get(did)
        if not discussion or (discussion.uid != ses[0] and not user.access & ACCESS["ADMIN"]):
            flash("没有权限修改该讨论","danger")
            return redirect("/discuss/%d/"%did)
    if request.method == "POST":
        if not lin(["title","content","pid"],request.form):
            flash("请填写标题和内容","danger")
            return redirect("/discuss/new/")
        discussion.title = request.form["title"]
        discussion.content = request.form["content"]
        try:
            discussion.pid = int(request.form["pid"])
            problem = Problem.query.get(discussion.pid)
            if not problem or problem.deleted:
                raise ValueError("Problem not found.")
        except:
            flash("输入数据有误：题目编号为整数且对应题目存在。","danger")
            return redirect("/discuss/new/")
        db.session.add(discussion)
        db.session.commit()
        flash("讨论成功","success")
        return redirect("/discuss/%d/"%discussion.id)
    return render_template("discuss/edit.html",discussion=discussion,**default_dict(ses[1],request,user))