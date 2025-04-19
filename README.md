# Patient错误日志
### 代码构建环境
* 操作系统：Mint 22.1 x64 内核:6.8.0-53-generic
* Python 3.12.3
* Flask 3.1.0
* Flask-SQLAlchemy 3.1.1
* Flask-Migrate 4.1.0
### 构建方法
1. 安装依赖包
在项目根目录下执行以下命令安装依赖包：
```bash
pipenv install
```
2. 创建设置文件
在项目根目录下创建 `settings.py` 文件，并添加以下内容：
```python
GARAGE_AVAILABLE = []                                  # 可用的车库列表
TYPE_OF_MACHINE = []                                   # 设备类型列表
CONFIG = {
    "SQLALCHEMY_DATABASE_URI":"sqlite:///db.sqlite3",  # 数据库URI，这里是测试数据库，如需生产部署请使用高性能数据库
    "SQLALCHEMY_TRACK_MODIFICATIONS":False
}
```
3. 修改 `judgelib.py` 中的 `judgers`，以添加所有稳定评测机。
4. 创建数据库
在项目根目录下执行以下命令创建数据库以及所需文件夹（因为评测机模块缘故，需要手动 `Ctrl + C` 退出：
```bash
mkdir testcases
python3 init_db.py
python3 migrate.py init
```
5. 部署
请使用systemctl/supervisor，uwsgi/gunicorn，nginx/apache反向代理进行部署。