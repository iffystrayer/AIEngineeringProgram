"""
Custom Exceptions for U-AIP

Implements M-3 security requirement: Granular error handling with
specific exception types for better debugging, monitoring, and user feedback.

Security Impact:
- Prevents information leakage via generic error messages
- Enables targeted error handling and recovery
- Improves observability and debugging
- Better user experience with specific error messages
"""


# ============================================================================
# BASE EXCEPTIONS
# ============================================================================


class UAIPException(Exception):
    """
    Base exception for all U-AIP errors.

    All custom exceptions inherit from this class, enabling
    catch-all error handling when needed.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Optional dict with additional context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ============================================================================
# SESSION MANAGEMENT EXCEPTIONS
# ============================================================================


class SessionError(UAIPException):
    """Base exception for session-related errors."""
    pass


class SessionNotFoundError(SessionError):
    """Raised when session ID does not exist."""

    def __init__(self, session_id: str):
        super().__init__(
            f"Session not found: {session_id}",
            details={"session_id": session_id}
        )
        self.session_id = session_id


class SessionInvalidStateError(SessionError):
    """Raised when session is in invalid state for requested operation."""

    def __init__(self, session_id: str, current_state: str, required_state: str):
        super().__init__(
            f"Session {session_id} is in state '{current_state}', "
            f"but '{required_state}' is required",
            details={
                "session_id": session_id,
                "current_state": current_state,
                "required_state": required_state
            }
        )
        self.session_id = session_id
        self.current_state = current_state
        self.required_state = required_state


class SessionAlreadyExistsError(SessionError):
    """Raised when attempting to create duplicate session."""

    def __init__(self, session_id: str):
        super().__init__(
            f"Session already exists: {session_id}",
            details={"session_id": session_id}
        )
        self.session_id = session_id


# ============================================================================
# STAGE EXECUTION EXCEPTIONS
# ============================================================================


class StageExecutionError(UAIPException):
    """Base exception for stage execution errors."""
    pass


class InvalidStageNumberError(StageExecutionError):
    """Raised when stage number is invalid."""

    def __init__(self, stage_number: int):
        super().__init__(
            f"Invalid stage number: {stage_number}. Must be 1-5.",
            details={"stage_number": stage_number}
        )
        self.stage_number = stage_number


class StageSkipError(StageExecutionError):
    """Raised when attempting to skip stages."""

    def __init__(self, requested_stage: int, current_stage: int):
        super().__init__(
            f"Cannot skip to stage {requested_stage}. "
            f"Current stage is {current_stage}.",
            details={
                "requested_stage": requested_stage,
                "current_stage": current_stage
            }
        )
        self.requested_stage = requested_stage
        self.current_stage = current_stage


class StageNotImplementedError(StageExecutionError):
    """Raised when stage agent is not implemented."""

    def __init__(self, stage_number: int):
        super().__init__(
            f"Stage {stage_number} agent not implemented",
            details={"stage_number": stage_number}
        )
        self.stage_number = stage_number


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================


class ValidationError(UAIPException):
    """Base exception for validation errors."""
    pass


class InputValidationError(ValidationError):
    """Raised when input fails validation."""

    def __init__(self, field_name: str, reason: str, provided_value: str = None):
        message = f"Invalid {field_name}: {reason}"
        details = {"field_name": field_name, "reason": reason}

        if provided_value:
            details["provided_value"] = provided_value[:100]  # Truncate for safety

        super().__init__(message, details)
        self.field_name = field_name
        self.reason = reason


class QualityValidationError(ValidationError):
    """Raised when response quality validation fails."""

    def __init__(self, quality_score: int, threshold: int, issues: list):
        super().__init__(
            f"Response quality ({quality_score}) below threshold ({threshold})",
            details={
                "quality_score": quality_score,
                "threshold": threshold,
                "issues": issues
            }
        )
        self.quality_score = quality_score
        self.threshold = threshold
        self.issues = issues


class StageGateValidationError(ValidationError):
    """Raised when stage gate validation fails."""

    def __init__(self, stage_number: int, missing_items: list, concerns: list):
        super().__init__(
            f"Stage {stage_number} validation failed",
            details={
                "stage_number": stage_number,
                "missing_items": missing_items,
                "validation_concerns": concerns
            }
        )
        self.stage_number = stage_number
        self.missing_items = missing_items
        self.validation_concerns = concerns


# ============================================================================
# SECURITY EXCEPTIONS
# ============================================================================


class SecurityError(UAIPException):
    """Base exception for security-related errors."""
    pass


class PromptInjectionError(SecurityError):
    """Raised when prompt injection attempt is detected."""

    def __init__(self, pattern: str, text_preview: str = None):
        super().__init__(
            "Potential prompt injection detected",
            details={"pattern": pattern, "text_preview": text_preview}
        )
        self.pattern = pattern


class InputSizeLimitError(SecurityError):
    """Raised when input exceeds size limits (DoS prevention)."""

    def __init__(self, input_type: str, max_length: int, actual_length: int):
        super().__init__(
            f"{input_type} exceeds maximum length. "
            f"Maximum {max_length} characters, got {actual_length}",
            details={
                "input_type": input_type,
                "max_length": max_length,
                "actual_length": actual_length
            }
        )
        self.input_type = input_type
        self.max_length = max_length
        self.actual_length = actual_length


class RateLimitExceededError(SecurityError):
    """Raised when rate limit is exceeded."""

    def __init__(self, user_id: str, limit: int, window: str):
        super().__init__(
            f"Rate limit exceeded for user {user_id}. "
            f"Limit: {limit} requests per {window}",
            details={
                "user_id": user_id,
                "limit": limit,
                "window": window
            }
        )
        self.user_id = user_id
        self.limit = limit
        self.window = window


# ============================================================================
# LLM INTEGRATION EXCEPTIONS
# ============================================================================


class LLMError(UAIPException):
    """Base exception for LLM-related errors."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM API call times out."""

    def __init__(self, timeout_seconds: int, operation: str):
        super().__init__(
            f"LLM {operation} timed out after {timeout_seconds} seconds",
            details={"timeout_seconds": timeout_seconds, "operation": operation}
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class LLMProviderError(LLMError):
    """Raised when LLM provider returns error."""

    def __init__(self, provider: str, error_message: str, status_code: int = None):
        super().__init__(
            f"LLM provider '{provider}' error: {error_message}",
            details={
                "provider": provider,
                "error_message": error_message,
                "status_code": status_code
            }
        )
        self.provider = provider
        self.error_message = error_message
        self.status_code = status_code


class LLMAPIKeyError(LLMError):
    """Raised when LLM API key is invalid or missing."""

    def __init__(self, provider: str):
        super().__init__(
            f"Invalid or missing API key for provider '{provider}'",
            details={"provider": provider}
        )
        self.provider = provider


# ============================================================================
# DATABASE EXCEPTIONS
# ============================================================================


class DatabaseError(UAIPException):
    """Base exception for database errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, reason: str, retry_count: int = 0):
        super().__init__(
            f"Database connection failed: {reason}",
            details={"reason": reason, "retry_count": retry_count}
        )
        self.reason = reason
        self.retry_count = retry_count


class DatabaseQueryError(DatabaseError):
    """Raised when database query fails."""

    def __init__(self, query: str, reason: str):
        super().__init__(
            f"Database query failed: {reason}",
            details={"query": query[:200], "reason": reason}  # Truncate query
        )
        self.query = query
        self.reason = reason


# ============================================================================
# CHECKPOINT EXCEPTIONS
# ============================================================================


class CheckpointError(UAIPException):
    """Base exception for checkpoint-related errors."""
    pass


class CheckpointNotFoundError(CheckpointError):
    """Raised when checkpoint does not exist."""

    def __init__(self, checkpoint_id: str):
        super().__init__(
            f"Checkpoint not found: {checkpoint_id}",
            details={"checkpoint_id": checkpoint_id}
        )
        self.checkpoint_id = checkpoint_id


class CheckpointCorruptedError(CheckpointError):
    """Raised when checkpoint data is corrupted."""

    def __init__(self, checkpoint_id: str, reason: str):
        super().__init__(
            f"Checkpoint {checkpoint_id} is corrupted: {reason}",
            details={"checkpoint_id": checkpoint_id, "reason": reason}
        )
        self.checkpoint_id = checkpoint_id
        self.reason = reason


# ============================================================================
# CONVERSATION ENGINE EXCEPTIONS
# ============================================================================


class ConversationError(UAIPException):
    """Base exception for conversation engine errors."""
    pass


class ConversationStateError(ConversationError):
    """Raised when conversation is in invalid state."""

    def __init__(self, current_state: str, required_state: str, operation: str):
        super().__init__(
            f"Cannot {operation} in state '{current_state}'. "
            f"Required state: '{required_state}'",
            details={
                "current_state": current_state,
                "required_state": required_state,
                "operation": operation
            }
        )
        self.current_state = current_state
        self.required_state = required_state
        self.operation = operation


class MaxAttemptsExceededError(ConversationError):
    """Raised when maximum quality loop attempts exceeded."""

    def __init__(self, max_attempts: int, question: str = None):
        super().__init__(
            f"Maximum attempts ({max_attempts}) exceeded",
            details={"max_attempts": max_attempts, "question": question}
        )
        self.max_attempts = max_attempts
        self.question = question


# ============================================================================
# GOVERNANCE EXCEPTIONS
# ============================================================================


class GovernanceError(UAIPException):
    """Base exception for governance-related errors."""
    pass


class GovernanceDecisionError(GovernanceError):
    """Raised when governance decision cannot be made."""

    def __init__(self, reason: str, missing_data: list = None):
        super().__init__(
            f"Cannot make governance decision: {reason}",
            details={"reason": reason, "missing_data": missing_data}
        )
        self.reason = reason
        self.missing_data = missing_data or []


class CharterGenerationError(GovernanceError):
    """Raised when charter generation fails."""

    def __init__(self, reason: str, missing_stages: list = None):
        super().__init__(
            f"Charter generation failed: {reason}",
            details={"reason": reason, "missing_stages": missing_stages}
        )
        self.reason = reason
        self.missing_stages = missing_stages or []


# ============================================================================
# CONFIGURATION EXCEPTIONS
# ============================================================================


class ConfigurationError(UAIPException):
    """Base exception for configuration errors."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(self, config_key: str):
        super().__init__(
            f"Missing required configuration: {config_key}",
            details={"config_key": config_key}
        )
        self.config_key = config_key


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration value is invalid."""

    def __init__(self, config_key: str, value: str, reason: str):
        super().__init__(
            f"Invalid configuration for '{config_key}': {reason}",
            details={
                "config_key": config_key,
                "value": value,
                "reason": reason
            }
        )
        self.config_key = config_key
        self.value = value
        self.reason = reason


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_user_friendly_message(exception: Exception) -> str:
    """
    Convert exception to user-friendly message.

    Hides technical details for security, provides helpful guidance.

    Args:
        exception: Exception to convert

    Returns:
        User-friendly error message
    """
    if isinstance(exception, SessionNotFoundError):
        return "The session you're looking for doesn't exist. Please start a new session."

    if isinstance(exception, SessionInvalidStateError):
        return "This operation is not allowed in the current session state. Please try again or start a new session."

    if isinstance(exception, InvalidStageNumberError):
        return "Invalid stage number. Stages must be 1-5."

    if isinstance(exception, StageSkipError):
        return "You must complete stages in order. Please complete the current stage first."

    if isinstance(exception, PromptInjectionError):
        return "Invalid input detected. Please rephrase your response."

    if isinstance(exception, InputSizeLimitError):
        return f"Input is too long. Please limit to {exception.max_length} characters."

    if isinstance(exception, LLMTimeoutError):
        return "The AI service is taking too long to respond. Please try again."

    if isinstance(exception, LLMProviderError):
        return "The AI service encountered an error. Please try again later."

    if isinstance(exception, DatabaseConnectionError):
        return "Unable to connect to database. Please try again later."

    if isinstance(exception, MaxAttemptsExceededError):
        return f"You've reached the maximum number of attempts ({exception.max_attempts}). Moving to next question."

    if isinstance(exception, CharterGenerationError):
        return "Unable to generate charter. Please ensure all stages are completed."

    # Generic fallback
    if isinstance(exception, UAIPException):
        return exception.message

    return "An unexpected error occurred. Please try again or contact support."


def get_http_status_code(exception: Exception) -> int:
    """
    Get appropriate HTTP status code for exception.

    Args:
        exception: Exception to map

    Returns:
        HTTP status code (400, 404, 500, etc.)
    """
    # 404 Not Found
    if isinstance(exception, (SessionNotFoundError, CheckpointNotFoundError)):
        return 404

    # 400 Bad Request
    if isinstance(exception, (
        InputValidationError,
        InvalidStageNumberError,
        StageSkipError,
        PromptInjectionError,
        InputSizeLimitError,
        SessionInvalidStateError,
        ConversationStateError
    )):
        return 400

    # 409 Conflict
    if isinstance(exception, SessionAlreadyExistsError):
        return 409

    # 429 Too Many Requests
    if isinstance(exception, RateLimitExceededError):
        return 429

    # 503 Service Unavailable
    if isinstance(exception, (DatabaseConnectionError, LLMTimeoutError)):
        return 503

    # 502 Bad Gateway
    if isinstance(exception, LLMProviderError):
        return 502

    # 500 Internal Server Error (default)
    return 500
