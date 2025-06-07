from requests import post,get,ConnectionError,ConnectTimeout
from constances import *
from settings import *
from model import *
from time import sleep
from threading import Thread
from json import dumps
from datetime import timedelta,datetime
from .core import *
from .queues import RedisPoolQueue,BasicActivity
class JudgeActivity(BasicActivity):
    def __init__(self,id,judger_ip,judger_port,app=None):
        super().__init__(id)
        self.id = id
        self.judger_ip = judger_ip
        self.judger_port = judger_port
        self.judger_record_id = None
        self.judger_endtime = None
        self.app = app
    def check_available(self):
        if self.error:
            self.available = False
            return False
        global judgers_online,judgers
        try:
            self.available = (get(f"http://{self.judger_ip}:{self.judger_port}/heartbeat").status_code==200)
        except (ConnectTimeout,ConnectionError):
            self.available = 0
        if not self.available and self.id in judgers_online:
            judgers_online.remove(self.id)
        if self.available and self.id not in judgers_online:
            judgers_online.append(self.id)
            # self.busy = 0
        return self.available
    def process(self,callback,item):
        self.busy = True
        rid = int(item.decode("utf-8"))
        self.judger_record_id = rid
        with self.app.app_context():
            record:Record = Record.query.get(rid)
            problem:Problem = Problem.query.get(record.pid)
        self.judger_endtime = datetime.now() + timedelta(seconds=problem.time_limit * problem.testcases / 1000 * 1.5)
        try:
            res = post(f"http://{self.judger_ip}:{self.judger_port}/",files={"testcases":open(problem.testcases_zip,"rb")},data={"problem_id":record.pid,"record_id":rid,"time":problem.time_limit,"memory":problem.memory_limit,"language":record.language,"O2":record.O2,"code":record.code,"tests":problem.testcases}).json()
        except:
            self.error = True
            res = {"status":"ERROR","message":"Judger has some problems to solve."}
            return res
        while self.busy:
            try:
                res = get(f"http://{self.judger_ip}:{self.judger_port}/record/{self.judger_record_id}").json()
            except (ConnectTimeout,ConnectionError):
                self.available = False
                sleep(5)
                continue
            except:
                self.error = True
                res = {"status":"ERROR","message":"Judger has some problems to solve."}
                return res
            if res["status"] == "OK":
                with self.app.app_context():
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
                self.busy = False
                self.judger_record_id = None
            elif datetime.now() > self.judger_endtime:
                with self.app.app_context():
                    record:Record = Record.query.get(self.judger_record_id)
                    record.result = "UKE"
                    db.session.add(record)
                    db.session.commit()
                    self.error = True
                    syslog(f"Judger {self.id} timeout.",S2NCATEGORY["WARNING"])
                self.error = True
                self.judger_record_id = None
            sleep(0.5)
        callback(self.id)
    def event_loop(self,app):
        while True:
            self.check_available()
            sleep(5)
    def init_app(self,app):
        self.app = app
    def start(self):
        Thread(target=self.event_loop,args=(self.app,)).start()
judgers = {i[0]:JudgeActivity(*i) for i in JUDGER_LIST}
judgers_online = []
judgequeue = RedisPoolQueue(judgers,"judge_queue")