from json import loads
from RMJDrivers import *
from settings import *
from constances import *
from lib.queues import BasicActivity,RedisPoolQueue
from model import *
def build_judger(drivername,name,host,scheme,username=None,password=None):
    if drivername == "Genuine":
        return GenuineDriver(name,host,scheme,username,password)
    else:
        return None
remotejudges = {i["name"]:build_judger(i["RMJDriver"],i["name"],i["host"],i["scheme"],i["username"],i["password"]) for i in RMJSERVERS}
class SubmitActivity(BasicActivity):
    app = None
    def process(self,callback,item):
        self.busy = True
        item = loads(item.decode("utf-8"))
        # try:
        with self.app.app_context():
            user = User.query.filter_by(id=item["user"]).first()
            record = Record.query.filter_by(id=item["record"]).first()
        remotejudges[item["name"]].submit(item["problem_id"],record,user,self.app)
        # except Exception as e:
        #     print(e)
        #     self.error = True
        self.busy = False
        callback(self.id)
rmjqueue = RedisPoolQueue({i:SubmitActivity(i) for i in range(3)},"rmjqueue")