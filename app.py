from datetime import datetime
from data_tables import engine, project_table, users_table, expenses_table, type_table, project_breakdown
from flask import Flask, flash, redirect, render_template, request, session
from form import RegistrationForm, LoginForm, AddExpenseForm, AddProject, ProjectBreakdown
from helper import login_required, get_x,get_monthly_expense, get_project_list,delete_records
from sqlalchemy import insert, select, join, text, func, update, delete
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)
    
@app.route("/")
@login_required
def index():
    with engine.connect() as conn:
        stmt = select(func.sum(project_table.c.amount)).select_from(project_table)
        contract_amount = conn.execute(stmt).first()
        stmt2 = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == 1)
        total_admin = conn.execute(stmt2).first()

    monthly = get_monthly_expense()
    expense_total = 0
    for i in monthly:
        expense_total += i

    project_list = []
    get_project_list(project_list)

    labels_chart2 = []
    for i in project_list:
        labels_chart2.append(i["po"])
    
    project_expenses = 0
    for i in project_list:
        project_expenses += i["expense"]

    return render_template("home.html",monthly=monthly,total_amount=contract_amount.sum_1,expense_total=expense_total,labels_chart2=labels_chart2,project_list=project_list,total_admin=total_admin,project_expenses=project_expenses)


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
    breakdown2 = []
    with engine.connect() as conn:
        statement = select(project_table)
        projects = conn.execute(statement)
        proj = conn.execute(statement)
        proj2 = conn.execute(statement)
        y = conn.execute(statement)
        for i in y:
            stmt = select(project_breakdown.c.project_id, project_breakdown.c.labor, project_breakdown.c.representation, project_breakdown.c.remittance, project_breakdown.c.misc, project_breakdown.c.ppe, project_breakdown.c.materials, project_breakdown.c.tools_equip).where(project_breakdown.c.project_id == i.id)
            proj_break = conn.execute(stmt).first()
            if proj_break != None:
                x = get_x(proj_break,i,conn)
                breakdown.append(x)
                breakdown2.append(x)
            else:
                x = {"status":False, "project_id":i.id}
                breakdown.append(x)
                breakdown2.append(x)
    return render_template("projects.html", projects=projects, proj=proj, breakdown=breakdown,proj2=proj2,breakdown2=breakdown2)

@app.route("/project/delete",methods=["POST"])
@login_required
def delproject():
    project_id = int(request.form.get('pro_id'))
    delete_records(project_id)
    flash("Expense Added Successfully", "success")    
    return redirect("/project")


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
        statement = text("SELECT expenses.id,title,date,description,type,recipt,recipt_no,no_items,unit_cost,total_cost FROM expenses JOIN projects ON expenses.project_id = projects.id JOIN type ON expenses.type_id = type.id")
        expenses = conn.execute(statement)

    return render_template("expense.html",expenses=expenses)

@app.route("/expense/delete", methods=["POST"])
@login_required
def expense_delete():
    form_data = []
    for name,value in request.form.items():
        if name == "table_length":
            continue
        else:
            form_data.append(int(value))

    if not form_data:
        flash("No items Deleted (Nothing was checked in the check boxes)", "danger")
        return redirect("/expense")

    with engine.connect() as conn:
        for i in form_data:
            stmt = delete(expenses_table).where(expenses_table.c.id == i)
            conn.execute(stmt)
        conn.commit()
        flash(f"{len(form_data)} Items Successfully deleted", "success")
    return redirect("/expense")

@app.route("/breakdown", methods=["POST"])
@login_required
def breakdown():
    if request.form.get("source") == "projects":
        form = ProjectBreakdown()
        project_id = request.form.get("project_id")
        return render_template("breakdown.html", project_id=project_id, form=form)
    else:
        project_id = request.form.get("project_id")
        form = ProjectBreakdown()
        if form.validate_on_submit():
            with engine.connect() as conn:
                stmt = select(project_table.c.amount).where(project_table.c.id == project_id)
                budget = conn.execute(stmt).first()

            if budget.amount < form.total.data:
                flash("Total Amount is greater than contract amount", "danger")
                return render_template("breakdown.html", project_id=project_id, form=form)
            
            with engine.connect() as conn:
                stmt = insert(project_breakdown).values(project_id=project_id, labor=form.labor.data, representation=form.representation.data, remittance=form.remittance.data, misc=form.misc.data, ppe=form.ppe.data, materials=form.materials.data, tools_equip=form.tools_equip.data)
                conn.execute(stmt)
                conn.commit()
                flash("Breakdown Successfully Added", "success")
                return redirect("/project")
        return render_template("breakdown.html", project_id=project_id, form=form)
    
@app.route("/breakdown/update", methods=["POST"])
@login_required
def breakdownupdate():
    if request.form.get("source_update") == "projects":
        form = ProjectBreakdown()
        last_breakdown = {}
        last_breakdown["labor"] = float(request.form.get("labor_breakdown"))
        last_breakdown["representation"] = float(request.form.get("representation_breakdown"))
        last_breakdown["remittance"] = float(request.form.get("remittance_breakdown"))
        last_breakdown["misc"] = float(request.form.get("misc_breakdown"))
        last_breakdown["ppe"] = float(request.form.get("ppe_breakdown"))
        last_breakdown["materials"] = float(request.form.get("materials_breakdown"))
        last_breakdown["tools_equip"] = float(request.form.get("tools_equip_breakdown"))
        last_breakdown["total"] = float(request.form.get("total_breakdown"))
        last_breakdown["id"] = request.form.get("project_id_breakdown")

        project_id = request.form.get("project_id_breakdown")

        return render_template("update_breakdown.html",last_breakdown=last_breakdown, project_id=project_id,form=form)
    else:
        form = ProjectBreakdown()
        if form.validate_on_submit:
            id = int(request.form.get("project_id_breakdown"))

            with engine.connect() as conn:
                stmt = select(project_table.c.amount).where(project_table.c.id == id)
                budget = conn.execute(stmt).first()

            if budget.amount < form.total.data:
                flash("Total Amount is greater than contract amount", "danger")
                last_breakdown = None
                return render_template("update_breakdown.html", project_id=id,form=form,last_breakdown=last_breakdown)

            with engine.connect() as conn:
                stmt2 = update(project_breakdown).where(project_breakdown.c.project_id == id).values(labor=form.labor.data, representation=form.representation.data, remittance=form.remittance.data, misc=form.misc.data, ppe=form.ppe.data, materials=form.materials.data, tools_equip=form.tools_equip.data)
                conn.execute(stmt2)
                conn.commit()
            flash("Updated Successfully", "success")
        return redirect("/project")
    
@app.route("/admin")    
@login_required
def admin():
    with engine.connect() as conn:        
        statement = text("SELECT date,description,type,recipt,recipt_no,no_items,unit_cost,total_cost FROM expenses JOIN projects ON expenses.project_id = projects.id JOIN type ON expenses.type_id = type.id WHERE expenses.project_id = 1")
        expenses = conn.execute(statement)
    return render_template("admin.html",expenses=expenses)


if __name__ == "__main__":
    app.run(debug=True)