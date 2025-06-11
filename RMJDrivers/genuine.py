from requests import post,get
from .basic import *
from json import dumps,loads
from model import *
from time import sleep
class GenuineDriver(RMJDriver):
    def __init__(self,*args):
        super().__init__(*args)
        self.mapping = {
            -3: "Waiting",
            -2: "CE",
            -1: "WA",
            0: "AC",
            1: "TLE",
            2: "MLE",
            3: "RE",
            4: "SE",
        }
        self.languages = {
            "C":'c',
            "C++ 14":"cpp",
            "C++14 (GCC)":"gcccpp14",
            "C++ 11":"cpp11",
            "C++ 17":"cpp17",
            "C++ 20":"cpp20",
            "C++ 98":"cpp98",
            "Python 3":"python3",
            "Java":"java"
        }
    def login(self):
        res = post(f"{self.scheme}://{self.host}/api/user/login/",data={
            "username": self.username,
            "password": self.password,
            "captcha": ""
        })
        if res.status_code == 200:
<<<<<<< HEAD
            self.session = res.cookies.get("sessionid")
=======
            # self.session = res.cookies.get("sessionid")
            self.session = "ol1lqv34nskekys5lm9re29jo02kzgc4"
>>>>>>> 1605e82a7143aa0556ea80881789869aed989d74
    def login_user(self,username,password):
        res = post(f"{self.scheme}://{self.host}/api/user/login/",data={
            "username": username,
            "password": password,
            "captcha": ""
        })
        if res.status_code == 200:
            return res.cookies.get("sessionid")
        return None
    def getproblemlist(self,page,perpage=30,searchtext=""):
        res = get(f"{self.scheme}://{self.host}/api/problem/",params={
            "limit": perpage,
            "offset": (page - 1) * perpage,
            "search": searchtext,
            "tags": "",
        },cookies={"sessionid":self.session})
        if res.status_code == 403:
            self.login()
            return self.getproblemlist(page,perpage,searchtext)
        elif res.status_code != 200:
            return [],-1
        problems = res.json()["results"]
        processed = []
        for i in range(len(problems)):
            processedproblem = RMJProblem()
            processedproblem.id = problems[i]["id"]
            processedproblem.title = problems[i]["title"]
            processedproblem.submit = problems[i]["submission_count"]
            processedproblem.accepted = problems[i]["accepted_count"]
            processedproblem.time_limit = "Unknown "
            processedproblem.memory_limit = "Unknown "
            processed.append(processedproblem)
        return processed,(res.json()["count"] + perpage - 1) // perpage
    def getproblem(self,problem_id):
        res = get(f"{self.scheme}://{self.host}/api/problem/{problem_id}/",cookies={"sessionid":self.session})
        if res.status_code == 403:
            self.login()
            return self.getproblem(problem_id)
        elif res.status_code != 200:
            return None,False
        problem = res.json()
        processedproblem = RMJProblem()
        processedproblem.id = problem["id"]
        processedproblem.title = problem["title"]
        processedproblem.submit = problem["submission_count"]
        processedproblem.accepted = problem["accepted_count"]
        processedproblem.time_limit = problem["time_limit"]
        processedproblem.memory_limit = problem["memory_limit"] * 1024
        processedproblem.background = problem["background"]
        processedproblem.description = problem["description"]
        processedproblem.inputformat = problem["input_format"]
        processedproblem.outputformat = problem["output_format"]
        processedproblem.hint = problem["hint"]
        processedproblem.sample = [[i["input"],i["output"]] for i in problem["samples"]]
        while processedproblem.sample and processedproblem.sample[-1] == ["",""]:
            processedproblem.sample.pop()
        processedproblem.sample = dumps(processedproblem.sample)
        return processedproblem,problem["allow_submit"]
    def submit(self,problem_id,record:Record,user,app):
        def rmjle(record,app):
            with app.app_context():
                record.result = "RMJLE"
                db.session.add(record)
                db.session.commit()
        if not user.rmjuser:
            rmjle(record,app)
            return
        rmjuser = loads(user.rmjuser).get(self.name,None)
        if not rmjuser:
            rmjle(record,app)
            return
        sessionid = self.login_user(rmjuser["username"],rmjuser["password"])
        if not sessionid:
            rmjle(record,app)
            return
        res = post(f"{self.scheme}://{self.host}/api/submission/",data={
            "problem_id": str(problem_id),
            "language": self.languages[record.language],
            "source": record.code,
            "_is_hidden": False,
            "captcha": "",
        },cookies={"sessionid":sessionid})
        if res.status_code == 200 or res.status_code == 201:
            index = res.json()["id"]
            while True:
                sleep(3)
                res = get(f"{self.scheme}://{self.host}/api/submission/{index}/",cookies={"sessionid":sessionid})
                if res.status_code != 200:
                    rmjle(record,app)
                    return
                json = res.json()
                if json["status"] != -3:
                    record.result = self.mapping[json["status"]]
                    record.runtime = json["execute_time"]
                    record.memory = json["execute_memory"]/1048576
                    testcases = []
                    for i in json["detail"]:
                        testcases.append([None,self.mapping[i["status"]],i["statistics"]["memory"]//1048576,i["statistics"]["time"]])
                    record.detail = dumps(testcases)
                    break
            with app.app_context():
                db.session.add(record)
                db.session.commit()
            return
        rmjle(record,app)