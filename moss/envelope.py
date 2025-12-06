from dataclasses import dataclass


@dataclass
class Envelope:
    spec: str
    version: int
    alg: str
    subject: str
    key_version: int
    seq: int
    issued_at: int
    payload_hash: str
    signature: str

    def to_dict(self) -> dict:
        return {
            "spec": self.spec,
            "version": self.version,
            "alg": self.alg,
            "subject": self.subject,
            "key_version": self.key_version,
            "seq": self.seq,
            "issued_at": self.issued_at,
            "payload_hash": self.payload_hash,
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Envelope":
        return cls(
            spec=d["spec"],
            version=d["version"],
            alg=d["alg"],
            subject=d["subject"],
            key_version=d["key_version"],
            seq=d["seq"],
            issued_at=d["issued_at"],
            payload_hash=d["payload_hash"],
            signature=d["signature"]
        )
