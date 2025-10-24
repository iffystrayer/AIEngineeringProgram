"""
Authentication and JWT Security Module

Provides JWT token generation, validation, and password hashing for user authentication.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordManager:
    """Manages password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Previously hashed password

        Returns:
            bool: True if passwords match, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)


class TokenManager:
    """Manages JWT token generation and validation."""

    @staticmethod
    def create_access_token(
        user_id: str, email: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User UUID as string
            email: User email address
            expires_delta: Custom expiration time (default: 24 hours)

        Returns:
            str: Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            dict: Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None or email is None:
                logger.warning("Token missing required fields")
                return None

            return {"user_id": user_id, "email": email}

        except JWTError as e:
            logger.warning(f"Token validation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            return None


# Convenience functions for use in FastAPI dependencies
def hash_password(password: str) -> str:
    """Hash a password."""
    return PasswordManager.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return PasswordManager.verify_password(plain_password, hashed_password)


def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    return TokenManager.create_access_token(user_id, email)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    return TokenManager.verify_token(token)
