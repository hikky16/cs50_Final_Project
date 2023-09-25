from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, IntegerField, TextAreaField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
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


class AddExpenseForm (FlaskForm):
    project_id = SelectField("Project", choices=[])
    date = DateField("Date")


class AddProject (FlaskForm):
    po = IntegerField("PO Number", validators=[DataRequired(), NumberRange(min= 21000000, max=30000000)])
    title = TextAreaField("Title", validators=[DataRequired()])
    amount = FloatField("Contract Amount", validators=[DataRequired()])
    duration = IntegerField("Contract Duration", validators=[DataRequired()])
    status = SelectField("Project Status", choices=[("ONGOING", "ONGOING"), ("DONE","DONE"), ("ONHOLD", "ONHOLD")])
    start = DateTimeField("Date Started")
    end = DateTimeField("Date Ended")
    submit = SubmitField("Submit")