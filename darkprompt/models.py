from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class EvaluationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    ERROR = "error"
    SKIPPED = "skipped"
    INCONCLUSIVE = "inconclusive"


class Redaction(BaseModel):
    pattern: str
    replacement: str = "[REDACTED]"
    match_count: int = 0


class ToolCall(BaseModel):
    name: str
    arguments: str
    result: Optional[str] = None


class TraceError(BaseModel):
    type: str
    message: str
    retryable: bool = False
    status_code: Optional[int] = None


class EvaluationResult(BaseModel):
    status: EvaluationStatus
    reason: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)


class ConversationMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ExecutionTrace(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    test_case_id: str
    prompts: List[str] = Field(default_factory=list)
    responses: List[str] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    redactions: List[Redaction] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[TraceError] = None
    evaluation: Optional[EvaluationResult] = None


class TestCase(BaseModel):
    id: str
    name: str
    category: str
    prompt: str
    expected_outcome: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    chain: List[str] = Field(default_factory=list)

    @field_validator("id", "name", "category", "prompt")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value


class TestPack(BaseModel):
    name: str
    description: str
    version: str
    cases: List[TestCase] = Field(default_factory=list)
