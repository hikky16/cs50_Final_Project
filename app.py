from flask import Flask, flash, redirect, render_template,request
from form import RegistrationForm, LoginForm


app = Flask(__name__)

app.config["SECRET_KEY"] = "jan"


@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        return render_template("login.html")
    else:
        return render_template("login.html", form=form)

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()

    if request.method == "POST":

        return render_template("register.html")
    
    else:
        return render_template("register.html", form=form)




if __name__ == "__main__":
    app.run(debug=True)