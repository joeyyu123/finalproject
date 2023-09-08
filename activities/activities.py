# activities.py
from flask import Blueprint, render_template, redirect, request, session, flash, url_for, jsonify
from cs50 import SQL
from auth.auth import login_required

activities_bp = Blueprint("activities", __name__)

db = SQL("sqlite:///database.db")

# 活動創建路由
@activities_bp.route("/create_activity", methods=["GET", "POST"])
@login_required
def create_activity():
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
        flash("開團成功！")
        return render_template("create_activity.html")
    
    return render_template("create_activity.html")

# 查看用戶歷史紀錄
@activities_bp.route("/created_history")
@login_required
def created_history():
    userid = session.get("user_id")
    
    # 獲取用戶開團和報名的紀錄
    created_activities = db.execute("SELECT * FROM activities WHERE user_id = ? AND date >= date('now') ORDER BY date", userid)    
    
    return render_template("created_history.html", created_activities=created_activities)

# 查詢活動路由
@activities_bp.route("/find_activity", methods=["GET"])
def find_activity():
    # 獲取用戶提交的篩選條件
    date = request.args.get("date")
    sport = request.args.get("sport")

    # 構建SQL查詢
    query = "SELECT * FROM activities WHERE date >= date('now')"

    # 初始化參數字典
    params = {}

    # 添加日期篩選
    if date:
        query += " AND date = :date"
        params["date"] = date

    # 添加運動類型篩選
    if sport:
        query += " AND type = :sport"
        params["sport"] = sport

    # 日期排序
    query += " ORDER BY date"

    # 執行SQL查詢
    activities = db.execute(query, **params)

    return render_template("find_activity.html", activities=activities)


# 編輯活動路由
@activities_bp.route("/edit_activity/<int:activity_id>", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    if request.method == "POST":
        userid = session.get("user_id")
        type = request.form.get("sport")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        location = request.form.get("location")

        price = request.form.get("price")
        participants = request.form.get("participants")
        remark = request.form.get("remark")
        
        db.execute("UPDATE activities SET type=?, date=?, start_time=?, end_time=?, location=?, price=?, participants=?, remark=?, user_id=? WHERE id=?"
                                            , type, date, start_time, end_time, location, price, participants, remark, userid, activity_id )
        flash("編輯完成！")
        activity = db.execute("SELECT * FROM activities WHERE id = ?", activity_id)
        return redirect(url_for('signups.view_signups', activity_id=activity_id))
        
    activity = db.execute("SELECT * FROM activities WHERE id = ?", activity_id)
    return render_template("edit_activity.html",activity=activity[0])

# 刪除
@activities_bp.route("/delete_activity", methods=["POST"])
@login_required
def delete_activity():
    try:
        activity_id = request.json.get("activity_id")
        if activity_id is None:
            return jsonify({"message": "無效的請求"}), 400
        # 先刪除與該活動相關的報名紀錄
        db.execute("DELETE FROM signups WHERE activity_id = ?", activity_id)

        # 再刪除該活動
        db.execute("DELETE FROM activities WHERE id = ?", activity_id)

        return jsonify({"message": "刪除成功"}), 200

    except Exception as e:
        return jsonify({"message": "删除失敗", "error": str(e)}), 500