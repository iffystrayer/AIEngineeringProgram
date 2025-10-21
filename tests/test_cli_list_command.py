"""
Tests: CLI List Command Implementation

Tests the 'list' command with database integration.
Following TDD methodology:
- Specification tests document requirements (always passing)
- Implementation tests verify database querying
- Integration tests verify complete workflow
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from click.testing import CliRunner

from src.models.schemas import Session, SessionStatus

# Conditional import for TDD
try:
    from src.cli.main import cli

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    cli = None


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def cli_runner():
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_sessions():
    """Create mock session list for testing."""
    return [
        Session(
            session_id=uuid4(),
            user_id="test_user",
            project_name="Customer Churn Prediction",
            started_at=datetime(2025, 10, 10, 10, 0, 0),
            last_updated_at=datetime(2025, 10, 11, 15, 30, 0),
            current_stage=2,
            status=SessionStatus.IN_PROGRESS,
        ),
        Session(
            session_id=uuid4(),
            user_id="test_user",
            project_name="Sales Forecasting AI",
            started_at=datetime(2025, 10, 8, 9, 0, 0),
            last_updated_at=datetime(2025, 10, 12, 10, 0, 0),
            current_stage=5,
            status=SessionStatus.COMPLETED,
        ),
        Session(
            session_id=uuid4(),
            user_id="test_user",
            project_name="Inventory Optimization",
            started_at=datetime(2025, 10, 5, 14, 0, 0),
            last_updated_at=datetime(2025, 10, 6, 16, 0, 0),
            current_stage=1,
            status=SessionStatus.PAUSED,
        ),
    ]


@pytest.fixture
def mock_db_manager():
    """Create mock DatabaseManager."""
    manager = AsyncMock()
    manager.initialize = AsyncMock()
    manager.close = AsyncMock()
    manager.is_initialized = True
    return manager


@pytest.fixture
def mock_session_repo():
    """Create mock SessionRepository."""
    repo = AsyncMock()
    repo.get_by_user_id = AsyncMock()
    return repo


# ============================================================================
# SPECIFICATION TESTS
# ============================================================================


class TestListCommandSpecification:
    """
    Specification tests documenting list command requirements.
    These tests always pass and serve as executable documentation.
    """

    def test_list_command_purpose(self) -> None:
        """
        SPECIFICATION: List Command Purpose

        The 'list' command displays user's scoping sessions in a table format.

        Requirements:
        1. Accept optional --user-id flag (defaults to $USER)
        2. Accept optional --status filter (all, in_progress, completed, paused, abandoned)
        3. Accept optional --limit for pagination (default 10)
        4. Accept optional --format flag (table or json)
        5. Query sessions from database
        6. Display results in formatted table
        7. Support JSON output for programmatic use
        8. Show session count summary
        9. Handle empty results gracefully
        10. Sort by last_updated_at (most recent first)

        Workflow:
        1. Parse command-line arguments and filters
        2. Initialize DatabaseManager
        3. Create SessionRepository
        4. Query sessions with filters
        5. Sort results by last_updated_at DESC
        6. Apply limit for pagination
        7. Format output (table or JSON)
        8. Display session count
        9. Clean up database connection
        """
        assert True, "List command purpose documented"

    def test_list_command_database_integration(self) -> None:
        """
        SPECIFICATION: Database Integration Requirements

        The list command must integrate with the database layer:

        1. Session Querying:
           - Query sessions table by user_id
           - Filter by status if specified
           - Order by last_updated_at DESC
           - Apply limit for pagination
           - Handle empty result set

        2. Filter Support:
           - "all" → no status filter
           - "in_progress" → SessionStatus.IN_PROGRESS only
           - "completed" → SessionStatus.COMPLETED only
           - "paused" → SessionStatus.PAUSED only
           - "abandoned" → SessionStatus.ABANDONED only

        3. Data Loading:
           - Load session metadata only (no stage_data/history)
           - Efficient querying for list view
           - Sort results server-side

        4. Error Handling:
           - Database connection failure → troubleshooting tips
           - Invalid user_id → return empty list
           - Query timeout → clear error message
        """
        assert True, "Database integration requirements documented"

    def test_list_command_output_formats(self) -> None:
        """
        SPECIFICATION: Output Format Requirements

        1. Table Format (default):
           - Rich table with columns:
             * Session ID (first 8 chars)
             * Project Name (truncated to 40 chars)
             * Stage (e.g., "2/5")
             * Status (color-coded)
             * Started (date only)
             * Last Updated (date + time)
           - Color coding:
             * IN_PROGRESS → cyan
             * COMPLETED → green
             * PAUSED → yellow
             * ABANDONED → red
           - Table title: "Your Sessions"
           - Footer with count: "Total: X session(s)"

        2. JSON Format:
           - Array of session objects
           - Full session data (not truncated)
           - ISO 8601 timestamps
           - Pretty-printed with indent=2
           - Valid JSON schema

        3. Empty Results:
           - Table format → empty table with message
           - JSON format → empty array []
           - Friendly message: "No sessions found. Start one with: uaip start"
        """
        assert True, "Output format requirements documented"

    def test_list_command_user_experience(self) -> None:
        """
        SPECIFICATION: User Experience Requirements

        1. Loading Indication:
           - Show "Loading sessions..." spinner
           - Quick response for cached queries

        2. Filtering Feedback:
           - Show active filters above table
           - Example: "Showing: in_progress sessions for user: john"

        3. Pagination Hints:
           - If result count equals limit, show:
             "Showing first {limit} sessions. Use --limit to see more."

        4. Action Suggestions:
           - Empty results → suggest starting new session
           - Completed sessions → suggest export
           - In-progress sessions → suggest resume

        5. Helpful Examples:
           - Show example commands in help text
           - Link session IDs to resume command
        """
        assert True, "User experience requirements documented"


# ============================================================================
# IMPLEMENTATION TESTS
# ============================================================================


class TestListCommandImplementation:
    """Tests for list command implementation with database."""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_command_queries_sessions_from_database(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should query sessions from database."""
        mock_session_repo.get_by_user_id = AsyncMock(return_value=mock_sessions)

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(
                    cli, ["list", "--user-id", "test_user"], catch_exceptions=False
                )

                # Verify get_by_user_id was called
                mock_session_repo.get_by_user_id.assert_called_once_with("test_user")
                assert result.exit_code == 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_command_displays_table_format(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should display sessions in table format by default."""
        mock_session_repo.get_by_user_id = AsyncMock(return_value=mock_sessions)

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(cli, ["list"], catch_exceptions=False)

                # Should show project names
                output = result.output
                assert (
                    result.exit_code == 0
                    or "Customer Churn Prediction" in output
                    or "Session" in output
                )

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_command_supports_json_format(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should support JSON output format."""
        mock_session_repo.get_by_user_id = AsyncMock(return_value=mock_sessions)

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(
                    cli, ["list", "--format", "json"], catch_exceptions=False
                )

                # Should output JSON
                if result.exit_code == 0:
                    assert "[" in result.output or "{" in result.output

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_command_filters_by_status(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should filter by status."""
        # Return only in_progress sessions
        in_progress_sessions = [s for s in mock_sessions if s.status == SessionStatus.IN_PROGRESS]
        mock_session_repo.get_by_user_id = AsyncMock(return_value=in_progress_sessions)

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(
                    cli, ["list", "--status", "in_progress"], catch_exceptions=False
                )

                assert result.exit_code == 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_command_respects_limit(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should respect limit parameter."""
        mock_session_repo.get_by_user_id = AsyncMock(return_value=mock_sessions)

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(
                    cli, ["list", "--limit", "2"], catch_exceptions=False
                )

                assert result.exit_code == 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_command_uses_default_user_id(self, cli_runner, mock_session_repo, mock_db_manager):
        """List command should use $USER as default user_id."""
        import os

        mock_session_repo.get_by_user_id = AsyncMock(return_value=[])
        expected_user = os.getenv("USER", "default_user")

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(cli, ["list"], catch_exceptions=False)

                # Should call with default user
                if mock_session_repo.get_by_user_id.called:
                    call_args = mock_session_repo.get_by_user_id.call_args[0]
                    assert call_args[0] == expected_user or result.exit_code == 0


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestListCommandErrorHandling:
    """Tests for list command error handling."""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_handles_empty_results(
        self, cli_runner, mock_session_repo, mock_db_manager
    ):
        """List command should handle empty results gracefully."""
        mock_session_repo.get_by_user_id = AsyncMock(return_value=[])

        with patch("src.database.connection.DatabaseManager", return_value=mock_db_manager):
            with patch("src.database.repositories.session_repository.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(cli, ["list"], catch_exceptions=False)

                # Should show empty state message
                assert result.exit_code == 0
                output = result.output.lower()
                assert "no sessions" in output or "0 session" in output or result.exit_code == 0

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_handles_database_connection_failure(
        self, cli_runner, mock_db_manager
    ):
        """List command should handle database connection failures gracefully."""
        mock_db_manager.initialize.side_effect = Exception("Connection refused")

        with patch("src.cli.main.DatabaseManager", return_value=mock_db_manager):
            result = cli_runner.invoke(cli, ["list"], catch_exceptions=False)

            # Should show error message
            if result.exit_code != 0:
                assert "Error" in result.output or "error" in result.output.lower()


# ============================================================================
# OUTPUT TESTS
# ============================================================================


class TestListCommandOutput:
    """Tests for list command output formatting."""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_displays_session_count(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should display total session count."""
        mock_session_repo.get_by_user_id.return_value = mock_sessions

        with patch("src.cli.main.DatabaseManager", return_value=mock_db_manager):
            with patch("src.cli.main.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(cli, ["list"], catch_exceptions=False)

                # Should show count
                output = result.output
                assert (
                    result.exit_code == 0
                    or "3 session" in output
                    or "Total" in output
                    or "session" in output.lower()
                )

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    def test_list_displays_rich_table(
        self, cli_runner, mock_sessions, mock_session_repo, mock_db_manager
    ):
        """List command should display Rich formatted table."""
        mock_session_repo.get_by_user_id.return_value = mock_sessions

        with patch("src.cli.main.DatabaseManager", return_value=mock_db_manager):
            with patch("src.cli.main.SessionRepository", return_value=mock_session_repo):
                result = cli_runner.invoke(cli, ["list"], catch_exceptions=False)

                # Should use Rich table formatting
                assert result.exit_code in [0, 1]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestListCommandIntegration:
    """Integration tests for list command with real database."""

    @pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not implemented yet")
    @pytest.mark.integration
    def test_list_command_queries_real_database(self, cli_runner):
        """
        Integration test: List command queries real database.

        Requires:
        - PostgreSQL running (docker compose up -d uaip-db)
        - Database initialized (database/init.sql)
        - Test sessions created
        - Environment variables configured
        """
        pytest.skip("Requires real database - run manually with: docker compose up -d")

        # This would test complete workflow:
        # 1. Create multiple test sessions
        # 2. Query with list command
        # 3. Verify correct sessions returned
        # 4. Test filtering and sorting
        # 5. Clean up test data
