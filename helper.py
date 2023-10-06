from flask import redirect, session
from functools import wraps
from sqlalchemy import select,func,text, delete
from data_tables import expenses_table, engine, project_table,project_breakdown


def login_required(f):
    "FROM CS50 finance helper"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_x(proj_break,i,conn):
    labor_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 16)
    rep_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 6)
    rem_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 14)
    misc_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 7)
    ppe_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 1)
    mat_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 3)
    tol_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id, expenses_table.c.type_id == 2)
    total_stmt = select(func.sum(expenses_table.c.total_cost)).select_from(expenses_table).where(expenses_table.c.project_id == i.id)

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

    total = conn.execute(total_stmt).first()
    if total.sum_1 == None:
        total = 0
    else:
        total = total.sum_1

    total_budget = proj_break.labor + proj_break.representation + proj_break.remittance + proj_break.misc + proj_break.ppe + proj_break.materials + proj_break.tools_equip
    total_rem = total_budget - total
    pro_expenses = conn.execute(text(f"SELECT title,date,description,type,recipt,recipt_no,no_items,unit_cost,total_cost FROM expenses JOIN projects ON expenses.project_id = projects.id JOIN type ON expenses.type_id = type.id WHERE project_id ={i.id} ORDER BY date DESC"))
    expen = []
    for z in pro_expenses:
        expen.append(z)
    x = {"project_id":proj_break.project_id, "labor":proj_break.labor, "representation":proj_break.representation, "remittance":proj_break.remittance, "misc":proj_break.misc, "ppe":proj_break.ppe, "materials":proj_break.materials, "tools_equip":proj_break.tools_equip, "status":True, "re_labor":proj_break.labor - labor, "re_representation":proj_break.representation - rep, "re_remittance":proj_break.remittance - remit, "re_misc":proj_break.misc - misc, "re_ppe":proj_break.ppe - ppe, "re_materials":proj_break.materials - mat, "re_tools_equip":proj_break.tools_equip - tol, "pro_expen":expen, "total":total_budget, "re_total":total_rem, "ex_total":total}
    return x

def get_monthly_expense():
    with engine.connect() as conn:
        stmt = text("SELECT strftime('%Y-%m', date) AS 'month_date', SUM(total_cost) AS total_cost_sum FROM expenses GROUP BY strftime('%Y-%m', date) ORDER BY 'month_date'")
        expenses = conn.execute(stmt)

    date_list = ["2023-01","2023-02","2023-03","2023-04","2023-05","2023-06","2023-07","2023-08","2023-09","2023-10","2023-11","2023-12"]
    data = {}
    for i in expenses:
       data[i.month_date] = i.total_cost_sum

    data_date = data.keys()

    monthly = []
    for i in date_list:
        if i in data_date:
            monthly.append(data[i])
        else:
            monthly.append(0)

    return monthly

def get_project_list(project_list):
    with engine.connect() as conn:
        stmt2 = select(project_table.c.id,project_table.c.po,project_table.c.amount)
        project_amounts = conn.execute(stmt2)
        for i in project_amounts:
            if i.id == 1:
                continue
            stmt3 = select(func.sum(expenses_table.c.total_cost)).where(expenses_table.c.project_id == i.id)
            x = conn.execute(stmt3).first()
            if x.sum_1 == None:
                y = 0 
            else: 
                y = x.sum_1
            z = {"po":i.po, "amount":i.amount, "expense":y}
            project_list.append(z)

def delete_records(project_id):
    with engine.connect() as conn:
        stmt = delete(project_breakdown).where(project_breakdown.c.project_id == project_id)
        stmt2 = delete(expenses_table).where(expenses_table.c.project_id == project_id)
        stmt3 = delete(project_table).where(project_table.c.id == project_id)
        statements = [stmt,stmt2,stmt3]
        for i in statements:
            conn.execute(i)
        conn.commit()