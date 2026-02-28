import os
import httpx
from ..adapter import TargetAdapter
from ..models import TestCase, ExecutionTrace

class MistralAdapter(TargetAdapter):
    """v0.2.2: Adapter for Mistral AI API."""
    def __init__(self, model: str = "mistral-large-latest", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.url = "https://api.mistral.ai/v1/chat/completions"

    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        if not self.api_key:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=["[ERROR] Mistral API key missing."],
                metadata={"error": True}
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": test_case.prompt}],
            **test_case.parameters
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                response_text = data["choices"][0]["message"]["content"]
                
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
                responses=[f"[ERROR] Mistral request failed: {str(e)}"],
                metadata={"error": True}
            )
