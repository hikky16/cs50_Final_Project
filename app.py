from flask import Flask, flash, redirect, render_template, request, session
from form import RegistrationForm, LoginForm
from sqlalchemy import insert, select
from data_tables import users_table,engine,meta
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = "jan"

    
@app.route("/")
def index():
    return redirect("/login")


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

        return render_template("dashboard.html")
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




if __name__ == "__main__":
    app.run(debug=True)