from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "teatimecafe_secret"

DATABASE = "tea.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tea_menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM tea_menu ORDER BY id DESC")
    teas = c.fetchall()
    conn.close()
    return render_template("index.html", teas=teas)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        description = request.form["description"]

        image_filename = None

        if "image" in request.files:
            file = request.files["image"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO tea_menu (name, category, price, description, image)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, description, image_filename))
        conn.commit()
        conn.close()

        flash("New tea menu added successfully!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM tea_menu WHERE id = ?", (id,))
    tea = c.fetchone()

    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        description = request.form["description"]

        image_filename = tea[5]

        if "image" in request.files:
            file = request.files["image"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        c.execute("""
            UPDATE tea_menu
            SET name = ?, category = ?, price = ?, description = ?, image = ?
            WHERE id = ?
        """, (name, category, price, description, image_filename, id))

        conn.commit()
        conn.close()

        flash("Tea menu updated successfully!", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", tea=tea)


@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT image FROM tea_menu WHERE id = ?", (id,))
    image = c.fetchone()

    if image and image[0]:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image[0])
        if os.path.exists(image_path):
            os.remove(image_path)

    c.execute("DELETE FROM tea_menu WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Tea menu deleted successfully!", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)