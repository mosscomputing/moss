import os
import json
import time
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .encoding import b64url_encode, b64url_decode
from .errors import KeyNotFound, DecryptionFailed, InvalidSubject

MOSS_DIR = Path.home() / ".moss"
KEYS_DIR = MOSS_DIR / "keys"


def _get_passphrase() -> bytes:
    """Get passphrase from env or use default (for dev)."""
    pp = os.environ.get("MOSS_KEY_PASSPHRASE", "moss-dev-passphrase")
    return pp.encode('utf-8')


def _derive_key(salt: bytes) -> bytes:
    """Derive 256-bit key from passphrase using Scrypt."""
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(_get_passphrase())


def _encrypt(data: bytes, salt: bytes) -> tuple[bytes, bytes]:
    """Encrypt data with AES-256-GCM. Returns (nonce, ciphertext)."""
    key = _derive_key(salt)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce, ct


def _decrypt(nonce: bytes, ciphertext: bytes, salt: bytes) -> bytes:
    """Decrypt data with AES-256-GCM."""
    key = _derive_key(salt)
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise DecryptionFailed(f"Failed to decrypt key: {e}")


def get_key_path(subject: str) -> Path:
    """Convert subject to file path: moss:ns:name -> ns/name.json"""
    parts = subject.split(":")
    if len(parts) != 3 or parts[0] != "moss":
        raise InvalidSubject(f"Invalid subject format: {subject}")
    namespace, name = parts[1], parts[2]
    return KEYS_DIR / namespace / f"{name}.json"


def save_keys(subject: str, public_key: bytes, secret_key: bytes, key_version: int = 1):
    """Save encrypted key pair to local storage."""
    path = get_key_path(subject)
    path.parent.mkdir(parents=True, exist_ok=True)

    salt = os.urandom(16)
    nonce, encrypted_sk = _encrypt(secret_key, salt)

    data = {
        "version": 1,
        "subject": subject,
        "key_version": key_version,
        "alg": "ML-DSA-44",
        "public_key": b64url_encode(public_key),
        "encrypted_secret_key": b64url_encode(encrypted_sk),
        "salt": b64url_encode(salt),
        "nonce": b64url_encode(nonce),
        "seq": 0,
        "created_at": int(time.time())
    }

    path.write_text(json.dumps(data, indent=2))
    os.chmod(path, 0o600)


def load_keys(subject: str) -> dict:
    """Load and decrypt key data from local storage."""
    path = get_key_path(subject)
    if not path.exists():
        raise KeyNotFound(f"No keys found for {subject}")

    data = json.loads(path.read_text())

    salt = b64url_decode(data["salt"])
    nonce = b64url_decode(data["nonce"])
    encrypted_sk = b64url_decode(data["encrypted_secret_key"])
    secret_key = _decrypt(nonce, encrypted_sk, salt)

    return {
        "subject": data["subject"],
        "key_version": data["key_version"],
        "public_key": b64url_decode(data["public_key"]),
        "secret_key": secret_key,
        "seq": data["seq"]
    }


def increment_seq(subject: str) -> int:
    """Atomically increment and return next sequence number."""
    path = get_key_path(subject)
    data = json.loads(path.read_text())
    data["seq"] += 1
    path.write_text(json.dumps(data, indent=2))
    return data["seq"]


def get_public_key(subject: str) -> bytes:
    """Get just the public key (no decryption needed)."""
    path = get_key_path(subject)
    if not path.exists():
        raise KeyNotFound(f"No keys found for {subject}")
    data = json.loads(path.read_text())
    return b64url_decode(data["public_key"])
