from flask import Flask, flash, jsonify, redirect, render_template, request, session
from datetime import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies?)

@app.route('/')
def homepage():
    return render_template("index.html", year=datetime.now().year)


@app.route('/register', methods=["GET", "POST"])
def register():
    """Register a new user"""
    return render_template(".html")


@app.route('/login', methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        # Ensure username and password were submited
        if not request.form.get("username"):
            return apology("must provide username", 403)
        
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Query database for username

        # Ensure username exists and password is correct

        # Remember which user has logged in

        # Redirect user to home page
        return redirect("/")
    
    # User reached route via GET
    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user id
    session.clear()

    # Redirect user to login form
    return redirect("/")
