"""
Conversation engine for U-AIP Scoping Assistant.

Manages stateful conversations with turn-taking, quality validation loops,
and reflection agent integration.
"""

import asyncio
import logging
import re
from enum import Enum
from typing import Optional, Dict, Any

from src.conversation.context import ConversationContext
from src.conversation.types import MessageRole, ValidationResult
from src.utils.logging_sanitizer import setup_sanitized_logging
from src.utils.type_validators import validate_conversation_engine_inputs
from src.exceptions import (
    PromptInjectionError,
    InputSizeLimitError,
    ConversationStateError,
    LLMTimeoutError,
)
from pydantic import ValidationError as PydanticValidationError

logger = logging.getLogger(__name__)

# M-1 Security Fix: Enable PII sanitization for this logger
setup_sanitized_logging(logger)

# Security constants
MAX_QUESTION_LENGTH = 500
MAX_RESPONSE_LENGTH = 10000
MAX_FOLLOW_UP_LENGTH = 2000
TIMEOUT_SECONDS = 30

# Prompt injection detection patterns
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior)\s+instructions',
    r'new\s+instruction',
    r'system\s+prompt',
    r'forget\s+(everything|all|previous)',
    r'you\s+are\s+now',
    r'disregard\s+(all|previous)',
    r'override\s+',
]


class ConversationState(Enum):
    """
    Conversation state machine states.

    State transitions:
    - IDLE -> ASKING: Start a new turn
    - ASKING -> WAITING_FOR_RESPONSE: Question sent to user
    - WAITING_FOR_RESPONSE -> VALIDATING: User response received
    - VALIDATING -> ASKING: Quality check failed, ask follow-up
    - VALIDATING -> COMPLETE: Quality check passed
    - Any -> ERROR: Error occurred
    """
    IDLE = "idle"
    ASKING = "asking"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    VALIDATING = "validating"
    COMPLETE = "complete"
    ERROR = "error"


