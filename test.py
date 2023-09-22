from sqlalchemy import select
from data_tables import users_table, engine

with engine.connect() as conn:
    statement = select(users_table).where(users_table.c.id == 2)
    user = conn.execute(statement).first()

print(user.username)