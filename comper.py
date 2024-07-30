def defaultdiff(a,b):
    r = [i.strip() for i in a.strip("\n").split("\n")]
    t = [i.strip() for i in b.strip("\n").split("\n")]
    return r == t