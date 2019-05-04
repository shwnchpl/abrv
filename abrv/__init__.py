import os

from getpass import getuser

from flask import Flask

from . import db
from . import url


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE={
            'database': 'abrv',
            'user': getuser(),
            'password': '',
        }
    )

    if test_config is None:
        try:
            app.config.from_pyfile('config.py', silent=False)
        except FileNotFoundError:
            app.logger.warning('Running with insecure built-in configuration.')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(url.bp)

    return app
