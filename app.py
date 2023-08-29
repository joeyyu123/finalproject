import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

# 自動重新加載
app.config["TEMPLATES_AUTO_RELOAD"] = True


# SESSION
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# 配置 CS50 Library 使用 SQLite 
db = SQL("sqlite:///database.db")

# 要求登入
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

# 確保響應不被緩存
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# apology
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

# 主頁
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# 登入路由
@app.route("/login", methods=["GET", "POST"])
def login():
    # 清除任何用户ID
    session.clear()

    if request.method == "POST":
        # 确保提交了用户名
        if not request.form.get("username"):
            return apology("必須提供用戶名", 403)

        # 确保提交了密码
        elif not request.form.get("password"):
            return apology("必須輸入密碼", 403)

        # 查询数据库获取用户名
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # 确保用户名存在且密码正确
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("無效的用戶名或密碼", 403)

        # 记住已登录用户
        session["user_id"] = rows[0]["id"]

        # 重定向用户到主页
        return redirect("/")

    else:
        return render_template("login.html")

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# 註冊路由
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            alert = "請輸入用戶名。"
            return render_template("register.html", alert=alert)
        
        elif not request.form.get("password"):
            alert = "必須提供密碼。"
            return render_template("register.html", alert=alert)
        
        elif request.form.get("password") != request.form.get("confirmation"):
            alert = "請輸入相同的密碼。"
            return render_template("register.html", alert=alert)
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        if rows:
            alert = "用戶名已被使用。"
            return render_template("register.html", alert=alert)
        
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, password)
        
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    
    return render_template("register.html")

# 活動創建
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
        
        db.execute("INSERT INTO activities(type, date, start_time, end_time, location, level, price, participants, remark, user_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", type, date, start_time, end_time, location, level, price, participants, remark, userid)
        
        return render_template("group.html")
    
    return render_template("group.html")

# 檢視
@app.route("/find")
def find():
    activities = db.execute("SELECT * FROM activities WHERE date >= date('now') ORDER BY date DESC")
    return render_template("find.html", activities=activities)

# 查看用戶歷史紀錄
@app.route("/myhistory")
def myhistory():
    userid = session.get("user_id")
    activities = db.execute("SELECT a.* FROM activities a INNER JOIN users u ON a.user_id = u.id WHERE a.date >= date('now') AND u.id = ? ORDER BY a.date DESC", userid)
    return render_template("myhistory.html", activities=activities)

# 刪除
@app.route("/delete_activity", methods=["POST"])
def delete_activity():
    try:
        activity_id = request.json.get("activity_id")
        if activity_id is None:
            return jsonify({"message": "無效的請求"}), 400

        db.execute("DELETE FROM activities WHERE id = ?", activity_id)
        return jsonify({"message": "刪除成功"}), 200

    except Exception as e:
        return jsonify({"message": "删除失败", "error": str(e)}), 500


