"""Mock input handler for Phase 2 testing.

Provides mock implementations of user input handling
for testing orchestrator without interactive prompts.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MockUserResponse:
    """A mock user response."""

    question: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    stage_number: Optional[int] = None


class MockInputHandler:
    """Mock input handler for testing."""

    def __init__(self):
        """Initialize mock input handler."""
        self.responses: Dict[str, str] = {}
        self.response_history: List[MockUserResponse] = []
        self.question_count = 0

    def set_response(self, question_key: str, response: str) -> None:
        """Set a predefined response for a question.

        Args:
            question_key: Key to identify the question
            response: Response to return
        """
        self.responses[question_key] = response

    def set_responses(self, responses: Dict[str, str]) -> None:
        """Set multiple predefined responses.

        Args:
            responses: Dictionary of question_key -> response
        """
        self.responses.update(responses)

    async def ask_user_question(
        self, question: str, stage_number: Optional[int] = None
    ) -> str:
        """Ask user a question and return mock response.

        Args:
            question: Question to ask
            stage_number: Current stage number

        Returns:
            Mock response
        """
        self.question_count += 1

        # Try to find a matching response
        response = self._find_response(question)

        # Record the interaction
        mock_response = MockUserResponse(
            question=question, response=response, stage_number=stage_number
        )
        self.response_history.append(mock_response)

        return response

    def _find_response(self, question: str) -> str:
        """Find a response for the given question.

        Args:
            question: Question to find response for

        Returns:
            Response or default response
        """
        # Try exact match first
        if question in self.responses:
            return self.responses[question]

        # Try partial match
        for key, response in self.responses.items():
            if key.lower() in question.lower():
                return response

        # Return default response
        return f"Mock response to: {question[:50]}..."

    def get_question_history(self) -> List[MockUserResponse]:
        """Get history of all questions asked.

        Returns:
            List of MockUserResponse objects
        """
        return self.response_history.copy()

    def get_question_count(self) -> int:
        """Get total number of questions asked.

        Returns:
            Number of questions
        """
        return self.question_count

    def clear_history(self) -> None:
        """Clear question history."""
        self.response_history.clear()
        self.question_count = 0

    def get_responses_for_stage(self, stage_number: int) -> List[MockUserResponse]:
        """Get all responses for a specific stage.

        Args:
            stage_number: Stage number

        Returns:
            List of responses for that stage
        """
        return [
            r for r in self.response_history if r.stage_number == stage_number
        ]


# Global mock input handler instance
_mock_input_handler: Optional[MockInputHandler] = None


def get_mock_input_handler() -> MockInputHandler:
    """Get or create global mock input handler.

    Returns:
        MockInputHandler instance
    """
    global _mock_input_handler
    if _mock_input_handler is None:
        _mock_input_handler = MockInputHandler()
    return _mock_input_handler


def reset_mock_input_handler() -> None:
    """Reset global mock input handler."""
    global _mock_input_handler
    _mock_input_handler = None


def create_mock_input_handler() -> MockInputHandler:
    """Create a new mock input handler instance.

    Returns:
        New MockInputHandler instance
    """
    return MockInputHandler()


# Predefined response sets for common scenarios

STAGE1_RESPONSES = {
    "problem": "We need to build an AI system to automate customer support",
    "business_context": "Our support team is overwhelmed with tickets",
    "success_criteria": "Reduce response time by 50% and improve satisfaction",
}

STAGE2_RESPONSES = {
    "scope": "Build a chatbot for tier-1 support tickets",
    "constraints": "Must integrate with existing ticketing system",
    "assumptions": "We have 6 months and a team of 3 engineers",
}

STAGE3_RESPONSES = {
    "approach": "Use LLM with RAG for knowledge base integration",
    "architecture": "Microservices with API gateway",
    "technology": "Python, FastAPI, PostgreSQL, OpenAI API",
}

STAGE4_RESPONSES = {
    "resources": "3 engineers, 1 PM, 1 QA",
    "timeline": "6 months with 2-week sprints",
    "budget": "500000",
}

STAGE5_RESPONSES = {
    "risks": "API rate limits, data privacy concerns",
    "mitigation": "Implement caching, ensure GDPR compliance",
    "metrics": "Response time, accuracy, user satisfaction",
}

