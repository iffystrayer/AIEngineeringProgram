"""
Runtime Type Validation - M-4 Security Implementation

Provides Pydantic-based runtime type validation for all critical input structures.

Security Impact:
- Prevents type confusion attacks
- Catches invalid inputs before processing
- Provides clear validation error messages
- Complements existing input sanitization (H-1, H-2)

Compliance:
- NFR-5.3: Input validation requirements
- Security Review M-4: Runtime type checking for critical inputs
- SWE Spec: Production-grade error handling

Usage:
    # ConversationEngine validation
    validated = validate_conversation_engine_inputs(
        question="What is your project goal?",
        user_response=None
    )

    # Orchestrator validation
    validated = validate_orchestrator_inputs(
        theme="Customer Service AI",
        parameters={"priority": "high"},
        session_id=uuid4()
    )

    # Stage agent validation
    validated = validate_stage_agent_inputs(context=agent_context)
"""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
import logging

logger = logging.getLogger(__name__)

# Security constants (matching engine.py)
MAX_QUESTION_LENGTH = 500
MAX_RESPONSE_LENGTH = 10000
MAX_THEME_LENGTH = 200


# ==============================================================================
# PYDANTIC MODELS
# ==============================================================================


class ConversationEngineInputs(BaseModel):
    """
    Validation model for ConversationEngine inputs.

    Validates:
    - question: String input for start_turn() - max 500 characters
    - user_response: String input for process_response() - max 10,000 characters

    Raises:
        ValidationError: If inputs violate type or constraint requirements
    """

    question: Optional[str] = Field(
        None,
        min_length=1,
        max_length=MAX_QUESTION_LENGTH,
        description="Question to ask user (max 500 chars)"
    )

    user_response: Optional[str] = Field(
        None,
        min_length=1,
        max_length=MAX_RESPONSE_LENGTH,
        description="User response text (max 10,000 chars)"
    )

    @field_validator("question")
    @classmethod
    def validate_question_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure question is not whitespace-only."""
        if v is not None and not v.strip():
            raise ValueError("Question cannot be empty or whitespace only")
        return v

    @field_validator("user_response")
    @classmethod
    def validate_response_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure user response is not whitespace-only."""
        if v is not None and not v.strip():
            raise ValueError("User response cannot be empty or whitespace only")
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-strip whitespace
        validate_assignment=True    # Validate on attribute assignment
    )


