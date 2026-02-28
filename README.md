# DarkPrompt - AI Adversarial Toolkit (AAT) v1.0.0

A comprehensive AI adversarial toolkit for model-agnostic security auditing, featuring systematic mutation sensitivity analysis, multi-turn stateful attacks, and ExploitRank intelligence integration.

## Features

- **Multi-Model Coverage**: Target any LLM endpoint including **OpenAI, Anthropic, Gemini, Mistral, Ollama**, and **Hugging Face**.
- **Adversarial Mutation Engine**: Automatically obfuscate prompts using 6 distinct transformation types:
    - **Leetspeak** (bypass keyword filters)
    - **Base64 Wrapping** (payload encoding)
    - **Caesar Cipher** (obfuscated execution)
    - **Character Noise** (tokenization disruption)
    - **Reverse Text** (string reversal)
    - **Payload Splitting** (variable-based reconstruction)
- **Systematic Sensitivity Analysis**: Systematic testing of every mutation type to identify a model's exact breaking points.
- **Multi-turn Stateful Runner**: Support for chain-based attacks to test complex, multi-step jailbreak scenarios.
- **ExploitRank Bridge**: Direct integration with the Exploit Intelligence Engine (EIE) to pull real-world CVE data for high-fidelity adversarial payloads.
- **Risk Exposure Heatmap**: Automated reporting with resistance scoring and visual risk assessment tables.

## Installation

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .
```

## Usage

```bash
# Run a baseline security audit with sensitivity analysis
darkprompt run --pack ./sample_pack --target ollama --model mistral --sensitivity

# Run a real-world exploit audit using ExploitRank
darkprompt run --target openai --model gpt-4 --exploit-rank --redact "sk_live"
```

## Roadmap
- Automated prompt mutation/obfuscation refinement
- Advanced multi-turn interaction scenarios
- Integration with ZeroSignal Network orchestration

## License
Apache 2.0
