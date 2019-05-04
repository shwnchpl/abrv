import binascii

from base64 import urlsafe_b64decode, urlsafe_b64encode


class B64DecodeError(Exception):
    pass


def b64_to_id(s):
    try:
        # XXX: Really, just adding two '=' is a bit of a hack.
        # This could/should be following RFC7515 directly, but
        # since trailing '=' are ignored by urlsafe_b64decode
        # this always works.
        id_ = int.from_bytes(
            urlsafe_b64decode((s + '==').encode('ascii')),
            'big'
        )
    except binascii.Error as e:
        raise B64DecodeError() from e
    else:
        return id_


def id_to_b64(x):
    return urlsafe_b64encode(
        x.to_bytes((x.bit_length() + 7) // 8, 'big')
    ).replace(b'=', b'').decode('ascii')


def djb2_hash(s):
    h = 5381
    for c in s:
        h = ((h << 5) + h) + ord(c)
    return h & 0xfffffffffffffff
