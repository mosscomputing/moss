# MOSS

Know exactly which agent produced what.

MOSS (Message-Origin Signing System) is a cryptographic signing protocol for AI agents. It binds identities to agents and produces verifiable signatures on their outputs.

[![CI](https://github.com/mosscomputing/moss/actions/workflows/ci.yml/badge.svg)](https://github.com/mosscomputing/moss/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/moss-sdk)](https://pypi.org/project/moss-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Install
```bash
pip install moss-sdk
```

## Usage
```python
from moss import Subject

agent = Subject.create("moss:dev:my-agent")
envelope = agent.sign({"action": "approved", "amount": 500})

result = Subject.verify(envelope)
assert result.valid
```

## Framework Integrations
```bash
pip install moss-crewai    # CrewAI
pip install moss-autogen   # AutoGen
pip install moss-langgraph # LangGraph
pip install moss-langchain # LangChain
```

## CLI
```bash
moss subject create moss:dev:my-agent
echo '{"action": "test"}' | moss sign moss:dev:my-agent - > envelope.json
moss verify payload.json envelope.json
```

## Protocol

MOSS implements `moss-0001`. See [SPEC.md](SPEC.md).

### Envelope
```json
{
  "spec": "moss-0001",
  "version": 1,
  "alg": "ML-DSA-44",
  "subject": "moss:acme:order-bot",
  "key_version": 1,
  "seq": 42,
  "issued_at": 1733200000,
  "payload_hash": "<base64url(SHA-256(canonical(payload)))>",
  "signature": "<base64url(ML-DSA-44 signature)>"
}
```

### Verification

1. Check `spec == "moss-0001"`
2. Compute `hash = base64url(SHA-256(canonical(payload)))`
3. Assert `hash == envelope.payload_hash`
4. Resolve `(subject, key_version) → public_key`
5. Verify `ML-DSA-44.verify(public_key, canonical(signed_bytes), signature)`

## Cryptography

| | |
|---|---|
| Signatures | ML-DSA-44 (FIPS 204) |
| Hash | SHA-256 |
| Encoding | base64url, no padding |
| Canonicalization | RFC 8785 |
| Key storage | AES-256-GCM + Scrypt |

Keys stored at `~/.moss/keys/`. Set `MOSS_KEY_PASSPHRASE` to encrypt at rest.

## Links

- [mosscomputing.com](https://mosscomputing.com) — Project site
- [SPEC.md](SPEC.md) — Protocol specification
- [PyPI](https://pypi.org/project/moss-sdk/) — Package

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Report vulnerabilities to moss@iampass.com. See [SECURITY.md](SECURITY.md).

## License

MIT
