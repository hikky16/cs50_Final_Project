from sqlalchemy import select, insert
from data_tables import users_table, engine, project_table, type_table,expenses_table
from csv import DictReader
from datetime import datetime

# Fuels
# SOP/Project
# Misc. Operation
# Overhead payroll
# Office Supply
# Water Utility
# Power Utility
# Trans
# Misc. Admin
# Insurance
# Cash Advance
# Labor
# Solicitation
# Asset
# Repair & Maintenan



# Tools and Equip False
# SOP/ Project False
# Rental False
date_now = datetime.utcnow()

with open("expense.csv") as file:
    reader = DictReader(file)
    with engine.connect() as conn:
        stmt = select(project_table.c.id,project_table.c.po)
        stmt2 = select(type_table.c.id,type_table.c.type)
        proj = conn.execute(stmt)
        typ = conn.execute(stmt2)

    projects = {}
    for i in proj:
        projects[i.po] = i.id

    types = {}
    for i in typ:
        types[i.type] = i.id

    type_list = []
    for i in reader:
        if i["PROJECT"] == "ADMIN":
            i["PROJECT"] = 1
        else:
            i["PROJECT"] = int(i["PROJECT"].split()[0])
            i["PROJECT"] = projects[i["PROJECT"]]

        i["DATE"] = datetime.strptime(i["DATE"],"%m/%d/%Y")
        i["NO. ITEMS"] = int(float(i["NO. ITEMS"]))
        i[" UNIT COST "] = float(i[" UNIT COST "])
        i[" TOTAL COST "] = float(i[" TOTAL COST "])
        if i[" TYPE "] == "Tools and Equip":
            i[" TYPE "] = 2
        elif i[" TYPE "] == "SOP/ Project":
            i[" TYPE "] = 6
        elif i[" TYPE "] == "Rental":
            i[" TYPE "] = 4
        elif i[" TYPE "] == "Misc. Operation":
            i[" TYPE "] = 7
        else:
            i[" TYPE "] = types[i[" TYPE "]]
        
        with engine.connect() as conn:
            stmt = insert(expenses_table).values(project_id=i["PROJECT"],date=i["DATE"],description=i[" DESCRIPTION "],type_id=i[" TYPE "],recipt=i["RECIPT TYPE"],recipt_no=i["RECIPT NUMBER"],no_items=i["NO. ITEMS"],unit_cost=i[" UNIT COST "],total_cost=i[" TOTAL COST "],time_entered=date_now)
            conn.execute(stmt)
            conn.commit()
        
print(">>>>>>>>>>>>>>>DONE<<<<<<<<<<<<<<<<<<")
    