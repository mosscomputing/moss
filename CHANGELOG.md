# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-06

### Added
- Initial release of MOSS SDK
- `Subject.create()` - Create agent identity with ML-DSA-44 keypair
- `Subject.load()` - Load existing identity from keystore
- `Subject.sign()` - Sign payloads and return envelopes
- `Subject.verify()` - Verify envelopes with replay protection
- CLI commands: `moss subject create`, `moss sign`, `moss verify`, `moss diff`
- Encrypted keystore (AES-256-GCM + Scrypt)
- RFC 8785 JSON canonicalization
- Conformance test vectors
- Full `moss-0001` specification

### Security
- Post-quantum signatures (ML-DSA-44 / FIPS 204)
- Keys encrypted at rest
- Replay protection via sequence numbers

[Unreleased]: https://github.com/mosscomputing/moss/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mosscomputing/moss/releases/tag/v0.1.0
