import re
from typing import List
from .models import ExecutionTrace, Redaction

class RegexRedactor:
    def __init__(self, patterns: List[str]):
        self.patterns = patterns

    def redact(self, trace: ExecutionTrace) -> ExecutionTrace:
        for pattern in self.patterns:
            regex = re.compile(pattern)
            
            # Redact prompts
            new_prompts = []
            for p in trace.prompts:
                new_p, count = regex.subn("[REDACTED]", p)
                new_prompts.append(new_p)
                if count > 0:
                    trace.redactions.append(Redaction(pattern=pattern, match_count=count))
            trace.prompts = new_prompts
            
            # Redact responses
            new_responses = []
            for r in trace.responses:
                new_r, count = regex.subn("[REDACTED]", r)
                new_responses.append(new_r)
                if count > 0:
                    trace.redactions.append(Redaction(pattern=pattern, match_count=count))
            trace.responses = new_responses
            
        return trace
