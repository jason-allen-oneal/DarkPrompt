import os
import httpx
from ..adapter import TargetAdapter
from ..models import TestCase, ExecutionTrace

class GeminiAdapter(TargetAdapter):
    """v0.2.2: Adapter for Google Gemini API."""
    def __init__(self, model: str = "gemini-1.5-flash", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        if not self.api_key:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=["[ERROR] Gemini API key missing."],
                metadata={"error": True}
            )

        payload = {
            "contents": [{
                "parts": [{"text": test_case.prompt}]
            }],
            "generationConfig": test_case.parameters
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract text from Gemini response structure
                response_text = data['candidates'][0]['content']['parts'][0]['text']
                
                return ExecutionTrace(
                    test_case_id=test_case.id,
                    prompts=[test_case.prompt],
                    responses=[response_text],
                    metadata={"model": self.model}
                )
        except Exception as e:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=[f"[ERROR] Gemini request failed: {str(e)}"],
                metadata={"error": True}
            )
