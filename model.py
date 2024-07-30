from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
# userproblem = db.Table("user_problem",
#                        db.Column("user_id",db.Integer,db.ForeignKey("user.id"),primary_key=True),
#                        db.Column("problem_id",db.Integer,db.ForeignKey("problem.id"),primary_key=True))
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.Unicode(64),nullable=False,index=True,unique=True)
    password = db.Column(db.String(256),nullable=False)
    accnt = db.Column(db.Integer,index=True,default=0)
    problems = db.relationship("Problem",secondary="userproblem",backref="users")
    verified = db.Column(db.Boolean,default=False)
    disabled = db.Column(db.Boolean,default=False)
    admin = db.Column(db.Boolean,default=False)
class Problem(db.Model):
    __tablename__ = "problem"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Unicode(128),index=True,nullable=False)
    markdown = db.Column(db.UnicodeText)
    points = db.Column(db.UnicodeText)
    time = db.Column(db.Integer,default=1000)
    mem = db.Column(db.Integer,default=65536)
    diff = db.Column(db.String(16),default="defaultdiff")
class UserProblem(db.Model):
    __tablename__ = "userproblem"
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    problem_id = db.Column(db.Integer,db.ForeignKey("problem.id"),nullable=False)
    score = db.Column(db.Integer,default=0)
class Record(db.Model):
    __tablename__ = "record"
    id = db.Column(db.Integer,primary_key=True)
    problem_id = db.Column(db.Integer,db.ForeignKey("problem.id"))
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    score = db.Column(db.Integer)
    detail = db.Column(db.UnicodeText)