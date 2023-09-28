from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from form import RegistrationForm, LoginForm, AddExpenseForm, AddProject
from helper import login_required
from sqlalchemy import insert, select, join, text
from data_tables import engine, project_table, users_table, expenses_table, type_table, project_breakdown
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = "jan"

    
@app.route("/")
@login_required
def index():
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out Successfully","success")
    return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with engine.connect() as conn:
            statement = select(users_table).where(users_table.c.username == form.username.data)
            user = conn.execute(statement).first()
        if not user or user.username != form.username.data:
            flash("Login unsuccessful, Invalid Username","danger")
            return render_template("login.html", form=form)

        if not check_password_hash(user.password, form.password.data):
            flash("Login unsuccessful, Invalid Password","danger")
            return render_template("login.html", form=form)
        
        session["username"] = user.username

        return redirect("/")
    return render_template("login.html", form=form)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with engine.connect() as conn:
            password_hash = generate_password_hash(form.password.data)
            statement = insert(users_table).values(username=form.username.data, password=password_hash)
            conn.execute(statement)
            conn.commit()      
        flash("Account created Successfully", "success")
        return redirect("/login")
    return render_template("register.html", form=form)

@app.route("/addexpense", methods=["POST", "GET"])
@login_required
def add():
    form = AddExpenseForm()
    if form.validate_on_submit():
        with engine.connect() as conn:
            date_now = datetime.utcnow()
            statement = insert(expenses_table).values(project_id=form.project_id.data, date=form.date.data, description=form.description.data, type_id=form.type_id.data, recipt=form.recipt.data, recipt_no=form.recipt_no.data, no_items=form.no_items.data, unit_cost=form.unit_cost.data, total_cost=form.total_cost.data, time_entered=date_now)
            conn.execute(statement)
            conn.commit()
            flash("Expense Added Successfully", "success")
        return redirect("/addexpense")
    return render_template("addexpense.html", form=form)

@app.route("/project")
@login_required
def project():
    breakdown = []
    with engine.connect() as conn:
        statement = select(project_table)
        projects = conn.execute(statement)
        proj = conn.execute(statement)
        y = conn.execute(statement)
        for i in y:
            stmt = select(project_breakdown.c.project_id, project_breakdown.c.labor, project_breakdown.c.representation, project_breakdown.c.remittance, project_breakdown.c.misc, project_breakdown.c.ppe, project_breakdown.c.materials, project_breakdown.c.tools_equip).where(project_breakdown.c.id == i.id)
            proj_break = conn.execute(stmt).first()
            if proj_break != None:
                x = {"project_id":proj_break.project_id, "labor":proj_break.labor, "representation":proj_break.represenation, "remittance":proj_break.remittance, "misc":proj_break.misc, "ppe":proj_break.ppe, "materials":proj_break.materials, "tools_equip":proj_break.tools_equip, "status":True}
                breakdown.append(x)
            else:
                x = {"status":False, "project_id":i.id}
                breakdown.append(x)

        print(breakdown)
    return render_template("projects.html", projects=projects, proj=proj, breakdown=breakdown)

@app.route("/addproject", methods=["POST", "GET"])
@login_required
def addproject():
    form = AddProject()
    if form.validate_on_submit():
        with engine.connect() as conn:
            statement = insert(project_table).values(po=form.po.data, title=form.title.data, amount=form.amount.data, duration=form.duration.data, status=form.status.data, start_date=form.start.data, end_date=form.end.data)
            conn.execute(statement)
            conn.commit()
            flash("Added New Projects", "success")
            return redirect("/project")
        
    return render_template("addprojects.html", form=form)

@app.route("/expense")
@login_required
def expense():
    with engine.connect() as conn:        
        statement = text("SELECT title,date,description,type,recipt,recipt_no,no_items,unit_cost,total_cost FROM expenses JOIN projects ON expenses.project_id = projects.id JOIN type ON expenses.type_id = type.id")
        expenses = conn.execute(statement)

    return render_template("expense.html",expenses=expenses)

if __name__ == "__main__":
    app.run(debug=True)