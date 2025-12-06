import pytest
from unittest.mock import patch

from moss.sequence import (
    get_last_seen_seq, update_last_seen_seq, check_and_update_seq
)


@pytest.fixture
def temp_seq_dir(tmp_path):
    """Use a temporary directory for sequence tracking"""
    test_seq_dir = tmp_path / "seq"
    with patch('moss.sequence.SEQ_DIR', test_seq_dir):
        yield test_seq_dir


class TestGetLastSeenSeq:
    def test_nonexistent_returns_zero(self, temp_seq_dir):
        result = get_last_seen_seq("moss:test:new", 1)
        assert result == 0

    def test_returns_stored_value(self, temp_seq_dir):
        update_last_seen_seq("moss:test:stored", 1, 42)
        result = get_last_seen_seq("moss:test:stored", 1)
        assert result == 42


class TestUpdateLastSeenSeq:
    def test_creates_file(self, temp_seq_dir):
        update_last_seen_seq("moss:test:create", 1, 10)
        assert get_last_seen_seq("moss:test:create", 1) == 10

    def test_updates_existing(self, temp_seq_dir):
        update_last_seen_seq("moss:test:update", 1, 5)
        update_last_seen_seq("moss:test:update", 1, 10)
        assert get_last_seen_seq("moss:test:update", 1) == 10


class TestCheckAndUpdateSeq:
    def test_first_seq_valid(self, temp_seq_dir):
        result = check_and_update_seq("moss:test:first", 1, 1)
        assert result is True

    def test_increasing_seq_valid(self, temp_seq_dir):
        check_and_update_seq("moss:test:inc", 1, 1)
        result = check_and_update_seq("moss:test:inc", 1, 2)
        assert result is True

    def test_same_seq_invalid(self, temp_seq_dir):
        check_and_update_seq("moss:test:same", 1, 5)
        result = check_and_update_seq("moss:test:same", 1, 5)
        assert result is False

    def test_lower_seq_invalid(self, temp_seq_dir):
        check_and_update_seq("moss:test:lower", 1, 10)
        result = check_and_update_seq("moss:test:lower", 1, 5)
        assert result is False

    def test_different_key_versions(self, temp_seq_dir):
        check_and_update_seq("moss:test:ver", 1, 5)
        result = check_and_update_seq("moss:test:ver", 2, 1)
        assert result is True
