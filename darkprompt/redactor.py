from __future__ import annotations

import re
from typing import Iterable, Pattern

from .models import ExecutionTrace, Redaction


class RedactionPatternError(ValueError):
    pass


class RegexRedactor:
    def __init__(self, patterns: Iterable[str]):
        self.patterns: list[tuple[str, Pattern[str]]] = []
        for pattern in patterns:
            try:
                self.patterns.append((pattern, re.compile(pattern)))
            except re.error as exc:
                raise RedactionPatternError(f"Invalid redaction pattern {pattern!r}: {exc}") from exc

    def redact(self, trace: ExecutionTrace) -> ExecutionTrace:
        for raw_pattern, regex in self.patterns:
            total = 0
            trace.prompts, prompt_count = self._redact_values(trace.prompts, regex)
            trace.responses, response_count = self._redact_values(trace.responses, regex)
            total += prompt_count + response_count

            if trace.error:
                trace.error.message, error_count = regex.subn("[REDACTED]", trace.error.message)
                total += error_count

            if trace.evaluation:
                trace.evaluation.reason, reason_count = regex.subn(
                    "[REDACTED]", trace.evaluation.reason
                )
                trace.evaluation.evidence, evidence_count = self._redact_values(
                    trace.evaluation.evidence, regex
                )
                total += reason_count + evidence_count

            if total:
                trace.redactions.append(Redaction(pattern=raw_pattern, match_count=total))

        return trace

    @staticmethod
    def _redact_values(values: list[str], regex: Pattern[str]) -> tuple[list[str], int]:
        redacted: list[str] = []
        total = 0
        for value in values:
            new_value, count = regex.subn("[REDACTED]", value)
            redacted.append(new_value)
            total += count
        return redacted, total
