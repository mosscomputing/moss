# Contributing to MOSS

Thank you for your interest in contributing to MOSS!

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/mosscomputing/moss/issues)
2. If not, create a new issue using the Bug Report template
3. Include reproduction steps, expected behavior, and environment details

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue using the Feature Request template
3. Explain the problem and proposed solution

### Proposing Spec Changes

Protocol changes require careful consideration. Use the Spec Change Proposal template and expect thorough review.

**Spec changes must:**
- Maintain backward compatibility (or provide migration path)
- Include test vectors
- Address security implications
- Be approved by maintainers

## Development Setup

```bash
# Clone the repo
git clone https://github.com/mosscomputing/moss.git
cd moss

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests** and ensure they pass:
   ```bash
   pytest tests/ -v
   ruff check moss/ tests/
   ```
5. **Commit** with a clear message:
   ```bash
   git commit -m "Add: description of change"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** against `main`

### Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `Add:` New feature
- `Fix:` Bug fix
- `Docs:` Documentation
- `Test:` Test changes
- `Refactor:` Code refactoring
- `Spec:` Specification changes

### Code Style

- Use [ruff](https://github.com/astral-sh/ruff) for linting
- Follow PEP 8
- Add type hints where practical
- Document public APIs with docstrings

### Tests

- All changes must include tests
- Tests must pass in CI
- Conformance tests must not be broken
- Aim for clear, readable test code

## Areas for Contribution

### Good First Issues

Look for issues labeled `good first issue` — these are suitable for newcomers.

### Documentation

- Improve README and guides
- Add code examples
- Translate documentation

### Framework Integrations

Help build integrations for:
- CrewAI (`moss-crewai`)
- AutoGen (`moss-autogen`)
- LangGraph (`moss-langgraph`)
- LangChain (`moss-langchain`)

### Language SDKs

Help port MOSS to other languages:
- TypeScript/JavaScript
- Go
- Rust

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

## Questions?

- Open a [Discussion](https://github.com/mosscomputing/moss/discussions)
- Join our [Discord](https://discord.gg/mosscomputing)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
