from flask import Flask, render_template
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///database.db")  # 配置資料庫連接

# 設置其他全局配置，例如路由前綴等

# 確保響應不被緩存
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# 主頁
@app.route("/", methods=["GET", "POST"])
def index():
    activities = db.execute("SELECT * FROM activities WHERE date >= date('now') ORDER BY date")
    return render_template("index.html",activities=activities)

# 注冊Blueprint模組
from auth.auth import auth_bp
from activities.activities import activities_bp
from signups.signups import signups_bp


app.register_blueprint(auth_bp)
app.register_blueprint(activities_bp, url_prefix="/activities")
app.register_blueprint(signups_bp, url_prefix="/signups")

if __name__ == "__main__":
    app.run()
