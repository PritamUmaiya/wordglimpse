from datetime import timedelta
from flask import Flask, send_from_directory
from flask_session import Session

from user.main import main_bp
from user.helpers import apology, CATEGORIES

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=3)  # Set session lifetime to 3 day
Session(app)

# Configure image upload
app.config['UPLOAD_AVATAR_FOLDER'] = 'uploads/avatar'
app.config['UPLOAD_COVER_FOLDER'] = 'uploads/cover'
app.config['UPLOAD_POST_FOLDER'] = 'uploads/post'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Register the Blueprint
app.register_blueprint(main_bp)


@app.context_processor
def inject_categories():
    """Inject categories into the template context"""
    return dict(categories=CATEGORIES)


"""Send users directory"""
@app.route('/uploads/avatar/<filename>')
def uploaded_avatar(filename):
    return send_from_directory(app.config['UPLOAD_AVATAR_FOLDER'], filename)

@app.route('/uploads/cover/<filename>')
def uploaded_cover(filename):
    return send_from_directory(app.config['UPLOAD_COVER_FOLDER'], filename)

@app.route('/uploads/post/<filename>')
def uploaded_post(filename):
    return send_from_directory(app.config['UPLOAD_POST_FOLDER'], filename)


''' ---- Error Handlers ---- '''

@app.errorhandler(404)
def page_not_found(e):
    """Handle Not Found Error"""
    return apology('Page not found!', 404)


@app.errorhandler(500)
def internale_server_error(e):
    """Internale Server Error"""
    return apology('Internal Server Error!', 500)


if __name__ == '__main__':
    app.run(debug=True)