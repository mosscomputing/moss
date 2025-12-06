# MOSS

**Know exactly which agent produced what.**

MOSS (Machine to Machine Operation Security System) is a cryptographic signing protocol for AI agents. Every agent gets an identity. Every output gets a signature. Verifiable, tamper-proof, reproducible.

[![CI](https://github.com/mosscomputing/moss/actions/workflows/ci.yml/badge.svg)](https://github.com/mosscomputing/moss/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/moss.svg)](https://badge.fury.io/py/moss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install moss
```

## Quick Start

```python
from moss import Subject

# Create an agent identity
agent = Subject.create("moss:dev:my-agent")

# Sign any output
envelope = agent.sign({"action": "approved", "amount": 500})

# Verify
result = Subject.verify(envelope)
assert result.valid
print(result.subject)  # moss:dev:my-agent
```

## Why MOSS?

Multi-agent pipeline breaks, four agents touched it, no idea which one — you've been there. MOSS gives every agent an identity and signs every output so you can trace, diff, and verify.

**Security guarantees:**
- **Identity** — Unique subject per agent, bound to cryptographic key pair
- **Integrity** — Payload hash detects any modification
- **Replay protection** — Sequence numbers prevent reuse
- **Post-quantum** — ML-DSA-44 (FIPS 204) signatures survive quantum

## CLI

```bash
# Create a subject
moss subject create moss:dev:my-agent

# Sign a payload
echo '{"action": "test"}' | moss sign moss:dev:my-agent - > envelope.json

# Verify
moss verify payload.json envelope.json

# Compare envelopes
moss diff envelope1.json envelope2.json
```

## Framework Integrations

```bash
pip install moss-crewai    # CrewAI
pip install moss-autogen   # AutoGen
pip install moss-langgraph # LangGraph
pip install moss-langchain # LangChain
```

## Specification

MOSS implements the `moss-0001` specification. See [SPEC.md](SPEC.md) for the full protocol specification.

### Envelope Format

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

### Verification Procedure

1. Require `spec == "moss-0001"`
2. Compute `hash = base64url(SHA-256(canonical(payload)))`
3. Assert `hash == envelope.payload_hash`
4. Resolve `(subject, key_version) → public_key`
5. Verify `ML-DSA-44.verify(public_key, canonical(signed_bytes), signature)`

## Local-First

MOSS works entirely offline. Keys are stored locally at `~/.moss/keys/`. No account required. No cloud. No tracking.

To encrypt keys at rest, set:
```bash
export MOSS_KEY_PASSPHRASE="your-secure-passphrase"
```

## What MOSS Collects

**In the envelope:** `subject`, `payload_hash` (not the payload itself), `seq`, `issued_at`, `signature`

**Never:** Your payload content, LLM prompts/responses, user data, PII, telemetry

## Technical Details

| Component | Value |
|-----------|-------|
| Signature | ML-DSA-44 (FIPS 204, Dilithium2) |
| Hash | SHA-256 |
| Encoding | base64url (no padding) |
| Canonicalization | RFC 8785 (JCS) |
| Key encryption | AES-256-GCM + Scrypt |
| Public key size | 1312 bytes |
| Signature size | 2420 bytes |
| Overhead | <1ms sign, <1ms verify, ~2KB envelope |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## License

MIT — see [LICENSE](LICENSE)

## Links

- **Website:** [mosscomputing.com](https://mosscomputing.com)
- **Spec:** [SPEC.md](SPEC.md)
- **Discord:** [Join](https://discord.gg/mosscomputing)
