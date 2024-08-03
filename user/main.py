from cs50 import SQL
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, session
import json
from werkzeug.security import generate_password_hash

from user.actions import action_bp
from user.helpers import apology, login_required
from user.post_handler import post_bp
from user.validate import validate_bp, validate_signup, validate_login

# Create a Blueprint
main_bp = Blueprint('main', __name__)

# Register the Blueprints with the main Blueprint
main_bp.register_blueprint(validate_bp)
main_bp.register_blueprint(post_bp)
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
def send_profile_data(profile_id):
    """Send profile data to the template"""
    profiles = db.execute("SELECT * FROM users WHERE id = ?",  profile_id)

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


@main_bp.route('/@<username>')
def username_profile(username):
    # Check if username exists
    profiles = db.execute("SELECT * FROM users WHERE username = ?", username)

    if len(profiles) == 0:
        return apology("The user your are looking for was not found!", 404)

    profile_id = profiles[0]["id"]

    # Send profile data to the template
    return send_profile_data(profile_id)


@main_bp.route("/profile/<int:profile_id>")
def id_profile(profile_id):
    # Check if user_id is provided
    if not profile_id or profile_id == "":
        # If user has logged in then show him their profile
        if session.get("user_id") is not None:
            return redirect("/profile/" + str(session["user_id"]))
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

    # Send profile data to the template
    return send_profile_data(profile_id)


@main_bp.route("/profile")
def profile():
    # Check if user_id is provided
    if not session.get("user_id") or session.get("user_id") == "":
        # If user has logged in then show him their profile
        return redirect("/login")
    else:
        return redirect("/profile/" + str(session["user_id"]))


@main_bp.route("/profile/edit")
@login_required
def edit_profile():
    return render_template("edit_profile.html")


@main_bp.route("/posts/manage")
@login_required
def manage_posts():
    # Get the page number
    page = int(request.args.get('page', 1))
    offset = (int(page) - 1) * 10

    posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC LIMIT 10 OFFSET ?", session["user_id"], offset)
    total_posts = db.execute("SELECT COUNT(id) AS total FROM posts WHERE user_id = ?", session["user_id"])
    total_pages = (total_posts[0]["total"] + 9) // 10  # Calculate total number of pages

    return render_template("manage_posts.html", posts=posts, page=page, total_pages=total_pages)


@main_bp.route("/account")
@login_required
def account():
    return render_template("account.html")


@main_bp.route("/followings")
@login_required
def followings():
    """Profiles that user Follow"""
    # Get all the followings
    page = int(request.args.get("page", 1))
    offset = (page - 1) * 30
    followings_ids = db.execute("SELECT profile_id FROM followings WHERE user_id = ? ORDER BY id DESC LIMIT 30 OFFSET ?", session["user_id"], offset)
    followings_id = [row["profile_id"] for row in followings_ids]
    
    followings = []
    if len(followings_id) > 0:
        # Get all the followings
        followings = db.execute("SELECT * FROM users WHERE id IN (?)", followings_id)
    
    total_followings = len(followings)
    total_pages = (total_followings + 29) // 30  # Calculate total number of pages

    return render_template("followings.html", total_followings=total_followings, followings=followings, page=page, total_pages=total_pages)


@main_bp.route("/followers")
@login_required
def followers():
    """Profiles that follow user"""
    # Get all the followers
    page = int(request.args.get("page", 1))
    offset = (page - 1) * 30
    followers_ids = db.execute("SELECT user_id FROM followings WHERE profile_id = ? ORDER BY id DESC LIMIT 30 OFFSET ?", session["user_id"], offset)
    followers_id = [row["user_id"] for row in followers_ids]
    
    followers = []
    if len(followers_id) > 0:
        # Get all the followers
        followers = db.execute("SELECT * FROM users WHERE id IN (?)", followers_id)
    
    total_followers = len(followers)
    total_pages = (total_followers + 29) // 30  # Calculate total number of pages

    return render_template("followers.html", total_followers=total_followers, followers=followers, page=page, total_pages=total_pages)



@main_bp.route("/messages")
@login_required
def messages():
    """Get the messages"""
    page = int(request.args.get("page", 1))
    offset = (page - 1) * 10

    message_sender_ids = db.execute(
        "SELECT DISTINCT sender_id FROM messages WHERE receiver_id = ? ORDER BY id DESC LIMIT 10 OFFSET ?",
        session["user_id"], offset
    )

    messages_id = [row["sender_id"] for row in message_sender_ids]

    messages = []
    if len(messages_id) > 0:
        # Get messages (sender_id), users (id, fname, avatar), last message, and unread message count
        messages = db.execute(
            """
            SELECT 
                m.sender_id, 
                u.fname, 
                u.avatar, 
                COUNT(CASE WHEN m.seen = 0 THEN 1 END) AS unread_messages,
                lm.message AS last_message
            FROM 
                messages m
            JOIN 
                users u ON m.sender_id = u.id
            JOIN 
                (SELECT sender_id, MAX(id) as last_message_id 
                 FROM messages 
                 WHERE receiver_id = ? 
                 GROUP BY sender_id) lm_ids 
                ON m.sender_id = lm_ids.sender_id 
            JOIN 
                messages lm ON lm.id = lm_ids.last_message_id
            WHERE 
                m.receiver_id = ? AND m.sender_id IN ({})
            GROUP BY 
                m.sender_id, u.fname, u.avatar, lm.message
            ORDER BY 
                lm_ids.last_message_id DESC
            """.format(','.join('?' * len(messages_id))),
            session["user_id"], session["user_id"], *messages_id
        )

    for message_id in messages_id:
        messages = db.execute("SELECT COUNT(id) AS total FROM messages WHERE sender_id = ? AND receiver_id = ?", message_id)

    total_messages = db.execute(
        "SELECT COUNT(DISTINCT sender_id) AS total FROM messages WHERE receiver_id = ?",
        session["user_id"]
    )[0]["total"]

    total_pages = (total_messages + 9) // 10

    return render_template(
        "messages.html",
        messages=messages,
        page=page,
        total_pages=total_pages
    )

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