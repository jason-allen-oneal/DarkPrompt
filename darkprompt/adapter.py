from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .models import ExecutionTrace, TestCase, TraceError


@dataclass(frozen=True)
class AdapterCapabilities:
    multi_turn: bool = True
    images: bool = False
    tools: bool = False


class TargetAdapter(ABC):
    capabilities = AdapterCapabilities()

    @staticmethod
    def history(context: Dict[str, Any]) -> List[Dict[str, str]]:
        history = context.get("history", [])
        if not isinstance(history, list):
            return []

        normalized: List[Dict[str, str]] = []
        for item in history:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = item.get("content")
            if role in {"system", "user", "assistant"} and isinstance(content, str):
                normalized.append({"role": role, "content": content})
        return normalized

    @staticmethod
    def error_trace(
        test_case: TestCase,
        *,
        error_type: str,
        message: str,
        retryable: bool = False,
        status_code: Optional[int] = None,
    ) -> ExecutionTrace:
        return ExecutionTrace(
            test_case_id=test_case.id,
            prompts=[test_case.prompt],
            responses=[],
            metadata={"error": True},
            error=TraceError(
                type=error_type,
                message=message,
                retryable=retryable,
                status_code=status_code,
            ),
        )

    @abstractmethod
    def execute(self, test_case: TestCase, context: Dict[str, Any]) -> ExecutionTrace:
        """Execute one test case turn and return a structured trace."""
