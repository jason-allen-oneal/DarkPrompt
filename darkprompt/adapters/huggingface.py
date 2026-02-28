import os
import httpx
from ..adapter import TargetAdapter
from ..models import TestCase, ExecutionTrace

class HuggingFaceAdapter(TargetAdapter):
    """v0.2.1: Adapter for Hugging Face Inference API."""
    def __init__(self, model: str = "meta-llama/Llama-3.2-3B-Instruct", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.url = f"https://api-inference.huggingface.co/models/{model}"

    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        if not self.api_key:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=["[ERROR] Hugging Face API key missing."],
                metadata={"error": True}
            )

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": test_case.prompt,
            "parameters": test_case.parameters
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # HF Inference API returns a list of results
                response_text = data[0].get("generated_text", "") if isinstance(data, list) else str(data)
                
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
                responses=[f"[ERROR] Hugging Face request failed: {str(e)}"],
                metadata={"error": True}
            )
