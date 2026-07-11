# Changelog

All notable changes to DarkPrompt are documented here.

## 1.1.0

### Added

- Structured PASS, FAIL, PARTIAL, ERROR, SKIPPED, and INCONCLUSIVE evaluation statuses.
- Structured provider errors that no longer count as model responses.
- Real multi-turn history propagation across built-in chat adapters.
- Actual image payload construction for OpenAI, Anthropic, Gemini, Mistral, and Ollama.
- Deterministic mutation seeds and named mutation metadata.
- Concurrent sensitivity execution with a configurable worker limit.
- `validate-pack`, `list-providers`, `--fail-on-findings`, and configurable ExploitRank database options.
- Python 3.9, 3.11, and 3.13 CI coverage, package builds, static checks, and coverage enforcement.

### Changed

- Replaced refusal-count reporting with explicit per-trace evaluation results.
- Switched Ollama to the chat endpoint so conversation history is preserved.
- Made Hugging Face use its OpenAI-compatible chat router.
- Made package version metadata derive from `darkprompt.__version__`.
- Improved pack validation, redaction validation, Markdown escaping, and JSON report metadata.

### Fixed

- Multi-turn cases no longer send isolated prompts.
- OCR mutations are no longer passed to capable providers as plain path markers.
- Empty reports no longer divide by zero.
- Missing credentials and HTTP failures no longer appear as exposed-model findings.
- ExploitRank no longer depends on a developer-specific absolute filesystem path.
