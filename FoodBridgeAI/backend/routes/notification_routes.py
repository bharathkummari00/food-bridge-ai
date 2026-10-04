from flask import Blueprint, request, jsonify, session
from database.db import get_db

notification_bp = Blueprint("notification_bp", __name__)


@notification_bp.route("", methods=["GET"])
def get_notifications():
    user_id = session.get("user_id") or request.args.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,))
    else:
        cursor.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 15")

    rows = [dict(r) for r in cursor.fetchall()]

    if user_id:
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
    else:
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = 0")
    unread_count = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "success": True,
        "unread_count": unread_count,
        "notifications": rows
    })


@notification_bp.route("/<int:notif_id>/read", methods=["POST"])
def mark_read(notif_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Marked as read"})


@notification_bp.route("/read-all", methods=["POST"])
def mark_all_read():
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("UPDATE notifications SET is_read = 1")
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "All notifications marked as read"})
