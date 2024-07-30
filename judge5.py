import docker,os
from settings import *
from lib import *
from pickle import dump
from model import *
con = docker.from_env()
def sandbox(code,runid,testdata,diff="defaultdiff",time=1000,mem=64*1024):
    os.popen(f"mkdir '{runid}'").read()
    with open(f"{runid}/data.pk","wb") as file:
        dump(testdata,file)
    with open(f"{runid}/test.cpp","w") as file:
        file.write(code)
    os.popen(f"cp judger.py {runid}").read()
    os.popen(f"cp comper.py {runid}").read()
    ct = con.containers.run("psutil_gpp",f"python3 judger.py {diff} {time} {mem}",remove=True,volumes=[f"""{os.path.abspath(".")}/{runid}:/{runid}"""],working_dir = f"/{runid}",)
    print(ct.decode())
    ans = eval(ct.decode())
    os.popen(f"rm -r {runid}").read()
    return ans
def judge(app,code,problem,user):
    with app.app_context():
        cnt = Record.query.count()
        rec = Record()
        rec.user_id = user.id
        rec.problem_id = problem.id
        ans = sandbox(code,cnt+1,eval(problem.points),problem.diff,problem.time,problem.mem)
        ans[0] = int(ans[0])
        rec.score = ans[0]
        rec.detail = str(ans[1])
        uprecord = UserProblem.query.filter(UserProblem.user_id == user.id).filter(UserProblem.problem_id == problem.id).first()
        if ans[0] == 100:
            if not uprecord or uprecord.score != 100:
                user.accnt += 1
            if not uprecord:
                uprecord = UserProblem()
                uprecord.user_id = user.id
                uprecord.problem_id = problem.id
            uprecord.score = 100
        else:
            if not uprecord:
                uprecord = UserProblem()
                uprecord.user_id = user.id
                uprecord.problem_id = problem.id
                uprecord.score = ans[0]
        db.session.add(uprecord)
        db.session.add(rec)
        db.session.commit()