# MOSS Protocol Specification

**Spec ID:** `moss-0001`  
**Version:** 1  
**Status:** Draft  
**Author:** Carey D'Souza  
**Last Updated:** 2024-12-06

## Abstract

MOSS (Machine to Machine Operation Security System) is a cryptographic signing protocol for AI agent outputs. It provides identity, integrity, and replay protection using post-quantum cryptography.

## 1. Overview

MOSS enables any AI agent to:
1. Establish a cryptographic identity (subject)
2. Sign outputs with that identity
3. Allow verifiers to confirm authenticity

## 2. Subject Format

A subject is a unique identifier for an agent.

### 2.1 Format

```
moss:{namespace}:{name}
```

### 2.2 Constraints

- **Prefix:** Must start with `moss:`
- **Namespace:** Lowercase alphanumeric, hyphens, underscores (`[a-z0-9_-]+`)
- **Name:** Lowercase alphanumeric, hyphens, underscores (`[a-z0-9_-]+`)

### 2.3 Examples

```
moss:dev:my-agent
moss:acme:order-bot
moss:lab:researcher-v2
```

### 2.4 Regex

```
^moss:[a-z0-9_-]+:[a-z0-9_-]+$
```

## 3. Cryptographic Algorithms

### 3.1 Signature Algorithm

- **Algorithm:** ML-DSA-44 (FIPS 204, formerly Dilithium2)
- **Public key size:** 1312 bytes
- **Signature size:** 2420 bytes

### 3.2 Hash Algorithm

- **Algorithm:** SHA-256
- **Output:** 32 bytes

### 3.3 Encoding

- **Binary data:** base64url without padding (RFC 4648 §5)
- **JSON:** RFC 8785 JSON Canonicalization Scheme (JCS)

## 4. Envelope Format

The envelope is the signed output.

### 4.1 Fields

| Field | Type | Description |
|-------|------|-------------|
| `spec` | string | Specification identifier. MUST be `"moss-0001"` |
| `version` | integer | Spec version. MUST be `1` |
| `alg` | string | Signature algorithm. MUST be `"ML-DSA-44"` |
| `subject` | string | Agent identifier |
| `key_version` | integer | Version of the signing key (starts at 1) |
| `seq` | integer | Sequence number (monotonically increasing) |
| `issued_at` | integer | Unix timestamp (seconds) when signed |
| `payload_hash` | string | base64url(SHA-256(canonical(payload))) |
| `signature` | string | base64url(ML-DSA-44 signature) |

### 4.2 Example

```json
{
  "spec": "moss-0001",
  "version": 1,
  "alg": "ML-DSA-44",
  "subject": "moss:acme:order-bot",
  "key_version": 1,
  "seq": 42,
  "issued_at": 1733200000,
  "payload_hash": "eji_gfOD9pQzrW6QDTWz4jhVk_dqe3q11DVbi6Qe4ks",
  "signature": "..."
}
```

## 5. Signing Procedure

### 5.1 Input

- `payload`: The data to sign (any JSON-serializable value)
- `subject`: The agent's subject identifier
- `secret_key`: The agent's ML-DSA-44 secret key
- `key_version`: Current key version
- `seq`: Next sequence number

### 5.2 Procedure

1. **Canonicalize payload:**
   ```
   payload_canonical = JCS(payload)
   ```

2. **Hash payload:**
   ```
   payload_hash = base64url(SHA-256(payload_canonical))
   ```

3. **Build signed_bytes object:**
   ```json
   {
     "alg": "ML-DSA-44",
     "issued_at": <current_unix_timestamp>,
     "key_version": <key_version>,
     "payload_hash": "<payload_hash>",
     "seq": <seq>,
     "spec": "moss-0001",
     "subject": "<subject>",
     "version": 1
   }
   ```
   **Note:** Keys MUST be sorted lexicographically (per RFC 8785).

4. **Canonicalize signed_bytes:**
   ```
   signed_bytes = JCS(signed_bytes_object)
   ```

5. **Sign:**
   ```
   signature = ML-DSA-44.sign(secret_key, signed_bytes)
   ```

6. **Encode signature:**
   ```
   signature_b64 = base64url(signature)
   ```

7. **Build envelope** with all fields.

## 6. Verification Procedure

### 6.1 Input

- `envelope`: The envelope to verify
- `payload`: The original payload (optional)
- `public_key`: The signer's public key

### 6.2 Procedure

1. **Check spec:**
   ```
   REQUIRE envelope.spec == "moss-0001"
   REQUIRE envelope.version == 1
   REQUIRE envelope.alg == "ML-DSA-44"
   ```

2. **Verify payload hash (if payload provided):**
   ```
   computed_hash = base64url(SHA-256(JCS(payload)))
   REQUIRE computed_hash == envelope.payload_hash
   ```

