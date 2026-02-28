import yaml
import copy
from pathlib import Path
from typing import List
from .models import TestCase, TestPack, ExecutionTrace
from .adapter import TargetAdapter
from .redactor import RegexRedactor

class Runner:
    def __init__(self, adapter: TargetAdapter, redactor: RegexRedactor = None):
        self.adapter = adapter
        self.redactor = redactor

    def load_pack(self, pack_dir: Path) -> TestPack:
        pack_yaml = pack_dir / "pack.yaml"
        with open(pack_yaml, "r") as f:
            pack_data = yaml.safe_load(f)
        
        pack = TestPack(**pack_data)
        
        cases_dir = pack_dir / "cases"
        if cases_dir.exists():
            for case_file in sorted(cases_dir.glob("*.yaml")):
                with open(case_file, "r") as f:
                    case_data = yaml.safe_load(f)
                    if isinstance(case_data, list):
                        for c in case_data:
                            pack.cases.append(TestCase(**c))
                    else:
                        pack.cases.append(TestCase(**case_data))
        
        return pack

    def run_case(self, case: TestCase) -> ExecutionTrace:
        """Executes a single test case, supporting multi-turn chains."""
        context = {"history": []}
        trace = ExecutionTrace(test_case_id=case.id, prompts=[], responses=[])
        
        # Turn 1: Primary prompt
        current_case = copy.deepcopy(case)
        t_trace = self.adapter.execute(current_case, context)
        
        trace.prompts.append(current_case.prompt)
        trace.responses.append(t_trace.responses[0])
        trace.metadata.update(t_trace.metadata)
        
        # Update history for stateful adapters (if implemented)
        context["history"].append({"role": "user", "content": current_case.prompt})
        context["history"].append({"role": "assistant", "content": t_trace.responses[0]})

        # Turns 2-N: Follow-up chain
        for follow_up in case.chain:
            follow_up_case = copy.deepcopy(case)
            follow_up_case.prompt = follow_up
            
            # Note: v0.3.0 assumes adapter can handle context/history in metadata or state
            f_trace = self.adapter.execute(follow_up_case, context)
            
            trace.prompts.append(follow_up)
            trace.responses.append(f_trace.responses[0])
            
            context["history"].append({"role": "user", "content": follow_up})
            context["history"].append({"role": "assistant", "content": f_trace.responses[0]})

        if self.redactor:
            trace = self.redactor.redact(trace)
            
        return trace

    def run(self, pack: TestPack) -> List[ExecutionTrace]:
        traces = []
        for case in pack.cases:
            traces.append(self.run_case(case))
        return traces
