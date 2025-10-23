"""
Charter Repository

Provides CRUD operations for AI Project Charter management.
Handles storage and retrieval of final charter documents.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from src.database.connection import DatabaseManager
from src.models.schemas import AIProjectCharter, GovernanceDecision

logger = logging.getLogger(__name__)


class CharterRepositoryError(Exception):
    """Base exception for charter repository operations."""

    pass


class CharterRepository:
    """
    Repository for AI Project Charter CRUD operations.

    Manages persistence of final charter documents with governance decisions.
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

    async def create_charter(
        self,
        charter: AIProjectCharter,
        markdown_path: Optional[str] = None,
        pdf_path: Optional[str] = None,
    ) -> None:
        """
        Create a charter for a session.

        Args:
            charter: AIProjectCharter to persist
            markdown_path: Optional path to markdown export
            pdf_path: Optional path to PDF export

        Raises:
            CharterRepositoryError: If operation fails
        """
        try:
            # Convert charter to JSON-serializable dict
            charter_dict = self._charter_to_dict(charter)

            async with self.db.transaction() as conn:
                await conn.execute(
                    """
                    INSERT INTO project_charters (
                        session_id, charter_content, governance_decision,
                        generated_at, markdown_path, pdf_path, version
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (session_id)
                    DO UPDATE SET
                        charter_content = EXCLUDED.charter_content,
                        governance_decision = EXCLUDED.governance_decision,
                        generated_at = EXCLUDED.generated_at,
                        markdown_path = EXCLUDED.markdown_path,
                        pdf_path = EXCLUDED.pdf_path,
                        version = EXCLUDED.version
                    """,
                    charter.session_id,
                    json.dumps(charter_dict),
                    charter.governance_decision.value,
                    charter.completed_at,
                    markdown_path,
                    pdf_path,
                    charter.version,
                )

                logger.info(f"Created/updated charter for session {charter.session_id}")

        except Exception as e:
            logger.error(f"Failed to create charter: {e}")
            raise CharterRepositoryError(f"Charter creation failed: {e}") from e

    # ========================================================================
    # RETRIEVAL OPERATIONS
    # ========================================================================

    async def get_charter_by_session(self, session_id: UUID) -> Optional[AIProjectCharter]:
        """
        Retrieve charter by session ID.

        Args:
            session_id: Session UUID

        Returns:
            Optional[AIProjectCharter]: Charter if exists, None otherwise

        Raises:
            CharterRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT charter_content, governance_decision,
                           generated_at, markdown_path, pdf_path, version
                    FROM project_charters
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                if row is None:
                    return None

                # Deserialize charter from JSON
                charter_dict = json.loads(row["charter_content"])
                charter = self._dict_to_charter(charter_dict)

                return charter

        except Exception as e:
            logger.error(f"Failed to get charter: {e}")
            raise CharterRepositoryError(f"Charter retrieval failed: {e}") from e

    async def get_charter_paths(self, session_id: UUID) -> Optional[Dict[str, Optional[str]]]:
        """
        Get file paths for charter exports.

        Args:
            session_id: Session UUID

        Returns:
            Optional[dict]: Dict with 'markdown_path' and 'pdf_path' keys

        Raises:
            CharterRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT markdown_path, pdf_path
                    FROM project_charters
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                if row is None:
                    return None

                return {
                    "markdown_path": row["markdown_path"],
                    "pdf_path": row["pdf_path"],
                }

        except Exception as e:
            logger.error(f"Failed to get charter paths: {e}")
            raise CharterRepositoryError(f"Charter paths retrieval failed: {e}") from e

    # ========================================================================
    # UPDATE OPERATIONS
    # ========================================================================

    async def update_charter_paths(
        self,
        session_id: UUID,
        markdown_path: Optional[str] = None,
        pdf_path: Optional[str] = None,
    ) -> None:
        """
        Update file paths for charter exports.

        Args:
            session_id: Session UUID
            markdown_path: Path to markdown file
            pdf_path: Path to PDF file

        Raises:
            CharterRepositoryError: If update fails
            ValueError: If charter doesn't exist
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    UPDATE project_charters
                    SET markdown_path = COALESCE($2, markdown_path),
                        pdf_path = COALESCE($3, pdf_path)
                    WHERE session_id = $1
                    """,
                    session_id,
                    markdown_path,
                    pdf_path,
                )

                if result == "UPDATE 0":
                    raise ValueError(f"Charter for session {session_id} not found")

                logger.info(f"Updated charter paths for session {session_id}")

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to update charter paths: {e}")
            raise CharterRepositoryError(f"Charter paths update failed: {e}") from e

    # ========================================================================
    # DELETE OPERATIONS
    # ========================================================================

    async def delete_charter(self, session_id: UUID) -> bool:
        """
        Delete charter for a session.

        Args:
            session_id: Session UUID

        Returns:
            bool: True if deleted, False if not found

        Raises:
            CharterRepositoryError: If deletion fails
        """
        try:
            async with self.db.transaction() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM project_charters
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                deleted = result != "DELETE 0"
                if deleted:
                    logger.info(f"Deleted charter for session {session_id}")
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete charter: {e}")
            raise CharterRepositoryError(f"Charter deletion failed: {e}") from e

    # ========================================================================
    # QUERY OPERATIONS
    # ========================================================================

    async def exists(self, session_id: UUID) -> bool:
        """
        Check if charter exists for a session.

        Args:
            session_id: Session UUID

        Returns:
            bool: True if charter exists

        Raises:
            CharterRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                exists = await conn.fetchval(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM project_charters
                        WHERE session_id = $1
                    )
                    """,
                    session_id,
                )
                return bool(exists)

        except Exception as e:
            logger.error(f"Failed to check charter existence: {e}")
            raise CharterRepositoryError(f"Charter existence check failed: {e}") from e

    async def get_governance_decision(self, session_id: UUID) -> Optional[GovernanceDecision]:
        """
        Get governance decision for a charter.

        Args:
            session_id: Session UUID

        Returns:
            Optional[GovernanceDecision]: Governance decision or None

        Raises:
            CharterRepositoryError: If query fails
        """
        try:
            async with self.db.acquire() as conn:
                decision = await conn.fetchval(
                    """
                    SELECT governance_decision
                    FROM project_charters
                    WHERE session_id = $1
                    """,
                    session_id,
                )

                return GovernanceDecision(decision) if decision else None

        except Exception as e:
            logger.error(f"Failed to get governance decision: {e}")
            raise CharterRepositoryError(f"Governance decision retrieval failed: {e}") from e

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _charter_to_dict(self, charter: AIProjectCharter) -> dict:
        """Convert AIProjectCharter to JSON-serializable dict."""
        # Simple implementation - convert dataclass to dict
        # In production, use dataclasses.asdict() or custom serialization
        return {
            "session_id": str(charter.session_id),
            "project_name": charter.project_name,
            "created_at": charter.created_at.isoformat(),
            "completed_at": charter.completed_at.isoformat(),
            "governance_decision": charter.governance_decision.value,
            "overall_feasibility": charter.overall_feasibility.value,
            "critical_success_factors": charter.critical_success_factors,
            "major_risks": charter.major_risks,
            "version": charter.version,
            # Simplified - in production, serialize full stage deliverables
        }

    def _dict_to_charter(self, charter_dict: dict) -> AIProjectCharter:
        """Convert dict to AIProjectCharter (simplified)."""
        # Simplified implementation for now
        # In production, fully deserialize all stage deliverables
        from uuid import UUID

        return AIProjectCharter(
            session_id=UUID(charter_dict["session_id"]),
            project_name=charter_dict["project_name"],
            created_at=datetime.fromisoformat(charter_dict["created_at"]),
            completed_at=datetime.fromisoformat(charter_dict["completed_at"]),
            problem_statement=None,  # type: ignore
            metric_alignment_matrix=None,  # type: ignore
            data_quality_scorecard=None,  # type: ignore
            user_context=None,  # type: ignore
            ethical_risk_report=None,  # type: ignore
            governance_decision=GovernanceDecision(charter_dict["governance_decision"]),
            overall_feasibility=charter_dict.get("overall_feasibility", "medium"),  # type: ignore
            critical_success_factors=charter_dict.get("critical_success_factors", []),
            major_risks=charter_dict.get("major_risks", []),
            version=charter_dict.get("version", "1.0"),
        )
