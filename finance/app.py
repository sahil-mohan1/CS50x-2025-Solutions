import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Homepage


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    owned_symbols_result = db.execute(
        # list of dicts
        "select distinct symbol from transactions where user_id = ?", session["user_id"])
    owned_symbols = [d['symbol'] for d in owned_symbols_result]  # values only list
    print("owned:", owned_symbols)
    symbol_info_lst = []
    for symbol in owned_symbols:
        symbol_info = lookup(symbol)
        net_qty_query = """
                        SELECT SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE -shares END) as net_shares
                        FROM transactions
                        WHERE user_id = ? AND symbol = ?
                        """
        symbol_info['qty'] = (db.execute(
            net_qty_query, session["user_id"], symbol)[0]['net_shares'])
        if symbol_info['qty'] != 0:
            symbol_info['value'] = symbol_info['qty'] * symbol_info['price']
            symbol_info_lst.append(symbol_info)

    # Balance in cash
    balance = db.execute("select cash from users where id= ?", session["user_id"])[0]['cash']
    # Balance in cash + value of owned stocks
    grand_total = sum(s['value'] for s in symbol_info_lst) + balance

    return render_template("index.html", symbols=symbol_info_lst, balance=balance, grand_total=grand_total)

# Buy stocks


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").strip().upper()
        try:
            shares = int(request.form.get("shares"))
        except (TypeError, ValueError):
            return apology("Invalid buy quantity")
        symbol_info = lookup(symbol)
        if not symbol_info:
            return apology("Symbol does not exist")

        if int(shares) < 1:
            return apology("Shares quantity cannot be less than 1")

        cash = db.execute("select cash from users where id = ?", session['user_id'])[0]['cash']
        buy_value = symbol_info['price'] * shares
        if (buy_value) > cash:
            return apology("You do not have sufficient funds")

        db.execute("insert into transactions (user_id, symbol, shares, price) values (?,?,?,?)",
                   session['user_id'], symbol, shares, symbol_info['price'])
        cash = cash - (buy_value)
        db.execute("update users set cash = ? where id = ?", cash, session['user_id'])

        flash(f"Purchased {shares} shares of {symbol} for {usd(buy_value)}")
        return redirect("/")

    return render_template("buy.html")

# Transaction history (buy and sell)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("select * from transactions where user_id = ?", session['user_id'])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# Lookup the price of a symbol


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol").strip()
        symbol_info = lookup(symbol)
        if not symbol_info:
            return apology("Symbol does not exist")
        return render_template("quoted.html", symbol=symbol_info)

    return render_template("quote.html")

# Register as a new user


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmation = request.form.get("confirmation").strip()

        if not username:
            return apology("Username cannot be blank")
        users = db.execute("select * from users where username = ?", username)
        if len(users) > 0:
            print("Duplicate username detected")
            return apology("Username already exists")

        if not password or not confirmation:
            return apology("Password cannot be blank")
        if password != confirmation:
            return apology("Password and confirmation do not match")
        # Hashing the password for secure storage
        hashedPassword = generate_password_hash(password)
        db.execute("insert into users (username, hash) values (?, ?)", username, hashedPassword)
        return redirect("/")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    transacted_symbols_result = db.execute(
        # list of dicts
        "select distinct symbol from transactions where user_id = ?", session["user_id"])
    transacted_symbols = [d['symbol'] for d in transacted_symbols_result]
    owned_symbols = []
    for symbol in transacted_symbols:
        net_qty_query = """
                        SELECT SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE -shares END) as net_shares
                        FROM transactions
                        WHERE user_id = ? AND symbol = ?
                        """
        if (db.execute(net_qty_query, session["user_id"], symbol)[0]['net_shares']) != 0:
            owned_symbols.append(symbol)
    if len(owned_symbols) == 0:
        return apology("You do not have any stocks to sell")

    if request.method == "POST":
        symbol = request.form.get("symbol")
        try:
            sell_qty = int(request.form.get("shares"))
        except (TypeError, ValueError):
            return apology("Invalid sell quantity")
        net_qty_query = """
                        SELECT SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE -shares END) as net_shares
                        FROM transactions
                        WHERE user_id = ? AND symbol = ?
                        """
        owned_qty = (db.execute(net_qty_query, session["user_id"], symbol)[0]['net_shares'])
        price = lookup(symbol)['price']

        if not symbol or symbol not in owned_symbols:
            print(symbol, "a", owned_symbols)
            return apology("Invalid Stock Symbol")

        if not sell_qty or sell_qty < 1:
            return apology("Sell quantity must be 1 or greater")
        if sell_qty > owned_qty:
            return apology("You do not own enough shares")

        db.execute("insert into transactions (user_id,symbol,shares, price, transaction_type) values (?,?,?,?, 'SELL')",
                   session["user_id"], symbol, sell_qty, price)
        value = sell_qty * price
        db.execute("update users set cash = cash + ? where id = ?", value, session['user_id'])
        return redirect("/")

    return render_template("sell.html", shares=owned_symbols)


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """Change password and deposit cash or withdraw cash"""
    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "password":
            password = request.form.get("password").strip()
            cnf_password = request.form.get("cnf_password").strip()
            if not password or not cnf_password:
                return apology("Invalid password")
            if password != cnf_password:
                return apology("Passwords do not match")

            hashedPassword = generate_password_hash(password)
            db.execute("update users set hash = ? where id = ?", hashedPassword, session["user_id"])
            flash("Password changed successfully!")
            return redirect("/account")

        elif form_type == "transact":
            amount = int(request.form.get("amount"))
            action = request.form.get("action")
            if not amount or amount < 1:
                return apology("Invalid Amount")
            else:
                if action == "deposit":
                    db.execute("update users set cash = cash + ? where id = ?",
                               amount, session["user_id"])
                elif action == "withdraw":
                    cash = db.execute("select cash from users where id = ?",
                                      session["user_id"])[0]["cash"]
                    if amount > cash:
                        return apology("You do not have sufficient funds")
                    else:
                        db.execute("update users set cash = cash - ? where id = ?",
                                   amount, session["user_id"])
                flash("Transaction successful!")
                return redirect("/account")

    return render_template("account.html")
