import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == "__main__":
    app.run(debug=True)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username"):
            alert ="please input username. "
            
            return render_template("register.html", alert=alert)

        elif not request.form.get("password"):
            alert = "must provide password"
            
            return render_template("register.html", alert=alert)

        elif request.form.get("password") != request.form.get("confirmation"):
            alert = "please enter the same password"
            
            return render_template("register.html", alert=alert)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if rows:
            alert = "username already been used"
            
            return render_template("register.html", alert=alert)

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, password)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("register.html")

@app.route("/group", methods=["GET", "POST"])
def group():
    if request.method == "POST":
        
        userid = session.get("user_id")
        
        type = request.form.get("sport")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        location = request.form.get("location")
        level = request.form.get("level")
        price = request.form.get("price")
        participants = request.form.get("participants")
        remark = request.form.get("remark")
        
        db.execute("INSERT INTO activities(type, date, start_time, end_time, location, level, price, participants, remark,user_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", type, date, start_time, end_time, location, level, price, participants, remark, userid)
        
        return render_template("group.html")
    
    return render_template("group.html")


@app.route("/find")
def find():
    activities = db.execute("SELECT * FROM activities WHERE date >= date('now') ORDER BY date DESC")
    
    
    return render_template("find.html", activities=activities)