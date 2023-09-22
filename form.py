from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from sqlalchemy import select
from data_tables import users_table, engine

class RegistrationForm (FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min= 3, max= 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min= 5, max= 20)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("SignUp")

    def validate_username(self, username):
        with engine.connect() as conn:
            statement = select(users_table.c.username).where(users_table.c.username == username.data)
            user = conn.execute(statement)
            for i in user:
                if username.data in i:
                    raise ValidationError("That username is taken")
                
class LoginForm (FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min= 3, max= 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min= 5, max= 20)])
    remeber = BooleanField("Remember Me")
    submit = SubmitField("Login")


