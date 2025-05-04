from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
class Logging(db.Model):
    def __todict__(self):
        return {
            'id':self.id,
            'uid':self.uid,
            'describe':self.describe,
            'category':self.category,
            'date':self.date.strftime("%Y/%m/%d %H:%M"),
        }
    id = db.Column(db.Integer,primary_key=True)
    uid = db.Column(db.Integer,nullable=False,index=True,default=-1)
    describe = db.Column(db.UnicodeText,nullable=False,server_default='')
    category = db.Column(db.Integer,nullable=False)
    date = db.Column(db.DateTime,nullable=False)
class Session(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
    session_id = db.Column(db.String(32),nullable=False,index=True)
    content = db.Column(db.Text)
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.Unicode(64),unique=True,nullable=False,index=True)
    password = db.Column(db.String(162),nullable=False)#hashed password
    access = db.Column(db.Integer,nullable=False,default=0)
    created_time = db.Column(db.DateTime,default=datetime.now)
    latest_login_time = db.Column(db.DateTime,default=datetime.now)
class Problem(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Unicode(64),nullable=False,unique=True,index=True)
    background = db.Column(db.Text)
    description = db.Column(db.Text)
    inputformat = db.Column(db.Text)
    outputformat = db.Column(db.Text)
    sample = db.Column(db.Text)  # json
    hint = db.Column(db.Text)
    accepted = db.Column(db.Integer,nullable=False,default=0)
    submit = db.Column(db.Integer,nullable=False,default=0)
    time_limit = db.Column(db.Integer,nullable=False,default=1000)
    memory_limit = db.Column(db.Integer,nullable=False,default=65536)
    testcases_zip = db.Column(db.String(128),nullable=False)
    testcases = db.Column(db.Integer,nullable=False)
    deleted = db.Column(db.Integer,server_default="0")
class Record(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
    pid = db.Column(db.Integer,db.ForeignKey('problem.id'),nullable=False,index=True)
    code = db.Column(db.Text,nullable=False)
    language = db.Column(db.String(10),nullable=False)
    result = db.Column(db.String(10))
    O2 = db.Column(db.Integer,default=0)
    submit_time = db.Column(db.DateTime,default=datetime.now)
    runtime = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    detail = db.Column(db.Text)
class Announcement(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Unicode(64),nullable=False,index=True)
    content = db.Column(db.Text)
    created_time = db.Column(db.DateTime,default=datetime.now)
class Discussion(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Unicode(64),nullable=False,index=True)
    pid = db.Column(db.Integer,db.ForeignKey('problem.id'),nullable=False,index=True)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
    content = db.Column(db.Text)
    created_time = db.Column(db.DateTime,default=datetime.now)
    top = db.Column(db.Integer,default=0)
class DiscussionComment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    did = db.Column(db.Integer,db.ForeignKey('discussion.id'),nullable=False,index=True)
    cid = db.Column(db.Integer,db.ForeignKey('discussion_comment.id'),nullable=True,index=True)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False,index=True)
    content = db.Column(db.Text)
    created_time = db.Column(db.DateTime,default=datetime.now)