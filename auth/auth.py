# auth.py
from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from functools import wraps

auth_bp = Blueprint("auth", __name__)

db = SQL("sqlite:///database.db")

# 登入路由
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # 清除任何用戶ID
    session.clear()

    if request.method == "POST":
        # 確認帳號已輸入
        if not request.form.get("username"):
            alert = "請輸入用戶名。"
            return render_template("login.html", alert=alert)

        # 確認密碼已輸入
        elif not request.form.get("password"):
            alert = "請輸入密碼。"
            return render_template("login.html", alert=alert)

        # 查詢資料庫
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # 確認用戶名存在且正確
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            alert = "帳號或密碼錯誤"
            return render_template("login.html", alert=alert)

        # 記住已經登入的用戶
        session["user_id"] = rows[0]["id"]

        # 重新整理網頁
        return redirect("/activities/find_activity")

    else:
        return render_template("login.html")

# 登出
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# 註冊路由
@auth_bp.route("/register", methods=["GET", "POST"])
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

# 登入驗證裝飾器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
