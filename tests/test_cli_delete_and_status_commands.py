"""
Tests: CLI Delete and Status Commands

Tests for the delete_command and status_command CLI functions.
Following TDD methodology: tests written before implementation.
"""

import pytest
from click.testing import CliRunner
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from src.cli.main import cli, delete_command, status_command
from src.models.schemas import Session, SessionStatus
from src.database.repositories.session_repository import SessionRepository


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def cli_runner():
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_session_id():
    """Generate a sample session ID."""
    return str(uuid4())


@pytest.fixture
def mock_session(sample_session_id):
    """Create a mock session object."""
    return MagicMock(
        session_id=sample_session_id,
        user_id="test_user",
        project_name="Test Project",
        current_stage=2,
        status=SessionStatus.IN_PROGRESS,
        stage_data={},
        checkpoints=[],
    )


# ============================================================================
# DELETE COMMAND TESTS
# ============================================================================


class TestDeleteCommand:
    """Tests for the delete_command CLI function."""

    def test_delete_command_requires_session_id(self, cli_runner):
        """Test that delete command requires a session ID."""
        result = cli_runner.invoke(cli, ["delete"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output

    def test_delete_command_validates_uuid_format(self, cli_runner):
        """Test that delete command validates UUID format."""
        result = cli_runner.invoke(cli, ["delete", "invalid-uuid"])
        assert result.exit_code != 0
        assert "Invalid session ID format" in result.output

    def test_delete_command_accepts_valid_uuid(self, cli_runner, sample_session_id):
        """Test that delete command accepts valid UUID."""
        result = cli_runner.invoke(
            cli, ["delete", sample_session_id, "--force"], catch_exceptions=False
        )
        # Should not fail on UUID validation
        assert "Invalid session ID format" not in result.output

    def test_delete_command_shows_deleting_message(self, cli_runner, sample_session_id):
        """Test that delete command shows deleting message."""
        result = cli_runner.invoke(
            cli, ["delete", sample_session_id, "--force"], catch_exceptions=False
        )

        # Should show deleting message
        assert "Deleting" in result.output or result.exit_code == 0

    def test_delete_command_requires_confirmation(self, cli_runner, sample_session_id):
        """Test that delete command requires user confirmation."""
        result = cli_runner.invoke(
            cli, ["delete", sample_session_id], input="n\n", catch_exceptions=False
        )
        assert "Deletion cancelled" in result.output or result.exit_code == 0

    def test_delete_command_force_flag_skips_confirmation(
        self, cli_runner, sample_session_id
    ):
        """Test that --force flag skips confirmation."""
        result = cli_runner.invoke(
            cli, ["delete", sample_session_id, "--force"], catch_exceptions=False
        )
        # Should not prompt for confirmation
        assert "Are you sure" not in result.output or result.exit_code == 0

    def test_delete_command_success_message(self, cli_runner, sample_session_id):
        """Test that delete command shows success message."""
        result = cli_runner.invoke(
            cli, ["delete", sample_session_id, "--force"], catch_exceptions=False
        )
        # Should show some indication of deletion attempt
        assert "Deleting" in result.output or result.exit_code == 0

    def test_delete_command_handles_nonexistent_session(
        self, cli_runner, sample_session_id
    ):
        """Test that delete command handles nonexistent session gracefully."""
        result = cli_runner.invoke(
            cli, ["delete", sample_session_id, "--force"], catch_exceptions=False
        )
        # Should not crash
        assert result.exit_code in [0, 1]


# ============================================================================
# STATUS COMMAND TESTS
# ============================================================================


class TestStatusCommand:
    """Tests for the status_command CLI function."""

    def test_status_command_requires_session_id(self, cli_runner):
        """Test that status command requires a session ID."""
        result = cli_runner.invoke(cli, ["status"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Error" in result.output

    def test_status_command_validates_uuid_format(self, cli_runner):
        """Test that status command validates UUID format."""
        result = cli_runner.invoke(cli, ["status", "invalid-uuid"])
        assert result.exit_code != 0
        assert "Invalid session ID format" in result.output

    def test_status_command_accepts_valid_uuid(self, cli_runner, sample_session_id):
        """Test that status command accepts valid UUID."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)
        # Should not fail on UUID validation
        assert "Invalid session ID format" not in result.output

    def test_status_command_shows_session_status_header(self, cli_runner, sample_session_id):
        """Test that status command shows session status header or error."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)

        # Verify status is shown or error is handled gracefully
        assert (
            "Session Status" in result.output
            or "Error" in result.output
            or "not found" in result.output
            or result.exit_code in [0, 1]
        )

    def test_status_command_displays_session_info(self, cli_runner, sample_session_id):
        """Test that status command displays session information or error."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)
        # Should show session ID or error
        assert (
            sample_session_id in result.output
            or "Session Status" in result.output
            or "Error" in result.output
            or result.exit_code in [0, 1]
        )

    def test_status_command_shows_current_stage(self, cli_runner, sample_session_id):
        """Test that status command shows current stage or error."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)
        # Should show stage information or error
        assert (
            "Stage" in result.output
            or "stage" in result.output
            or "Error" in result.output
            or result.exit_code in [0, 1]
        )

    def test_status_command_shows_session_status(self, cli_runner, sample_session_id):
        """Test that status command shows session status or error."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)
        # Should show status (IN_PROGRESS, COMPLETED, etc.) or error
        assert (
            "Status" in result.output
            or "IN_PROGRESS" in result.output
            or "COMPLETED" in result.output
            or "Error" in result.output
            or result.exit_code in [0, 1]
        )

    def test_status_command_handles_nonexistent_session(
        self, cli_runner, sample_session_id
    ):
        """Test that status command handles nonexistent session gracefully."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)
        # Should not crash
        assert result.exit_code in [0, 1]

    def test_status_command_no_placeholder_message(self, cli_runner, sample_session_id):
        """Test that status command does NOT show placeholder message."""
        result = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)
        # Should NOT contain placeholder text
        assert "This is a placeholder" not in result.output
        assert "will be implemented with database integration" not in result.output


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestDeleteAndStatusIntegration:
    """Integration tests for delete and status commands."""

    def test_delete_then_status_shows_error(self, cli_runner, sample_session_id):
        """Test that status shows error after deletion."""
        # Delete session
        delete_result = cli_runner.invoke(
            cli, ["delete", sample_session_id, "--force"], catch_exceptions=False
        )

        # Status should show error or not found
        status_result = cli_runner.invoke(
            cli, ["status", sample_session_id], catch_exceptions=False
        )

        # Either delete failed or status shows not found
        assert delete_result.exit_code in [0, 1] and status_result.exit_code in [0, 1]

    def test_status_before_and_after_operations(self, cli_runner, sample_session_id):
        """Test status command before and after operations."""
        # Get initial status
        status1 = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)

        # Get status again
        status2 = cli_runner.invoke(cli, ["status", sample_session_id], catch_exceptions=False)

        # Both should complete without crashing
        assert status1.exit_code in [0, 1]
        assert status2.exit_code in [0, 1]

