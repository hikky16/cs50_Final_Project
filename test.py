from sqlalchemy import select, insert
from data_tables import users_table, engine, project_table, type_table

# type_list = ["PPE","Tools and Equipment", "Materials" , "Rentals" , "Fuels" , "SOP/Project" , "Misc.Operation" , "Overhead payroll" , "Office Supply" , "Water Utility" , "Power Utility" , "Transportaion" , "Misc. Admin" , "Insurance" , "Cash Advance" , "Labor" , "Solicitation" , "Asset" , "Repair & Maintenance"]
# with engine.connect() as conn:
#     for i in type_list:
#         statement = insert(type_table).values(type=i)
#         conn.execute(statement)
#         conn.commit()



# Fuels
# SOP/ Project
# Misc. Operation
# Overhead payroll
# Office Supply
# Water Utility
# Power Utility
# Trans
# "Misc. Admin" , "Insurance" , "Cash Advance" , "Labor" , "Solicitation" , "Asset" , "Repair & Maintenance"
# Insurance
# Cash Advance
# Labor
# Solicitation
# Asset
# Repair & Maintenan

with engine.connect() as conn:
    statement = select(project_table.c.amount).where(project_table.c.id == 9)
    amount = conn.execute(statement).first()
    
print(amount.amount)