class ConversationEngine:
    """
    Manages stateful conversation flow with quality validation.

    Coordinates turn-taking between agent and user, integrates with
    ResponseQualityAgent for validation, and enforces max attempt limits.

    Compliance:
    - FR-1.4: Maintains conversation context across stages
    - FR-2.2: Generates contextual follow-up questions
    - FR-3.5: Limits follow-up loops to maximum 3 attempts
    - NFR-1.1: Responds within 3 seconds (async design)

    Attributes:
        quality_agent: ResponseQualityAgent for response validation
        llm_router: LLM router for generating follow-up questions
        context: ConversationContext managing state and history
        state: Current conversation state
    """

    def __init__(
        self,
        quality_agent: Any,  # ResponseQualityAgent
        llm_router: Any,  # LLMRouter
        context: ConversationContext
    ):
        """
        Initialize ConversationEngine.

        Args:
            quality_agent: Agent for response quality validation
            llm_router: Router for LLM API calls
            context: Conversation context manager
        """
        self.quality_agent = quality_agent
        self.llm_router = llm_router
        self.context = context
        self.state = ConversationState.IDLE

        logger.info(
            f"ConversationEngine initialized for session {context.session_id}, "
            f"stage {context.stage_number}"
        )

    def _sanitize_for_prompt(self, text: str, max_length: int = MAX_FOLLOW_UP_LENGTH) -> str:
        """
        Sanitize user input for safe LLM prompt inclusion.

        Prevents prompt injection by:
        - Limiting text length
        - Removing triple quotes (prompt escape attempts)
        - Normalizing whitespace
        - Removing control characters

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text safe for prompt inclusion
        """
        if not text:
            return ""

        # Limit length to prevent DoS
        text = text[:max_length]

        # Remove potential prompt escape sequences
        text = text.replace('"""', '').replace("'''", '')
        text = text.replace('\\n', ' ').replace('\\r', '')

        # Normalize whitespace
        text = ' '.join(text.split())

        return text.strip()

    def _detect_injection(self, text: str) -> bool:
        """
        Detect potential prompt injection attempts.

        Checks for common injection patterns like:
        - "ignore all previous instructions"
        - "new instruction"
        - "forget everything"

        Args:
            text: User input to check

        Returns:
            True if injection pattern detected, False otherwise
        """
        if not text:
            return False

        text_lower = text.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                logger.warning(
                    f"Potential prompt injection detected",
                    extra={"pattern": pattern, "text_preview": text_lower[:100]}
                )
                return True

        return False

    async def start_turn(self, question: str) -> None:
        """
        Start a new conversation turn with a question.

        Args:
            question: The question to ask the user (max 500 chars)

        Raises:
            PydanticValidationError: If question violates type or constraint requirements
            ConversationStateError: If conversation is not in valid state
        """
        # M-4: Runtime type validation with Pydantic
        try:
            validated = validate_conversation_engine_inputs(question=question)
            question = validated["question"]
        except PydanticValidationError as e:
            logger.error(f"Question validation failed: {e}")
            raise

        # M-3: Use specific exception for state errors
        if self.state not in [ConversationState.IDLE, ConversationState.COMPLETE]:
            raise ConversationStateError(
                current_state=self.state.value,
                required_state="IDLE or COMPLETE",
                operation="start new turn"
            )

        # Sanitize question
        sanitized_question = question.strip()

        # Update context
        self.context.update_current_question(sanitized_question)

        # Add question to history
        self.context.add_message(MessageRole.ASSISTANT, question)

        # Transition state
        self.state = ConversationState.ASKING
        logger.debug(f"Started turn with question: {question[:50]}...")

        # Move to waiting for response
        self.state = ConversationState.WAITING_FOR_RESPONSE

    async def process_response(self, user_response: str) -> Dict[str, Any]:
        """
        Process user response with quality validation.

        Validates response quality and generates follow-ups if needed.
        Enforces max 3 attempts per FR-3.5.

        Args:
            user_response: User's response text (max 10,000 chars)

        Returns:
            Dict containing:
                - quality_score: int
                - is_acceptable: bool
                - issues: List[str]
                - suggested_followups: List[str]
                - escalated: bool (True if max attempts reached)

        Raises:
            PydanticValidationError: If user_response violates type or constraint requirements
            PromptInjectionError: If injection pattern detected
            ConversationStateError: If conversation is not waiting for response
        """
        # M-4: Runtime type validation with Pydantic
        try:
            validated = validate_conversation_engine_inputs(user_response=user_response)
            user_response = validated["user_response"]
        except PydanticValidationError as e:
            logger.error(f"User response validation failed: {e}")
            raise

        # M-3: Use specific exception for injection detection
        if self._detect_injection(user_response):
            logger.warning(
                "Potential prompt injection attempt blocked in user response",
                extra={"response_preview": user_response[:100]}
            )
            # Find which pattern matched
            pattern_matched = "unknown"
            for pattern in INJECTION_PATTERNS:
                if re.search(pattern, user_response.lower()):
                    pattern_matched = pattern
                    break

            raise PromptInjectionError(
                pattern=pattern_matched,
                text_preview=user_response[:100]
            )

        # M-3: Use specific exception for state errors
        if self.state != ConversationState.WAITING_FOR_RESPONSE:
            raise ConversationStateError(
                current_state=self.state.value,
                required_state="WAITING_FOR_RESPONSE",
                operation="process response"
            )

        # Add user response to history
        self.context.add_message(MessageRole.USER, user_response)

        # Increment attempt counter
        self.context.increment_attempt()

        # Transition to validation
        self.state = ConversationState.VALIDATING
        logger.debug(
            f"Processing response (attempt {self.context.attempt_count}): "
            f"{user_response[:50]}..."
        )

        # Validate response quality using ResponseQualityAgent
        validation_result = await self._validate_quality(user_response)

        # Check if max attempts reached
        if self.context.is_max_attempts_reached():
            logger.warning(
                f"Max attempts ({self.context.max_attempts}) reached. Escalating."
            )
            self.state = ConversationState.COMPLETE
            return {
                **validation_result,
                "escalated": True,
                "message": "Maximum attempts reached. Moving to next question."
            }

        # If quality acceptable, complete turn
        if validation_result["is_acceptable"]:
            self.state = ConversationState.COMPLETE
            logger.info(f"Response accepted with score {validation_result['quality_score']}")
            return {
                **validation_result,
                "escalated": False
            }

        # Quality not acceptable - generate follow-up question
        follow_up = await self._generate_follow_up(
            question=self.context.current_question,
            response=user_response,
            issues=validation_result["issues"],
            suggested_followups=validation_result["suggested_followups"]
        )

        # Add follow-up question to history
        self.context.add_message(
            MessageRole.ASSISTANT,
            follow_up,
            metadata={"type": "follow_up", "attempt": self.context.attempt_count}
        )

        # Transition back to waiting for response
        self.state = ConversationState.WAITING_FOR_RESPONSE
        logger.debug(f"Generated follow-up question: {follow_up[:50]}...")

        return {
            **validation_result,
            "escalated": False,
            "follow_up_question": follow_up
        }

    async def _validate_quality(self, user_response: str) -> Dict[str, Any]:
        """
        Validate response quality using ResponseQualityAgent.

        Args:
            user_response: User's response text

        Returns:
            Validation result dict with quality score and feedback
        """
        try:
            # Call ResponseQualityAgent with timeout
            result = await asyncio.wait_for(
                self.quality_agent.evaluate_response(
                    question=self.context.current_question,
                    response=user_response,
                    context={
                        "stage_number": self.context.stage_number,
                        "attempt": self.context.attempt_count
                    }
                ),
                timeout=TIMEOUT_SECONDS
            )

            return {
                "quality_score": result.get("quality_score", 0),
                "is_acceptable": result.get("is_acceptable", False),
                "issues": result.get("issues", []),
                "suggested_followups": result.get("suggested_followups", [])
            }

        except asyncio.TimeoutError:
            logger.error(
                f"Quality validation timed out after {TIMEOUT_SECONDS} seconds",
                extra={"question": self.context.current_question[:100]}
            )
            self.state = ConversationState.ERROR
            return {
                "quality_score": 5,
                "is_acceptable": False,
                "issues": ["Validation timed out - please try again"],
                "suggested_followups": ["Please rephrase your response"]
            }

        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            self.state = ConversationState.ERROR
            # Return low quality score on error
            return {
                "quality_score": 5,
                "is_acceptable": False,
                "issues": ["Validation error occurred"],
                "suggested_followups": ["Please rephrase your response"]
            }

    async def _generate_follow_up(
        self,
        question: str,
        response: str,
        issues: list[str],
        suggested_followups: list[str]
    ) -> str:
        """
        Generate contextual follow-up question using LLM.

        Args:
            question: Original question
            response: User's response
            issues: Quality issues identified
            suggested_followups: Suggested follow-up questions from quality agent

        Returns:
            Follow-up question text
        """
        try:
            # Use first suggested follow-up if available
            if suggested_followups:
                return suggested_followups[0]

            # Sanitize inputs before including in prompt
            sanitized_question = self._sanitize_for_prompt(question, MAX_QUESTION_LENGTH)
            sanitized_response = self._sanitize_for_prompt(response, MAX_FOLLOW_UP_LENGTH)
            sanitized_issues = [
                self._sanitize_for_prompt(issue, MAX_FOLLOW_UP_LENGTH)
                for issue in issues
            ]

            # Use structured prompt with sanitized inputs
            prompt = f"""The user was asked: "{sanitized_question}"

They responded: "{sanitized_response}"

Issues with the response:
{chr(10).join(f"- {issue}" for issue in sanitized_issues)}

Generate a specific follow-up question to address these issues and get a more complete answer."""

            # Call LLM with timeout
            follow_up = await asyncio.wait_for(
                self.llm_router.complete(
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7
                ),
                timeout=TIMEOUT_SECONDS
            )

            return follow_up.strip()

        except asyncio.TimeoutError:
            logger.error(
                f"Follow-up generation timed out after {TIMEOUT_SECONDS} seconds",
                extra={"question": sanitized_question[:100]}
            )
            # Fallback to generic follow-up
            return "Could you please provide more specific details about your answer?"

        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            # Fallback to generic follow-up
            return "Could you please provide more specific details about your answer?"

    def get_state(self) -> ConversationState:
        """
        Get current conversation state.

        Returns:
            Current ConversationState
        """
        return self.state

    def get_context(self) -> ConversationContext:
        """
        Get conversation context.

        Returns:
            ConversationContext instance
        """
        return self.context

    def reset(self) -> None:
        """
        Reset conversation engine to IDLE state.

        Resets state but preserves context and history.
        """
        self.state = ConversationState.IDLE
        self.context.reset_attempts()
        logger.debug("ConversationEngine reset to IDLE state")
