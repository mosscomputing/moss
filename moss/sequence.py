import json
from pathlib import Path

MOSS_DIR = Path.home() / ".moss"
SEQ_DIR = MOSS_DIR / "seq"


def get_last_seen_seq(subject: str, key_version: int) -> int:
    """Get last seen sequence for (subject, key_version)."""
    path = SEQ_DIR / f"{subject.replace(':', '_')}_{key_version}.json"
    if not path.exists():
        return 0
    data = json.loads(path.read_text())
    return data.get("last_seq", 0)


def update_last_seen_seq(subject: str, key_version: int, seq: int):
    """Update last seen sequence."""
    SEQ_DIR.mkdir(parents=True, exist_ok=True)
    path = SEQ_DIR / f"{subject.replace(':', '_')}_{key_version}.json"
    path.write_text(json.dumps({"last_seq": seq}))


def check_and_update_seq(subject: str, key_version: int, seq: int) -> bool:
    """Check if seq is valid (greater than last seen) and update. Returns True if valid."""
    last = get_last_seen_seq(subject, key_version)
    if seq <= last:
        return False
    update_last_seen_seq(subject, key_version, seq)
    return True
