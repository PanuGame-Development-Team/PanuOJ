from os import urandom
CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:root@localhost:3306/PojFrontend',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    "SQLALCHEMY_ENGINE_OPTIONS": {
        "pool_size": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
}
SECRET_KEY = urandom(32)
HOST = "127.0.0.1"
PORT = 7695
JUDGER_LIST = [["Mercury","192.168.3.23",34734]]