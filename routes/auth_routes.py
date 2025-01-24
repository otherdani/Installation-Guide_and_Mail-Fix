import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
from flask_mail import Message

from models import User
from forms import LoginForm, RegisterForm, ResetPasswordForm, RestorePasswordForm
from helpers import error_message, login_required


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
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

@auth_bp.route('/logout')
def logout():
    """Log user out"""
    # Forget any user id
    session.clear()

    # Redirect user to welcome page
    return redirect("/")

@auth_bp.route("/register", methods=["GET", "POST"])
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
            s = Serializer(current_app.secret_key)
            token = s.dumps(email, salt='email-confirm')

            # Create the confirmation URL
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('email_confirmation.html', confirm_url=confirm_url)
            subject = "Confirm your email"

            logging.basicConfig(level=logging.DEBUG)
            mail = current_app.extensions['mail']

            # Send the confirmation email
            msg = Message(subject, sender=os.getenv("PETPAL_EMAIL"), recipients=[email])
            msg.html = html
            mail.send(msg)

            flash("A confirmation email has been sent. Please check your inbox and your spam folder.", "info")
            return redirect("/")

        except (KeyError, ValueError) as e:
            current_app.logger.error("Error during email sending or token generation: %s", e)
            session.clear()  # Clean up session on failure
            return error_message("An error occurred. Please try again.", 500)

    # User reached route via GET
    return render_template("register.html", form=form)


@auth_bp.route("/confirm/<token>")
def confirm_email(token):
    """Validate email"""
    db = current_app.extensions['sqlalchemy']
    try:
        # Deserialize token
        s = Serializer(current_app.secret_key)
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except (BadSignature, SignatureExpired) as e:
        current_app.logger.error("Token error: %s", e)
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

@auth_bp.route("/restore_password", methods=["GET", "POST"])
def restore_password():
    """Request password reset"""
    form = RestorePasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if not user:
            return error_message("This email is not registered.", 404)

        # Generate reset token
        s = Serializer(current_app.secret_key)
        token = s.dumps(email, salt='password-reset')

        # Create the reset URL
        reset_url = url_for('reset_password', token=token, _external=True)
        html = render_template('password_reset_email.html', reset_url=reset_url)
        subject = "Password Reset Request"

        try:
            # Send the password reset email
            mail = current_app.extensions['mail']
            msg = Message(subject, sender=os.getenv("PETPAL_EMAIL"), recipients=[email])
            msg.html = html
            mail.send(msg)

            flash("A password reset link has been sent to your email address. Please check your inbox.", "info")
            return redirect("/")

        except Exception as e:
            current_app.logger.error("Error sending password reset email: %s", e)
            return error_message("An error occurred while sending the email. Please try again.", 500)

    return render_template("restore_password.html", form=form)

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset password using token"""
    db = current_app.extensions['sqlalchemy']
    try:
        # Deserialize token
        s = Serializer(current_app.secret_key)
        email = s.loads(token, salt='password-reset', max_age=3600)
    except (BadSignature, SignatureExpired) as e:
        current_app.logger.error("Token error: %s", e)
        flash("The reset link is invalid or has expired. Please request a new link.", "danger")
        return redirect("/restore_password")

    # Handle password reset
    form = ResetPasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        new_password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No user found with this email.", "danger")
            return redirect("/restore_password")

        # Update password hash
        user.pw_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Your password has been reset successfully!", "success")
        return redirect("/login")

    return render_template("reset_password.html", form=form)
