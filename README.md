# PanuOJ
### 代码构建环境
* 操作系统：Mint 22.1 x64 内核:6.8.0-53-generic
* Python 3.12.3
* Flask 3.1.0
* Flask-SQLAlchemy 3.1.1
* Flask-Migrate 4.1.0
* fortune-mod version 9708 at /usr/games/fortune
### 构建方法
1. 安装依赖包
在项目根目录下执行以下命令安装依赖包：
```bash
pipenv install
```
Debian系列用户：
```bash
sudo apt install fortune-mod
```
CentOS系列用户：
```bash
sudo yum install fortune-mod
```
2. 创建设置文件
在项目根目录下创建 `settings.py` 文件，并添加以下内容：
```python
from os import urandom
CONFIG = {
    "SQLALCHEMY_DATABASE_URI":"sqlite:///db.sqlite3",  # 数据库URI，这里是测试数据库，如需生产部署请使用高性能数据库
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    "SQLALCHEMY_ENGINE_OPTIONS": {
        "pool_size": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
}
SECRET_KEY = urandom(32)
HOST = "127.0.0.1"      # 主机地址
PORT = 7695             # 端口
JUDGER_LIST = [["Mercury","xxx.xxx.xxx.xxx",34734]]    # 评测机列表
SMTP_SERVICE = "smtp.xxxxxxx.com"                      # smtp服务
SMTP_USER = "xxx@xxxxxxx.com"                          # 开通smtp服务的邮箱
SMTP_PASSWD = "xxxxxxxxxxxxxxxxxxxxxx"                 # 密钥
REDIS_DB = 0                                           # redis数据库
RMJSERVERS = [                                         # RMJ评测机服务器列表
    {
        "RMJDriver": "Genuine",
        "name": "QAOJ",
        "host": "ojorigin.qdzx.icu",
        "scheme": "http",
        "username":"",
        "password":""
    }
]
```
3. 修改 `judgelib.py` 中的 `judgers`，以添加所有稳定评测机。
4. 创建数据库
在项目根目录下执行以下命令创建数据库以及所需文件夹：
```bash
mkdir testcases
mkdir -r static/icons
python3 init_db.py
python3 migrate.py init
```
5. 部署
请使用systemctl/supervisor，uwsgi/gunicorn，nginx/apache反向代理进行部署。
注意：wsgi启动时切忌使用多进程，因为心跳与评测队列位于独立进程中导致ISE，多线程不受影响，建议启动方式：（nginx反向将127.0.0.1公开到外部）
```bash
gunicorn -w 1 --threads 8 -b 127.0.0.1:7695 main:app --worker-class gthread
```