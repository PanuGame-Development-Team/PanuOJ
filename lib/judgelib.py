from requests import post,get,ConnectionError,ConnectTimeout
from constances import *
from settings import *
from model import *
from time import sleep
from threading import Thread
from json import dumps
from datetime import timedelta,datetime
from .core import syslog
class Judger:
    def __init__(self,judger_id,judger_ip,judger_port,app=None):
        self.judger_id = judger_id
        self.judger_ip = judger_ip
        self.judger_port = judger_port
        self.judger_online = 1
        self.judger_busy = 0
        self.judger_record_id = None
        self.judger_endtime = None
        self.app = app
    def heartbeat(self):
        global judgers_online,judgers
        try:
            self.judger_online = (get(f"http://{self.judger_ip}:{self.judger_port}/heartbeat").status_code==200)
        except (ConnectTimeout,ConnectionError):
            self.judger_online = 0
        if not self.judger_online and self.judger_id in judgers_online:
            judgers_online.remove(self.judger_id)
        if self.judger_online and self.judger_id not in judgers_online:
            judgers_online.append(self.judger_id)
            self.judger_busy = 0
    def get_response(self,app):
        if self.judger_online and self.judger_busy:
            try:
                res = get(f"http://{self.judger_ip}:{self.judger_port}/record/{self.judger_record_id}").json()
            except:
                res = {"status":"ERROR","message":"Judger has some problems to solve."}
            if res["status"] == "OK":
                with app.app_context():
                    record:Record = Record.query.get(self.judger_record_id)
                    record.runtime = int(res["runtime"])
                    record.memory = int(res["memory"])
                    record.detail = dumps(res["detail"])
                    if res["result"] == "CE":
                        record.result = "CE"
                    else:
                        record.result = "AC"
                        for i in res["detail"]:
                            if i[1] == "WA":
                                record.result = "WA"
                                break
                            elif i[1] == "RE":
                                record.result = "RE"
                                break
                            elif i[1] == "TLE":
                                record.result = "TLE"
                                break
                            elif i[1] == "MLE":
                                record.result = "MLE"
                                break
                            elif i[1] == "OLE":
                                record.result = "OLE"
                                break
                            elif i[1] == "FE":
                                record.result = "FE"
                                break
                    db.session.add(record)
                    db.session.commit()
                    if record.result == "AC":
                        problem:Problem = Problem.query.get(record.pid)
                        problem.accepted += 1
                        db.session.add(problem)
                        db.session.commit()
                self.judger_busy = 0
                self.judger_record_id = None
            elif datetime.now() > self.judger_endtime:
                with app.app_context():
                    record:Record = Record.query.get(self.judger_record_id)
                    record.result = "UKE"
                    db.session.add(record)
                    db.session.commit()
                    syslog(f"Judger {self.judger_id} timeout.",S2NCATEGORY["WARNING"])
                self.judger_busy = 0
                self.judger_record_id = None
    def submit(self,rid):
        self.judger_record_id = rid
        with self.app.app_context():
            record:Record = Record.query.get(rid)
            problem:Problem = Problem.query.get(record.pid)
        self.judger_endtime = datetime.now() + timedelta(seconds=problem.time_limit * problem.testcases / 1000 * 1.5)
        self.judger_busy = 1
        self.heartbeat()
        if self.judger_online:
            try:
                return post(f"http://{self.judger_ip}:{self.judger_port}/",files={"testcases":open(problem.testcases_zip,"rb")},data={"problem_id":record.pid,"record_id":rid,"time":problem.time_limit,"memory":problem.memory_limit,"language":record.language,"O2":record.O2,"code":record.code,"tests":problem.testcases}).json()
            except:
                res = {"status":"ERROR","message":"Judger has some problems to solve."}
        else:
            return {"status":"OFFLINE","message":"Judger is offline."}
    def event_loop(self,app):
        while True:
            self.heartbeat()
            for i in range(6):
                self.get_response(app)
                sleep(0.5)
    def init_app(self,app):
        self.app = app
    def start(self):
        Thread(target=self.event_loop,args=(self.app,)).start()
judgers = {i[0]:Judger(*i) for i in JUDGER_LIST}
judgers_online = []
judge_queue = []
def distribute():
    qsize = len(judge_queue)
    if qsize > 0:
        for judger in judgers_online:
            if not judgers[judger].judger_busy:
                if judgers[judger].submit(judge_queue.pop(0))["status"] != "OK":
                    continue
                qsize -= 1
                if qsize == 0:
                    break
    return qsize
def distribute_loop():
    while True:
        distribute()
        sleep(0.1)