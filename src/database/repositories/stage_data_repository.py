"""
Stage Data Repository

Provides CRUD operations for stage data storage.
Handles JSONB serialization for complex stage deliverables.
"""

import json
import logging
from typing import Any
from uuid import UUID

from src.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


class StageDataRepositoryError(Exception):
    """Base exception for stage data repository operations."""

    pass


class StageDataRepository:
    """
    Repository for stage data CRUD operations.

    Manages storage of structured responses for each of the 5 stages,
    with JSONB support for complex data structures.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize repository with database manager.

        Args:
            db_manager: Initialized DatabaseManager instance
        """
        self.db = db_manager

    # ========================================================================
    # SAVE OPERATIONS (CREATE/UPDATE - UPSERT pattern)
    # ========================================================================

    async def save_field(
        self,
        session_id: UUID,
        stage_number: int,
        field_name: str,
        field_value: Any,
        quality_score: float | None = None,
    ) -> None:
        """
        Save or update a single field for a stage (UPSERT).

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)
            field_name: Name of the field
            field_value: Value to store (will be JSON serialized)
            quality_score: Optional quality score (0-10)

        Raises:
            ValueError: If stage_number invalid or quality_score out of range
            StageDataRepositoryError: If save fails
        """
        if stage_number < 1 or stage_number > 5:
            raise ValueError(f"stage_number must be 1-5, got {stage_number}")

        if quality_score is not None and (quality_score < 0 or quality_score > 10):
            raise ValueError(f"quality_score must be 0-10, got {quality_score}")

        try:
            # Serialize value to JSON
            json_value = json.dumps(field_value, default=str)

            async with self.db.transaction() as conn:
                # UPSERT: Insert or update on conflict
                await conn.execute(
                    """
                    INSERT INTO stage_data (
                        session_id, stage_number, field_name,
                        field_value, quality_score
                    ) VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (session_id, stage_number, field_name)
                    DO UPDATE SET
                        field_value = EXCLUDED.field_value,
                        quality_score = EXCLUDED.quality_score,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    session_id,
                    stage_number,
                    field_name,
                    json_value,
                    quality_score,
                )

                logger.info(
                    f"Saved field '{field_name}' for session {session_id}, stage {stage_number}"
                )

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to save field '{field_name}': {e}")
            raise StageDataRepositoryError(f"Field save failed: {e}") from e

    async def save_stage_fields(
        self, session_id: UUID, stage_number: int, fields_dict: dict[str, Any]
    ) -> None:
        """
        Save multiple fields for a stage at once.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)
            fields_dict: Dictionary of field_name -> field_value

        Raises:
            ValueError: If stage_number invalid
            StageDataRepositoryError: If save fails
        """
        if stage_number < 1 or stage_number > 5:
            raise ValueError(f"stage_number must be 1-5, got {stage_number}")

        try:
            async with self.db.transaction() as conn:
                for field_name, field_value in fields_dict.items():
                    json_value = json.dumps(field_value, default=str)

                    await conn.execute(
                        """
                        INSERT INTO stage_data (
                            session_id, stage_number, field_name, field_value
                        ) VALUES ($1, $2, $3, $4)
                        ON CONFLICT (session_id, stage_number, field_name)
                        DO UPDATE SET
                            field_value = EXCLUDED.field_value,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        session_id,
                        stage_number,
                        field_name,
                        json_value,
                    )

                logger.info(
                    f"Saved {len(fields_dict)} fields for session {session_id}, "
                    f"stage {stage_number}"
                )

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to save stage fields: {e}")
            raise StageDataRepositoryError(f"Bulk field save failed: {e}") from e

    # ========================================================================
    # RETRIEVAL OPERATIONS
    # ========================================================================

    async def get_field(self, session_id: UUID, stage_number: int, field_name: str) -> Any | None:
        """
        Retrieve a specific field value.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)
            field_name: Name of the field

        Returns:
            Optional[Any]: Deserialized field value or None if not found

        Raises:
            StageDataRepositoryError: If retrieval fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT field_value
                    FROM stage_data
                    WHERE session_id = $1
                      AND stage_number = $2
                      AND field_name = $3
                    """,
                    session_id,
                    stage_number,
                    field_name,
                )

                if row is None:
                    return None

                # Deserialize JSON value
                return json.loads(row["field_value"])

        except Exception as e:
            logger.error(f"Failed to get field '{field_name}': {e}")
            raise StageDataRepositoryError(f"Field retrieval failed: {e}") from e

    async def get_stage_data(self, session_id: UUID, stage_number: int) -> dict[str, Any]:
        """
        Retrieve all field data for a specific stage.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)

        Returns:
            Dict[str, Any]: Dictionary of field_name -> field_value

        Raises:
            StageDataRepositoryError: If retrieval fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT field_name, field_value
                    FROM stage_data
                    WHERE session_id = $1 AND stage_number = $2
                    ORDER BY created_at ASC
                    """,
                    session_id,
                    stage_number,
                )

                stage_data = {}
                for row in rows:
                    stage_data[row["field_name"]] = json.loads(row["field_value"])

                return stage_data

        except Exception as e:
            logger.error(f"Failed to get stage {stage_number} data: {e}")
            raise StageDataRepositoryError(f"Stage data retrieval failed: {e}") from e

    async def get_all_stage_data(self, session_id: UUID) -> dict[int, dict[str, Any]]:
        """
        Retrieve all stage data for a session.

        Args:
            session_id: Session UUID

        Returns:
            Dict[int, Dict[str, Any]]: Nested dict {stage_number: {field_name: value}}

        Raises:
            StageDataRepositoryError: If retrieval fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT stage_number, field_name, field_value
                    FROM stage_data
                    WHERE session_id = $1
                    ORDER BY stage_number ASC, created_at ASC
                    """,
                    session_id,
                )

                all_data: dict[int, dict[str, Any]] = {}
                for row in rows:
                    stage_num = row["stage_number"]
                    if stage_num not in all_data:
                        all_data[stage_num] = {}
                    all_data[stage_num][row["field_name"]] = json.loads(row["field_value"])

                return all_data

        except Exception as e:
            logger.error(f"Failed to get all stage data: {e}")
            raise StageDataRepositoryError(f"All stage data retrieval failed: {e}") from e

    async def get_field_quality_score(
        self, session_id: UUID, stage_number: int, field_name: str
    ) -> float | None:
        """
        Get quality score for a specific field.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)
            field_name: Name of the field

        Returns:
            Optional[float]: Quality score or None

        Raises:
            StageDataRepositoryError: If retrieval fails
        """
        try:
            async with self.db.acquire() as conn:
                score = await conn.fetchval(
                    """
                    SELECT quality_score
                    FROM stage_data
                    WHERE session_id = $1
                      AND stage_number = $2
                      AND field_name = $3
                    """,
                    session_id,
                    stage_number,
                    field_name,
                )

                return score

        except Exception as e:
            logger.error(f"Failed to get quality score for field '{field_name}': {e}")
            raise StageDataRepositoryError(f"Quality score retrieval failed: {e}") from e

    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def delete_field(self, session_id: UUID, stage_number: int, field_name: str) -> bool:
        """
        Delete a specific field.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)
            field_name: Name of the field

        Returns:
            bool: True if deleted, False if not found

        Raises:
            StageDataRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM stage_data
                    WHERE session_id = $1
                      AND stage_number = $2
                      AND field_name = $3
                    """,
                    session_id,
                    stage_number,
                    field_name,
                )

                deleted = result != "DELETE 0"
                if deleted:
                    logger.info(
                        f"Deleted field '{field_name}' from session {session_id}, "
                        f"stage {stage_number}"
                    )
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete field '{field_name}': {e}")
            raise StageDataRepositoryError(f"Field deletion failed: {e}") from e

    async def delete_stage(self, session_id: UUID, stage_number: int) -> int:
        """
        Delete all fields for a specific stage.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)

        Returns:
            int: Number of fields deleted

        Raises:
            StageDataRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM stage_data
                    WHERE session_id = $1 AND stage_number = $2
                    """,
                    session_id,
                    stage_number,
                )

                # Extract count from "DELETE n" result
                count = int(result.split()[-1]) if result != "DELETE 0" else 0
                logger.info(
                    f"Deleted {count} fields from session {session_id}, stage {stage_number}"
                )
                return count

        except Exception as e:
            logger.error(f"Failed to delete stage {stage_number} data: {e}")
            raise StageDataRepositoryError(f"Stage deletion failed: {e}") from e

    async def delete_all_for_session(self, session_id: UUID) -> int:
        """
        Delete all stage data for a session.

        Args:
            session_id: Session UUID

        Returns:
            int: Number of fields deleted

        Raises:
            StageDataRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM stage_data
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                count = int(result.split()[-1]) if result != "DELETE 0" else 0
                logger.info(f"Deleted {count} fields for session {session_id}")
                return count

        except Exception as e:
            logger.error(f"Failed to delete all stage data for session {session_id}: {e}")
            raise StageDataRepositoryError(f"Session stage data deletion failed: {e}") from e

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    async def get_stages_completed(self, session_id: UUID) -> list[int]:
        """
        Get list of stage numbers that have data.

        Args:
            session_id: Session UUID

        Returns:
            List[int]: List of stage numbers with data (1-5)

        Raises:
            StageDataRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT DISTINCT stage_number
                    FROM stage_data
                    WHERE session_id = $1
                    ORDER BY stage_number ASC
                    """,
                    session_id,
                )

                return [row["stage_number"] for row in rows]

        except Exception as e:
            logger.error(f"Failed to get completed stages: {e}")
            raise StageDataRepositoryError(f"Completed stages query failed: {e}") from e

    async def is_stage_complete(
        self, session_id: UUID, stage_number: int, required_fields: list[str]
    ) -> bool:
        """
        Check if a stage has all required fields.

        Args:
            session_id: Session UUID
            stage_number: Stage number (1-5)
            required_fields: List of required field names

        Returns:
            bool: True if all required fields present

        Raises:
            StageDataRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT field_name
                    FROM stage_data
                    WHERE session_id = $1 AND stage_number = $2
                    """,
                    session_id,
                    stage_number,
                )

                existing_fields = {row["field_name"] for row in rows}
                required_set = set(required_fields)

                return required_set.issubset(existing_fields)

        except Exception as e:
            logger.error(f"Failed to check stage {stage_number} completeness: {e}")
            raise StageDataRepositoryError(f"Stage completeness check failed: {e}") from e

    async def get_field_history(self, session_id: UUID, field_name: str) -> list[dict[str, Any]]:
        """
        Get update history for a field across all stages.

        Args:
            session_id: Session UUID
            field_name: Name of the field

        Returns:
            List[Dict]: List of {stage_number, value, quality_score, updated_at}

        Raises:
            StageDataRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT stage_number, field_value, quality_score,
                           created_at, updated_at
                    FROM stage_data
                    WHERE session_id = $1 AND field_name = $2
                    ORDER BY updated_at DESC
                    """,
                    session_id,
                    field_name,
                )

                history = []
                for row in rows:
                    history.append(
                        {
                            "stage_number": row["stage_number"],
                            "value": json.loads(row["field_value"]),
                            "quality_score": row["quality_score"],
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"],
                        }
                    )

                return history

        except Exception as e:
            logger.error(f"Failed to get field history for '{field_name}': {e}")
            raise StageDataRepositoryError(f"Field history query failed: {e}") from e
