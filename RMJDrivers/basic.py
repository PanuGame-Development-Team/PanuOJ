class RMJDriver:
    def __init__(self,name,host,scheme,username=None,password=None):
        self.name = name
        self.host = host
        self.scheme = scheme
        self.username = username
        self.password = password
        self.session = None
        self.languages = {}
        self.mapping = {}
        self.login()
    def login(self):
        raise NotImplementedError("Login method must be implemented in subclass.")
    def getproblemlist(self,page,perpage=30,searchtext=""):
        raise NotImplementedError("getproblemlist method must be implemented in subclass.")
    def getproblem(self,problem_id):
        raise NotImplementedError("getproblem method must be implemented in subclass.")
    def submit(self,problem_id,code,language,user):
        raise NotImplementedError("submit method must be implemented in subclass.")
class RMJProblem:
    id = None
    title = ""
    background = ""
    description = ""
    inputformat = ""
    outputformat = ""
    sample = ""
    hint = ""
    accepted = 0
    submit = 0
    time_limit = 1000
    memory_limit = 65536
    deleted = 0
class RMJTestcase:
    status = ""
    time = 0
    memory = 0