from cs50 import SQL
from flask import Blueprint, request
import json
import re
from werkzeug.security import check_password_hash


validate_bp = Blueprint('validate', __name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wg.db")


@validate_bp.route("/validate_name", methods=["POST"])
def validate_name():
    fname = request.form.get("fname")
    lname = request.form.get("lname")

    # List of errors
    errors = []

    # Validate Fname
    if not fname or fname == "":
        errors.append({"fname": "Required!"})

    elif len(fname) < 2:
        errors.append({"fname": "Min 2 characters required!"})
    
    elif len(fname) > 20:
        errors.append({"fname": "Max 20 characters are allowed!"})
    
    if len(errors) > 0:
        # Return as JSON object
        return json.dumps(errors)
    
    elif not fname.isalpha():
        errors.append({"fname": "Name musht be aphabets only!"})

    # Validate Lname if provided
    if lname:
        if len(lname) < 2:
            errors.append({"lname": "Min 2 characters required!"})

        elif len(lname) > 20:
            errors.append({"lname": "Max 20 characters are allowed!"})

        elif not fname.isalpha():
            errors.append({"fname": "Name musht be aphabets only!"})

    # Return as JSON object
    return json.dumps(errors)


@validate_bp.route("/validate_signup", methods=["POST"])
def validate_signup():
    """Validate users data before signup"""
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # List of errors
    errors = []

    # Validate Name
    errors += json.loads(validate_name())
    # Validate email
    if not email:
        errors.append({"email": "Please enter your email!"})
        
    elif not re.search(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        errors.append({"email": "Invalid email format!"})

    # Check if email already exists
    users = db.execute("SELECT id, email FROM users WHERE email = ?", email)
    
    if not len(users) == 0:
        errors.append({"email": "Email already exists!"})
    
    # Validate password
    if not password:
        errors.append({"password": "Enter your password!"})
    
    elif len(password) < 5 or len(password) > 30:
        errors.append({"password": "Password must have 5 to 30 characters!"})

    # Validate confirmation
    if not confirmation:
        errors.append({"confirmation": "Confirm your password!"})

    elif confirmation != password:
        errors.append({"confirmation": "Password did not matched!"})

    # Return as JSON object
    return json.dumps(errors)


@validate_bp.route("/validate_login", methods=["POST"])
def validate_login():
    """Validate users data befor login"""
    email = request.form.get('email')
    password = request.form.get('password')

    # Errors list
    errors = []

    # Ensure proper use
    if not email:
        errors.append({"email": "Please enter your email"})

    if not password:
        errors.append({"password": "Please enter your password"})
    
    # Send errors for input first
    if len(errors) != 0:
        return json.dumps(errors)
    
    # Query database for username
    users = db.execute("SELECT id, password FROM users WHERE email = ?", email)

    # Ensure username exists and password is correct
    if len(users) != 1 or not check_password_hash(users[0]["password"], password):
        errors.append({"auth": "Invalid email and/or password"})

    # Return as JSON object
    return json.dumps(errors)