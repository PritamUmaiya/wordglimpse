from cs50 import SQL
from flask import Blueprint, current_app, request, flash, redirect, session, jsonify
import json
import os
import re
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

from user.helpers import apology, login_required, resize_and_compress
from user.validate import validate_name, validate_username, validate_image, validate_post

action_bp = Blueprint('updates', __name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wg.db")


@action_bp.route("/create_post", methods=["POST"])
@login_required
def create_post():
    """Create Post"""
    # Get form data
    file = request.files['post-image']
    title = request.form.get("post-title")
    category = request.form.get("post-category")
    content = request.form.get("post-content")

    # Validate form data
    if len(json.loads(validate_post())) > 0:
        flash("Could not create post, please check the errors", "danger")
        return redirect(request.referrer)

    # Insert the post first to get its ID
    db.execute("INSERT INTO posts (user_id, image, title, category, content) VALUES (?, ?, ?, ?, ?)", session["user_id"], "", title, category, content)

    # Get the ID of the last inserted post
    last_id = db.execute("SELECT last_insert_rowid()")[0]['last_insert_rowid()']
    post_id = last_id

    # Save the file with the ID as its name
    filename = secure_filename(str(post_id) + os.path.splitext(file.filename)[1])
    file_path = os.path.join(current_app.config['UPLOAD_POST_FOLDER'], filename)
    file.save(file_path)

    # Resize and compress the image
    output_path = os.path.join(current_app.config['UPLOAD_POST_FOLDER'], filename)
    resize_and_compress(file_path, output_path, max_kb=100)  # Example: compress to max 100 KB

    # If user had images with other extensions then delete them
    for junk_filename in [str(post_id) + ext for ext in [".png", ".jpg", ".jpeg"]]:
        junk_file = os.path.join(current_app.config['UPLOAD_POST_FOLDER'], junk_filename)
        if os.path.exists(junk_file) and junk_filename != filename:
            os.remove(junk_file)

    # Update the post with the correct image path
    db.execute("UPDATE posts SET image = ? WHERE id = ?", "/" + output_path, post_id)

    flash("Posted successfully", "success")
    return redirect(request.referrer)


''' ---- Profile page actions ---- '''

@action_bp.route("/follow_profile", methods=["POST"])
@login_required
def follow():
    data = request.get_json()
    profile_id = data.get('profile_id')

    if not profile_id:
        return jsonify({'message': 'User not found!'})
    
    # If user already follows the profile then unfollow it
    followings = db.execute("SELECT COUNT(id) AS count FROM followings WHERE user_id = ? AND profile_id = ?", session["user_id"], profile_id)
    
    if followings[0]['count'] > 0:
        db.execute("DELETE FROM followings WHERE user_id = ? AND profile_id = ?", session["user_id"], profile_id)
        return jsonify({'message': 'unfollowed'})
        
    else:
        # Follow the profile
        db.execute("INSERT INTO followings (user_id, profile_id) VALUES (?, ?)", session["user_id"], profile_id)
        return jsonify({'message': 'followed'})


''' --- Account Actions --- '''

@action_bp.route("/update_avatar", methods=["POST"])
@login_required
def update_avatar():
    """Upload user avatar"""
    errors = json.loads(validate_image())
    if len(errors) > 0:
        flash(errors[0]['image'], "danger")
        return redirect(request.referrer)

    file = request.files['image']

    filename = secure_filename(str(session["user_id"]) + os.path.splitext(file.filename)[1])
   
    file_path = os.path.join(current_app.config['UPLOAD_AVATAR_FOLDER'], filename)
    
    # Save the original file
    file.save(file_path)

    # Resize and compress the image
    output_path = os.path.join(current_app.config['UPLOAD_AVATAR_FOLDER'], filename)
    resize_and_compress(file_path, output_path, max_kb=100)  # Example: compress to max 100 KB

    # If user had images with other extension then delete it
    for junk_filename in [str(session["user_id"]) + ".png", str(session["user_id"]) + ".jpg", str(session["user_id"]) + ".jpeg"]:
        junk_file = os.path.join(current_app.config['UPLOAD_AVATAR_FOLDER'], junk_filename)
        if os.path.exists(junk_file) and junk_filename != filename:
            os.remove(junk_file)

    # Update user database
    db.execute("UPDATE users SET avatar = ? WHERE id = ?", "/" + output_path, session["user_id"])

    flash("Profile picture updated successfully!", "success")
    return redirect(request.referrer)


@action_bp.route('/delete_avatar', methods=["POST"])
@login_required
def delete_avatar():
    """Delete user avatar"""
    user_id = session["user_id"]
    
    # Fetch the user's current avatar filename from the database
    users = db.execute("SELECT avatar FROM users WHERE id = ?", (user_id,))
    user = users[0]
    
    if user and user["avatar"]:
        avatar_filename = user["avatar"]

        # Delete the avatar file if it exists
        if os.path.exists(avatar_filename[1:]):
            os.remove(avatar_filename[1:])
        
        # Update the user's record in the database
        db.execute("UPDATE users SET avatar = NULL WHERE id = ?", (user_id,))
        flash("Profile picture deleted successfully!", "success")
    else:
        flash("No profile picture to delete.", "danger")
    
    return redirect(request.referrer)


@action_bp.route("/update_cover", methods=["POST"])
@login_required
def update_cover():
    """Upload user cover"""
    errors = json.loads(validate_image())

    if len(errors) > 0:
        flash(errors[0]['image'], "danger")
        return redirect(request.referrer)

    file = request.files['image']
    
    filename = secure_filename(str(session["user_id"]) + os.path.splitext(file.filename)[1])
    file_path = os.path.join(current_app.config['UPLOAD_COVER_FOLDER'], filename)

    # Save the original file
    file.save(file_path)

    # Resize and compress the image
    output_path = os.path.join(current_app.config['UPLOAD_COVER_FOLDER'], filename)
    resize_and_compress(file_path, output_path, max_kb=100)  # Example: compress to max 100 KB

    # If user had images with other extension then delete it
    for junk_filename in [str(session["user_id"]) + ".png", str(session["user_id"]) + ".jpg", str(session["user_id"]) + ".jpeg"]:
        junk_file = os.path.join(current_app.config['UPLOAD_COVER_FOLDER'], junk_filename)
        if os.path.exists(junk_file) and junk_filename != filename:
            os.remove(junk_file)

    # Update user database
    db.execute("UPDATE users SET cover = ? WHERE id = ?", "/" + output_path, session["user_id"])

    flash("Cover photo updated successfully!", "success")
    return redirect(request.referrer)


@action_bp.route('/delete_cover', methods=["POST"])
@login_required
def delete_cover():
    user_id = session["user_id"]
    
    # Fetch the user's current avatar filename from the database
    users = db.execute("SELECT cover FROM users WHERE id = ?", (user_id,))
    user = users[0]
    
    if user and user["cover"]:
        cover_filename = user["cover"]

        # Delete the avatar file if it exists
        if os.path.exists(cover_filename[1:]):
            os.remove(cover_filename[1:])
        
        # Update the user's record in the database
        db.execute("UPDATE users SET cover = NULL WHERE id = ?", (user_id,))
        flash("Cover photo deleted successfully!", "success")
    else:
        flash("No cover photo to delete.", "danger")
    
    return redirect(request.referrer)


@action_bp.route("/update_profile_details", methods=["POST"])
@login_required
def update_profile_details():
    """Update user profile details"""
    profession = request.form.get('profession')
    bio = request.form.get('bio')
    facebook = request.form.get('facebook')
    github = request.form.get('github')
    linkedin = request.form.get('linkedin')
    instagram = request.form.get('instagram')
    twitter = request.form.get('twitter')
    public_email = request.form.get('public_email')
    website = request.form.get('website')

    # Validate and update profession
    # Delete profession if empty
    if not profession or profession == '':
        db.execute("UPDATE users SET profession = NULL WHERE id = ?", session["user_id"])
    elif len(profession) > 50:
        flash("Profession can not exceed 100 character!", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET profession = ? WHERE id = ?", profession, session["user_id"])
        
    # Validate and update bio
    # Delete bio if empty
    if not bio or bio == '':
        db.execute("UPDATE users SET bio = NULL WHERE id = ?", session["user_id"])
    elif len(bio) > 100:
        flash("Bio can not exceed 100 character!", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET bio = ? WHERE id = ?", bio, session["user_id"])
        
    # Validate and update facebook
    # Delete facebook if empty
    if not facebook or facebook == '':
        db.execute("UPDATE users SET facebook = NULL WHERE id = ?", session["user_id"])
    elif len(facebook) > 100:
        flash("Facebook link can not exceed 100 character", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET facebook = ? WHERE id = ?", facebook, session["user_id"])

    # Validate and update github
    # Delete github if empty
    if not github or github == '':
        db.execute("UPDATE users SET github = NULL WHERE id = ?", session["user_id"])
    elif len(github) > 100:
        flash("Github link can not exceed 100 character", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET github = ? WHERE id = ?", github, session["user_id"])

    # Validate and update linkedin
    # Delete linkedin if empty
    if not linkedin or linkedin == '':
        db.execute("UPDATE users SET linkedin = NULL WHERE id = ?", session["user_id"])
    elif len(linkedin) > 100:
        flash("Linkedin link can not exceed 100 character", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET linkedin = ? WHERE id = ?", linkedin, session["user_id"])

    # Validate and update instagram
    # Delete instagram if empty
    if not instagram or instagram == '':
        db.execute("UPDATE users SET instagram = NULL WHERE id = ?", session["user_id"])
    elif len(instagram) > 100:
        flash("Instagram link can not exceed 100 character", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET instagram = ? WHERE id = ?", instagram, session["user_id"])

    # Validate and update twitter
    # Delete twitter if empty
    if not twitter or twitter == '':
        db.execute("UPDATE users SET twitter = NULL WHERE id = ?", session["user_id"])
    elif len(twitter) > 100:
        flash("Twitter link can not exceed 100 character", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET twitter = ? WHERE id = ?", twitter, session["user_id"])
    
    # Validate and update public_email
    # Delete public_email if empty
    if not public_email or public_email == '':
        db.execute("UPDATE users SET public_email = NULL WHERE id = ?", session["user_id"])
    elif len(public_email) > 100:
        flash("Public email can not exceed 100 character", "danger")
        return redirect(request.referrer)
    elif not re.search("^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", public_email):
        flash("Inavlid email format!", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET public_email = ? WHERE id = ?", public_email, session["user_id"])

    # Validate and update website
    # Delete website if empty
    if not website or website == '':
        db.execute("UPDATE users SET website = NULL WHERE id = ?", session["user_id"])
    elif len(website) > 100:
        flash("Website link can not exceed 100 character", "danger")
        return redirect(request.referrer)
    else:
        db.execute("UPDATE users SET website = ? WHERE id = ?", website, session["user_id"])

    flash("Profile details updated successfully", "success")
    return redirect(request.referrer)



    ''' ---- Account Settings ----- '''


''' ----- Account Settings ----- '''

@action_bp.route("/update_name", methods=["POST"])
@login_required
def update_name():
    fname = request.form.get('fname')
    lname = request.form.get('lname')

    # Validate errors
    if (len(json.loads(validate_name())) != 0):
        return apology("Could not process your request!")
    
    # Capitalize names
    fname = fname.capitalize()
    if lname:
        lname = lname.capitalize()

    # Set lname to null if not provided
    if not lname or lname == '':
        # Add user to user db
        db.execute("UPDATE users SET fname = ?, lname = NULL WHERE id = ?", fname, session["user_id"])
    else:
        # Add user to user db
        db.execute("UPDATE users SET fname = ?, lname = ? WHERE id = ?", fname, lname, session["user_id"])

    flash("Name updated successfully!", "success")
    return redirect(request.referrer)


@action_bp.route("/update_username", methods=["POST"])
@login_required
def update_username():
    username = request.form.get("username")

    usernames = db.execute("SELECT username FROM users WHERE id = ? AND username IS NOT NULL", session["user_id"])
    
    # If no username and user already had a username then delete it
    if len(usernames) > 0 and (not username or username == ""):
        db.execute("UPDATE users SET username = NULL WHERE id = ?", session["user_id"])
        flash("Username deleted!", "info")
        return redirect(request.referrer)

    # Validate username
    error = json.loads(validate_username())
    if len(error) != 0:
        flash("Invalid response!", "info")
        return redirect(request.referrer)
   
    # Update username in the database
    db.execute("UPDATE users SET username = ? WHERE id = ?", username.lower(), session["user_id"])
    flash("Username updated!", "success")
    return redirect(request.referrer)


@action_bp.route("/update_email", methods=["POST"])
@login_required
def update_email():
    email = request.form.get('email')

    # Validate email
    if not email:
        flash("Please enter your email!", "danger")
        return redirect(request.referrer)

    elif not re.search("^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email):
        flash("Inavlid email format!", "danger")
        return redirect(request.referrer)

    # Check if email already exists
    users = db.execute("SELECT email FROM users WHERE email = ? AND id != ?", email, session["user_id"])
    
    if not len(users) == 0:
        flash("Email already exists!", "danger")
        return redirect(request.referrer)

    # Update users email
    db.execute("UPDATE users SET email = ? WHERE id = ?", email, session["user_id"])
    
    flash("Email updated successfully!", "success")
    return redirect(request.referrer)


@action_bp.route("/update_password", methods=["POST"])
@login_required
def update_password():
    password = request.form.get("password")
    new_password = request.form.get("new-password")
    confirm_password = request.form.get("confirm-password")

    if not password or not new_password or not confirm_password:
        flash("Please enter your passwords correctly!", "danger")
        return redirect(request.referrer)

    # Check if users has entered correct password
    users = db.execute("SELECT password FROM users WHERE id = ?", session["user_id"])

    if not check_password_hash(users[0]["password"], password):
        flash("Incorrect password!", "danger")
        return redirect(request.referrer)

    if len(new_password) < 5 or len(new_password) > 30:
        flash("Password must have 5 to 30 characters!", "danger")
        return redirect(request.referrer)

    elif confirm_password != new_password:
        flash("Password did not matched!", "danger")
        return redirect(request.referrer)

    # Update password
    db.execute("UPDATE users SET password = ? WHERE id = ?", generate_password_hash(new_password), session["user_id"])

    # Redirct to account page
    flash("Password updated successfully!", "success")
    return redirect(request.referrer)

    
""" -- DELETE USER ACCOUNT -- """

@action_bp.route("/delete_post_images", methods=["POST"])
@login_required
def delete_post_images():
    # Fetch all images of user
    images = db.execute("SELECT image FROM posts WHERE user_id = ?", session["user_id"])

    # Delete all images
    for image in images:
        if image["image"]:
            if os.path.exists(image["image"][1:]):
                os.remove(image["image"][1:])


@action_bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    password = request.form.get("password")
    if not password:
        flash("Please enter your password!", "danger")
        return redirect(request.referrer)
    
    # Check if users has entered correct password
    users = db.execute("SELECT password FROM users WHERE id = ?", session["user_id"])

    if not check_password_hash(users[0]["password"], password):
        flash("Incorrect password!", "danger")
        return redirect(request.referrer)

    # Delete all uploaded images of user
    delete_avatar()
    delete_cover()
    delete_post_images()

    # Delete user account
    db.execute("DELETE FROM users WHERE id = ?", session["user_id"])

    # Forgot user id and redirct to homepage
    session.clear()

    flash("Your account was deleted!", "info")
    return redirect("/")