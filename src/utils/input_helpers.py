"""
Input Helper Utilities

Provides reusable utilities for handling user input gracefully across all stage agents.
"""

import logging
from typing import Any, Dict, Callable, Awaitable
from pydantic import ValidationError as PydanticValidationError
from rich.console import Console

logger = logging.getLogger(__name__)


async def process_user_response_with_retry(
    engine: Any,  # ConversationEngine
    user_response: str,
    input_prompt_callback: Callable[[], Awaitable[str]] = None
) -> Dict[str, Any]:
    """
    Process user response through ConversationEngine with graceful error handling.

    If the user provides an empty response, this function will display a friendly
    error message and re-prompt the user.

    Args:
        engine: ConversationEngine instance
        user_response: The user's initial response
        input_prompt_callback: Optional async callback to get a new response if needed

    Returns:
        Dict containing validation result from ConversationEngine

    Raises:
        PydanticValidationError: If validation fails for non-empty response reasons
    """
    console = Console()

    # Try processing the initial response
    try:
        result = await engine.process_response(user_response)
        return result
    except PydanticValidationError as e:
        # Check if this is an empty response error
        error_details = str(e)
        if "string_too_short" in error_details or "at least 1 character" in error_details:
            # This is an empty response - handle gracefully
            console.print("\n[yellow]⚠️  Please provide an answer - empty responses are not accepted.[/yellow]")
            console.print("[dim]Press Enter after typing your response.[/dim]\n")

            # If no callback provided, re-raise the error
            if input_prompt_callback is None:
                raise

            # Keep prompting until we get a valid response
            while True:
                try:
                    user_response = await input_prompt_callback()
                    result = await engine.process_response(user_response)
                    return result
                except PydanticValidationError as retry_error:
                    retry_error_details = str(retry_error)
                    if "string_too_short" in retry_error_details or "at least 1 character" in retry_error_details:
                        console.print("\n[yellow]⚠️  Please provide an answer - empty responses are not accepted.[/yellow]")
                        console.print("[dim]Press Enter after typing your response.[/dim]\n")
                        continue
                    else:
                        # Different validation error - re-raise it
                        raise
        else:
            # Not an empty response error - re-raise it
            raise


async def get_user_response_with_validation(
    engine: Any,  # ConversationEngine
    input_prompt_callback: Callable[[], Awaitable[str]]
) -> Dict[str, Any]:
    """
    Get user response with automatic empty-response retry loop.

    This is a convenience wrapper around process_user_response_with_retry
    that handles the initial prompt automatically.

    Args:
        engine: ConversationEngine instance
        input_prompt_callback: Async callback to get user response

    Returns:
        Dict containing validation result from ConversationEngine
    """
    console = Console()

    while True:
        try:
            user_response = await input_prompt_callback()
            result = await engine.process_response(user_response)
            return result
        except PydanticValidationError as e:
            # Check if this is an empty response error
            error_details = str(e)
            if "string_too_short" in error_details or "at least 1 character" in error_details:
                console.print("\n[yellow]⚠️  Please provide an answer - empty responses are not accepted.[/yellow]")
                console.print("[dim]Press Enter after typing your response.[/dim]\n")
                # Loop continues to re-prompt
                continue
            else:
                # Different validation error - re-raise it
                raise
