import re
import time
from dataclasses import dataclass
from typing import Any, Optional, Union

from .crypto import MossCrypto
from .canonical import cjjson, payload_hash
from .encoding import b64url_encode, b64url_decode
from .keystore import save_keys, load_keys, increment_seq, get_public_key
from .sequence import check_and_update_seq
from .envelope import Envelope
from .errors import InvalidSubject

SPEC = "moss-0001"
VERSION = 1
SUBJECT_PATTERN = re.compile(r"^moss:[a-z0-9_-]+:[a-z0-9_-]+$")


@dataclass
class VerifyResult:
    valid: bool
    subject: Optional[str] = None
    payload_hash: Optional[str] = None
    reason: Optional[str] = None
    error_code: Optional[str] = None


class Subject:
    def __init__(self, subject: str, secret_key: bytes, public_key: bytes, key_version: int):
        self.subject = subject
        self.secret_key = secret_key
        self.public_key = public_key
        self.key_version = key_version

    @classmethod
    def create(cls, subject: str) -> "Subject":
        """Create a new subject with fresh ML-DSA-44 keypair."""
        if not SUBJECT_PATTERN.match(subject):
            raise InvalidSubject(
                f"Invalid subject format: {subject}. "
                f"Expected: moss:namespace:name (lowercase alphanumeric, hyphens, underscores)"
            )

        pk, sk = MossCrypto.keygen()
        save_keys(subject, pk, sk, key_version=1)

        return cls(subject=subject, secret_key=sk, public_key=pk, key_version=1)

    @classmethod
    def load(cls, subject: str) -> "Subject":
        """Load existing subject from local keystore."""
        data = load_keys(subject)
        return cls(
            subject=data["subject"],
            secret_key=data["secret_key"],
            public_key=data["public_key"],
            key_version=data["key_version"]
        )

    def sign(self, payload: Any) -> Envelope:
        """Sign a payload and return an envelope."""
        seq = increment_seq(self.subject)
        issued_at = int(time.time())
        p_hash = payload_hash(payload)

        signed_bytes_obj = {
            "spec": SPEC,
            "version": VERSION,
            "alg": MossCrypto.ALG,
            "subject": self.subject,
            "key_version": self.key_version,
            "seq": seq,
            "issued_at": issued_at,
            "payload_hash": p_hash
        }
        signed_bytes = cjjson(signed_bytes_obj)

        signature = MossCrypto.sign(self.secret_key, signed_bytes)

        return Envelope(
            spec=SPEC,
            version=VERSION,
            alg=MossCrypto.ALG,
            subject=self.subject,
            key_version=self.key_version,
            seq=seq,
            issued_at=issued_at,
            payload_hash=p_hash,
            signature=b64url_encode(signature)
        )

    @staticmethod
    def verify(
        envelope: Union[Envelope, dict],
        payload: Any = None,
        public_key: Optional[bytes] = None,
        check_replay: bool = True
    ) -> VerifyResult:
        """
        Verify an envelope.

        Args:
            envelope: Envelope object or dict
            payload: Original payload (optional, for hash verification)
            public_key: Public key bytes (optional, will load from keystore if not provided)
            check_replay: Whether to check/update sequence numbers

        Returns:
            VerifyResult with valid=True/False and details
        """
        if isinstance(envelope, dict):
            try:
                envelope = Envelope.from_dict(envelope)
            except (KeyError, TypeError) as e:
                return VerifyResult(
                    valid=False,
                    reason=f"Malformed envelope: {e}",
                    error_code="MOSS_ERR_003"
                )

        if envelope.spec != SPEC:
            return VerifyResult(
                valid=False,
                reason=f"Unknown spec: {envelope.spec}",
                error_code="MOSS_ERR_003"
            )

        if payload is not None:
            computed_hash = payload_hash(payload)
            if computed_hash != envelope.payload_hash:
                return VerifyResult(
                    valid=False,
                    subject=envelope.subject,
                    reason=f"Payload hash mismatch: expected {envelope.payload_hash}, got {computed_hash}",
                    error_code="MOSS_ERR_005"
                )

        if check_replay:
            if not check_and_update_seq(envelope.subject, envelope.key_version, envelope.seq):
                return VerifyResult(
                    valid=False,
                    subject=envelope.subject,
                    reason=f"Replay detected: seq {envelope.seq} already seen for {envelope.subject}",
                    error_code="MOSS_ERR_006"
                )

        if public_key is None:
            try:
                public_key = get_public_key(envelope.subject)
            except Exception as e:
                return VerifyResult(
                    valid=False,
                    subject=envelope.subject,
                    reason=f"Could not load public key: {e}",
                    error_code="MOSS_ERR_002"
                )

        signed_bytes_obj = {
            "spec": envelope.spec,
            "version": envelope.version,
            "alg": envelope.alg,
            "subject": envelope.subject,
            "key_version": envelope.key_version,
            "seq": envelope.seq,
            "issued_at": envelope.issued_at,
            "payload_hash": envelope.payload_hash
        }
        signed_bytes = cjjson(signed_bytes_obj)

        signature = b64url_decode(envelope.signature)
        if not MossCrypto.verify(public_key, signed_bytes, signature):
            return VerifyResult(
                valid=False,
                subject=envelope.subject,
                reason="Invalid signature",
                error_code="MOSS_ERR_004"
            )

        return VerifyResult(
            valid=True,
            subject=envelope.subject,
            payload_hash=envelope.payload_hash
        )
