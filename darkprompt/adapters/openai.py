import os
from openai import OpenAI
from ..adapter import TargetAdapter
from ..models import TestCase, ExecutionTrace, ToolCall

class OpenAIAdapter(TargetAdapter):
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None):
        self.model = model
        # Use provided key or fallback to env
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            # We don't raise here to allow initialization, but execute will fail if still missing
            pass
        self.client = OpenAI(api_key=api_key)

    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        if not self.client.api_key:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=["[ERROR] OpenAI API key missing. Set OPENAI_API_KEY environment variable."],
                metadata={"error": True}
            )

        try:
            # v0.1 supports basic chat completion with parameters from test_case
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": test_case.prompt}],
                **test_case.parameters
            )
            
            response_text = response.choices[0].message.content
            
            trace = ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=[response_text],
                metadata={
                    "model": self.model, 
                    "usage": response.usage.model_dump() if hasattr(response, 'usage') else {}
                }
            )
            
            # Extract tool calls if present
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    trace.tool_calls.append(ToolCall(
                        name=tc.function.name,
                        arguments=tc.function.arguments
                    ))
                    
            return trace
        except Exception as e:
            return ExecutionTrace(
                test_case_id=test_case.id,
                prompts=[test_case.prompt],
                responses=[f"[ERROR] OpenAI request failed: {str(e)}"],
                metadata={"error": True}
            )
