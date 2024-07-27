from flask import redirect, render_template, redirect, session
from functools import wraps
import os
from PIL import Image

# Extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Catagories allowed to be posted
CATEGORIES = ['education', 'entertainment', 'news', 'stories', 'wellness', 'technology', 'finance', 'lifestyle', 'environment', 'sports']



def apology(message, code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", code=code, message=message), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


''' ---- Image Handling function ---- '''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def resize_and_compress(image_path, output_path, max_kb=100):
    """Resize and compress images before uploading"""
    # Open the image
    img = Image.open(image_path)

    # Resize the image while maintaining aspect ratio
    img.thumbnail((700, 700))

    # Initial quality setting
    quality = 85

    # Compress and save the image
    img.save(output_path, optimize=True, quality=quality)

    # Check if the file size is within the limit
    while os.path.getsize(output_path) > max_kb * 1024:  # Convert max_kb to bytes
        quality -= 5
        if quality < 10:  # Prevent quality from going too low
            break
        img.save(output_path, optimize=True, quality=quality)