import httpx
import json
from ..adapter import TargetAdapter
from ..models import TestCase, ExecutionTrace

class OllamaAdapter(TargetAdapter):
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate" # Using /api/generate for simplicity in v0.1

    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        payload = {
            "model": self.model,
            "prompt": test_case.prompt,
            "stream": False,
            "options": test_case.parameters
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.base_url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                response_text = data.get("response", "")
                
                trace = ExecutionTrace(
                    test_case_id=test_case.id,
                    prompts=[test_case.prompt],
                    responses=[response_text],
                    metadata={"model": self.model, "total_duration": data.get("total_duration")}
                )
                return trace
        except Exception as e:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=[f"[ERROR] Ollama request failed: {str(e)}"],
                metadata={"error": True}
            )
