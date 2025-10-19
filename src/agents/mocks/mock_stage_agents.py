"""Mock stage agents for Phase 2 testing.

Provides mock implementations of Stage1Agent through Stage5Agent
for testing orchestrator stage progression and context passing.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MockStageResponse:
    """Response from a mock stage agent."""

    stage_number: int
    output: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    context_received: Optional[Dict[str, Any]] = None


class MockStageAgent:
    """Base mock stage agent for testing."""

    def __init__(self, stage_number: int, session_id: str):
        """Initialize mock stage agent.

        Args:
            stage_number: Stage number (1-5)
            session_id: Session ID for context
        """
        self.stage_number = stage_number
        self.session_id = session_id
        self.execution_count = 0
        self.last_response: Optional[MockStageResponse] = None

    async def run_stage(
        self, context: Optional[Dict[str, Any]] = None
    ) -> MockStageResponse:
        """Run mock stage with optional context.

        Args:
            context: Context from previous stages

        Returns:
            MockStageResponse with stage output
        """
        self.execution_count += 1

        # Generate mock output based on stage
        output = self._generate_stage_output()

        response = MockStageResponse(
            stage_number=self.stage_number,
            output=output,
            context_received=context,
        )

        self.last_response = response
        return response

    def _generate_stage_output(self) -> Dict[str, Any]:
        """Generate mock output for this stage."""
        if self.stage_number == 1:
            return {
                "problem_statement": "Mock problem statement",
                "business_context": "Mock business context",
                "success_criteria": ["Criterion 1", "Criterion 2"],
            }
        elif self.stage_number == 2:
            return {
                "scope_definition": "Mock scope",
                "constraints": ["Constraint 1", "Constraint 2"],
                "assumptions": ["Assumption 1"],
            }
        elif self.stage_number == 3:
            return {
                "technical_approach": "Mock technical approach",
                "architecture": "Mock architecture",
                "technology_stack": ["Tech 1", "Tech 2"],
            }
        elif self.stage_number == 4:
            return {
                "resource_plan": "Mock resource plan",
                "timeline": "Mock timeline",
                "budget_estimate": 100000,
            }
        elif self.stage_number == 5:
            return {
                "risk_assessment": "Mock risk assessment",
                "mitigation_strategies": ["Strategy 1", "Strategy 2"],
                "success_metrics": ["Metric 1", "Metric 2"],
            }
        else:
            return {"error": f"Unknown stage: {self.stage_number}"}

    async def validate_stage(self) -> bool:
        """Validate stage completion."""
        return self.last_response is not None

    def get_execution_history(self) -> int:
        """Get number of times this stage was executed."""
        return self.execution_count


class MockStage1Agent(MockStageAgent):
    """Mock Stage 1 agent - Problem Statement."""

    def __init__(self, session_id: str):
        super().__init__(1, session_id)


class MockStage2Agent(MockStageAgent):
    """Mock Stage 2 agent - Scope Definition."""

    def __init__(self, session_id: str):
        super().__init__(2, session_id)


class MockStage3Agent(MockStageAgent):
    """Mock Stage 3 agent - Technical Approach."""

    def __init__(self, session_id: str):
        super().__init__(3, session_id)


class MockStage4Agent(MockStageAgent):
    """Mock Stage 4 agent - Resource Planning."""

    def __init__(self, session_id: str):
        super().__init__(4, session_id)


class MockStage5Agent(MockStageAgent):
    """Mock Stage 5 agent - Risk Assessment."""

    def __init__(self, session_id: str):
        super().__init__(5, session_id)


def create_mock_stage_agent(stage_number: int, session_id: str) -> MockStageAgent:
    """Factory function to create mock stage agents.

    Args:
        stage_number: Stage number (1-5)
        session_id: Session ID

    Returns:
        Appropriate mock stage agent

    Raises:
        ValueError: If stage_number is not 1-5
    """
    if stage_number == 1:
        return MockStage1Agent(session_id)
    elif stage_number == 2:
        return MockStage2Agent(session_id)
    elif stage_number == 3:
        return MockStage3Agent(session_id)
    elif stage_number == 4:
        return MockStage4Agent(session_id)
    elif stage_number == 5:
        return MockStage5Agent(session_id)
    else:
        raise ValueError(f"Invalid stage number: {stage_number}")

