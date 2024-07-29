from cs50 import SQL
from datetime import datetime, timedelta
from flask import Flask, redirect, send_from_directory, session, request
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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///wg.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Register the Blueprint
app.register_blueprint(main_bp)

# Jinja template filters
@app.template_filter('format_date')
def format_date(d):
    """Format datetime as string."""
    d = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
    return d.strftime('%d %B %Y')

@app.template_filter('short_number')
def short_number_format(value):
    """Format a number with a short representation (e.g., 1.2k for 1200)."""
    if value >= 1_000_000:
        formatted_value = f'{value / 1_000_000:.1f}M'
    elif value >= 1_000:
        formatted_value = f'{value / 1_000:.1f}k'
    else:
        return str(value)

    # Remove the trailing '.0' if present
    if formatted_value.endswith('.0k'):
        formatted_value = formatted_value[:-3] + 'k'
    elif formatted_value.endswith('.0M'):
        formatted_value = formatted_value[:-3] + 'M'

    return formatted_value


@app.context_processor
def inject_user():
    """Inject categories into the template context"""
    if session.get("user_id") is None:
            return dict(categories=CATEGORIES)

    users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    if len(users) == 0:
        """If user is not found, logout"""
        session.clear()
        return redirect("/")

    return dict(categories=CATEGORIES, user=users[0])


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