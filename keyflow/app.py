import sqlite3
from flask import Flask, redirect, render_template, session, request, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology

# Initialize global DB connection (consistent with the original script)
conn = sqlite3.connect("keyflow.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def create_app():
    """Application factory for Flask."""
    app = Flask(__name__)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    @app.route("/")
    def index():
        """Show the main typing test page."""
        is_logged_in = "user_id" in session
        return render_template("index.html", is_logged_in=is_logged_in)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in."""
        if request.method == "POST":
            session.clear()

            username = request.form.get("username", "").strip()
            if not username:
                return apology("Username is required!")

            user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            password = request.form.get("password", "").strip()
            if not password:
                return apology("Password is required!")

            if not user or not check_password_hash(user["hash"], password):
                return apology("Incorrect username or password")

            session["user_id"] = user["id"]
            return redirect("/")

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Register user."""
        if request.method == "POST":
            session.clear()

            username = request.form.get("username", "").strip()
            if not username:
                return apology("Username is required")
            
            users = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()
            if len(users) != 0:
                return apology("Username already exists")

            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()
            if not password or not confirm_password:
                return apology("Password is required!")

            if password != confirm_password:
                return apology("Passwords do not match")

            hash = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
            conn.commit()
            flash("Registered successfully! Please log in.")
            return redirect("/login")

        return render_template("register.html")

    @app.route("/leaderboard")
    @login_required
    def leaderboard():
        """Show leaderboard for different time categories."""
        time_category = request.args.get("time", 30, type=int)

        query = """
            SELECT u.username, s.wpm, s.accuracy, s.timestamp
            FROM scores s
            JOIN users u ON s.user_id = u.id
            WHERE s.test_time = ?
            ORDER BY s.wpm DESC, s.accuracy DESC
            LIMIT 5
        """
        scores = cursor.execute(query, (time_category,)).fetchall()

        return render_template("leaderboard.html", scores=scores, current_time=time_category)

    @app.route("/save-score", methods=["POST"])
    @login_required
    def save_score():
        """Save a user's score to the database."""
        data = request.get_json()
        wpm = data.get("wpm")
        accuracy = data.get("accuracy")
        test_time = data.get("test_time")
        user_id = session.get("user_id")

        if not all([wpm, accuracy, test_time, user_id]):
            return apology("Missing data", 400)

        cursor.execute(
            "INSERT INTO scores (user_id, wpm, accuracy, test_time) VALUES (?, ?, ?, ?)",
            (user_id, wpm, accuracy, test_time)
        )
        conn.commit()
        return {"status": "success"}, 200

    @app.route("/logout")
    def logout():
        """Log user out."""
        if session.get("user_id"):
            session.clear()
            return render_template("logout.html")
        else:
            return apology("Invalid request!")

    return app

# Add 'app' variable so 'flask run' still works as expected
app = create_app()
