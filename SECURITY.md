# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

### How to Report

Email security concerns to: **ysablewolf@iampass.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

1. **Acknowledgment** within 48 hours
2. **Initial assessment** within 7 days
3. **Resolution timeline** communicated based on severity
4. **Credit** in security advisory (if desired)

### Severity Levels

| Level | Description | Target Resolution |
|-------|-------------|-------------------|
| Critical | Remote code execution, key compromise | 24-48 hours |
| High | Signature bypass, replay in default config | 7 days |
| Medium | Information disclosure, DoS | 30 days |
| Low | Minor issues, hardening | 90 days |

## Security Considerations

### Cryptography

MOSS uses:
- **ML-DSA-44** (FIPS 204) — Post-quantum digital signatures
- **AES-256-GCM** — Key encryption at rest
- **Scrypt** — Key derivation
- **SHA-256** — Payload hashing

### Known Limitations

1. **Default passphrase** — Development default (`moss-dev-passphrase`) is not secure. Production deployments MUST set `MOSS_KEY_PASSPHRASE`.

2. **Local keystore** — Keys are stored in `~/.moss/keys/`. File permissions are set to `0600` but the directory must be protected.

3. **No clock enforcement** — `issued_at` is not validated against current time. Implementations should add bounds checking if needed.

4. **Sequence tracking** — Replay protection requires persistent storage. If verifier state is lost, replays may succeed.

### Best Practices

1. **Set a strong passphrase:**
   ```bash
   export MOSS_KEY_PASSPHRASE="$(openssl rand -base64 32)"
   ```

2. **Protect the keystore:**
   ```bash
   chmod 700 ~/.moss
   ```

3. **Rotate keys periodically** — Use `key_version` to track rotations.

4. **Back up keys securely** — Encrypted backups only.

## Security Audits

MOSS has not yet undergone a formal security audit. If you're interested in sponsoring an audit, please contact us.

## PGP Key

For encrypted communications, use our PGP key:

```
[PGP key to be added]
```
