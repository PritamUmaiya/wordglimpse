from cs50 import SQL
from flask import Blueprint, current_app, request, session
import json
import re
from werkzeug.security import check_password_hash
from user.helpers import CATEGORIES, allowed_file, login_required


validate_bp = Blueprint('validate', __name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wg.db")


@validate_bp.route("/validate_image", methods=["POST"])
@login_required
def validate_image():
    """Validate image"""
    errors = []

    if 'image' not in request.files:
        errors.append({"image": "Please select an image!"})

    file = request.files['image']
    if file.filename == '':
        errors.append({"image": "Please select an image!"})

    elif not allowed_file(file.filename):
        errors.append({"image": "Please select images only!"})
    
    # Make sure file size does not exceed 16MB
    if file and file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
        errors.append({"image": "Please select an image less than 16MB!"})

    return json.dumps(errors)


@validate_bp.route("/validate_post", methods=["POST"])
@login_required
def validate_post():
    """Validate Post"""
    # Get form data
    title = request.form.get("post-title")
    category = request.form.get("post-category")
    content = request.form.get("post-content")

    # Validate form data
    errors = []

    errors += json.loads(validate_image())

    if not title:
        errors.append({"title": "Please enter a title!"})
    
    elif len(title) > 100 or len(title) < 5:
        errors.append({"title": "Title must be between 5 and 100 characters!"})
    
    if not category:
        errors.append({"category": "Please select a category!"})
    
    elif category not in CATEGORIES:
        errors.append({"category": "Please select a valid category!"})

    if not content:
        errors.append({"content": "Please enter your content!"})
    
    elif len(content) > 1000 or len(content) < 200:
        errors.append({"content": "Content must be between 200 and 1000 characters!"})

    return json.dumps(errors)


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


@validate_bp.route("/validate_username", methods=["GET", "POST"])  
@login_required
def validate_username():
    """Handle for both post and get"""
    if request.method == "POST":
        username = request.form.get("username")
        has_username = request.form.get("has_username")

    else:
        username = request.args.get("username")
        has_username = request.args.get("has_username")

    # If user had username but send empty then it should be deleted
    if (request.method == "GET") and has_username and (not username or username == ""):
        return json.dumps(['<small class="text-info">Delete username!</small>'])

    if not has_username and (not username or username == ""):
        return json.dumps(['<small class="text-danger">Please choose username!</small>'])
    
    # Make sure that username starts with alphabets only, can contain numbers, [- _] and case insensitive
    if not re.match("^[a-z][a-z0-9]*([.][a-z0-9]+)*$", username.lower()):
        return json.dumps(['<small class="text-danger">Invalid username!</small>'])

    elif len(username) < 2 :
        return json.dumps(['<small class="text-danger">Min 2 characters are required!</small>'])
    
    elif len(username) > 20:
        return json.dumps(['<small class="text-danger">Max 20 characters are allowed!</small>'])

    # Normalize the input username
    normalized_username = username.replace('.', '').lower()

    # Query the database for normalized usernames
    usernames = db.execute("""
        SELECT username 
        FROM users 
        WHERE REPLACE(username, '.', '') = ? AND id != ?
    """, normalized_username, session["user_id"])

    if len(usernames) != 0:
        return json.dumps(['<small class="text-danger">Username not available!</small>'])

    # Return empty list if success
    return json.dumps([])


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