# Contributing

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,media]'
```

## Required checks

Run these before opening a pull request:

```bash
ruff check .
pytest --cov=darkprompt --cov-report=term-missing
python -m build
```

The test suite must remain offline by default. Mock provider APIs rather than requiring live credentials.

## Design requirements

- Provider failures must use structured trace errors, not synthetic model responses.
- Multi-turn adapters must preserve prior user and assistant messages.
- New mutations must support deterministic execution when a seed is supplied.
- Unsupported capabilities must fail explicitly instead of silently degrading.
- Reports must distinguish findings, provider errors, skipped cases, and inconclusive evaluations.
- Test pack IDs must remain unique and validated.

## Pull requests

Include:

- The problem being fixed.
- Expected and actual behavior.
- Tests covering the change.
- Any provider-specific assumptions.
- Security and compatibility impact.

Do not include API keys, private prompts, customer data, or unsanitized provider responses.

## Security issues

Do not disclose vulnerabilities in public issues. Follow [SECURITY.md](SECURITY.md).
