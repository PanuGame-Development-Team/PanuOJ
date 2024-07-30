from settings import *
from model import *
from lib import *
from random import randint
from flask import *
name = "pagetest"
describe = "测试页面"
use_mainpage = True
use_headers = True
use_route = True
mainpage_width = 3
mainpage_allowpost = True

def init(m):
    global mods
    mods = m
    print("loading module pagetest")
    print("module pagetest loaded")

def render_mainpage(sesdic):
    s = f"""
<form action="" method="POST">
    <input class="form-control mb-3" name="{name}-pid" placeholder="请输入题号"/>
    <button class="btn btn-primary mr-3" type="submit">跳转</button>
    <a href="/problems/%d" class="btn btn-primary"><font color="{WHITE}">随机跳题</font></a>
</form>
""".replace("    ","").replace("\n","")
    pcnt = Problem.query.count()
    return s%randint(1,pcnt)

def handle_mainpagepost(dic):
    try:
        if Problem.query.get(int(dic["pid"])):
            flash("跳转成功","success")
            return redirect("/problems/%s"%dic["pid"])
        else:
            flash("题号不存在，跳转失败","danger")
            return redirect("/")
    except:
        flash("出现错误，跳转失败","danger")
        return redirect("/")

app = Blueprint(name,name)
@app.route("/")
def index():
    return "pagetest"
@app.route("/hw")
def hw():
    return "Hello,World!"