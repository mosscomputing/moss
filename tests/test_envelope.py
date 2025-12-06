import pytest
from moss.envelope import Envelope


class TestEnvelope:
    def test_to_dict(self):
        env = Envelope(
            spec="moss-0001",
            version=1,
            alg="ML-DSA-44",
            subject="moss:test:agent",
            key_version=1,
            seq=42,
            issued_at=1733200000,
            payload_hash="abc123",
            signature="sig456"
        )
        d = env.to_dict()
        assert d["spec"] == "moss-0001"
        assert d["version"] == 1
        assert d["alg"] == "ML-DSA-44"
        assert d["subject"] == "moss:test:agent"
        assert d["key_version"] == 1
        assert d["seq"] == 42
        assert d["issued_at"] == 1733200000
        assert d["payload_hash"] == "abc123"
        assert d["signature"] == "sig456"

    def test_from_dict(self):
        d = {
            "spec": "moss-0001",
            "version": 1,
            "alg": "ML-DSA-44",
            "subject": "moss:test:agent",
            "key_version": 1,
            "seq": 42,
            "issued_at": 1733200000,
            "payload_hash": "abc123",
            "signature": "sig456"
        }
        env = Envelope.from_dict(d)
        assert env.spec == "moss-0001"
        assert env.version == 1
        assert env.alg == "ML-DSA-44"
        assert env.subject == "moss:test:agent"
        assert env.key_version == 1
        assert env.seq == 42
        assert env.issued_at == 1733200000
        assert env.payload_hash == "abc123"
        assert env.signature == "sig456"

    def test_roundtrip(self):
        original = Envelope(
            spec="moss-0001",
            version=1,
            alg="ML-DSA-44",
            subject="moss:test:roundtrip",
            key_version=2,
            seq=100,
            issued_at=1733200000,
            payload_hash="hash",
            signature="sig"
        )
        d = original.to_dict()
        restored = Envelope.from_dict(d)
        assert restored == original

    def test_from_dict_missing_key(self):
        d = {"spec": "moss-0001"}
        with pytest.raises(KeyError):
            Envelope.from_dict(d)
