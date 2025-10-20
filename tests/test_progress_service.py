"""
Tests for ProgressService - Real-time progress tracking for questionnaire and charter generation.

TDD approach: Tests written first, implementation follows.
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any

from src.services.progress_service import (
    ProgressService,
    ProgressEvent,
    ProgressEventType,
    SessionProgress,
    StageProgress,
    CharterGenerationProgress,
)


@pytest.fixture
def progress_service():
    """Create a ProgressService instance for testing."""
    return ProgressService()


@pytest.fixture
def session_id():
    """Generate a test session ID."""
    return uuid4()


class TestProgressEventCreation:
    """Test ProgressEvent creation and validation."""

    def test_create_stage_completed_event(self):
        """Test creating a stage completed event."""
        event = ProgressEvent(
            event_type=ProgressEventType.STAGE_COMPLETED,
            session_id=uuid4(),
            stage_number=1,
            timestamp=datetime.now(),
            data={"questions_answered": 5, "quality_score": 8.5},
        )
        assert event.event_type == ProgressEventType.STAGE_COMPLETED
        assert event.stage_number == 1
        assert event.data["questions_answered"] == 5

    def test_create_charter_generating_event(self):
        """Test creating a charter generating event."""
        event = ProgressEvent(
            event_type=ProgressEventType.CHARTER_GENERATING,
            session_id=uuid4(),
            timestamp=datetime.now(),
            data={"progress": 0.25, "status": "GENERATING"},
        )
        assert event.event_type == ProgressEventType.CHARTER_GENERATING
        assert event.data["progress"] == 0.25

    def test_create_reflection_iteration_event(self):
        """Test creating a reflection iteration event."""
        event = ProgressEvent(
            event_type=ProgressEventType.REFLECTION_ITERATION,
            session_id=uuid4(),
            timestamp=datetime.now(),
            data={"iteration": 1, "status": "IN_PROGRESS"},
        )
        assert event.event_type == ProgressEventType.REFLECTION_ITERATION
        assert event.data["iteration"] == 1

    def test_create_error_event(self):
        """Test creating an error event."""
        event = ProgressEvent(
            event_type=ProgressEventType.ERROR,
            session_id=uuid4(),
            timestamp=datetime.now(),
            data={"error": "Stage validation failed", "details": "Missing field"},
        )
        assert event.event_type == ProgressEventType.ERROR
        assert "error" in event.data


class TestProgressServiceTracking:
    """Test ProgressService tracking functionality."""

    def test_initialize_session_progress(self, progress_service, session_id):
        """Test initializing session progress."""
        progress = progress_service.initialize_session(session_id)
        assert progress.session_id == session_id
        assert progress.status == "IN_PROGRESS"
        assert progress.current_stage == 0
        assert progress.questions_answered == 0

    def test_record_stage_started(self, progress_service, session_id):
        """Test recording stage started event."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_stage_started(session_id, stage_number=1)
        assert event.event_type == ProgressEventType.STAGE_STARTED
        assert event.stage_number == 1

    def test_record_question_answered(self, progress_service, session_id):
        """Test recording question answered event."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_question_answered(
            session_id, stage_number=1, question_id="q1", quality_score=8.5
        )
        assert event.event_type == ProgressEventType.QUESTION_ANSWERED
        assert event.data["quality_score"] == 8.5

    def test_record_stage_completed(self, progress_service, session_id):
        """Test recording stage completed event."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_stage_completed(
            session_id, stage_number=1, validation_passed=True
        )
        assert event.event_type == ProgressEventType.STAGE_COMPLETED
        assert event.data["validation_passed"] is True

    def test_record_charter_generation_started(self, progress_service, session_id):
        """Test recording charter generation started."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_charter_generation_started(session_id)
        assert event.event_type == ProgressEventType.CHARTER_GENERATING
        assert event.data["status"] == "STARTED"

    def test_record_charter_generation_progress(self, progress_service, session_id):
        """Test recording charter generation progress."""
        progress_service.initialize_session(session_id)
        progress_service.record_charter_generation_started(session_id)
        event = progress_service.record_charter_generation_progress(
            session_id, progress=0.5, current_section="Problem Definition"
        )
        assert event.data["progress"] == 0.5
        assert event.data["current_section"] == "Problem Definition"

    def test_record_reflection_iteration(self, progress_service, session_id):
        """Test recording reflection loop iteration."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_reflection_iteration(
            session_id, iteration_number=1, status="IN_PROGRESS"
        )
        assert event.event_type == ProgressEventType.REFLECTION_ITERATION
        assert event.data["iteration"] == 1

    def test_record_error(self, progress_service, session_id):
        """Test recording an error event."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_error(
            session_id, error_message="Validation failed", error_details="Missing field"
        )
        assert event.event_type == ProgressEventType.ERROR
        assert event.data["error"] == "Validation failed"


class TestSessionProgress:
    """Test SessionProgress model."""

    def test_session_progress_initialization(self, session_id):
        """Test SessionProgress initialization."""
        progress = SessionProgress(session_id=session_id)
        assert progress.session_id == session_id
        assert progress.status == "IN_PROGRESS"
        assert progress.current_stage == 0
        assert progress.questions_answered == 0
        assert progress.charter_status == "NOT_STARTED"

    def test_session_progress_update_stage(self, session_id):
        """Test updating session progress stage."""
        progress = SessionProgress(session_id=session_id)
        progress.current_stage = 1
        progress.questions_answered = 5
        assert progress.current_stage == 1
        assert progress.questions_answered == 5

    def test_session_progress_completion(self, session_id):
        """Test marking session as completed."""
        progress = SessionProgress(session_id=session_id)
        progress.status = "COMPLETED"
        progress.charter_status = "COMPLETED"
        assert progress.status == "COMPLETED"
        assert progress.charter_status == "COMPLETED"


class TestProgressEventRetrieval:
    """Test retrieving progress events."""

    def test_get_session_events(self, progress_service, session_id):
        """Test retrieving all events for a session."""
        progress_service.initialize_session(session_id)
        progress_service.record_stage_started(session_id, stage_number=1)
        progress_service.record_question_answered(
            session_id, stage_number=1, question_id="q1", quality_score=8.0
        )
        
        events = progress_service.get_session_events(session_id)
        assert len(events) >= 2
        assert events[0].event_type == ProgressEventType.STAGE_STARTED

    def test_get_session_progress(self, progress_service, session_id):
        """Test retrieving current session progress."""
        progress_service.initialize_session(session_id)
        progress_service.record_stage_started(session_id, stage_number=1)
        
        progress = progress_service.get_session_progress(session_id)
        assert progress.session_id == session_id
        assert progress.current_stage == 1

    def test_get_stage_progress(self, progress_service, session_id):
        """Test retrieving progress for a specific stage."""
        progress_service.initialize_session(session_id)
        progress_service.record_stage_started(session_id, stage_number=1)
        progress_service.record_question_answered(
            session_id, stage_number=1, question_id="q1", quality_score=8.0
        )
        
        stage_progress = progress_service.get_stage_progress(session_id, stage_number=1)
        assert stage_progress.stage_number == 1
        assert stage_progress.questions_answered == 1


class TestProgressEventPersistence:
    """Test persisting progress events to database."""

    def test_save_progress_event(self, progress_service, session_id):
        """Test saving a progress event."""
        progress_service.initialize_session(session_id)
        event = progress_service.record_stage_started(session_id, stage_number=1)
        
        # Event should be persisted
        saved_event = progress_service.get_event_by_id(event.id)
        assert saved_event is not None
        assert saved_event.event_type == ProgressEventType.STAGE_STARTED

    def test_retrieve_persisted_events(self, progress_service, session_id):
        """Test retrieving persisted events."""
        progress_service.initialize_session(session_id)
        progress_service.record_stage_started(session_id, stage_number=1)
        progress_service.record_question_answered(
            session_id, stage_number=1, question_id="q1", quality_score=8.0
        )
        
        events = progress_service.get_session_events(session_id)
        assert len(events) >= 2

