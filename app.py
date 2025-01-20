import os
import logging
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired


from extensions import db, migrate, session as session_ext, csrf
from helpers import error_message, login_required
from forms import RegisterForm, LoginForm, PetForm
from models import User, Breed, Species, Pet

# Configure application
load_dotenv() #Load variables from .env
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Verify if secret key is correctly loaded
if not app.secret_key:
    raise ValueError("No SECRET_KEY found in environment")

# Set folder for photos
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOADED_PHOTOS_DEST'] = app.config['UPLOAD_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024  # Max size: 6MB

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

# Initialize CSRF protection with the app
csrf.init_app(app)

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
    form = LoginForm()

    # User reached route via POST
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.pw_hash, password):
            return error_message("Invalid email &/or password", 403)
      
        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        flash("Login successful", "success")
        return redirect("/")

    # User reached route via GET
    return render_template("login.html", form=form)


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
    form = RegisterForm()

    # User reached route via POST
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirmation = form.confirmation.data

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return error_message("This email is already registered. Try to login", 400)
        
        # Check password = confirmation
        if password != confirmation:
            return error_message("Passwords must match.", 400)

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
    return render_template("register.html", form=form)


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
    form = PetForm()

    # Populate species choices dynamically
    form.species.choices = [(species.id, species.name) for species in Species.query.all()]
    
    # Populate breed choices dynamically based on selected species
    if form.species.data:
        form.breed.choices = [(breed.id, breed.name) for breed in Breed.query.filter_by(species_id=form.species.data).all()]
    
    # User reached route via POST
    if request.method == 'POST':
        if form.validate_on_submit():
            # Extract form data
            pet_name = form.name.data
            birth_date = form.birth_date.data
            adoption_date = form.adoption_date.data
            sex = form.sex.data
            species_id = form.species.data
            breed_id = form.breed.data
            sterilized = form.sterilized.data
            microchip_number = form.microchip_number.data
            insurance_company = form.insurance_company.data
            insurance_number = form.insurance_number.data

            # Handling the uploaded pet profile photo
            if form.pet_profile_photo.data:
                photo = form.pet_profile_photo.data
                filename = secure_filename(photo.filename)
                pet_profile_photo = filename
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                
            else:
                pet_profile_photo = None

            # Save pet data to the database
            new_pet = Pet(
                user_id=session["user_id"],
                pet_profile_photo=pet_profile_photo,
                name=pet_name,
                birth_date=birth_date,
                adoption_date=adoption_date,
                sex=sex,
                species_id=species_id,
                breed_id=breed_id,
                sterilized=sterilized,
                microchip_number=microchip_number,
                insurance_company=insurance_company,
                insurance_number=insurance_number
            )
            db.session.add(new_pet)
            db.session.commit()

            flash('Pet registered successfully!', 'success')
            return redirect("/")

        else:
            return error_message("An error occurred. Please try again.", form.errors)
        
    # User reached route via GET
    return render_template('new_pet.html', form=form)


@app.route('/get_breeds/<int:species_id>', methods=['GET'])
@login_required
def get_breeds(species_id):
    """Show breed list"""
    breeds = Breed.query.filter_by(species_id=species_id).all()
    breed_data = [{"id": breed.id, "name": breed.name} for breed in breeds]
    return jsonify(breed_data)

@app.route('/delete_pet/<int:pet_id>', methods=['GET'])
@login_required
def delete_pet(pet_id):
    """Delete a pet from db"""
    pet = Pet.query.get_or_404(pet_id)
    try:
        db.session.delete(pet)
        db.session.commit()
        flash('Pet deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting pet: {str(e)}', 'danger')
    return redirect('/')

@app.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    """Edit pet info"""
    pet = Pet.query.get_or_404(pet_id)
    form = PetForm(obj=pet)
    # Populate species choices dynamically
    form.species.choices = [(species.id, species.name) for species in Species.query.all()]

    if form.validate_on_submit():
        try:
            pet.name = form.name.data
            pet.birth_date = form.birth_date.data
            pet.adoption_date = form.adoption_date.data
            pet.sex = form.sex.data
            pet.species_id = form.species.data
            pet.breed_id = form.breed.data
            pet.sterilized = form.sterilized.data
            pet.microchip_number = form.microchip_number.data
            pet.insurance_company = form.insurance_company.data
            pet.insurance_number = form.insurance_number.data
            if form.pet_profile_photo.data:
                # Delete old photo if it exists
                if pet.pet_profile_photo:
                    old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], pet.profile_photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                # Save new photo
                filename = secure_filename(form.pet_profile_photo.data.filename)
                form.pet_profile_photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pet.pet_profile_photo = filename

            db.session.commit()
            flash('Pet information updated successfully!', 'success')
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating pet: {str(e)}")
            flash(f'Error updating pet: {str(e)}', 'danger')

    # User reached route via GET
    if request.method == 'GET':
        form.name.data = pet.name
        form.birth_date.data = pet.birth_date
        form.adoption_date.data = pet.adoption_date
        form.sex.data = pet.sex
        form.species.data = pet.species_id
        form.breed.data = pet.breed_id
        form.sterilized.data = pet.sterilized
        form.microchip_number.data = pet.microchip_number
        form.insurance_company.data = pet.insurance_company
        form.insurance_number.data = pet.insurance_number
    return render_template('edit_pet.html', form=form, pet=pet)

if __name__ == "__main__":
    app.run(debug=True)
