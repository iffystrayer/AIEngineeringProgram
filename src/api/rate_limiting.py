"""
Rate Limiting Module

Provides rate limiting functionality for API endpoints using slowapi.
Implements both per-user and global rate limiting strategies.
"""

import logging
from typing import Callable, Optional

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# Initialize limiter with get_remote_address as key function
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    # Authentication endpoints - strict limits
    "auth_register": "5 per hour",  # Prevent brute force registration
    "auth_login": "10 per hour",    # Prevent brute force login attempts

    # Session endpoints - per-user limits
    "session_create": "100 per hour",
    "session_list": "100 per hour",
    "session_get": "100 per hour",

    # General endpoints
    "default": "1000 per hour",     # Global default for other endpoints
}


def get_user_id_from_request(request: Request) -> str:
    """
    Extract user_id from request for per-user rate limiting.

    Attempts to get user_id from:
    1. JWT token in Authorization header
    2. Query parameter (for testing)
    3. Remote address (fallback)

    Args:
        request: FastAPI Request object

    Returns:
        str: User identifier (user_id, query param, or IP address)
    """
    # Try to extract from JWT token in Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            # In production, would decode JWT here to get user_id
            # For now, we'll use the token prefix as identifier
            return f"user_{token[:20]}"
        except Exception:
            pass

    # Fallback to remote address
    return get_remote_address(request)


def create_user_limiter() -> Limiter:
    """
    Create a limiter that uses user_id for rate limiting.

    Returns:
        Limiter: Configured limiter for per-user rate limiting
    """
    return Limiter(key_func=get_user_id_from_request)


# Per-user limiter (for authenticated endpoints)
user_limiter = create_user_limiter()


class RateLimitInfo:
    """Information about rate limit status."""

    def __init__(
        self,
        limit: str,
        remaining: int,
        reset_time: Optional[int] = None,
    ):
        """
        Initialize rate limit info.

        Args:
            limit: Rate limit specification (e.g., "100 per hour")
            remaining: Number of requests remaining
            reset_time: Unix timestamp when limit resets
        """
        self.limit = limit
        self.remaining = remaining
        self.reset_time = reset_time


def log_rate_limit_hit(request: Request, endpoint: str, limit: str) -> None:
    """
    Log when a rate limit is hit.

    Args:
        request: FastAPI Request object
        endpoint: Endpoint name
        limit: Rate limit specification
    """
    remote_addr = get_remote_address(request)
    logger.warning(
        f"Rate limit exceeded",
        extra={
            "endpoint": endpoint,
            "limit": limit,
            "remote_addr": remote_addr,
            "user_agent": request.headers.get("user-agent", "unknown"),
        },
    )
