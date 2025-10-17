"""
Conversation context management for U-AIP Scoping Assistant.

Manages conversation state, history, and attempt tracking.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from uuid import UUID

from src.conversation.types import Message, MessageRole


@dataclass
class ConversationContext:
    """
    Maintains conversation state and history.

    Tracks conversation flow, attempt counts, and message history to enable
    quality validation loops and context-aware follow-up questions.

    Attributes:
        session_id: Unique session identifier
        stage_number: Current stage (1-5)
        current_question: The current question being asked
        conversation_history: List of all messages
        attempt_count: Number of attempts for current question
        max_attempts: Maximum allowed attempts (default: 3 per FR-3.5)
        metadata: Additional context metadata
    """
    session_id: UUID
    stage_number: int
    current_question: str
    conversation_history: List[Message] = field(default_factory=list)
    attempt_count: int = 0
    max_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to conversation history.

        Args:
            role: Who sent the message (ASSISTANT, USER, SYSTEM)
            content: Message text
            metadata: Optional additional metadata
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.conversation_history.append(message)

    def get_history(self) -> List[Message]:
        """
        Get complete conversation history.

        Returns:
            List of all messages in chronological order
        """
        return self.conversation_history.copy()

    def increment_attempt(self) -> None:
        """
        Increment attempt counter for current question.

        Used to track quality validation loops (max 3 per FR-3.5).
        """
        self.attempt_count += 1

    def reset_attempts(self) -> None:
        """
        Reset attempt counter to 0.

        Called when moving to next question or when quality threshold is met.
        """
        self.attempt_count = 0

    def is_max_attempts_reached(self) -> bool:
        """
        Check if maximum attempts reached.

        Returns:
            True if attempt_count >= max_attempts
        """
        return self.attempt_count >= self.max_attempts

    def get_last_user_message(self) -> Optional[Message]:
        """
        Get the most recent user message.

        Returns:
            Last user message or None if no user messages exist
        """
        for message in reversed(self.conversation_history):
            if message.role == MessageRole.USER:
                return message
        return None

    def get_last_assistant_message(self) -> Optional[Message]:
        """
        Get the most recent assistant message.

        Returns:
            Last assistant message or None if no assistant messages exist
        """
        for message in reversed(self.conversation_history):
            if message.role == MessageRole.ASSISTANT:
                return message
        return None

    def update_current_question(self, question: str) -> None:
        """
        Update the current question being asked.

        Args:
            question: New question text
        """
        self.current_question = question
        self.reset_attempts()  # Reset attempts for new question
