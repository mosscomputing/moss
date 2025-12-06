import json
import hashlib

from .encoding import b64url_encode


def cjjson(obj: dict) -> bytes:
    """
    RFC 8785 JSON Canonicalization Scheme.
    - Sort keys lexicographically (Unicode code point order)
    - No whitespace
    - UTF-8 encoding
    """
    return json.dumps(
        obj,
        separators=(',', ':'),
        sort_keys=True,
        ensure_ascii=False
    ).encode('utf-8')


def sha256_b64url(data: bytes) -> str:
    """SHA-256 hash, returned as base64url (43 chars)."""
    return b64url_encode(hashlib.sha256(data).digest())


def payload_hash(payload: dict) -> str:
    """Compute payload_hash per moss-0001."""
    return sha256_b64url(cjjson(payload))
