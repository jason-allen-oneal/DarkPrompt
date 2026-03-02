# Contributing

## Development

### Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
```

### Pre-push checks

Before pushing, run:

```bash
pytest
```

## Issues

- Include the exact command, expected vs actual behavior, and relevant logs.
- Do not include secrets.

## Security issues

See `SECURITY.md`.
