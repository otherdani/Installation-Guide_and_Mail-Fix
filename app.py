import os
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
import logging
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired


from extensions import db, migrate, session as session_ext
from helpers import error_message, login_required, is_valid_email
from models import User, Breed, Species, Pet

# Configure application
load_dotenv() #Load variables from .env
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Verify if secret key is correctly loaded
if not app.secret_key:
    raise ValueError("No SECRET_KEY found in environment")

# Set up the database URI (SQLite in this case)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petpal.db"

# Disable tracking modifications for performance reasons
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db
db.init_app(app)
migrate.init_app(app, db)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
session_ext.init_app(app)  # Initialize session

# Configure OAuth
oauth = OAuth(app)

# Configure Flask-Mail
# Sentitive data is in a .env file to improve security
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("PETPAL_EMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("PETPAL_EMAIL_PW")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


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
    pets = Pet.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", pets=pets)


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
            return error_message("This email is already registered.", 400)

        # Hash the user's password
        pw_hash = generate_password_hash(password)

        # Store username and hashed pw temporarily in session for confirmation
        session['username'] = username
        session['password'] = pw_hash

        try:
            # Generate token and send email
            s = Serializer(app.secret_key)
            token = s.dumps(email, salt='email-confirm')

            # Create the confirmation URL
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('email_confirmation.html', confirm_url=confirm_url)
            subject = "Confirm your email"

            logging.basicConfig(level=logging.DEBUG)
            # Send the confirmation email
            msg = Message(subject, sender=os.getenv("PETPAL_EMAIL"), recipients=[email])
            msg.html = html
            mail.send(msg)

            flash("A confirmation email has been sent. Please check your inbox and your spam folder.", "info")
            return redirect("/")

        except (KeyError, ValueError) as e:
            app.logger.error("Error during email sending or token generation: %s", e)
            session.clear()  # Clean up session on failure
            return error_message("An error occurred. Please try again.", 500)

    # User reached route via GET
    return render_template("register.html")


@app.route("/confirm/<token>")
def confirm_email(token):
    """Validate email"""
    try:
        # Deserialize token
        s = Serializer(app.secret_key)
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except (BadSignature, SignatureExpired) as e:
        app.logger.error("Token error: %s", e)
        flash("The confirmation link is invalid or has expired. Please request a new confirmation email.", "danger")
        return redirect("/register")

    # Verify user doesn't already exist
    if User.query.filter_by(email=email).first():
        flash("This email has already been confirmed.", "info")
        return redirect("/login")

    # Create new user from session-stored data
    username = session.pop('username', None)
    password = session.pop('password', None)

    if not username or not password:
        flash("Error: Missing user information.", "danger")
        return redirect("/register")

    new_user = User(username=username, email=email, pw_hash=password)
    db.session.add(new_user)
    db.session.commit()

    # Log in user
    session["user_id"] = new_user.id
    flash("Registration successful!", "success")
    return redirect("/")


@app.route("/welcome")
def welcome():
    """Display Welcome page"""
    return render_template("welcome.html")

@app.route("/new_pet", methods=["GET", "POST"])
@login_required
def new_pet():
    """Add new pet to database"""
    if request.method == 'POST':
        # Get pet data
        pet_name = request.form.get('name')
        birth_date = request.form.get('birth_date') if request.form.get('birth_date') else None
        adoption_date = request.form.get('adoption_date') if request.form.get('adoption_date') else None
        sex = request.form.get('sex')
        species = request.form.get('species')
        breed = request.form.get('breed')
        sterilized = request.form.get('sterilized') == 'yes'
        microchip_number = request.form.get('microchip_number') if request.form.get('microchip_number') else None
        insurance_company = request.form.get('insurance_company') if request.form.get('insurance_company') else None
        insurance_number = request.form.get('insurance_number') if request.form.get('insurance_number') else None

        # Convert dates
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
        adoption_date = datetime.strptime(adoption_date, '%Y-%m-%d')

        # Save pet data in database
        new_pet_data = Pet(user_id = session["user_id"],name=pet_name, birth_date=birth_date, adoption_date=adoption_date,
                      sex=sex, species_id=species, breed_id=breed,
                      sterilized=sterilized, microchip_number=microchip_number,
                      insurance_company=insurance_company, insurance_number=insurance_number)
        db.session.add(new_pet_data)
        db.session.commit()

        # Redirect to homepage
        return redirect("/")
    
    # User reached route via GET
    species = Species.query.all()  # Obtain species
    print(species)
    return render_template('new_pet.html', species=species)


@app.route('/get_breeds/<int:species_id>', methods=['GET'])
@login_required
def get_breeds(species_id):
    """Show breed list"""
    breeds = Breed.query.filter_by(species_id=species_id).all()
    breed_data = [{"id": breed.id, "name": breed.name} for breed in breeds]
    return jsonify(breed_data)


if __name__ == "__main__":
    app.run(debug=True)
