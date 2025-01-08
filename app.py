import os
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from helpers import error_message, login_required

# Configure application
load_dotenv() #Load variables .env
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Verify if secret key is correctly loaded
if not app.secret_key:
    raise ValueError("No SECRET_KEY found in environment")

# Set up the database URI (SQLite in this case)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petpal.db"

# Disable tracking modifications for performance reasons
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure OAuth
oauth = OAuth(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
@login_required
def home():
    """Display homepage"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            return error_message("must provide email", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return error_message("must provide password", 403)

        # Query database for username
        user = User.query.filter_by(email=request.form.get("email")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, request.form.get("password")):
            return error_message("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username, email and password were submitted
        if not username:
            return error_message("must provide username", 400)
        if not email:
            return error_message("must provide email", 400)
        if not password:
            return error_message("must provide password", 400)
        if not confirmation:
            return error_message("must provide password", 400)

        # Check matching passwords
        if not password == confirmation:
            return error_message("passwords must match", 400)

        # Check if username is already taken
        existing_user = db.execute("SELECT * FROM users WHERE email = ?", email)
        if existing_user:
            return error_message("You already have an account", 400)

        else:
            # Hash user password
            hash = generate_password_hash(password)

            # Insert user in database
            db.execute("INSERT INTO users (username, email, hash) VALUES(?, ?, ?)", username, email, hash)

            # Redirect user to home page
            return redirect('/')

    else:
        return render_template("register.html")

@app.route("/welcome")
def welcome():
    """Display Welcome page"""
    return render_template("welcome.html")
