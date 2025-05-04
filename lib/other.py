from os import popen as _popen
def get_fortune():
    fortune = _popen("fortune").read()
    return fortune