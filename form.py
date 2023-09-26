from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, IntegerField, TextAreaField, FloatField, DateField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from sqlalchemy import select
from data_tables import users_table, engine, project_table, type_table

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
    with engine.connect() as conn:
        statement = select(project_table.c.id, project_table.c.title)
        state_type = select(type_table)
        contracts = conn.execute(statement)
        types = conn.execute(state_type)
    

    project_id = SelectField("Project", choices=[(i.id, i.title) for i in contracts], validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()], format="%Y-%m-%d")
    description = StringField("Description", validators=[DataRequired(), Length(max=200)])
    type_id = SelectField("Expense Type", choices=[(i.id, i.type) for i in types])
    recipt = RadioField("Recipt Type", choices=[("VC","Voucher"),("OR","Official Recipt")], validators=[DataRequired()])
    recipt_no = StringField("Recipt No.", validators=[DataRequired()])
    no_items = IntegerField("Number of Items", validators=[DataRequired(), NumberRange(min=1)])
    unit_cost = FloatField("Cost per Item", validators=[DataRequired(), NumberRange(min=0.1)])
    total_cost = FloatField("Total Cost", validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField("Add")

class AddProject (FlaskForm):
    po = IntegerField("PO Number", validators=[DataRequired(), NumberRange(min= 21000000, max=30000000)])
    title = TextAreaField("Title", validators=[DataRequired()])
    amount = FloatField("Contract Amount", validators=[DataRequired()])
    duration = IntegerField("Contract Duration", validators=[DataRequired()])
    status = SelectField("Project Status", choices=[("ONGOING", "ONGOING"), ("DONE","DONE"), ("ONHOLD", "ONHOLD")])
    start = DateField("Date Started", format="%Y-%m-%d")
    end = DateField("Date Ended", format="%Y-%m-%d")
    submit = SubmitField("Submit")

    def validate_po(self, po):
        with engine.connect() as conn:
            statement = select(project_table.c.po).where(project_table.c.po == po.data)
            po1 = conn.execute(statement).first()
        
        if po1:
            raise ValidationError("Duplicate PO Number")