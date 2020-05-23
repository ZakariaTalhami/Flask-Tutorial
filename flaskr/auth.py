from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from .db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import functools

bp = Blueprint("auth", __name__ , url_prefix="/auth")


# calls to route "/auth/register" will call the register function
@bp.route("/register", methods=("GET", "POST"))
def register():  # view functions/endpoint
    if request.method == "POST":

        # "request.form" is a dict mapping of the
        # key, value submitted in the post request
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        # validate the form
        if not username:
            error = "Username is required"
        elif not password:
            error = 'Password is required'
        elif db.execute(
            'SELECT id FROM user where username = ?', (username, )
        ).fetchone() is not None:
            error = f"{username} already exists"

        if not error:
            db.execute(
                'INSERT INTO user (username, password) values (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # "url_for" generate the url based on the view name/endpoint,
            # allows the url to change without affecting the redirect.
            return redirect(url_for("auth.login"))

        # stores the message to be used while rendering the template
        flash(error)

    return render_template('auth/register.html')


@bp.route("/login", methods=("GET", "POST"))
def login():  # view functions/endpoint
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username  = ? ', (username, )
        ).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect login Credentials."

        if error is None:
            # sessions is a dict that store data across requests.
            # sessions are set to the browser and stored as cookies,
            # and sent with subsequent requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template("auth/login.html")


# defaults to "GET" method
@bp.route("/logout")
def logout():
    session.clear()
    redirect(url_for("index"))


# Runs the function before the view functions
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if not user_id:
        g.user = None
    else:
        # fetches the user information, making it available for the views.
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id  = ? ', (user_id, )
        ).fetchone()


def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view
