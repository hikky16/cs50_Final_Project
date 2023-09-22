from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm (FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min= 3, max= 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min= 5, max= 20)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("SignUp")


class LoginForm (FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min= 3, max= 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min= 5, max= 20)])
    remeber = BooleanField("Remember Me")
    submit = SubmitField("Login")


