from functools import wraps
import re
from flask import redirect, session, render_template
import dns.resolver


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/welcome")
        return f(*args, **kwargs)

    return decorated_function


def error_message(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", top=code, bottom=escape(message)), code


def is_valid_email(email):
    """Validate email format with regex"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False

    # Extraer el dominio después del "@"
    domain = email.split('@')[1]

    # Validar que el dominio tenga registros DNS MX
    return has_valid_dns(domain)

def has_valid_dns(domain):
    """Validate email domain"""
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

