from dilithium_py.dilithium import Dilithium2


class MossCrypto:
    ALG = "ML-DSA-44"
    EXPECTED_PK_LEN = 1312
    EXPECTED_SIG_LEN = 2420

    @classmethod
    def keygen(cls) -> tuple[bytes, bytes]:
        """Generate (public_key, secret_key) pair."""
        pk, sk = Dilithium2.keygen()
        assert len(pk) == cls.EXPECTED_PK_LEN, f"Bad pk length: {len(pk)}"
        return pk, sk

    @classmethod
    def sign(cls, secret_key: bytes, message: bytes) -> bytes:
        """Sign message with secret key."""
        sig = Dilithium2.sign(secret_key, message)
        assert len(sig) == cls.EXPECTED_SIG_LEN, f"Bad sig length: {len(sig)}"
        return sig

    @classmethod
    def verify(cls, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify signature. Returns True/False, never raises."""
        try:
            return Dilithium2.verify(public_key, message, signature)
        except Exception:
            return False
