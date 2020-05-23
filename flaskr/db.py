import sqlite3

import click

# g contains information used for the current request,
# so instances can be used with multiple functions
from flask import current_app, g
from flask.cli import with_appcontext


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init_db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


# Create a DB connection for the request
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
                # get the DB file path from app configuration
                current_app.config["DATABASE"],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row
    return g.db


# Close the DB connection before ending the request
def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    # add a teardown callback when cleaning up from request
    app.teardown_appcontext(close_db)
    # Adds a command that can be invoked by flask
    app.cli.add_command(init_db_command)
