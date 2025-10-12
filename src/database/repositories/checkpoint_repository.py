"""
Checkpoint Repository

Provides CRUD operations for checkpoint management.
Focused repository for session recovery points.
"""

import json
import logging
from uuid import UUID

from src.database.connection import DatabaseManager
from src.models.schemas import Checkpoint

logger = logging.getLogger(__name__)


class CheckpointRepositoryError(Exception):
    """Base exception for checkpoint repository operations."""

    pass


class CheckpointRepository:
    """
    Repository for checkpoint CRUD operations.

    Manages persistence of stage completion checkpoints for session recovery.
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

    async def create_checkpoint(self, session_id: UUID, checkpoint: Checkpoint) -> None:
        """
        Create a checkpoint for a session.

        Args:
            session_id: Session UUID
            checkpoint: Checkpoint to create

        Raises:
            CheckpointRepositoryError: If operation fails
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
                    f"Created checkpoint for session {session_id}, "
                    f"stage {checkpoint.stage_number}"
                )

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            raise CheckpointRepositoryError(f"Checkpoint creation failed: {e}") from e

    # ========================================================================
    # RETRIEVAL OPERATIONS
    # ========================================================================

    async def get_latest_checkpoint(self, session_id: UUID) -> Checkpoint | None:
        """
        Get the most recent checkpoint for a session.

        Args:
            session_id: Session UUID

        Returns:
            Optional[Checkpoint]: Latest checkpoint or None

        Raises:
            CheckpointRepositoryError: If query fails
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
            logger.error(f"Failed to get latest checkpoint: {e}")
            raise CheckpointRepositoryError(f"Checkpoint retrieval failed: {e}") from e

    async def get_checkpoint_by_stage(
        self, session_id: UUID, stage_number: int
    ) -> Checkpoint | None:
        """
        Get checkpoint for a specific stage.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)

        Returns:
            Optional[Checkpoint]: Checkpoint for the stage or None

        Raises:
            CheckpointRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT stage_number, checkpoint_timestamp,
                           data_snapshot, validation_passed
                    FROM checkpoints
                    WHERE session_id = $1 AND stage_number = $2
                    ORDER BY checkpoint_timestamp DESC
                    LIMIT 1
                    """,
                    session_id,
                    stage_number,
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
            logger.error(f"Failed to get checkpoint for stage {stage_number}: {e}")
            raise CheckpointRepositoryError(f"Stage checkpoint retrieval failed: {e}") from e

    async def get_all_checkpoints(self, session_id: UUID) -> list[Checkpoint]:
        """
        Get all checkpoints for a session.

        Args:
            session_id: Session UUID

        Returns:
            List[Checkpoint]: All checkpoints in chronological order

        Raises:
            CheckpointRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
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

        except Exception as e:
            logger.error(f"Failed to get all checkpoints: {e}")
            raise CheckpointRepositoryError(f"Checkpoints retrieval failed: {e}") from e

    async def get_validated_checkpoints(self, session_id: UUID) -> list[Checkpoint]:
        """
        Get only validated (passed) checkpoints.

        Args:
            session_id: Session UUID

        Returns:
            List[Checkpoint]: Validated checkpoints

        Raises:
            CheckpointRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT stage_number, checkpoint_timestamp,
                           data_snapshot, validation_passed
                    FROM checkpoints
                    WHERE session_id = $1 AND validation_passed = TRUE
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

        except Exception as e:
            logger.error(f"Failed to get validated checkpoints: {e}")
            raise CheckpointRepositoryError(f"Validated checkpoints retrieval failed: {e}") from e

    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def delete_checkpoint(self, session_id: UUID, stage_number: int) -> bool:
        """
        Delete checkpoint for a specific stage.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)

        Returns:
            bool: True if deleted, False if not found

        Raises:
            CheckpointRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM checkpoints
                    WHERE session_id = $1 AND stage_number = $2
                    """,
                    session_id,
                    stage_number,
                )

                deleted = result != "DELETE 0"
                if deleted:
                    logger.info(
                        f"Deleted checkpoint for session {session_id}, stage {stage_number}"
                    )
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}")
            raise CheckpointRepositoryError(f"Checkpoint deletion failed: {e}") from e

    async def delete_all_for_session(self, session_id: UUID) -> int:
        """
        Delete all checkpoints for a session.

        Args:
            session_id: Session UUID

        Returns:
            int: Number of checkpoints deleted

        Raises:
            CheckpointRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM checkpoints
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                count = int(result.split()[-1]) if result != "DELETE 0" else 0
                logger.info(f"Deleted {count} checkpoints for session {session_id}")
                return count

        except Exception as e:
            logger.error(f"Failed to delete all checkpoints: {e}")
            raise CheckpointRepositoryError(f"All checkpoints deletion failed: {e}") from e

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    async def count_checkpoints(self, session_id: UUID) -> int:
        """
        Count total checkpoints for a session.

        Args:
            session_id: Session UUID

        Returns:
            int: Total checkpoint count

        Raises:
            CheckpointRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                count = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM checkpoints
                    WHERE session_id = $1
                    """,
                    session_id,
                )
                return count or 0

        except Exception as e:
            logger.error(f"Failed to count checkpoints: {e}")
            raise CheckpointRepositoryError(f"Checkpoint count failed: {e}") from e

    async def has_checkpoint_for_stage(self, session_id: UUID, stage_number: int) -> bool:
        """
        Check if checkpoint exists for a stage.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)

        Returns:
            bool: True if checkpoint exists

        Raises:
            CheckpointRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                exists = await conn.fetchval(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM checkpoints
                        WHERE session_id = $1 AND stage_number = $2
                    )
                    """,
                    session_id,
                    stage_number,
                )
                return bool(exists)

        except Exception as e:
            logger.error(f"Failed to check checkpoint existence: {e}")
            raise CheckpointRepositoryError(f"Checkpoint existence check failed: {e}") from e
