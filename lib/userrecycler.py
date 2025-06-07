from .queues import RedisPoolQueue, BasicActivity
from settings import *
from constances import *
from model import *
from json import loads, dumps
from .core import syslog
from time import sleep
from datetime import datetime
class UserRecycleActivity(BasicActivity):
    app = None
    def process(self,callback,item):
        self.busy = True
        with self.app.app_context():
            user = User.query.get(int(item.decode("utf-8")))
            if user:
                while datetime.now() < user.verify_expireation:
                    sleep(10)
                try:
                    user = User.query.get(int(item.decode("utf-8")))
                    if not user.verified:
                        syslog(f"用户 {user.username} ({user.id}) 被回收。",S2NCATEGORY["DEBUG"],user.id)
                        Session.query.filter_by(uid=user.id).delete()
                        db.session.delete(user)
                        db.session.commit()
                except:
                    syslog(f"用户 {user.username} ({user.id}) 重复回收。",S2NCATEGORY["SUSPICIOUS"],user.id)
        self.busy = False
        callback(self.id)
userrecycler = RedisPoolQueue({i: UserRecycleActivity(i) for i in range(30)}, "user_recycle_queue")