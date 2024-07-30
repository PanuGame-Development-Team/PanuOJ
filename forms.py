from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired
class LoginForm(FlaskForm):
    username = StringField("用户名",validators=[DataRequired(message="用户名不能为空")])
    password = PasswordField("密码",validators=[DataRequired(message="密码不能为空")])
    submit = SubmitField("提交")