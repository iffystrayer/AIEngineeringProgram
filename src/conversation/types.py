"""
Type definitions for conversation engine.

Defines core data structures for managing conversation state and messages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID


class MessageRole(Enum):
    """Role of message sender in conversation."""
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"


@dataclass
class Message:
    """
    Represents a single message in conversation history.

    Attributes:
        role: Who sent the message (assistant, user, system)
        content: The message text
        timestamp: When the message was created
        metadata: Additional message metadata (quality scores, etc.)
    """
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure role is MessageRole enum."""
        if isinstance(self.role, str):
            self.role = MessageRole(self.role)


@dataclass
class Turn:
    """
    Represents a complete conversation turn (question + response).

    Attributes:
        question: The question asked
        response: User's response
        quality_score: Quality evaluation score (0-10)
        is_acceptable: Whether response meets quality threshold
        attempt_number: Which attempt this is (1-3)
        feedback: Quality feedback provided to user
        follow_up_question: Follow-up question if quality is low
    """
    question: str
    response: Optional[str] = None
    quality_score: Optional[int] = None
    is_acceptable: Optional[bool] = None
    attempt_number: int = 1
    feedback: Optional[str] = None
    follow_up_question: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationResult:
    """
    Result from quality validation.

    Attributes:
        quality_score: Score from 0-10
        is_acceptable: True if score >= 7
        issues: List of quality issues found
        suggested_followups: Follow-up questions to improve quality
        examples: Examples of better responses
    """
    quality_score: int
    is_acceptable: bool
    issues: list[str] = field(default_factory=list)
    suggested_followups: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
