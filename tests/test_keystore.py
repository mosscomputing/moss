import pytest
from unittest.mock import patch

from moss.keystore import (
    save_keys, load_keys, increment_seq, get_public_key, get_key_path
)
from moss.errors import KeyNotFound, InvalidSubject


@pytest.fixture
def temp_moss_dir(tmp_path):
    """Use a temporary directory for .moss"""
    test_keys_dir = tmp_path / "keys"
    with patch('moss.keystore.KEYS_DIR', test_keys_dir):
        yield test_keys_dir


class TestGetKeyPath:
    def test_valid_subject(self):
        path = get_key_path("moss:dev:test")
        assert "dev" in str(path)
        assert "test.json" in str(path)

    def test_invalid_subject_format(self):
        with pytest.raises(InvalidSubject):
            get_key_path("invalid")

    def test_invalid_subject_wrong_prefix(self):
        with pytest.raises(InvalidSubject):
            get_key_path("other:dev:test")


class TestSaveLoadKeys:
    def test_save_and_load(self, temp_moss_dir):
        subject = "moss:test:saveload"
        pk = b"x" * 1312
        sk = b"y" * 2528

        save_keys(subject, pk, sk, key_version=1)
        loaded = load_keys(subject)

        assert loaded["subject"] == subject
        assert loaded["public_key"] == pk
        assert loaded["secret_key"] == sk
        assert loaded["key_version"] == 1
        assert loaded["seq"] == 0

    def test_load_nonexistent(self, temp_moss_dir):
        with pytest.raises(KeyNotFound):
            load_keys("moss:test:nonexistent")

    def test_file_permissions(self, temp_moss_dir):
        subject = "moss:test:perms"
        pk = b"x" * 1312
        sk = b"y" * 2528

        save_keys(subject, pk, sk)
        path = temp_moss_dir / "test" / "perms.json"
        mode = oct(path.stat().st_mode)[-3:]
        assert mode == "600"


class TestIncrementSeq:
    def test_increment(self, temp_moss_dir):
        subject = "moss:test:seq"
        pk = b"x" * 1312
        sk = b"y" * 2528

        save_keys(subject, pk, sk)

        seq1 = increment_seq(subject)
        assert seq1 == 1

        seq2 = increment_seq(subject)
        assert seq2 == 2

        seq3 = increment_seq(subject)
        assert seq3 == 3


class TestGetPublicKey:
    def test_get_public_key(self, temp_moss_dir):
        subject = "moss:test:pubkey"
        pk = b"publickey" + b"x" * 1303
        sk = b"y" * 2528

        save_keys(subject, pk, sk)
        loaded_pk = get_public_key(subject)
        assert loaded_pk == pk

    def test_get_public_key_nonexistent(self, temp_moss_dir):
        with pytest.raises(KeyNotFound):
            get_public_key("moss:test:nope")
