import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired

from helpers import error_message, login_required, is_valid_email

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
migrate = Migrate(app, db)

class User(db.Model):
    """User for database"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure OAuth
oauth = OAuth(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Create a secret token
s = Serializer(app.config['SECRET_TOKEN'])

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

    # User reached route via POST
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return error_message("Must provide a valid email", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return error_message("Must provide a password", 403)

        # Query database for username
        user = User.query.filter_by(email=request.form.get("email")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.pw_hash, request.form.get("password")):
            return error_message("Invalid email &/or password", 403)
        
        # Remember which user has logged in
        else:
            session["user_id"] = user.id

            # Redirect user to home page
            flash("Login successful", "success")
            return redirect("/")

    # User reached route via GET
    return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user id
    session.clear()

    # Redirect user to welcome page
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
            return error_message("Must provide username", 400)
        if not is_valid_email(email):
            return error_message("Must provide a valid email", 400)
        if not password:
            return error_message("Must provide password", 400)
        if not confirmation:
            return error_message("Must provide password confirmation", 400)

        # Check matching passwords
        if password != confirmation:
            return error_message("Passwords must match", 400)

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return error_message("This email is already in use", 400)

        # Hash the user's password
        pw_hash = generate_password_hash(password)

        # Store username and hashed pw temporarily in session for confirmation
        session['username'] = username
        session['password'] = pw_hash

        # Generate verification token
        token = s.dumps(email, salt='email-confirm')

        # Create the confirmation URL
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email_confirmation.html', confirm_url=confirm_url)
        subject = "Confirm your email"

        # Send the confirmation email
        msg = Message(subject, sender='your_email@gmail.com', recipients=[email])
        msg.html = html
        mail.send(msg)

        flash("A confirmation email has been sent. Please check your inbox.", "info")
        return redirect("/")

    # User reached route via GET
    return render_template("register.html")


@app.route("/confirm/<token>")
def confirm_email(token):
    """Validate email"""
    try:
        # Decrypt the token to get the email
        email = s.loads(token, salt='email-confirm', max_age=3600)  # Token expires after 1 hour
    except (BadSignature, SignatureExpired):
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect("/register")

    # Check if email is already registered
    user = User.query.filter_by(email=email).first()

    if user:
        flash("This email has already been confirmed.", "info")
        return redirect("/login")

    # Retrieve username and hashed password from session
    username = session.pop('username', None)
    password = session.pop('password', None)

    if not username or not password:
        flash("Error: Missing user information.", "danger")
        return redirect("/register")

    # Create new user
    new_user = User(username=username, email=email, pw_hash=password)
    db.session.add(new_user)
    db.session.commit()

    # Automatically log in the user after registration
    session["user_id"] = new_user.id

    flash("Registration successful!", "success")
    return redirect('/')


@app.route("/welcome")
def welcome():
    """Display Welcome page"""
    return render_template("welcome.html")
