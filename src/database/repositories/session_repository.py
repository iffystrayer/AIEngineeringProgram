"""
Session Repository

Provides CRUD operations for Session model with database persistence.
Handles session lifecycle, checkpoints, and conversation history.
"""

import json
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import asyncpg

from src.database.connection import DatabaseManager
from src.models.schemas import Checkpoint, Message, Session, SessionStatus

logger = logging.getLogger(__name__)


class SessionRepositoryError(Exception):
    """Base exception for session repository operations."""

    pass


class SessionRepository:
    """
    Repository for Session CRUD operations.

    Manages persistence of user sessions including stage data,
    conversation history, and checkpoints.
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

    async def create(self, session: Session) -> Session:
        """
        Create a new session in the database.

        Args:
            session: Session object to persist

        Returns:
            Session: Created session with database-generated fields

        Raises:
            SessionRepositoryError: If creation fails
        """
        if not session.user_id or not session.project_name:
            raise ValueError("user_id and project_name are required")

        try:
            async with self.db.transaction() as conn:
                # Insert session
                await conn.execute(
                    """
                    INSERT INTO sessions (
                        session_id, user_id, project_name,
                        started_at, last_updated_at, current_stage, status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    session.session_id,
                    session.user_id,
                    session.project_name,
                    session.started_at,
                    session.last_updated_at,
                    session.current_stage,
                    session.status.value,
                )

                logger.info(f"Created session {session.session_id} for user {session.user_id}")
                return session

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise SessionRepositoryError(f"Session creation failed: {e}") from e

    async def create_new(self, user_id: str, project_name: str) -> Session:
        """
        Create a new session with default values.

        Args:
            user_id: User identifier
            project_name: Name of the AI project

        Returns:
            Session: Newly created session

        Raises:
            SessionRepositoryError: If creation fails
        """
        if not user_id or not project_name:
            raise ValueError("user_id and project_name are required")

        session = Session(
            session_id=uuid4(),
            user_id=user_id,
            project_name=project_name,
            started_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow(),
            current_stage=1,
            stage_data={},
            conversation_history=[],
            status=SessionStatus.IN_PROGRESS,
            checkpoints=[],
        )

        return await self.create(session)

    # ========================================================================
    # READ OPERATIONS
    # ========================================================================

    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """
        Retrieve session by ID.

        Args:
            session_id: Session UUID

        Returns:
            Optional[Session]: Session if found, None otherwise

        Raises:
            SessionRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT session_id, user_id, project_name, started_at,
                           last_updated_at, current_stage, status
                    FROM sessions
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                if row is None:
                    return None

                # Load related data
                stage_data = await self._load_stage_data(conn, session_id)
                conversation_history = await self._load_conversation_history(conn, session_id)
                checkpoints = await self._load_checkpoints(conn, session_id)

                return Session(
                    session_id=row["session_id"],
                    user_id=row["user_id"],
                    project_name=row["project_name"],
                    started_at=row["started_at"],
                    last_updated_at=row["last_updated_at"],
                    current_stage=row["current_stage"],
                    stage_data=stage_data,
                    conversation_history=conversation_history,
                    status=SessionStatus(row["status"]),
                    checkpoints=checkpoints,
                )

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            raise SessionRepositoryError(f"Failed to retrieve session: {e}") from e

    async def get_by_user_id(self, user_id: str, limit: int = 10) -> list[Session]:
        """
        Retrieve sessions for a specific user.

        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return (default 10)

        Returns:
            List[Session]: List of user's sessions, newest first

        Raises:
            SessionRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT session_id, user_id, project_name, started_at,
                           last_updated_at, current_stage, status
                    FROM sessions
                    WHERE user_id = $1
                    ORDER BY started_at DESC
                    LIMIT $2
                    """,
                    user_id,
                    limit,
                )

                sessions = []
                for row in rows:
                    # For list views, don't load full conversation history (performance)
                    session = Session(
                        session_id=row["session_id"],
                        user_id=row["user_id"],
                        project_name=row["project_name"],
                        started_at=row["started_at"],
                        last_updated_at=row["last_updated_at"],
                        current_stage=row["current_stage"],
                        stage_data={},  # Load on demand
                        conversation_history=[],  # Load on demand
                        status=SessionStatus(row["status"]),
                        checkpoints=[],  # Load on demand
                    )
                    sessions.append(session)

                return sessions

        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            raise SessionRepositoryError(f"Failed to retrieve sessions: {e}") from e

    async def get_active_sessions(self, user_id: str) -> list[Session]:
        """
        Get all active (in_progress) sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List[Session]: Active sessions

        Raises:
            SessionRepositoryError: If query fails
        """
        return await self.get_sessions_by_status(SessionStatus.IN_PROGRESS, user_id)

    async def get_sessions_by_status(
        self, status: SessionStatus, user_id: Optional[str] = None
    ) -> list[Session]:
        """
        Get sessions filtered by status.

        Args:
            status: SessionStatus to filter by
            user_id: Optional user filter

        Returns:
            List[Session]: Matching sessions

        Raises:
            SessionRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                if user_id:
                    rows = await conn.fetch(
                        """
                        SELECT session_id, user_id, project_name, started_at,
                               last_updated_at, current_stage, status
                        FROM sessions
                        WHERE status = $1 AND user_id = $2
                        ORDER BY started_at DESC
                        """,
                        status.value,
                        user_id,
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT session_id, user_id, project_name, started_at,
                               last_updated_at, current_stage, status
                        FROM sessions
                        WHERE status = $1
                        ORDER BY started_at DESC
                        """,
                        status.value,
                    )

                sessions = []
                for row in rows:
                    session = Session(
                        session_id=row["session_id"],
                        user_id=row["user_id"],
                        project_name=row["project_name"],
                        started_at=row["started_at"],
                        last_updated_at=row["last_updated_at"],
                        current_stage=row["current_stage"],
                        stage_data={},
                        conversation_history=[],
                        status=SessionStatus(row["status"]),
                        checkpoints=[],
                    )
                    sessions.append(session)

                return sessions

        except Exception as e:
            logger.error(f"Failed to get sessions by status {status}: {e}")
            raise SessionRepositoryError(f"Failed to retrieve sessions: {e}") from e

    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================

    async def update(self, session: Session) -> Session:
        """
        Update an existing session.

        Args:
            session: Session with updated fields

        Returns:
            Session: Updated session

        Raises:
            SessionRepositoryError: If update fails
            ValueError: If session doesn't exist
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    UPDATE sessions
                    SET current_stage = $2,
                        status = $3,
                        project_name = $4
                    WHERE session_id = $1
                    """,
                    session.session_id,
                    session.current_stage,
                    session.status.value,
                    session.project_name,
                )

                if result == "UPDATE 0":
                    raise ValueError(f"Session {session.session_id} not found")

                logger.info(f"Updated session {session.session_id}")
                return session

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update session {session.session_id}: {e}")
            raise SessionRepositoryError(f"Session update failed: {e}") from e

    async def update_stage(self, session_id: UUID, stage: int) -> None:
        """
        Update the current stage of a session.

        Args:
            session_id: Session UUID
            stage: New stage number (1-6)

        Raises:
            SessionRepositoryError: If update fails
            ValueError: If stage invalid or session doesn't exist
        """
        if stage < 1 or stage > 6:
            raise ValueError(f"Stage must be between 1 and 6, got {stage}")

        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    UPDATE sessions
                    SET current_stage = $2
                    WHERE session_id = $1
                    """,
                    session_id,
                    stage,
                )

                if result == "UPDATE 0":
                    raise ValueError(f"Session {session_id} not found")

                logger.info(f"Updated session {session_id} to stage {stage}")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update stage for session {session_id}: {e}")
            raise SessionRepositoryError(f"Stage update failed: {e}") from e

    async def update_status(self, session_id: UUID, status: SessionStatus) -> None:
        """
        Update the status of a session.

        Args:
            session_id: Session UUID
            status: New session status

        Raises:
            SessionRepositoryError: If update fails
            ValueError: If session doesn't exist
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    UPDATE sessions
                    SET status = $2
                    WHERE session_id = $1
                    """,
                    session_id,
                    status.value,
                )

                if result == "UPDATE 0":
                    raise ValueError(f"Session {session_id} not found")

                logger.info(f"Updated session {session_id} status to {status.value}")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update status for session {session_id}: {e}")
            raise SessionRepositoryError(f"Status update failed: {e}") from e

    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def delete(self, session_id: UUID) -> bool:
        """
        Delete a session and all related data (CASCADE).

        Args:
            session_id: Session UUID

        Returns:
            bool: True if deleted, False if not found

        Raises:
            SessionRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM sessions
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                deleted = result != "DELETE 0"
                if deleted:
                    logger.info(f"Deleted session {session_id}")
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise SessionRepositoryError(f"Session deletion failed: {e}") from e

    # ========================================================================
    # CHECKPOINT OPERATIONS
    # ========================================================================

    async def add_checkpoint(self, session_id: UUID, checkpoint: Checkpoint) -> None:
        """
        Add a checkpoint to a session.

        Args:
            session_id: Session UUID
            checkpoint: Checkpoint to add

        Raises:
            SessionRepositoryError: If operation fails
        """
        try:
            async with self.db.transaction() as conn:
                await conn.execute(
                    """
                    INSERT INTO checkpoints (
                        session_id, stage_number, checkpoint_timestamp,
                        data_snapshot, validation_passed
                    ) VALUES ($1, $2, $3, $4, $5)
                    """,
                    session_id,
                    checkpoint.stage_number,
                    checkpoint.timestamp,
                    json.dumps(checkpoint.data_snapshot),
                    checkpoint.validation_status,
                )

                logger.info(
                    f"Added checkpoint for session {session_id}, stage {checkpoint.stage_number}"
                )

        except Exception as e:
            logger.error(f"Failed to add checkpoint for session {session_id}: {e}")
            raise SessionRepositoryError(f"Checkpoint creation failed: {e}") from e

    async def get_latest_checkpoint(self, session_id: UUID) -> Optional[Checkpoint]:
        """
        Get the most recent checkpoint for a session.

        Args:
            session_id: Session UUID

        Returns:
            Optional[Checkpoint]: Latest checkpoint or None

        Raises:
            SessionRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT stage_number, checkpoint_timestamp,
                           data_snapshot, validation_passed
                    FROM checkpoints
                    WHERE session_id = $1
                    ORDER BY checkpoint_timestamp DESC
                    LIMIT 1
                    """,
                    session_id,
                )

                if row is None:
                    return None

                return Checkpoint(
                    stage_number=row["stage_number"],
                    timestamp=row["checkpoint_timestamp"],
                    data_snapshot=json.loads(row["data_snapshot"]),
                    validation_status=row["validation_passed"],
                )

        except Exception as e:
            logger.error(f"Failed to get latest checkpoint for session {session_id}: {e}")
            raise SessionRepositoryError(f"Checkpoint retrieval failed: {e}") from e

    # ========================================================================
    # CONVERSATION OPERATIONS
    # ========================================================================

    async def add_message(self, session_id: UUID, message: Message) -> None:
        """
        Add a message to session conversation history.

        Args:
            session_id: Session UUID
            message: Message to add

        Raises:
            SessionRepositoryError: If operation fails
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

        except Exception as e:
            logger.error(f"Failed to add message for session {session_id}: {e}")
            raise SessionRepositoryError(f"Message creation failed: {e}") from e

    async def get_conversation_history(self, session_id: UUID) -> list[Message]:
        """
        Get full conversation history for a session.

        Args:
            session_id: Session UUID

        Returns:
            List[Message]: Ordered conversation messages

        Raises:
            SessionRepositoryError: If query fails
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
            logger.error(f"Failed to get conversation history for session {session_id}: {e}")
            raise SessionRepositoryError(f"Conversation retrieval failed: {e}") from e

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    async def count_active_sessions(self) -> int:
        """
        Count total number of active sessions.

        Returns:
            int: Number of active sessions

        Raises:
            SessionRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                count = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM sessions
                    WHERE status = $1
                    """,
                    SessionStatus.IN_PROGRESS.value,
                )
                return count or 0

        except Exception as e:
            logger.error(f"Failed to count active sessions: {e}")
            raise SessionRepositoryError(f"Count query failed: {e}") from e

    async def mark_as_abandoned(self, session_id: UUID) -> None:
        """
        Mark a session as abandoned.

        Args:
            session_id: Session UUID

        Raises:
            SessionRepositoryError: If update fails
        """
        await self.update_status(session_id, SessionStatus.ABANDONED)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    async def _load_stage_data(self, conn: asyncpg.Connection, session_id: UUID) -> dict:
        """Load stage data for a session."""
        rows = await conn.fetch(
            """
            SELECT stage_number, field_name, field_value
            FROM stage_data
            WHERE session_id = $1
            ORDER BY stage_number
            """,
            session_id,
        )

        stage_data = {}
        for row in rows:
            stage_num = row["stage_number"]
            if stage_num not in stage_data:
                stage_data[stage_num] = {}
            stage_data[stage_num][row["field_name"]] = json.loads(row["field_value"])

        return stage_data

    async def _load_conversation_history(
        self, conn: asyncpg.Connection, session_id: UUID
    ) -> list[Message]:
        """Load conversation history for a session."""
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

    async def _load_checkpoints(
        self, conn: asyncpg.Connection, session_id: UUID
    ) -> list[Checkpoint]:
        """Load checkpoints for a session."""
        rows = await conn.fetch(
            """
            SELECT stage_number, checkpoint_timestamp,
                   data_snapshot, validation_passed
            FROM checkpoints
            WHERE session_id = $1
            ORDER BY checkpoint_timestamp ASC
            """,
            session_id,
        )

        checkpoints = []
        for row in rows:
            checkpoint = Checkpoint(
                stage_number=row["stage_number"],
                timestamp=row["checkpoint_timestamp"],
                data_snapshot=json.loads(row["data_snapshot"]),
                validation_status=row["validation_passed"],
            )
            checkpoints.append(checkpoint)

        return checkpoints
