from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Redaction(BaseModel):
    pattern: str
    replacement: str = "[REDACTED]"
    match_count: int = 0

class ToolCall(BaseModel):
    name: str
    arguments: str
    result: Optional[str] = None

class ExecutionTrace(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    test_case_id: str
    prompts: List[str]
    responses: List[str]
    tool_calls: List[ToolCall] = []
    redactions: List[Redaction] = []
    metadata: Dict[str, Any] = {}

class TestCase(BaseModel):
    id: str
    name: str
    category: str
    prompt: str
    expected_outcome: Optional[str] = None
    parameters: Dict[str, Any] = {}
    chain: List[str] = [] # For multi-turn support

class TestPack(BaseModel):
    name: str
    description: str
    version: str
    cases: List[TestCase] = []
