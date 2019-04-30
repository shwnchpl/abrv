import binascii

from base64 import urlsafe_b64decode, urlsafe_b64encode

from flask import (
    Blueprint, redirect, request, flash, render_template, g, abort
)

from .db import get_db


bp = Blueprint('url', __name__, url_prefix='')


@bp.route('/', methods=('GET', 'POST'))
def register_new_url():
    if request.method == 'POST':
        # TODO: Figure out if it would be better to use
        # json or form content for this request.
        url = request.form['url']
        # url = request.json['url']

        if url:
            short_path = get_or_create_short_path(url)

            if short_path is not None:
                g.most_recent_url = url
                g.most_recent_short = '{}{}'.format(request.url_root,
                                                    short_path)
        else:
            abort(400) # Bad request.

    return render_template('base.html')


@bp.route('/<string:id_b64>')
def process_url_req(id_b64):
    try:
        url_id = b64_to_id(id_b64)
    except RuntimeError:
        abort(404) # TODO: Should this really be 404?

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute('SELECT url FROM urls WHERE id = %s', (url_id,))
    except OverflowError:
        abort(404) # TODO: Should this really be 404?

    row = cursor.fetchone()
    cursor.close() # TODO: Remove if not needed.

    if row is None:
        abort(404) # TODO: Should this really be 404?

    return redirect(
        'http://' + row['url'] if row['url'].find('://') == -1 else row['url']
    )


def get_or_create_short_path(url):
    url_hash = djb2_hash(url)

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
        row = cursor.fetchone() # TODO: Catch error and rollback
        short_path = row['short_path']
        db.commit()
    else:
        short_path = row['short_path']

    cursor.close() # TODO: Remove if not needed.

    return short_path


def b64_to_id(s):
    try:
        # FIXME: Just adding two '=' is a bit of a hack.
        # Really, this should be following RFC7515 directly.
        id_ = int.from_bytes(
            urlsafe_b64decode((s + '==').encode('ascii')),
            'big'
        )
    except binascii.Error:
        # FIXME: Replace with custom exception.
        raise RuntimeError()
    else:
        return id_


# TODO: Remove? Or just use for testing. Possibly no longer needed.
def id_to_b64(x):
    return urlsafe_b64encode(
        x.to_bytes((x.bit_length() + 7) // 8, 'big')
    ).replace(b'=', b'').decode('ascii')


def djb2_hash(s):
    h = 5381
    for c in s:
        h = ((h << 5) + h) + ord(c)
    return h & 0xfffffffffffffff
