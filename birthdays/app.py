import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return redirect("/")

        month = request.form.get("month")
        if not month:
            return redirect("/")
        try:
            month = int(month)
        except ValueError:
            return redirect("/")
        if month < 1 or month > 12:
            return redirect("/")

        day = request.form.get("day")
        if not day:
            return redirect("/")
        try:
            day = int(day)
        except ValueError:
            return redirect("/")
        if day < 1 or day > 31:
            return redirect("/")

        max_id_result = db.execute("SELECT MAX(id) FROM birthdays")
        new_id = max_id_result[0]["MAX(id)"] + 1
        db.execute("insert into birthdays values (?, ?, ?, ?)",new_id, name, month, day)

        return redirect("/")

    else:

        bdays = db.execute("select * from birthdays")

        return render_template("index.html", bdays=bdays)

@app.route("/delete", methods=["POST"])
def delete():
    id = request.form.get("id")
    if id:
        db.execute("delete from birthdays where id = ?", id)
        return redirect("/")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    id = request.args.get("id")
    if not id:
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")
        if not name or not month or not day:
            return redirect(f"/edit?id={id}")
        try:
            month = int(month)
            day = int(day)
        except ValueError:
            return redirect(f"/edit?id={id}")
        if month < 1 or month > 12 or day < 1 or day > 31:
            return redirect(f"/edit?id={id}")

        db.execute(
            "UPDATE birthdays SET name = ?, month = ?, day = ? WHERE id = ?",
            name, month, day, id
        )
        return redirect("/")

    bday_lst = db.execute("SELECT * FROM birthdays WHERE id = ?", id)
    if not bday_lst:
        return redirect("/")
    bday = bday_lst[0]
    return render_template("edit.html", bday=bday)

