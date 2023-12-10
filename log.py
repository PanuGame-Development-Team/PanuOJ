import os
import time
class Logger:
    def __init__(self):
        self.loglist = []
    def addLog(self,log,type,tdelta):
        self.loglist.append([Log(log,type),tdelta])
    def getList(self):
        return self.loglist
    def getNewest(self):
        return self.loglist[-1]
class Log:
    def __init__(self,log,type):
        self.text = log
        self.type = type
class LogType:
    def __init__(self,showtext,textcolor=7,bgcolor=0,highlight=False):
        self.showtext = showtext + (8-len(showtext))*" "
        self.textcolor = textcolor
        self.highlight = highlight
        self.bgcolor = bgcolor
    def selfRender(self):
        return f"""\033[3{self.textcolor};4{self.bgcolor}{";1" if self.highlight else ""}m{self.showtext}\033[0m"""
class Timer:
    def __init__(self):
        self.start = time.time()
    def getTimeDelta(self):
        return time.time() - self.start
T_info = LogType("INFO")
T_warning = LogType("Warning",3)
T_note = LogType("Note",highlight=True)
T_error = LogType("ERROR",1,highlight=True)
T_OK = LogType("OK",2,highlight=True)
class Console:
    def __init__(self,logger,timer):
        os.system("")
        self.logger = logger
        self.timer = timer
    def log(self,text,type=T_info):
        self.logger.addLog(text,type,self.timer.getTimeDelta())
        self.update(self.logger.getNewest())
    def update(self,log):
        print("[" + str(round(log[1],5)) + (10-len(str(round(log[1],5)))) * " " + "] - [" + log[0].type.selfRender() + "] :" + log[0].text)
