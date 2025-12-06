from moss.canonical import cjjson, sha256_b64url, payload_hash


class TestCjjson:
    def test_simple_object(self):
        result = cjjson({"foo": "bar"})
        assert result == b'{"foo":"bar"}'

    def test_sorted_keys(self):
        result = cjjson({"b": 2, "a": 1})
        assert result == b'{"a":1,"b":2}'

    def test_nested_sorted(self):
        result = cjjson({"b": 2, "a": 1, "nested": {"y": "z", "x": "y"}})
        assert result == b'{"a":1,"b":2,"nested":{"x":"y","y":"z"}}'

    def test_no_whitespace(self):
        result = cjjson({"key": "value", "arr": [1, 2, 3]})
        assert b" " not in result
        assert b"\n" not in result

    def test_unicode(self):
        result = cjjson({"msg": "cafe", "lang": "fr"})
        assert result == '{"lang":"fr","msg":"cafe"}'.encode('utf-8')

    def test_unicode_preserved(self):
        result = cjjson({"emoji": "test"})
        assert "emoji" in result.decode('utf-8')


class TestSha256B64url:
    def test_known_hash(self):
        result = sha256_b64url(b"test")
        assert len(result) == 43

    def test_empty_input(self):
        result = sha256_b64url(b"")
        assert len(result) == 43


class TestPayloadHash:
    def test_simple_payload(self):
        result = payload_hash({"foo": "bar"})
        assert result == "eji_gfOD9pQzrW6QDTWz4jhVk_dqe3q11DVbi6Qe4ks"

    def test_nested_payload(self):
        result = payload_hash({"b": 2, "a": 1, "nested": {"y": "z", "x": "y"}})
        assert result == "zURBoOF4M_LkDVUg2MG_MWIvREB3t-Gdw_7GxsJ_bmI"

    def test_canonicalization_invariance(self):
        hash1 = payload_hash({"b": 2, "a": 1})
        hash2 = payload_hash({"a": 1, "b": 2})
        assert hash1 == hash2

    def test_deterministic(self):
        payload = {"action": "test", "data": {"nested": True}}
        hash1 = payload_hash(payload)
        hash2 = payload_hash(payload)
        assert hash1 == hash2
