import re
from cs50 import SQL
from flask import Blueprint, current_app, request, flash, redirect, render_template, session, jsonify
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

        # Get the author details of the post
        author = db.execute("SELECT * FROM users WHERE id = ?", post["user_id"])[0]

        # Get total upvotes and downvotes
        upvotes = db.execute("SELECT COUNT(*) AS total FROM voted_posts WHERE post_id = ? AND vote = ?", post_id, 1)[0]['total']
        downvotes = db.execute("SELECT COUNT(*) AS total FROM voted_posts WHERE post_id = ? AND vote = ?", post_id, -1)[0]['total']


        # If user has logged in check if he has saved the post and voted on the post
        saved = False
        voted = False
        if session.get("user_id"):
            saves = db.execute("SELECT * FROM saved_posts WHERE post_id = ? AND user_id = ?", post_id, session["user_id"])
            if len(saves) > 0:
                saved = True
            votes = db.execute("SELECT vote FROM voted_posts WHERE post_id = ? AND user_id = ?", post_id, session["user_id"])
            if len(votes) > 0:
                voted = votes[0]['vote'] # Get the vote 1 for upvote -1 for downvote

        # Get the comments of the post
        comments = db.execute("SELECT commented_posts.*, users.fname, users.avatar FROM commented_posts JOIN users ON commented_posts.user_id = users.id WHERE commented_posts.post_id = ?", post_id)
        
        return [post, author, upvotes, downvotes, saved, voted, comments]

    else:
        """Post with basic details"""
        post = db.execute("SELECT * FROM posts WHERE id = ?", post_id)[0]

        # Get the author details of the post
        author = db.execute("SELECT * FROM users WHERE id = ?", post["user_id"])[0]

        return [post, author]


# TODO: Add a function to get posts by user ID
def get_posts_by_user_id(user_id, detailed=False, sord_by='relevence', order_by='DESC', limit=10, offset=0):
    """Get posts by user ID"""
    ...


# TODO: Add a function to get posts by category
def get_post_by_category(category, detailed=False, sord_by='relevence', order_by='DESC', limit=10, offset=0):
    """Get posts by category"""
    ...


''''--- Post Routes ---'''
@post_bp.route("/post/<int:post_id>")
def post(post_id):
    """Post Page"""
    # Check if the post exists
    if not db.execute("SELECT id FROM posts WHERE id = ?", post_id):
        return apology("Post not found", 404)

    post, author, upvotes, downvotes, saved, voted, comments  = get_post_by_id(post_id, detailed=True)

    return render_template("post.html", post=post, author=author, upvotes=upvotes, downvotes=downvotes, saved=saved, voted=voted, comments=comments)


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


@post_bp.route("/save_post", methods=["POST"])
@login_required
def save_post():
    data = request.get_json()
    post_id = data.get('post_id')

    if not post_id:
        return jsonify({'message': 'Post ID not found!'})
    
    # Check if post exists
    posts = db.execute("SELECT id FROM posts WHERE id = ?", post_id)
    if len(posts) == 0:
        return jsonify({'message': 'Post not found!'})

    # Check if user already saved the post
    saved_posts = db.execute("SELECT id FROM saved_posts WHERE user_id = ? AND post_id = ?", session["user_id"], post_id)

    if len(saved_posts) > 0:
        db.execute("DELETE FROM saved_posts WHERE user_id = ? AND post_id = ?", session["user_id"], post_id)
        return jsonify({'message': 'unsaved'})

    # Save the post
    db.execute("INSERT INTO saved_posts (user_id, post_id) VALUES (?, ?)", session["user_id"], post_id)

    # Return a response
    return jsonify({'message': 'saved'})


@post_bp.route("/vote_post", methods=["POST"])
@login_required
def vote_post():
    data = request.get_json()
    post_id = data.get('post_id')

    if not post_id:
        return jsonify({'message': 'Post ID not found!'})

    # Check if post exists
    posts = db.execute("SELECT id FROM posts WHERE id = ?", post_id)
    if len(posts) == 0:
        return jsonify({'message': 'Post not found!'})
    
    # Check if user already voted on the post
    voted_posts = db.execute("SELECT vote FROM voted_posts WHERE user_id = ? AND post_id = ?", session["user_id"], post_id)

    if len(voted_posts) > 0:
        # Get the vote
        vote = voted_posts[0]['vote'] # 1 for upvote -1 for downvote

        # if vote matches remove the post
        if vote == data.get('vote'):
            # Remove the vote
            db.execute("DELETE FROM voted_posts WHERE user_id = ? AND post_id = ?", session["user_id"], post_id)

            # Return a response
            if vote == 1:
                return jsonify({'message': 'unvoted', 'upvote': -1})
            else:
                return jsonify({'message': 'unvoted', 'upvote': 0})
        
        else:
            # Update the vote
            db.execute("UPDATE voted_posts SET vote = ? WHERE user_id = ? AND post_id = ?", data.get('vote'), session["user_id"], post_id)

            # Return a response
            if data.get('vote') == 1:
                return jsonify({'message': 'upvoted', 'upvote': 1})
            else:
                return jsonify({'message': 'downvoted', 'upvote': -1})

    # Add the vote
    db.execute("INSERT INTO voted_posts (user_id, post_id, vote) VALUES (?, ?, ?)", session["user_id"], post_id, data.get('vote'))

    # Return a response
    if data.get('vote') == 1:
        return jsonify({'message': 'upvoted', 'upvote': 1})
    else:
        return jsonify({'message': 'downvoted', 'upvote': 0})

    
