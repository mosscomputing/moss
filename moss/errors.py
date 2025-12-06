class MossError(Exception):
    """Base exception for MOSS errors."""
    code = "MOSS_ERR_000"


class InvalidSubject(MossError):
    """Invalid subject format."""
    code = "MOSS_ERR_001"


class KeyNotFound(MossError):
    """No keys found for subject."""
    code = "MOSS_ERR_002"


class InvalidEnvelope(MossError):
    """Malformed envelope."""
    code = "MOSS_ERR_003"


class InvalidSignature(MossError):
    """Signature verification failed."""
    code = "MOSS_ERR_004"


class PayloadMismatch(MossError):
    """Payload hash does not match envelope."""
    code = "MOSS_ERR_005"


class ReplayDetected(MossError):
    """Sequence number already seen (replay attack)."""
    code = "MOSS_ERR_006"


class DecryptionFailed(MossError):
    """Failed to decrypt keystore (wrong passphrase?)."""
    code = "MOSS_ERR_007"