class OrchestratorInputs(BaseModel):
    """
    Validation model for Orchestrator inputs.

    Validates:
    - theme: Project theme string - max 200 characters
    - parameters: Configuration dictionary
    - session_id: UUID session identifier
    - stage_number: Stage number (1-5)

    Raises:
        ValidationError: If inputs violate type or constraint requirements
    """

    theme: Optional[str] = Field(
        None,
        min_length=1,
        max_length=MAX_THEME_LENGTH,
        description="Project theme (max 200 chars)"
    )

    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration parameters dictionary"
    )

    session_id: Optional[UUID] = Field(
        None,
        description="Session UUID identifier"
    )

    stage_number: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Stage number (1-5)"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure theme is not whitespace-only."""
        if v is not None and not v.strip():
            raise ValueError("Theme cannot be empty or whitespace only")
        return v

    @field_validator("parameters")
    @classmethod
    def validate_parameters_is_dict(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Ensure parameters is a dict if provided."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("Parameters must be a dictionary")
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class StageAgentContext(BaseModel):
    """
    Validation model for Stage agent AgentContext inputs.

    Validates:
    - project_id: UUID project identifier
    - theme: Project theme string
    - parameters: Configuration dictionary
    - inter_agent_context: Context passed between stages
    - vfs_workspace: Virtual filesystem workspace path
    - artifact_paths: Dictionary of artifact file paths

    Raises:
        ValidationError: If inputs violate type or constraint requirements
    """

    project_id: UUID = Field(
        ...,
        description="Project UUID identifier (required)"
    )

    theme: str = Field(
        ...,
        min_length=1,
        max_length=MAX_THEME_LENGTH,
        description="Project theme (required)"
    )

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration parameters"
    )

    inter_agent_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context passed between stages"
    )

    vfs_workspace: str = Field(
        ...,
        min_length=1,
        description="Virtual filesystem workspace path (required)"
    )

    artifact_paths: Dict[str, str] = Field(
        default_factory=dict,
        description="Artifact file paths"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme_not_empty(cls, v: str) -> str:
        """Ensure theme is not whitespace-only."""
        if not v.strip():
            raise ValueError("Theme cannot be empty or whitespace only")
        return v

    @field_validator("vfs_workspace")
    @classmethod
    def validate_workspace_not_empty(cls, v: str) -> str:
        """Ensure vfs_workspace is not whitespace-only."""
        if not v.strip():
            raise ValueError("VFS workspace path cannot be empty or whitespace only")
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class StageAgentInputs(BaseModel):
    """
    Validation model for Stage agent inputs.

    Validates:
    - context: AgentContext object or dict with required fields

    Raises:
        ValidationError: If inputs violate type or constraint requirements
    """

    context: StageAgentContext = Field(
        ...,
        description="Agent context with project information (required)"
    )

    model_config = ConfigDict(
        validate_assignment=True
    )


# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================


def validate_conversation_engine_inputs(
    question: Optional[str] = None,
    user_response: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate ConversationEngine inputs with Pydantic.

    Args:
        question: Question string to validate (for start_turn)
        user_response: User response string to validate (for process_response)

    Returns:
        Dict with validated inputs

    Raises:
        ValidationError: If inputs violate type or constraint requirements

    Example:
        >>> result = validate_conversation_engine_inputs(
        ...     question="What is your project goal?"
        ... )
        >>> assert result["question"] == "What is your project goal?"

        >>> # Raises ValidationError for invalid type
        >>> validate_conversation_engine_inputs(question=12345)
    """
    try:
        validated = ConversationEngineInputs(
            question=question,
            user_response=user_response
        )
        return validated.model_dump(exclude_none=True)

    except ValidationError as e:
        logger.error(
            f"ConversationEngine input validation failed: {e}",
            extra={"validation_errors": e.errors()}
        )
        raise


def validate_orchestrator_inputs(
    theme: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    session_id: Optional[UUID] = None,
    stage_number: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validate Orchestrator inputs with Pydantic.

    Args:
        theme: Project theme string
        parameters: Configuration parameters dict
        session_id: Session UUID identifier
        stage_number: Stage number (1-5)

    Returns:
        Dict with validated inputs

    Raises:
        ValidationError: If inputs violate type or constraint requirements

    Example:
        >>> result = validate_orchestrator_inputs(
        ...     theme="Customer Service AI",
        ...     parameters={"priority": "high"},
        ...     session_id=uuid4()
        ... )
        >>> assert result["theme"] == "Customer Service AI"

        >>> # Raises ValidationError for invalid stage number
        >>> validate_orchestrator_inputs(stage_number=10)
    """
    try:
        validated = OrchestratorInputs(
            theme=theme,
            parameters=parameters,
            session_id=session_id,
            stage_number=stage_number
        )
        return validated.model_dump(exclude_none=True)

    except ValidationError as e:
        logger.error(
            f"Orchestrator input validation failed: {e}",
            extra={"validation_errors": e.errors()}
        )
        raise


def validate_stage_agent_inputs(context: Any) -> Dict[str, Any]:
    """
    Validate Stage agent inputs with Pydantic.

    Args:
        context: AgentContext object or dict with required fields

    Returns:
        Dict with validated context

    Raises:
        ValidationError: If inputs violate type or constraint requirements

    Example:
        >>> context = {
        ...     "project_id": uuid4(),
        ...     "theme": "Test Theme",
        ...     "parameters": {},
        ...     "inter_agent_context": {},
        ...     "vfs_workspace": "/tmp/test",
        ...     "artifact_paths": {}
        ... }
        >>> result = validate_stage_agent_inputs(context=context)
        >>> assert result["context"]["theme"] == "Test Theme"

        >>> # Raises ValidationError for missing required fields
        >>> validate_stage_agent_inputs(context={"project_id": uuid4()})
    """
    try:
        # If context is a dict, validate with StageAgentContext
        if isinstance(context, dict):
            validated_context = StageAgentContext(**context)
        else:
            # If context is an object, convert to dict and validate
            context_dict = {
                "project_id": getattr(context, "project_id", None),
                "theme": getattr(context, "theme", None),
                "parameters": getattr(context, "parameters", {}),
                "inter_agent_context": getattr(context, "inter_agent_context", {}),
                "vfs_workspace": getattr(context, "vfs_workspace", None),
                "artifact_paths": getattr(context, "artifact_paths", {})
            }
            validated_context = StageAgentContext(**context_dict)

        validated = StageAgentInputs(context=validated_context)
        return validated.model_dump()

    except ValidationError as e:
        logger.error(
            f"Stage agent input validation failed: {e}",
            extra={"validation_errors": e.errors()}
        )
        raise


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


def get_validation_error_message(error: ValidationError) -> str:
    """
    Convert Pydantic ValidationError to user-friendly message.

    Args:
        error: Pydantic ValidationError

    Returns:
        Human-readable error message

    Example:
        >>> try:
        ...     validate_conversation_engine_inputs(question=12345)
        ... except ValidationError as e:
        ...     msg = get_validation_error_message(e)
        ...     assert "question" in msg
        ...     assert "string" in msg.lower()
    """
    errors = error.errors()

    if not errors:
        return "Invalid input provided"

    # Build user-friendly error message
    messages = []
    for err in errors:
        field = " -> ".join(str(loc) for loc in err["loc"])
        error_type = err["type"]
        error_msg = err["msg"]

        # Map Pydantic error types to user-friendly messages
        if "string_type" in error_type:
            messages.append(f"Field '{field}' must be a string")
        elif "int_type" in error_type:
            messages.append(f"Field '{field}' must be an integer")
        elif "dict_type" in error_type:
            messages.append(f"Field '{field}' must be a dictionary")
        elif "uuid_type" in error_type:
            messages.append(f"Field '{field}' must be a valid UUID")
        elif "string_too_long" in error_type:
            messages.append(f"Field '{field}' exceeds maximum length")
        elif "string_too_short" in error_type or "value_error.any_str.min_length" in error_type:
            messages.append(f"Field '{field}' cannot be empty")
        elif "missing" in error_type:
            messages.append(f"Field '{field}' is required")
        else:
            # Use Pydantic's error message as fallback
            messages.append(f"Field '{field}': {error_msg}")

    return "; ".join(messages)
