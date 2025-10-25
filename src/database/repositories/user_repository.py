"""
User Repository

Provides CRUD operations for User model with database persistence.
Handles user authentication data and account management.
"""

import logging
from typing import Optional
from uuid import UUID

import asyncpg

from src.auth.security import PasswordManager
from src.database.connection import DatabaseManager
from src.models.schemas import User

logger = logging.getLogger(__name__)


class UserRepositoryError(Exception):
    """Base exception for user repository operations."""

    pass


class UserRepository:
    """
    Repository for User CRUD operations.

    Manages persistence of user accounts including email, password hashes,
    and user profile information.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize repository with database manager.

        Args:
            db_manager: Initialized DatabaseManager instance
        """
        self.db = db_manager

    # ========================================================================
    # CREATE OPERATIONS
    # ========================================================================

    async def create(
        self, email: str, password_hash: str, name: str = ""
    ) -> User:
        """
        Create a new user account.

        Args:
            email: User email address (must be unique)
            password_hash: Hashed password
            name: User full name (optional)

        Returns:
            User: Created user with assigned user_id

        Raises:
            UserRepositoryError: If user creation fails
        """
        try:
            new_user = User(email=email, password_hash=password_hash, name=name)

            async with self.db.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO users (user_id, email, password_hash, name, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    str(new_user.user_id),
                    email,
                    password_hash,
                    name,
                    new_user.created_at,
                    new_user.updated_at,
                )

            logger.info(f"Created user: {email}")
            return new_user

        except asyncpg.UniqueViolationError:
            logger.warning(f"User with email {email} already exists")
            raise UserRepositoryError(f"User with email {email} already exists") from None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise UserRepositoryError(f"Failed to create user: {e}") from e

    # ========================================================================
    # READ OPERATIONS
    # ========================================================================

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve user by ID.

        Args:
            user_id: User UUID

        Returns:
            Optional[User]: User if found, None otherwise

        Raises:
            UserRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT user_id, email, password_hash, name, created_at, updated_at
                    FROM users
                    WHERE user_id = $1
                    """,
                    user_id,
                )

                if row is None:
                    return None

                return User(
                    user_id=row["user_id"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    name=row["name"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )

        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise UserRepositoryError(f"Failed to retrieve user: {e}") from e

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve user by email address.

        Args:
            email: User email address

        Returns:
            Optional[User]: User if found, None otherwise

        Raises:
            UserRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT user_id, email, password_hash, name, created_at, updated_at
                    FROM users
                    WHERE email = $1
                    """,
                    email,
                )

                if row is None:
                    return None

                return User(
                    user_id=row["user_id"],
                    email=row["email"],
                    password_hash=row["password_hash"],
                    name=row["name"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )

        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise UserRepositoryError(f"Failed to retrieve user: {e}") from e

    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================

    async def update(self, user: User) -> User:
        """
        Update user information.

        Args:
            user: User object with updated fields

        Returns:
            User: Updated user object

        Raises:
            UserRepositoryError: If update fails
        """
        try:
            user.updated_at = __import__("datetime").datetime.now()

            async with self.db.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE users
                    SET email = $1, password_hash = $2, name = $3, updated_at = $4
                    WHERE user_id = $5
                    """,
                    user.email,
                    user.password_hash,
                    user.name,
                    user.updated_at,
                    user.user_id,
                )

            logger.info(f"Updated user: {user.email}")
            return user

        except Exception as e:
            logger.error(f"Failed to update user {user.user_id}: {e}")
            raise UserRepositoryError(f"Failed to update user: {e}") from e

    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user account.

        Args:
            user_id: User UUID to delete

        Returns:
            bool: True if user was deleted, False otherwise

        Raises:
            UserRepositoryError: If deletion fails
        """
        try:
            async with self.db.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM users WHERE user_id = $1",
                    user_id,
                )

            if result == "DELETE 1":
                logger.info(f"Deleted user: {user_id}")
                return True
            else:
                logger.warning(f"User not found: {user_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise UserRepositoryError(f"Failed to delete user: {e}") from e

    # ========================================================================
    # AUTHENTICATION OPERATIONS
    # ========================================================================

    async def verify_credentials(self, email: str, password: str) -> Optional[User]:
        """
        Verify user email and password credentials.

        Args:
            email: User email
            password: Plain text password to verify

        Returns:
            Optional[User]: User if credentials are valid, None otherwise
        """
        try:
            user = await self.get_by_email(email)

            if user is None:
                logger.warning(f"Login attempt for non-existent user: {email}")
                return None

            if PasswordManager.verify_password(password, user.password_hash):
                logger.info(f"Successful login: {email}")
                return user
            else:
                logger.warning(f"Failed login attempt: {email}")
                return None

        except Exception as e:
            logger.error(f"Error verifying credentials: {e}")
            return None
