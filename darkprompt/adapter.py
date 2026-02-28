from abc import ABC, abstractmethod
from .models import TestCase, ExecutionTrace

class TargetAdapter(ABC):
    @abstractmethod
    def execute(self, test_case: TestCase, context: dict) -> ExecutionTrace:
        """Execute a single test case and return the trace."""
        pass
