
import click
import psycopg2 as pg2

from flask import current_app, g
from flask.cli import with_appcontext
from psycopg2.extras import DictCursor


def get_db():
    if 'db' not in g:
        g.db = pg2.connect(
            **current_app.config['DATABASE'],
        )
        g.db.cursor_factory = DictCursor

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    db.autocommit = True
    cur = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read().decode('utf8'))
    cur.close()
    db.autocommit = False


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
