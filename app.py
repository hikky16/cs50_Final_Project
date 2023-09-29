from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from form import RegistrationForm, LoginForm, AddExpenseForm, AddProject
from helper import login_required
from sqlalchemy import insert, select, join, text, func
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
            stmt = select(project_breakdown.c.project_id, project_breakdown.c.labor, project_breakdown.c.representation, project_breakdown.c.remittance, project_breakdown.c.misc, project_breakdown.c.ppe, project_breakdown.c.materials, project_breakdown.c.tools_equip).where(project_breakdown.c.project_id == i.id)
            proj_break = conn.execute(stmt).first()
            if proj_break != None:
                labor_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 16)
                rep_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 6)
                rem_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 14)
                misc_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 7)
                ppe_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 1)
                mat_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 3)
                tol_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 2)

                labor = conn.execute(labor_stmt).first()
                if labor.sum_1 == None:
                    labor = 0
                else:
                    labor = labor.sum_1

                rep = conn.execute(rep_stmt).first()
                if rep.sum_1 == None:
                    rep = 0
                else:
                    rep = rep.sum_1

                remit = conn.execute(rem_stmt).first()
                if remit.sum_1 == None:
                    remit = 0
                else:
                    remit = remit.sum_1

                misc = conn.execute(misc_stmt).first()
                if misc.sum_1 == None:
                    misc = 0
                else:
                    misc = misc.sum_1

                ppe = conn.execute(ppe_stmt).first()
                if ppe.sum_1 == None:
                    ppe = 0
                else:
                    ppe = ppe.sum_1

                mat = conn.execute(mat_stmt).first()
                if mat.sum_1 == None:
                    mat = 0
                else:
                    mat = mat.sum_1

                tol = conn.execute(tol_stmt).first()
                if tol.sum_1 == None:
                    tol = 0
                else:
                    tol = tol.sum_1

                pro_expenses = conn.execute(text(f"SELECT title,date,description,type,recipt,recipt_no,no_items,unit_cost,total_cost FROM expenses JOIN projects ON expenses.project_id = projects.id JOIN type ON expenses.type_id = type.id WHERE project_id ={i.id} ORDER BY date DESC"))
                expen = []
                for z in pro_expenses:
                    expen.append(z)
                x = {"project_id":proj_break.project_id, "labor":proj_break.labor, "representation":proj_break.representation, "remittance":proj_break.remittance, "misc":proj_break.misc, "ppe":proj_break.ppe, "materials":proj_break.materials, "tools_equip":proj_break.tools_equip, "status":True, "re_labor":proj_break.labor - labor, "re_representation":proj_break.representation - rep, "re_remittance":proj_break.remittance - remit, "re_misc":proj_break.misc - misc, "re_ppe":proj_break.ppe - ppe, "re_materials":proj_break.materials - mat, "re_tools_equip":proj_break.tools_equip - tol, "pro_expen":expen}
                breakdown.append(x)
            else:
                x = {"status":False, "project_id":i.id}
                breakdown.append(x)
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