import pytest
import json
from pathlib import Path

from moss.canonical import cjjson, payload_hash
from moss.crypto import MossCrypto


@pytest.fixture
def vectors():
    """Load conformance test vectors"""
    vectors_path = Path(__file__).parent.parent / "conformance" / "vectors.json"
    with open(vectors_path) as f:
        return json.load(f)


class TestConformanceVectors:
    def test_key_lengths(self, vectors):
        expected = vectors["meta"]["expected_lengths"]
        assert MossCrypto.EXPECTED_PK_LEN == expected["public_key_bytes"]
        assert MossCrypto.EXPECTED_SIG_LEN == expected["signature_bytes"]

    def test_actual_key_lengths(self, vectors):
        pk, sk = MossCrypto.keygen()
        assert len(pk) == vectors["meta"]["expected_lengths"]["public_key_bytes"]

        sig = MossCrypto.sign(sk, b"test")
        assert len(sig) == vectors["meta"]["expected_lengths"]["signature_bytes"]

    def test_simple_payload_canonical(self, vectors):
        case = vectors["cases"][0]
        assert case["name"] == "simple"

        canonical = cjjson(case["payload"])
        assert canonical.decode('utf-8') == case["payload_canonical"]

    def test_simple_payload_hash(self, vectors):
        case = vectors["cases"][0]
        computed = payload_hash(case["payload"])
        assert computed == case["payload_hash_b64url"]

    def test_nested_payload_canonical(self, vectors):
        case = vectors["cases"][1]
        assert case["name"] == "nested"

        canonical = cjjson(case["payload"])
        assert canonical.decode('utf-8') == case["payload_canonical"]

    def test_nested_payload_hash(self, vectors):
        case = vectors["cases"][1]
        computed = payload_hash(case["payload"])
        assert computed == case["payload_hash_b64url"]

    def test_unicode_payload_canonical(self, vectors):
        case = vectors["cases"][2]
        assert case["name"] == "unicode"

        canonical = cjjson(case["payload"])
        assert canonical.decode('utf-8') == case["payload_canonical"]

    def test_unicode_payload_hash(self, vectors):
        case = vectors["cases"][2]
        computed = payload_hash(case["payload"])
        assert computed == case["payload_hash_b64url"]

    def test_signed_bytes_format(self, vectors):
        case = vectors["cases"][0]
        fixed = vectors["fixed_fields"]

        signed_bytes_obj = {
            "spec": vectors["meta"]["spec"],
            "version": vectors["meta"]["version"],
            "alg": vectors["meta"]["alg"],
            "subject": fixed["subject"],
            "key_version": fixed["key_version"],
            "seq": fixed["seq"],
            "issued_at": fixed["issued_at"],
            "payload_hash": case["payload_hash_b64url"]
        }

        signed_bytes = cjjson(signed_bytes_obj)
        assert signed_bytes.decode('utf-8') == case["signed_bytes_canonical"]

    def test_all_cases_have_required_fields(self, vectors):
        for case in vectors["cases"]:
            assert "name" in case
            assert "payload" in case
            assert "payload_canonical" in case
            assert "payload_hash_b64url" in case
