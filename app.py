from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
from datetime import date

app = Flask(__name__)
DB = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agenda TEXT,
            discussion TEXT,
            responsibility TEXT,
            target_date TEXT,
            remarks TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB)

@app.route("/")
def index():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT * FROM tasks ORDER BY id ASC")
    rows = c.fetchall()

    total = len(rows)
    pending = len([r for r in rows if r[6] == "Pending"])
    completed = len([r for r in rows if r[6] == "Completed"])
    overdue = len([r for r in rows if r[4] and r[6] == "Pending"])

    conn.close()

    return render_template(
        "index.html",
        rows=rows,
        total=total,
        pending=pending,
        completed=completed,
        overdue=overdue
    )

@app.route("/add", methods=["POST"])
def add():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (agenda, discussion, responsibility, target_date, remarks, status) VALUES (?, ?, ?, ?, ?, ?)",
        (
            request.form["agenda"],
            request.form["discussion"],
            request.form["responsibility"],
            request.form["target_date"],
            request.form["remarks"],
            request.form["status"]
        )
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/update/<int:task_id>", methods=["POST"])
def update(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE tasks SET agenda=?, discussion=?, responsibility=?, target_date=?, remarks=?, status=? WHERE id=?",
        (
            request.form["agenda"],
            request.form["discussion"],
            request.form["responsibility"],
            request.form["target_date"],
            request.form["remarks"],
            request.form["status"],
            task_id
        )
    )
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/import", methods=["POST"])
def import_excel():
    file = request.files["file"]
    df = pd.read_excel(file, header=4)

    conn = get_conn()
    c = conn.cursor()

    for _, row in df.iterrows():
        agenda = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
        discussion = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
        responsibility = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
        target_date = pd.to_datetime(row.iloc[4]).strftime("%Y-%m-%d") if pd.notna(row.iloc[4]) else ""
        remarks = str(row.iloc[5]) if pd.notna(row.iloc[5]) else ""
        status = str(row.iloc[6]) if pd.notna(row.iloc[6]) else "Pending"

        if agenda.strip() != "":
            c.execute(
                "INSERT INTO tasks (agenda, discussion, responsibility, target_date, remarks, status) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    agenda,
                    discussion,
                    responsibility,
                    target_date,
                    remarks,
                    status
                )
            )

    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/")


import os

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))