import psutil
import os,sys
import io
from log import Timer
from threading import Thread
from subprocess import Popen,PIPE
dd = peak = 0
timer = Timer()
def do_c(options,name,argv,maxtime=1000,maxmem=512*1024*1024):
    global dd,peak
    def test():
        global dd,peak
        peak = 0
        while dd * 1000 < maxtime and state:
            dd = timer.getTimeDelta() - td
            try:
                r = p.memory_info().rss
                peak = r if r > peak else peak
            except:
                continue
        if p.is_running:
            os.popen(f"killall test").read()
    def same(a,b):
        r = [i.strip() for i in a.strip("\n").split("\n")]
        t = [i.strip() for i in b.strip("\n").split("\n")]
        return r == t
    if "--inans" in argv:
        oe = "ans"
    else:
        oe = "out"
    if "--namenum" in argv:
        fileformat = "{name}{i}"
    elif "--num" in argv:
        fileformat = "{i}"
    else:
        fileformat = "{i}"
    proc = Popen(options,shell=True,stdout=PIPE,stderr=PIPE,bufsize=-1)
    proc.wait()
    err = io.TextIOWrapper(proc.stderr,encoding='UTF-8')
    err = err.read().strip("\n")
    if err != "":
        return [0.0,{1:["CE","0.0KB","0.0s"]}]
    i = 1
    l = 0
    c = 0
    rtans = {}
    while os.path.exists(f"{fileformat.format(name=name,i=i)}.in") and os.path.exists(f"{fileformat.format(name=name,i=i)}.{oe}"):
        os.popen(f"cp {fileformat.format(name=name,i=i)}.in {name}.in").read()
        l += 1
        td = timer.getTimeDelta()
        t = Thread(target=test)
        state = True
        dd = 0
        p = psutil.Popen(f"./test < {name}.in > {name}.out",shell=True)
        t.start()
        p.wait()
        state = False
        t.join()
        if dd * 1000 < maxtime:
            if os.path.exists(f"{name}.out"):
                if peak <= maxmem:
                    with open(f"{name}.out") as file:
                        with open(f"{fileformat.format(name=name,i=i)}.{oe}") as file2:
                            if same(file.read(),file2.read()):
                                rtans[i] = ["AC",f"{round(peak/1024,2)}KB",f"{round(dd,2)}s"]
                                c += 1
                            else:
                                rtans[i] = ["WA",f"{round(peak/1024,2)}KB",f"{round(dd,2)}s"]
                else:
                    rtans[i] = ["MLE",f"{round(peak/1024,2)}KB",f"{round(dd,2)}s"]
            else:
                rtans[i] = ["NOFE",f"{round(peak/1024,2)}KB",f"{round(dd,2)}s"]
        else:
            rtans[i] = ["TLE",f"{round(peak/1024,2)}KB",f"{round(dd,2)}s"]
        i += 1
    os.popen("rm test").read()
    if l > 0:
        if os.path.isfile(f"{name}.in"):
            os.popen(f"rm {name}.in").read()
        if os.path.isfile(f"{name}.out"):
            os.popen(f"rm {name}.out").read()
        return [c/l*100,rtans]
    else:
        return [0.0,{1:["UKE","0.0KB","0.0s"]}]
# while not os.path.isfile("OK"):
#     time.sleep(0.01)
ans = do_c(sys.argv[1],sys.argv[2],sys.argv)
print(ans[0])
i = 1
while(i in ans[1].keys()):
    print(" ".join(ans[1][i]))
    i += 1