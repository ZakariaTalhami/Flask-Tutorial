from flask import Blueprint, render_template, redirect, request, g, url_for, flash, abort
from .db import get_db
from .auth import login_required

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p join user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route("/create", methods=("POST", "GET"))
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_ID)'
                'VALUES (?, ?, ?)',
                (title, body, g.user["id"])
            )
            db.commit()

            return redirect(url_for("index"))

        flash(error)

    return render_template("blog/create.html")


@bp.route('/<int:post_id>/update', methods=("POST", "GET"))
@login_required
def update(post_id):
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title is required."
        elif not body:
            error = "Body is required."

        if error is None:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, post_id)
            )
            db.commit()

            return redirect(url_for('index'))

        flash(error)

    post = get_post(post_id)
    return render_template('blog/update.html', post=post)


@bp.route("/<int:post_id>/delete", methods=("POST",))
@login_required
def delete(post_id):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    db.commit()

    return redirect(url_for('index'))


def get_post(post_id , check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p join user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    if not post:
        # Abort will raise a Exception resulting in an HTTP
        # status code being returned
        abort(404, f"Post id {post_id} doesnt exists.")

    if check_author and post['author_id'] != g.user['id']:
        # Abort will raise a Exception resulting in an HTTP
        # status code being returned
        abort(403)

    return post
