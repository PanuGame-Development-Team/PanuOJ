import psutil
import os,sys
import io
from threading import Thread
from subprocess import Popen,PIPE
from uuid import uuid4
from comper import *
from pickle import load
from time import time
runtime = peak = pid = 0
class Timer:
    def __init__(self):
        self.start = time()
    def getTimeDelta(self):
        return time() - self.start
timer = Timer()
def do_c(options,testdata,same,maxtime=1000,maxmem=512*1024):#ms,kb
    global runtime,peak,pid
    def test():
        global runtime,peak,pid
        peak = 0
        while runtime * 1000 < maxtime and state:
            runtime = timer.getTimeDelta() - timedelta
            try:
                rssmem = psutilTask.memory_info().rss/1024
                peak = rssmem if rssmem > peak else peak
                if peak > maxmem:
                    break
            except:
                continue
        if psutilTask.is_running():
            os.popen(f"kill -9 {pid}").read()
    try:
        proc = Popen(options,shell=True,stdout=PIPE,stderr=PIPE,bufsize=-1)
        proc.wait()
        err = io.TextIOWrapper(proc.stderr,encoding='UTF-8')
        err = err.read().strip("\n")
        if err != "":
            return [0.0,[["CE","Unknown","Unknown"]]]
        accnt = 0
        rtans = []
        for data in testdata:
            uurand = uuid4().hex
            with open(f"{uurand}.in","w") as file:
                file.write(data[0])
            timedelta = timer.getTimeDelta()
            testThread = Thread(target=test)
            state = True
            runtime = 0
            psutilTask = psutil.Popen(f"./test < {uurand}.in > {uurand}.out",shell=True)
            pid = psutilTask.pid
            testThread.start()
            psutilTask.wait()
            state = False
            testThread.join()
            mt = [f"{round(peak,2)}KB" if peak != 0 else "Unknown",f"{round(runtime,2)}s"]
            if runtime * 1000 < maxtime:
                if peak <= maxmem:
                    if os.path.exists(f"{uurand}.out"):
                        with open(f"{uurand}.out") as file:
                            if same(file.read(),data[1]):
                                rtans.append(["AC"] + mt)
                                accnt += 1
                            else:
                                rtans.append(["WA"] + mt)
                    else:
                        rtans.append(["IE"] + mt)
                else:
                    rtans.append(["MLE"] + mt)
            else:
                rtans.append(["TLE"] + mt)
        os.popen("rm test").read()
        return [accnt/len(testdata)*100,rtans]
    except Exception as e:
        print(e)
        return [0.0,[["UKE","Unknown","Unknown"]]]
with open("data.pk","rb") as file:
    data = load(file)
os.popen("rm data.pk").read()
ans = do_c("g++ test.cpp -o test -lm -O2 -std=c++14 -w",data,eval(sys.argv[1]),eval(sys.argv[2]),eval(sys.argv[3]))
print(ans)