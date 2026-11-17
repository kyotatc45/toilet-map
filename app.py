
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-key-change-this-before-deployment"
)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "kyoutasuzuki")

BUILDINGS = [
    "A", "B", "C", "D", "E", "F", "G", "H",
    "J", "K", "L", "M", "N", "Q", "R", "S"
]


@app.route("/")
def top():
    session.pop("admin_logged_in", None)
    return render_template("top.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        return render_template(
            "login.html",
            error="パスワードが違います。"
        )

    return render_template("login.html")


@app.route("/search")
def index():
    building = request.args.get("building")
    floor = request.args.get("floor")
    toilets = []

    if building and floor:
        try:
            floor = int(floor)
            if floor < 1:
                raise ValueError
        except (TypeError, ValueError):
            return "階の指定が正しくありません。", 400

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT floor, x, y
            FROM toilets
            WHERE building = ? AND floor = ?
            ORDER BY floor
        """, (building, floor))

        toilets = cursor.fetchall()
        conn.close()

    return render_template(
        "index.html",
        building=building,
        floor=floor,
        toilets=toilets
    )


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, building, floor
        FROM toilets
        ORDER BY building, floor
    """)

    toilets = cursor.fetchall()
    conn.close()

    return render_template(
        "admin.html",
        toilets=toilets
    )


@app.route("/admin/add", methods=["POST"])
def add_toilet():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    building = request.form.get("building")
    floor = request.form.get("floor")
    x = request.form.get("x")
    y = request.form.get("y")

    if building not in BUILDINGS:
        return "棟の指定が正しくありません。", 400

    try:
        floor = int(floor)
        if floor < 1:
            raise ValueError
    except (TypeError, ValueError):
        return "階は1以上の整数で入力してください。", 400

    if building == "S" and floor in [3, 4, 5, 6, 7]:
        try:
            x = float(x)
            y = float(y)

            if not (0 <= x <= 100 and 0 <= y <= 100):
                raise ValueError
        except (TypeError, ValueError):
            return "地図上の位置をクリックしてください。", 400
    else:
        x = None
        y = None

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO toilets (building, floor, toilet_type, x, y)
        VALUES (?, ?, ?, ?, ?)
    """, (building, floor, "未設定", x, y))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:toilet_id>", methods=["POST"])
def delete_toilet(toilet_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM toilets WHERE id = ?",
        (toilet_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route("/admin/delete-building/<building>", methods=["POST"])
def delete_building(building):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if building not in BUILDINGS:
        return "棟の指定が正しくありません。", 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM toilets WHERE building = ?",
        (building,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
