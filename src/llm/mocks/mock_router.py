"""Mock LLM router for Phase 2 testing.

Provides mock implementations of LLM routing
for testing without actual LLM calls.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MockLLMRequest:
    """A mock LLM request."""

    prompt: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockLLMResponse:
    """A mock LLM response."""

    content: str
    model: str
    tokens_used: int = 100
    timestamp: datetime = field(default_factory=datetime.now)


class MockLLMRouter:
    """Mock LLM router for testing."""

    def __init__(self):
        """Initialize mock LLM router."""
        self.request_history: List[MockLLMRequest] = []
        self.response_templates: Dict[str, str] = {}
        self.default_model = "mock-gpt-4"

    def set_response_template(self, key: str, response: str) -> None:
        """Set a response template for a specific key.

        Args:
            key: Key to identify the response
            response: Response template (can be JSON string)
        """
        self.response_templates[key] = response

    def set_response_templates(self, templates: Dict[str, str]) -> None:
        """Set multiple response templates.

        Args:
            templates: Dictionary of key -> response
        """
        self.response_templates.update(templates)

    async def route_request(
        self, prompt: str, model: Optional[str] = None, **kwargs: Any
    ) -> MockLLMResponse:
        """Route a request to mock LLM.

        Args:
            prompt: Prompt to send
            model: Model to use (optional)
            **kwargs: Additional parameters

        Returns:
            MockLLMResponse
        """
        model = model or self.default_model

        # Record request
        request = MockLLMRequest(
            prompt=prompt, model=model, parameters=kwargs
        )
        self.request_history.append(request)

        # Find matching response
        response_content = self._find_response(prompt)

        return MockLLMResponse(
            content=response_content,
            model=model,
            tokens_used=len(prompt.split()) + len(response_content.split()),
        )

    def _find_response(self, prompt: str) -> str:
        """Find a response for the given prompt.

        Args:
            prompt: Prompt to find response for

        Returns:
            Response content
        """
        # Try exact match first
        if prompt in self.response_templates:
            return self.response_templates[prompt]

        # Try partial match
        for key, response in self.response_templates.items():
            if key.lower() in prompt.lower():
                return response

        # Return default response
        return self._generate_default_response(prompt)

    def _generate_default_response(self, prompt: str) -> str:
        """Generate a default response for a prompt.

        Args:
            prompt: Prompt to respond to

        Returns:
            Default response
        """
        if "quality" in prompt.lower():
            return json.dumps({
                "is_acceptable": True,
                "quality_score": 0.85,
                "feedback": "Response meets quality standards"
            })
        elif "validation" in prompt.lower():
            return json.dumps({
                "can_proceed": True,
                "validation_issues": [],
                "missing_fields": []
            })
        elif "consistency" in prompt.lower():
            return json.dumps({
                "is_consistent": True,
                "contradictions": [],
                "recommendations": []
            })
        else:
            return "Mock response to prompt"

    def get_request_history(self) -> List[MockLLMRequest]:
        """Get history of all requests.

        Returns:
            List of MockLLMRequest objects
        """
        return self.request_history.copy()

    def get_request_count(self) -> int:
        """Get total number of requests.

        Returns:
            Number of requests
        """
        return len(self.request_history)

    def clear_history(self) -> None:
        """Clear request history."""
        self.request_history.clear()

    def get_requests_for_model(self, model: str) -> List[MockLLMRequest]:
        """Get all requests for a specific model.

        Args:
            model: Model name

        Returns:
            List of requests for that model
        """
        return [r for r in self.request_history if r.model == model]


# Global mock LLM router instance
_mock_router: Optional[MockLLMRouter] = None


def get_mock_router() -> MockLLMRouter:
    """Get or create global mock LLM router.

    Returns:
        MockLLMRouter instance
    """
    global _mock_router
    if _mock_router is None:
        _mock_router = MockLLMRouter()
    return _mock_router


def reset_mock_router() -> None:
    """Reset global mock LLM router."""
    global _mock_router
    _mock_router = None


def create_mock_router() -> MockLLMRouter:
    """Create a new mock LLM router instance.

    Returns:
        New MockLLMRouter instance
    """
    return MockLLMRouter()


# Predefined response templates

QUALITY_ASSESSMENT_RESPONSES = {
    "quality_check": json.dumps({
        "is_acceptable": True,
        "quality_score": 0.85,
        "feedback": "Response meets quality standards"
    }),
    "low_quality": json.dumps({
        "is_acceptable": False,
        "quality_score": 0.45,
        "feedback": "Response needs improvement"
    }),
}

VALIDATION_RESPONSES = {
    "stage_gate": json.dumps({
        "can_proceed": True,
        "validation_issues": [],
        "missing_fields": []
    }),
    "validation_failed": json.dumps({
        "can_proceed": False,
        "validation_issues": ["Missing problem statement"],
        "missing_fields": ["success_criteria"]
    }),
}

CONSISTENCY_RESPONSES = {
    "consistency_check": json.dumps({
        "is_consistent": True,
        "contradictions": [],
        "recommendations": []
    }),
    "inconsistent": json.dumps({
        "is_consistent": False,
        "contradictions": ["Timeline conflicts with resource plan"],
        "recommendations": ["Adjust timeline or add resources"]
    }),
}

