import binascii

from base64 import urlsafe_b64decode, urlsafe_b64encode

from flask import Blueprint, redirect, request, flash

from .db import get_db


bp = Blueprint('url', __name__, url_prefix='')


@bp.route('/', methods=('GET', 'POST'))
def register_new_url():
    if request.method == 'POST':
        # TODO: Figure out if it would be better to use
        # json or form content for this request.
        # url = request.form['url']
        url = request.json['url']
        db = get_db()

        error = None
        if not url:
            error = 'URL is required'

        if error is None:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO urls (url) VALUES (?)', (url,))
            ins_id = cursor.lastrowid
            b64_ins_id = id_to_b64(ins_id)
            cursor.execute(
                'UPDATE urls SET short_path = ? WHERE id = ?',
                (b64_ins_id, ins_id))
            db.commit()

            return 'Inserted as {}\n'.format(b64_ins_id)

        # TODO: Figure out what this does?
        flash(error)

    return 'Will be render template.'
    # TODO: figure out if this is actually desirable.
    # return render_template()

@bp.route('/<string:id_b64>')
def process_url_req(id_b64):
    # FIXME: Use real 404
    error_res = 'You requested an invalid id.'
    try:
        url_id = b64_to_id(id_b64)
    except RuntimeError:
        return error_res

    db = get_db()
    cursor = db.execute('SELECT url FROM urls WHERE id = ?', (url_id,))
    row = cursor.fetchone()
    if row is None:
        return error_res

    return redirect(row['url'])


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

def id_to_b64(x):
    return urlsafe_b64encode(
        x.to_bytes((x.bit_length() + 7) // 8, 'big')
    ).replace(b'=', b'').decode('ascii')
