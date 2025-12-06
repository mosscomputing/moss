from moss.crypto import MossCrypto


class TestMossCrypto:
    def test_keygen_lengths(self):
        pk, sk = MossCrypto.keygen()
        assert len(pk) == MossCrypto.EXPECTED_PK_LEN
        assert len(pk) == 1312

    def test_sign_length(self):
        pk, sk = MossCrypto.keygen()
        sig = MossCrypto.sign(sk, b"test message")
        assert len(sig) == MossCrypto.EXPECTED_SIG_LEN
        assert len(sig) == 2420

    def test_sign_verify_roundtrip(self):
        pk, sk = MossCrypto.keygen()
        message = b"test message"
        sig = MossCrypto.sign(sk, message)
        assert MossCrypto.verify(pk, message, sig) is True

    def test_verify_wrong_message(self):
        pk, sk = MossCrypto.keygen()
        sig = MossCrypto.sign(sk, b"original message")
        assert MossCrypto.verify(pk, b"wrong message", sig) is False

    def test_verify_wrong_key(self):
        pk1, sk1 = MossCrypto.keygen()
        pk2, sk2 = MossCrypto.keygen()
        message = b"test message"
        sig = MossCrypto.sign(sk1, message)
        assert MossCrypto.verify(pk2, message, sig) is False

    def test_verify_tampered_signature(self):
        pk, sk = MossCrypto.keygen()
        message = b"test message"
        sig = MossCrypto.sign(sk, message)
        tampered = bytearray(sig)
        tampered[0] ^= 0xFF
        assert MossCrypto.verify(pk, message, bytes(tampered)) is False

    def test_verify_never_raises(self):
        pk, sk = MossCrypto.keygen()
        result = MossCrypto.verify(pk, b"msg", b"invalid sig")
        assert result is False

    def test_alg_constant(self):
        assert MossCrypto.ALG == "ML-DSA-44"
