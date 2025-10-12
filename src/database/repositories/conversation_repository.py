"""
Conversation Repository

Provides CRUD operations for conversation history management.
Focused repository for message storage and retrieval.
"""

import json
import logging
from uuid import UUID

from src.database.connection import DatabaseManager
from src.models.schemas import Message

logger = logging.getLogger(__name__)


class ConversationRepositoryError(Exception):
    """Base exception for conversation repository operations."""

    pass


class ConversationRepository:
    """
    Repository for conversation history CRUD operations.

    Manages persistence of Q&A messages for audit trail and session replay.
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

    async def add_message(self, session_id: UUID, message: Message) -> None:
        """
        Add a message to conversation history.

        Args:
            session_id: Session UUID
            message: Message to add

        Raises:
            ConversationRepositoryError: If operation fails
        """
        try:
            async with self.db.transaction() as conn:
                await conn.execute(
                    """
                    INSERT INTO conversation_history (
                        session_id, role, content, timestamp,
                        stage_number, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    session_id,
                    message.role,
                    message.content,
                    message.timestamp,
                    message.stage_number,
                    json.dumps(message.metadata),
                )

                logger.info(f"Added {message.role} message to session {session_id}")

        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            raise ConversationRepositoryError(f"Message creation failed: {e}") from e

    async def add_messages_bulk(self, session_id: UUID, messages: list[Message]) -> None:
        """
        Add multiple messages in a single transaction.

        Args:
            session_id: Session UUID
            messages: List of messages to add

        Raises:
            ConversationRepositoryError: If operation fails
        """
        try:
            async with self.db.transaction() as conn:
                for message in messages:
                    await conn.execute(
                        """
                        INSERT INTO conversation_history (
                            session_id, role, content, timestamp,
                            stage_number, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        session_id,
                        message.role,
                        message.content,
                        message.timestamp,
                        message.stage_number,
                        json.dumps(message.metadata),
                    )

                logger.info(f"Added {len(messages)} messages to session {session_id}")

        except Exception as e:
            logger.error(f"Failed to add messages in bulk: {e}")
            raise ConversationRepositoryError(f"Bulk message creation failed: {e}") from e

    # ========================================================================
    # RETRIEVAL OPERATIONS
    # ========================================================================

    async def get_conversation_history(self, session_id: UUID) -> list[Message]:
        """
        Get full conversation history for a session.

        Args:
            session_id: Session UUID

        Returns:
            List[Message]: Ordered conversation messages (chronological)

        Raises:
            ConversationRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT role, content, timestamp, stage_number, metadata
                    FROM conversation_history
                    WHERE session_id = $1
                    ORDER BY timestamp ASC
                    """,
                    session_id,
                )

                messages = []
                for row in rows:
                    message = Message(
                        role=row["role"],
                        content=row["content"],
                        timestamp=row["timestamp"],
                        stage_number=row["stage_number"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    )
                    messages.append(message)

                return messages

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise ConversationRepositoryError(f"Conversation retrieval failed: {e}") from e

    async def get_messages_by_stage(self, session_id: UUID, stage_number: int) -> list[Message]:
        """
        Get conversation messages for a specific stage.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)

        Returns:
            List[Message]: Messages for the specified stage

        Raises:
            ConversationRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT role, content, timestamp, stage_number, metadata
                    FROM conversation_history
                    WHERE session_id = $1 AND stage_number = $2
                    ORDER BY timestamp ASC
                    """,
                    session_id,
                    stage_number,
                )

                messages = []
                for row in rows:
                    message = Message(
                        role=row["role"],
                        content=row["content"],
                        timestamp=row["timestamp"],
                        stage_number=row["stage_number"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    )
                    messages.append(message)

                return messages

        except Exception as e:
            logger.error(f"Failed to get stage {stage_number} messages: {e}")
            raise ConversationRepositoryError(f"Stage messages retrieval failed: {e}") from e

    async def get_recent_messages(self, session_id: UUID, limit: int = 10) -> list[Message]:
        """
        Get most recent messages for a session.

        Args:
            session_id: Session UUID
            limit: Maximum number of messages to return

        Returns:
            List[Message]: Recent messages (newest first)

        Raises:
            ConversationRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT role, content, timestamp, stage_number, metadata
                    FROM conversation_history
                    WHERE session_id = $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                    """,
                    session_id,
                    limit,
                )

                messages = []
                for row in rows:
                    message = Message(
                        role=row["role"],
                        content=row["content"],
                        timestamp=row["timestamp"],
                        stage_number=row["stage_number"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    )
                    messages.append(message)

                # Reverse to get chronological order
                return list(reversed(messages))

        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            raise ConversationRepositoryError(f"Recent messages retrieval failed: {e}") from e

    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def delete_all_for_session(self, session_id: UUID) -> int:
        """
        Delete all conversation history for a session.

        Args:
            session_id: Session UUID

        Returns:
            int: Number of messages deleted

        Raises:
            ConversationRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM conversation_history
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                count = int(result.split()[-1]) if result != "DELETE 0" else 0
                logger.info(f"Deleted {count} messages for session {session_id}")
                return count

        except Exception as e:
            logger.error(f"Failed to delete conversation history: {e}")
            raise ConversationRepositoryError(f"Conversation deletion failed: {e}") from e

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    async def count_messages(self, session_id: UUID) -> int:
        """
        Count total messages in a session.

        Args:
            session_id: Session UUID

        Returns:
            int: Total message count

        Raises:
            ConversationRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                count = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM conversation_history
                    WHERE session_id = $1
                    """,
                    session_id,
                )
                return count or 0

        except Exception as e:
            logger.error(f"Failed to count messages: {e}")
            raise ConversationRepositoryError(f"Message count failed: {e}") from e

    async def get_messages_by_role(self, session_id: UUID, role: str) -> list[Message]:
        """
        Get messages filtered by role (user, assistant, system).

        Args:
            session_id: Session UUID
            role: Message role to filter by

        Returns:
            List[Message]: Messages from the specified role

        Raises:
            ConversationRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT role, content, timestamp, stage_number, metadata
                    FROM conversation_history
                    WHERE session_id = $1 AND role = $2
                    ORDER BY timestamp ASC
                    """,
                    session_id,
                    role,
                )

                messages = []
                for row in rows:
                    message = Message(
                        role=row["role"],
                        content=row["content"],
                        timestamp=row["timestamp"],
                        stage_number=row["stage_number"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    )
                    messages.append(message)

                return messages

        except Exception as e:
            logger.error(f"Failed to get messages by role '{role}': {e}")
            raise ConversationRepositoryError(f"Role messages retrieval failed: {e}") from e
