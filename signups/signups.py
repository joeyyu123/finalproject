# signups.py
from flask import Blueprint, render_template, redirect, request, session, flash, url_for, jsonify
from cs50 import SQL
from auth.auth import login_required

signups_bp = Blueprint("signups", __name__)

db = SQL("sqlite:///database.db")

# 報名路由
@signups_bp.route("/signup/<int:activity_id>", methods=["GET", "POST"])
@login_required
def signup(activity_id):
    if request.method == "POST":
        userid = session.get("user_id")
        name = request.form.get("name")
        contact = request.form.get("contact")
        participants = int(request.form.get("participants"))  # 注意將字符串轉換為整數
        remark = request.form.get("remark")

        # 獲取活動資訊
        activity = db.execute("SELECT * FROM activities WHERE id = ?", activity_id)[0]
        applicants =  int(activity["applicants"]) + participants

        remaining_participants = int(activity["participants"]) - applicants

        if remaining_participants < 0:
            flash("報名人數超過剩餘名額。")
            return redirect(f"/signup/{activity_id}")
        
        db.execute("BEGIN")

        try:
            # 更新活動需求人數
            db.execute("UPDATE activities SET applicants = ? WHERE id = ?", applicants, activity_id)

            # 插入報名數據
            db.execute("INSERT INTO signups (activity_id, name, contact, user_id, participants, remark) VALUES (?, ?, ?, ?, ?, ?)"
                                            , activity_id, name, contact, userid, participants, remark)

            # 提交事務
            db.execute("COMMIT")

            flash("報名成功！感謝您的參與。")
            return redirect(url_for("activities.find_activity"))
        except Exception as e:
            # 回滾事務
            db.execute("ROLLBACK")

            flash("報名失敗。請稍後再試。")
            return redirect(f"/apply/{activity_id}")
    else:
        activity = db.execute("SELECT * FROM activities WHERE id = ?", activity_id)
        return render_template("apply.html", activity=activity[0])

# 查看用戶歷史紀錄
@signups_bp.route("/applied_history")
@login_required
def applied_history():
    userid = session.get("user_id")
    
    signed_up_activities = db.execute("SELECT a.*, s.participants AS signup_participants, s.id AS signup_id FROM activities a INNER JOIN signups s ON a.id = s.activity_id WHERE s.user_id = ? AND a.date >= date('now') ORDER BY a.date DESC", userid)
    
    
    return render_template("applied_history.html", signed_up_activities=signed_up_activities)

# 查看報名路由
@signups_bp.route("/view_signups/<int:activity_id>")
@login_required
def view_signups(activity_id):
    activity = db.execute("SELECT * FROM activities WHERE id = ?", activity_id)
    signups = db.execute("SELECT * FROM signups WHERE activity_id = ?", activity_id)
    return render_template("view_signups.html", activity=activity[0], signups=signups)

# 取消報名路由
@signups_bp.route("/cancel_signup/<int:signup_id>", methods=["POST"])
@login_required
def cancel_signup(signup_id):
    try:
        activity_id = request.json.get("activity_id")
        participants = request.json.get("participants") # 獲取報名人數
        
        if activity_id is None or participants is None:
            return jsonify({"message": "無效的請求"}), 400
        
        activity = db.execute("SELECT applicants FROM activities WHERE id = ?", activity_id)
        if not activity:
            return jsonify({"message": "找不到該活動"}), 404
        

        current_applicants = activity[0]["applicants"]
        
        # 根據報名人數進行修正
        new_applicants = int(current_applicants) - int(participants)
        

        db.execute("UPDATE activities SET applicants = ? WHERE id = ?", new_applicants, activity_id)

        #在取消報名成功後，刪除相關的報名紀錄
        signup_id = request.json.get("signup_id")
        db.execute("DELETE FROM signups WHERE id = ?", signup_id)
        
        return jsonify({"message": "已取消報名"}), 200

    except Exception as e:
        return jsonify({"message": "取消失敗", "error": str(e)}), 500