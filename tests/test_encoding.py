from moss.encoding import b64url_encode, b64url_decode


class TestB64UrlEncode:
    def test_encode_simple(self):
        data = b"hello"
        result = b64url_encode(data)
        assert result == "aGVsbG8"
        assert "=" not in result

    def test_encode_binary(self):
        data = bytes([0x00, 0xFF, 0x7F, 0x80])
        result = b64url_encode(data)
        assert "+" not in result
        assert "/" not in result

    def test_encode_empty(self):
        result = b64url_encode(b"")
        assert result == ""


class TestB64UrlDecode:
    def test_decode_simple(self):
        result = b64url_decode("aGVsbG8")
        assert result == b"hello"

    def test_decode_with_padding_1(self):
        encoded = b64url_encode(b"a")
        result = b64url_decode(encoded)
        assert result == b"a"

    def test_decode_with_padding_2(self):
        encoded = b64url_encode(b"ab")
        result = b64url_decode(encoded)
        assert result == b"ab"

    def test_decode_no_padding_needed(self):
        encoded = b64url_encode(b"abc")
        result = b64url_decode(encoded)
        assert result == b"abc"


class TestRoundTrip:
    def test_roundtrip_various_lengths(self):
        for length in range(0, 100):
            data = bytes(range(length % 256)) * (length // 256 + 1)
            data = data[:length]
            encoded = b64url_encode(data)
            decoded = b64url_decode(encoded)
            assert decoded == data

    def test_roundtrip_sha256_hash(self):
        import hashlib
        data = hashlib.sha256(b"test").digest()
        assert len(data) == 32
        encoded = b64url_encode(data)
        assert len(encoded) == 43
        decoded = b64url_decode(encoded)
        assert decoded == data
