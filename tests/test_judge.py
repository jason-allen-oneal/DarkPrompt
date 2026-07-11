from __future__ import annotations

import pytest

from darkprompt.adapter import TargetAdapter
from darkprompt.judge import JudgeFeedbackLoop
from darkprompt.models import EvaluationStatus, ExecutionTrace, TestCase as DarkTestCase


class SequenceAdapter(TargetAdapter):
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    def execute(self, test_case, context):
        self.calls += 1
        response = next(self.responses)
        return ExecutionTrace(
            test_case_id=test_case.id,
            prompts=[test_case.prompt],
            responses=[response],
        )


def make_case():
    return DarkTestCase(
        id="A",
        name="A",
        category="Injection",
        prompt="original prompt",
        expected_outcome="The model should refuse the request.",
    )


def test_adaptive_retries_until_compliance_is_found():
    adapter = SequenceAdapter(
        ["I cannot help with that.", "Here is the requested content."]
    )
    trace = JudgeFeedbackLoop(adapter).run_adaptive_case(make_case(), max_retries=2)

    assert adapter.calls == 2
    assert trace.metadata["retries"] == 1
    assert trace.metadata["attempts"][0]["status"] == "pass"
    assert trace.metadata["attempts"][1]["status"] == "fail"
    assert trace.evaluation.status == EvaluationStatus.FAIL


def test_adaptive_stays_pass_when_all_attempts_refuse():
    adapter = SequenceAdapter(
        [
            "I cannot help with that.",
            "I will not provide that.",
            "I am unable to assist.",
        ]
    )
    trace = JudgeFeedbackLoop(adapter).run_adaptive_case(make_case(), max_retries=2)

    assert adapter.calls == 3
    assert trace.metadata["retries"] == 2
    assert trace.evaluation.status == EvaluationStatus.PASS


def test_adaptive_rejects_negative_retry_count():
    with pytest.raises(ValueError):
        JudgeFeedbackLoop(SequenceAdapter([])).run_adaptive_case(
            make_case(), max_retries=-1
        )
