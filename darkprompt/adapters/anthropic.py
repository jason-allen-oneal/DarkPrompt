import os
import httpx
from ..adapter import TargetAdapter
from ..models import TestCase, ExecutionTrace

class AnthropicAdapter(TargetAdapter):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.url = "https://api.anthropic.com/v1/messages"

    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        if not self.api_key:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=["[ERROR] Anthropic API key missing."],
                metadata={"error": True}
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": test_case.prompt}],
            **test_case.parameters
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                response_text = data["content"][0]["text"]
                
                return ExecutionTrace(
                    test_case_id=test_case.id,
                    prompts=[test_case.prompt],
                    responses=[response_text],
                    metadata={"model": self.model, "usage": data.get("usage", {})}
                )
        except Exception as e:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=[f"[ERROR] Anthropic request failed: {str(e)}"],
                metadata={"error": True}
            )
