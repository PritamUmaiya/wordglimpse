from cs50 import SQL
from flask import Blueprint, current_app, request, flash, redirect, render_template, session
import json
import os
from werkzeug.utils import secure_filename

from user.helpers import apology, login_required, resize_and_compress
from user.validate import validate_post


post_bp = Blueprint('post_handler', __name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wg.db")


'''--- Post helpers functions ---'''

def get_post_by_id(post_id, detailed=False):
    """Get post by ID"""
    if detailed:
        """Post with full details"""
        post = db.execute("SELECT * FROM posts WHERE id = ?", post_id)[0]

        # Check if post exists
        if not post:
            return apology("Post not found", 404)

        # Get the author details of the post
        author = db.execute("SELECT * FROM users WHERE id = ?", post["user_id"])[0]

        # Get total upvotes and downvotes
        upvotes = db.execute("SELECT COUNT(*) AS total FROM voted_posts WHERE post_id = ? AND vote = ?", post_id, 1)[0]['total']
        downvotes = db.execute("SELECT COUNT(*) AS total FROM voted_posts WHERE post_id = ? AND vote = ?", post_id, -1)[0]['total']

        # If user has logged in check if he has voted on the post
        voted = False
        if session.get("user_id"):
            votes = db.execute("SELECT vote FROM voted_posts WHERE post_id = ? AND user_id = ?", post_id, session["user_id"])
            if len(votes) > 0:
                voted = votes['vote'] # Get the vote 1 for upvote -1 for downvote

        # Get the comments of the post
        comments = db.execute("SELECT commented_posts.*, users.fname, users.avatar FROM commented_posts JOIN users ON commented_posts.user_id = users.id WHERE commented_posts.post_id = ?", post_id)
        
        return [post, author, upvotes, downvotes, voted, comments]

    else:
        """Post with basic details"""
        post = db.execute("SELECT * FROM posts WHERE id = ?", post_id)[0]

        # Get the author details of the post
        author = db.execute("SELECT * FROM users WHERE id = ?", post["user_id"])[0]

        return [post, author]


def get_posts_by_user_id(user_id, detailed=False, order_by='DESC', limit=10, offset=0):
    """Get posts by user ID"""
    rows = db.execute("SELECT id FROM posts WHERE user_id = ? ORDER BY id ? LIMIT ? OFFSET ?", user_id, order_by, limit, offset)

    post_ids = [id for id in rows]

    posts = [get_post_by_id(id, detailed) for id in post_ids]

    return posts


def get_post_by_category(category, detailed=False, order_by='DESC', limit=10, offset=0):
    """Get posts by category"""
    rows = db.execute("SELECT id FROM posts WHERE category = ? ORDER BY id ? LIMIT ? OFFSET ?", category, order_by, limit, offset)

    post_ids = [id for id in rows]

    posts = [get_post_by_id(id, detailed) for id in post_ids]

    return posts



''''--- Post Routes ---'''
@post_bp.route("/post/<int:post_id>")
def post(post_id):
    """Post Page"""
    post, author, upvotes, downvotes, voted, comments  = get_post_by_id(post_id, detailed=True)

    return render_template("post.html", post=post, author=author, upvotes=upvotes, downvotes=downvotes, voted=voted, comments=comments)


''' --- Post Actions --- '''

@post_bp.route("/create_post", methods=["POST"])
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

