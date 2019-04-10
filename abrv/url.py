import binascii

from base64 import urlsafe_b64decode, urlsafe_b64encode

from flask import Blueprint

from .db import get_db


bp = Blueprint('url', __name__, url_prefix='')


@bp.route('/<string:id_b64>')
def process_url_req(id_b64):
    try:
        res = 'You requested {}'.format(b64_to_id(id_b64))
    except RuntimeError:
        res = 'You requested an invalid id.'
    finally:
        return res


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
