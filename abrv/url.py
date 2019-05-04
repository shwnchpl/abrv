from http import HTTPStatus

import psycopg2 as pg2

from flask import (
    Blueprint, redirect, request, render_template, g, abort
)

from . import util
from .db import get_db


bp = Blueprint('url', __name__, url_prefix='')


@bp.route('/', methods=('GET', 'POST'))
def register_new_url():
    if request.method == 'POST':
        url = request.form['url']

        if url:
            short_path = get_or_create_short_path(url)

            if short_path is not None:
                g.most_recent_url = url
                g.most_recent_short = '{}{}'.format(request.url_root,
                                                    short_path)
        else:
            abort(HTTPStatus.BAD_REQUEST.value)

    return render_template('base.html')


@bp.route('/<string:id_b64>')
def process_url_req(id_b64):
    try:
        url_id = util.b64_to_id(id_b64)
    except util.B64DecodeError:
        abort(HTTPStatus.BAD_REQUEST.value)

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute('SELECT url FROM urls WHERE id = %s', (url_id,))
    except OverflowError:
        abort(HTTPStatus.NOT_FOUND.value)

    row = cursor.fetchone()
    if row is None:
        abort(HTTPStatus.NOT_FOUND.value)

    return redirect(
        'http://' + row['url'] if row['url'].find('://') == -1 else row['url']
    )


def get_or_create_short_path(url):
    url_hash = util.djb2_hash(url)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT short_path FROM urls WHERE hash = %s and url = %s',
        (url_hash, url)
    )
    row = cursor.fetchone()
    short_path = None
    if row is None:
        cursor.execute(
            'INSERT INTO urls (url, hash, short_path) '
            'VALUES (%s, %s, i_to_wsb64(lastval())) '
            'RETURNING short_path',
            (url, url_hash))

        try:
            row = cursor.fetchone()
        except pg2.ProgrammingError:
            db.rollback()
            abort(HTTPStatus.INTERNAL_SERVER_ERROR.value)

        short_path = row['short_path']
        db.commit()
    else:
        short_path = row['short_path']

    return short_path
