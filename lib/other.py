from os import popen as _popen
def get_fortune():
    fortune = _popen("/usr/games/fortune").read()
    return fortune