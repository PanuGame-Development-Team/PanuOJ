import redis
from threading import Thread
from settings import *
from constances import *
db = redis.Redis("127.0.0.1",6379,db=REDIS_DB)
class BasicActivity:
    id = None
    available = True
    busy = False
    error = False
    def __init__(self,id):
        self.id = id
    def process(self,callback,item):
        self.busy = True
        item = item.decode("utf-8")
        self.busy = False
        callback(self.id)
    def check_available(self):
        if self.error:
            self.available = False
            return False
        self.available = True
        return self.available
class RedisPoolQueue:
    def __init__(self,pool,qname):
        self.pool = pool
        self.qname = qname
    def put(self,argv):
        db.rpush(self.qname,argv)
        self.allocate()
    def allocate(self,id=None):
        if id:
            if self.pool[id].check_available():
                item = db.lpop(self.qname)
                if item:
                    Thread(target=self.pool[id].process,args=(self.callback,item)).start()
        else:
            for id in self.pool:
                if not self.pool[id].busy and self.pool[id].check_available():
                    item = db.lpop(self.qname)
                    if not item:
                        break
                    Thread(target=self.pool[id].process,args=(self.callback,item)).start()
    callback = allocate
# Example usage:
# from time import time
# processor = {i:BasicActivity(i) for i in range(20)}
# queue = RedisPoolQueue(processor,"test_queue")
# t0 = time()
# for i in range(100):
#     queue.put(f"Task {i}")
# t1 = time()
# print(f"Put 100 tasks in {t1-t0} seconds.")