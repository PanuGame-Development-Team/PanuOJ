from settings import *
from model import *
from lib import *
from uuid import uuid4
from flask import *
from os import system,path
name = "addproblem"
describe = "题目添加"
use_mainpage = False
use_headers = True
use_route = True

def init(m):
    global mods
    system("mkdir -p /tmp/PanuOJProblemData")
    mods = m
    
def save_file(file,allowed):
    fileext = file.filename.strip().split(".")[-1].lower()
    if fileext in allowed:
        uuid = uuid4().hex
        system(f"mkdir -p /tmp/PanuOJProblemData/{uuid}")
        file.save(f"/tmp/PanuOJProblemData/{uuid}/{uuid}.zip")
        return f"/tmp/PanuOJProblemData/{uuid}",f"/tmp/PanuOJProblemData/{uuid}/{uuid}.zip"
    return None
def save_problem(file,dir):
    system(f"unzip {file} -d {dir}")
    problem = Problem()
    problem.title = open(dir + "/title.txt",encoding="UTF-8").read().replace("\r","").replace("\n","").strip()
    problem.diff = open(dir + "/diff.txt",encoding="UTF-8").read().replace("\r","").replace("\n","").strip()
    problem.markdown = open(dir + "/desc.md",encoding="UTF-8").read()
    problem.mem = int(open(dir + "/mem.txt",encoding="UTF-8").read().replace("\r","").replace("\n","").strip())
    problem.time = int(open(dir + "/time.txt",encoding="UTF-8").read().replace("\r","").replace("\n","").strip())
    ls = []
    i = 1
    while path.isfile(dir + f"/{i}.in") and path.isfile(dir + f"/{i}.ans"):
        fin = open(dir + f"/{i}.in",encoding="UTF-8").read()
        fout = open(dir + f"/{i}.ans",encoding="UTF-8").read()
        ls.append([fin,fout])
        i += 1
    problem.points = str(ls)
    db.session.add(problem)
    db.session.commit()
app = Blueprint(name,name)
@app.route("/",methods=["GET","POST"])
def index():
    sesdic,currentuser = readsession(session)
    if not currentuser.admin:
        flash("您不是管理员，不可添加题目","danger")
        return redirect("/")
    if request.method == "POST":
        if "data" in request.files:
            file = request.files.getlist("data")[0]
            if file:
                dir,fp = save_file(file,["zip"])
                save_problem(fp,dir)
                flash("添加成功","success")
                return redirect("/problems")
        abort(400)
    return render_template("mods/add_problem/upload.html",mods=mods,**sesdic)