3. **Check replay (if enabled):**
   ```
   last_seen = get_last_seq(envelope.subject, envelope.key_version)
   REQUIRE envelope.seq > last_seen
   update_last_seq(envelope.subject, envelope.key_version, envelope.seq)
   ```

4. **Reconstruct signed_bytes:**
   ```json
   {
     "alg": envelope.alg,
     "issued_at": envelope.issued_at,
     "key_version": envelope.key_version,
     "payload_hash": envelope.payload_hash,
     "seq": envelope.seq,
     "spec": envelope.spec,
     "subject": envelope.subject,
     "version": envelope.version
   }
   ```

5. **Canonicalize:**
   ```
   signed_bytes = JCS(signed_bytes_object)
   ```

6. **Decode signature:**
   ```
   signature = base64url_decode(envelope.signature)
   ```

7. **Verify:**
   ```
   REQUIRE ML-DSA-44.verify(public_key, signed_bytes, signature)
   ```

## 7. Key Management

### 7.1 Key Generation

Generate ML-DSA-44 keypair:
- Public key: 1312 bytes
- Secret key: 2560 bytes (implementation-dependent)

### 7.2 Key Storage

Keys SHOULD be stored encrypted at rest using:
- **KDF:** Scrypt (N=2^14, r=8, p=1)
- **Encryption:** AES-256-GCM
- **Location:** `~/.moss/keys/{namespace}/{name}.json`

### 7.3 Key Rotation

When rotating keys:
1. Increment `key_version`
2. Reset `seq` to 1
3. Old envelopes remain verifiable with old public key

### 7.4 Key Revocation

Revocation marks a key_version as invalid after a certain time. Verification MUST fail for envelopes with `issued_at` after revocation time.

## 8. Replay Protection

### 8.1 Sequence Numbers

- `seq` MUST be monotonically increasing per (subject, key_version)
- Verifiers MUST track last seen `seq` per (subject, key_version)
- Verification MUST fail if `seq <= last_seen_seq`

### 8.2 Verifier State

Verifiers maintain:
```
{subject}_{key_version} -> last_seen_seq
```

## 9. Canonicalization (RFC 8785)

JSON Canonicalization Scheme requirements:
- Object keys sorted lexicographically by UTF-16 code units
- No whitespace between tokens
- UTF-8 encoding
- No trailing commas
- Numbers: no leading zeros, no unnecessary decimal points

### 9.1 Example

Input:
```json
{"b": 2, "a": 1, "nested": {"y": "z", "x": "y"}}
```

Canonical output:
```json
{"a":1,"b":2,"nested":{"x":"y","y":"z"}}
```

## 10. Error Codes

| Code | Name | Description |
|------|------|-------------|
| MOSS_ERR_001 | InvalidSubject | Subject format is invalid |
| MOSS_ERR_002 | KeyNotFound | No key found for subject |
| MOSS_ERR_003 | InvalidEnvelope | Envelope is malformed |
| MOSS_ERR_004 | InvalidSignature | Signature verification failed |
| MOSS_ERR_005 | PayloadMismatch | Payload hash does not match |
| MOSS_ERR_006 | ReplayDetected | Sequence number already seen |
| MOSS_ERR_007 | DecryptionFailed | Key decryption failed |

## 11. Security Considerations

### 11.1 Post-Quantum Security

ML-DSA-44 is believed to be secure against quantum computers. Signatures created today will remain verifiable after quantum computers exist.

### 11.2 Key Protection

Secret keys MUST be encrypted at rest. The default passphrase is for development only. Production deployments MUST use a strong passphrase via `MOSS_KEY_PASSPHRASE`.

### 11.3 Replay Attacks

Verifiers MUST implement sequence tracking to prevent replay attacks. The `check_replay` parameter allows disabling this for idempotent operations.

### 11.4 Clock Skew

This specification does not enforce `issued_at` bounds. Implementations MAY reject envelopes with timestamps too far in the past or future.

## 12. Conformance

### 12.1 Requirements

Conforming implementations MUST:
- Support all fields in the envelope format
- Use ML-DSA-44 for signatures
- Use SHA-256 for hashing
- Use RFC 8785 for canonicalization
- Use base64url without padding for encoding
- Validate subject format

### 12.2 Test Vectors

See `conformance/vectors.json` for test vectors.

## Appendix A: Base64url Encoding

```
base64url(data) = base64(data)
                  .replace('+', '-')
                  .replace('/', '_')
                  .rstrip('=')
```

## Appendix B: References

- [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) — ML-DSA (Dilithium)
- [RFC 8785](https://tools.ietf.org/html/rfc8785) — JSON Canonicalization Scheme
- [RFC 4648](https://tools.ietf.org/html/rfc4648) — Base64 Encoding
