from cs50 import SQL
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, session
import json
from werkzeug.security import generate_password_hash

from user.actions import action_bp
from user.helpers import apology, login_required
from user.validate import validate_bp, validate_signup, validate_login

# Create a Blueprint
main_bp = Blueprint('main', __name__)

# Register the Blueprints with the main Blueprint
main_bp.register_blueprint(validate_bp)
main_bp.register_blueprint(action_bp)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wg.db")


''' ---- Index page routes ---- '''
@main_bp.route("/")
@main_bp.route("/home")
def index():
    return render_template("layout.html")


@main_bp.route("/following")
@login_required
def following():
    return render_template("layout.html")


@main_bp.route("/saved")
@login_required
def saved():
    return render_template("layout.html")


''' --- Pages from account menu --- '''

"""User profile page"""
@main_bp.route('/@<username>')
def username_profile(username):
    # Check if username exists
    profiles = db.execute("SELECT * FROM users WHERE username = ?", username)

    if len(profiles) == 0:
        return apology("The user your are looking for was not found!", 404)

    profile_id = profiles[0]["id"]

    # Total number of followers
    followers = db.execute("SELECT COUNT(id) AS total FROM followings WHERE profile_id = ?", profile_id)

    # Total nubmer of posts
    posts = db.execute("SELECT COUNT (id) AS total FROM posts WHERE user_id = ?", profile_id)

    # User is logged in and follows this profile
    following = False

    if session.get("user_id") is not None:
        rows = db.execute("SELECT id FROM followings WHERE user_id = ? AND profile_id = ?", session["user_id"], profile_id)
        if len(rows) > 0:
            following = True
    
    return render_template("profile.html", profile=profiles[0], total_followers=followers[0]["total"], following=following, total_posts=posts[0]["total"])


@main_bp.route("/profile")
def profile():
    profile_id = request.args.get("id")

    if not profile_id or profile_id == "":
        # If user has logged in then show him their profile
        if session.get("user_id") is not None:
            return redirect("/profile?id=" + str(session["user_id"]))
        else:
            return redirect("/login")
    
    # Check if user_id exists
    profiles = db.execute("SELECT * FROM users WHERE id = ?",  profile_id)

    if len(profiles) == 0:
        return apology("The user your are looking for was not found!", 404)

    # If profile has an username redirect to their username
    if profiles[0]["username"] != None:
        username_link = "/@" + profiles[0]["username"]
        return redirect(username_link)

    # Total number of followers
    followers = db.execute("SELECT COUNT(id) AS total FROM followings WHERE profile_id = ?", profile_id)

    # Total nubmer of posts
    posts = db.execute("SELECT COUNT (id) AS total FROM posts WHERE user_id = ?", profile_id)

    # User is logged in and follows this profile
    following = False

    if session.get("user_id") is not None:
        rows = db.execute("SELECT id FROM followings WHERE user_id = ? AND profile_id = ?", session["user_id"], profile_id)
        if len(rows) > 0:
            following = True
    
    return render_template("profile.html", profile=profiles[0], total_followers=followers[0]["total"], following=following, total_posts=posts[0]["total"])


@main_bp.route("/profile/edit")
@login_required
def edit_profile():
    return render_template("edit_profile.html")


@main_bp.route("/account")
@login_required
def account():
    return render_template("account.html")


""" --- User Authentication routes --- """

@main_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Ensure user had successfully validated data
        if len(json.loads(validate_signup())) != 0:
            return apology("Could not process your request!")

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the password
        password = generate_password_hash(password)

        # Get the current date to save as last active
        last_active = datetime.now()

        # Capitalize names
        fname = fname.capitalize()
        if lname:
            lname = lname.capitalize()

        # Set lname to null if not provided
        if not lname or lname == '':
            # Add user to user db
            db.execute("INSERT INTO users (fname, email, password, last_active) VALUES (?, ?, ?, ?)", fname, email, password, last_active)
        else:
            # Add user to user db
            db.execute("INSERT INTO users (fname, lname, email, password, last_active) VALUES (?, ?, ?, ?, ?)", fname, lname, email, password, last_active)

        # Get id of the user
        users = db.execute("SELECT id FROM users WHERE email = ?", email)

        # Forget any previews user_id
        session.clear()

        # Add the session for user
        session["user_id"] = users[0]["id"]
        
        # Greet user for the first time
        flash("Welcome " + fname + "!", "success")
        return redirect("/")

    else:
        return render_template("signup.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Validate user
        if len(json.loads(validate_login())) != 0:
            return apology("Could not process your request!")
    
        # Get user id
        users = db.execute("SELECT id FROM users WHERE email = ?", request.form.get('email'))

        last_active = datetime.now()

        # Update last login date
        db.execute("UPDATE users SET last_active = ? WHERE id = ?", last_active, users[0]["id"])

        # Forget any previews user_id
        session.clear()

        # Remember which user has logged in
        session["user_id"] = users[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")


@main_bp.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")