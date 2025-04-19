CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:root@localhost:3306/PojFrontend',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    "SQLALCHEMY_ENGINE_OPTIONS": {
        "pool_size": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
}
from os import urandom
SECRET_KEY = urandom(32)