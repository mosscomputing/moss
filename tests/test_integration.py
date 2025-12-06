import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from moss import Subject, Envelope, VerifyResult
from moss.errors import InvalidSubject, KeyNotFound


@pytest.fixture
def temp_moss_dir(tmp_path):
    """Use a temporary directory for all MOSS data"""
    keys_dir = tmp_path / "keys"
    seq_dir = tmp_path / "seq"
    with patch('moss.keystore.KEYS_DIR', keys_dir), \
         patch('moss.sequence.SEQ_DIR', seq_dir):
        yield tmp_path


class TestSubjectCreate:
    def test_create_valid_subject(self, temp_moss_dir):
        agent = Subject.create("moss:dev:my-agent")
        assert agent.subject == "moss:dev:my-agent"
        assert len(agent.public_key) == 1312
        assert agent.key_version == 1

    def test_create_invalid_subject_format(self, temp_moss_dir):
        with pytest.raises(InvalidSubject):
            Subject.create("invalid-format")

    def test_create_invalid_subject_uppercase(self, temp_moss_dir):
        with pytest.raises(InvalidSubject):
            Subject.create("moss:DEV:agent")


class TestSubjectLoad:
    def test_load_existing(self, temp_moss_dir):
        Subject.create("moss:dev:loadtest")
        loaded = Subject.load("moss:dev:loadtest")
        assert loaded.subject == "moss:dev:loadtest"

    def test_load_nonexistent(self, temp_moss_dir):
        with pytest.raises(KeyNotFound):
            Subject.load("moss:dev:nonexistent")


class TestSignAndVerify:
    def test_sign_creates_envelope(self, temp_moss_dir):
        agent = Subject.create("moss:dev:signer")
        envelope = agent.sign({"action": "test"})

        assert isinstance(envelope, Envelope)
        assert envelope.spec == "moss-0001"
        assert envelope.version == 1
        assert envelope.alg == "ML-DSA-44"
        assert envelope.subject == "moss:dev:signer"
        assert envelope.seq == 1

    def test_sign_verify_roundtrip(self, temp_moss_dir):
        agent = Subject.create("moss:dev:roundtrip")
        payload = {"action": "test", "data": {"nested": True}}
        envelope = agent.sign(payload)

        result = Subject.verify(envelope, payload, check_replay=False)
        assert result.valid is True
        assert result.subject == "moss:dev:roundtrip"

    def test_verify_tampered_payload(self, temp_moss_dir):
        agent = Subject.create("moss:dev:tamper")
        envelope = agent.sign({"original": "data"})

        result = Subject.verify(envelope, {"tampered": "data"}, check_replay=False)
        assert result.valid is False
        assert result.error_code == "MOSS_ERR_005"

    def test_verify_dict_envelope(self, temp_moss_dir):
        agent = Subject.create("moss:dev:dictenv")
        payload = {"test": True}
        envelope = agent.sign(payload)
        envelope_dict = envelope.to_dict()

        result = Subject.verify(envelope_dict, payload, check_replay=False)
        assert result.valid is True


class TestReplayDetection:
    def test_replay_detected(self, temp_moss_dir):
        agent = Subject.create("moss:dev:replay")
        payload = {"action": "test"}
        envelope = agent.sign(payload)

        result1 = Subject.verify(envelope, payload, check_replay=True)
        assert result1.valid is True

        result2 = Subject.verify(envelope, payload, check_replay=True)
        assert result2.valid is False
        assert result2.error_code == "MOSS_ERR_006"

    def test_no_replay_check(self, temp_moss_dir):
        agent = Subject.create("moss:dev:noreplay")
        payload = {"action": "test"}
        envelope = agent.sign(payload)

        result1 = Subject.verify(envelope, payload, check_replay=False)
        assert result1.valid is True

        result2 = Subject.verify(envelope, payload, check_replay=False)
        assert result2.valid is True


class TestSequenceIncrement:
    def test_seq_increments(self, temp_moss_dir):
        agent = Subject.create("moss:dev:seqinc")

        env1 = agent.sign({"n": 1})
        env2 = agent.sign({"n": 2})
        env3 = agent.sign({"n": 3})

        assert env1.seq == 1
        assert env2.seq == 2
        assert env3.seq == 3


class TestCanonicalInvariance:
    def test_key_order_invariance(self, temp_moss_dir):
        from moss.canonical import payload_hash
        hash1 = payload_hash({"b": 2, "a": 1})
        hash2 = payload_hash({"a": 1, "b": 2})
        assert hash1 == hash2


class TestOfflineMode:
    def test_verify_works_offline(self, temp_moss_dir):
        agent = Subject.create("moss:dev:offline")
        payload = {"offline": True}
        envelope = agent.sign(payload)

        result = Subject.verify(envelope, payload, check_replay=False)
        assert result.valid is True
