import base64


def b64url_encode(data: bytes) -> str:
    """base64url encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def b64url_decode(s: str) -> bytes:
    """base64url decode, handle missing padding."""
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s)
