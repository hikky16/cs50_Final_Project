from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, ForeignKey, Text, Float, DateTime

engine = create_engine("sqlite:///database.db", echo=True)

meta = MetaData()

users_table = Table(
    "users",
    meta,
    Column("id",Integer,primary_key=True),
    Column("username",String(20),nullable=False,unique=True),
    Column("password",String(200),nullable=False)
)

project_table = Table(
    "projects",
    meta,
    Column("id",Integer,primary_key=True),
    Column("po",Integer,unique=True,nullable=False),
    Column("title",Text,nullable=False),
    Column("amount",Float,nullable=False),
    Column("duration",Integer,nullable=False),
    Column("status",String(20),nullable=False),
    Column("start_date",DateTime,nullable=True,),
    Column("end_date",DateTime,nullable=True,),
)

type_table = Table(
    "type",
    meta,
    Column("id",Integer,primary_key=True),
    Column("type",String(20),nullable=False),
)

expenses_table = Table(
    "expenses",
    meta,
    Column("id",Integer,primary_key=True),
    Column("project_id",ForeignKey("projects.id"),nullable=False),
    Column("date",DateTime,nullable=False),
    Column("description",String(200),nullable=False),
    Column("type_id",ForeignKey("type.id"),nullable=False),
    Column("recipt",String(5),nullable=False),
    Column("recipt_no",String(20),nullable=False),
    Column("no_items",Integer,nullable=False),
    Column("unit_cost",Float,nullable=False),
    Column("total_cost",Float,nullable=False),
    Column("time_entered",DateTime,nullable=False),
)
