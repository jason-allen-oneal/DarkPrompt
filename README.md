# DarkPrompt - AI Adversarial Toolkit (AAT) v1.0.1

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.1-green.svg)](https://github.com/jason-allen-oneal/DarkPrompt/releases/tag/v1.0.1)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

**DarkPrompt** is a professional-grade adversarial framework designed for the systematic security auditing of Large Language Models (LLMs). It enables security researchers and engineers to identify vulnerabilities in model alignment, safety filters, and PII protection across any LLM provider.

---

## 🛠 Core Capabilities

### 1. Model-Agnostic Architecture
DarkPrompt is designed to be universal. It supports a wide array of target backends through a unified adapter interface:
*   **Proprietary API**: OpenAI, Anthropic, Google Gemini, Mistral AI.
*   **Local Infrastructure**: Seamless integration with **Ollama** for private, local testing.
*   **Open Source Ecosystem**: Native support for **Hugging Face Inference API**, providing access to thousands of open-source models (Llama, Falcon, Phi, etc.).
*   **Custom Endpoints**: Fully compatible with any OpenAI-style proxy (e.g., GitHub Models, Copilot).

### 2. Adversarial Mutation Engine
Go beyond simple keyword testing. DarkPrompt features an automated mutation engine that transforms raw prompts into advanced adversarial payloads using:
*   **Leetspeak**: Bypasses keyword-based filters (e.g., `jailbreak` -> `j41lbr34k`).
*   **Base64 Wrapping**: Encapsulates instructions within Base64 payloads to test model decoding/execution logic.
*   **Caesar Cipher**: Encrypts instructions to identify blind spots in the model's safety monitoring.
*   **Character Noise**: Injects delimiters (e.g., `H.e.l.p`) to disrupt tokenization-based security layers.
*   **Reverse Text**: Tests the model's ability to un-reverse and follow malicious instructions.
*   **Payload Splitting**: Fragments instructions into separate variables, instructing the model to reconstruct and execute them in-memory.

### 3. Systematic Sensitivity Analysis
Enable the `--sensitivity` flag to perform a exhaustive audit. DarkPrompt will take every test case in your pack and run it against **all** mutation types in parallel, generating a detailed report on which specific obfuscation techniques cause a model to break.

### 4. Stateful Multi-turn Runner
Support for complex, multi-turn "Social Engineering" scenarios. Define interaction chains where Turn 1 establishes a persona (e.g., a simulation or roleplay) and Turn 2+ executes the actual adversarial attempt.

### 5. ExploitRank Intelligence Bridge
Direct integration with the **Exploit Intelligence Engine (EIE)**. DarkPrompt can pull real-world CVE data, descriptions, and code snippets from **ExploitRank** to generate high-fidelity, targeted adversarial scenarios based on actual vulnerabilities.

---

## 📊 Reporting & Auditing

DarkPrompt generates comprehensive **Security Audit Reports** in Markdown and JSON formats, featuring:
*   **Risk Exposure Heatmap**: An at-a-glance visualization of model susceptibility categorized by attack type and mutation.
*   **Resistance Scoring**: Automated scoring based on the model's refusal success rate.
*   **PII Redaction**: Built-in regex redactor to ensure sensitive data (API keys, emails, internal domains) is scrubbed from generated reports.

---

## 🚀 Installation

### Prerequisites
*   Python 3.9+
*   Git

### Setup
```bash
git clone https://github.com/jason-allen-oneal/DarkPrompt.git
cd DarkPrompt
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## 📖 Usage Examples

### Standard Security Audit
Run a baseline test pack against a local Mistral model:
```bash
darkprompt run --pack ./sample_pack --target ollama --model mistral
```

### Systematic Sensitivity Analysis
Identify exactly which obfuscation types a model is weakest against:
```bash
darkprompt run --pack ./sample_pack --target anthropic --model claude-3-5-sonnet --sensitivity
```

### Real-World Exploit Audit
Pull latest CVE data from ExploitRank and audit a model's response to real-world threats:
```bash
darkprompt run --target openai --model gpt-4 --exploit-rank --redact "internal_domain\.local"
```

---

## 🛤 Roadmap
- [ ] Automated prompt mutation refinement via LLM-as-a-judge.
- [ ] Advanced multi-turn interaction branching logic.
- [ ] Integration with ZeroSignal Network orchestration for large-scale distributed auditing.

---

## ⚖️ License
Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

*“Security is not a product, but a process.”* – DarkPrompt is built to facilitate that process in the age of LLMs.
