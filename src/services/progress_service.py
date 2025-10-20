"""
ProgressService: Real-time progress tracking for questionnaire and charter generation.

Tracks:
- Session progress (current stage, questions answered)
- Stage progress (questions answered, validation status)
- Charter generation progress (current section, progress percentage)
- Reflection loop iterations
- Errors and failures

All events are persisted to database for real-time streaming to frontend.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.database.connection import DatabaseManager


class ProgressEventType(Enum):
    """Types of progress events."""
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    QUESTION_ANSWERED = "question_answered"
    CHARTER_GENERATING = "charter_generating"
    CHARTER_COMPLETED = "charter_completed"
    REFLECTION_ITERATION = "reflection_iteration"
    ERROR = "error"


@dataclass
class ProgressEvent:
    """A single progress event."""
    event_type: ProgressEventType
    session_id: UUID
    timestamp: datetime
    data: Dict[str, Any]
    stage_number: Optional[int] = None
    id: UUID = field(default_factory=uuid4)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "session_id": str(self.session_id),
            "stage_number": self.stage_number,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


@dataclass
class StageProgress:
    """Progress for a specific stage."""
    stage_number: int
    status: str  # NOT_STARTED, IN_PROGRESS, COMPLETED
    questions_answered: int = 0
    total_questions: int = 0
    quality_score: float = 0.0
    validation_passed: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class CharterGenerationProgress:
    """Progress for charter generation."""
    status: str  # NOT_STARTED, GENERATING, COMPLETED
    progress: float = 0.0  # 0.0 to 1.0
    current_section: str = ""
    reflection_iterations: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class SessionProgress:
    """Overall session progress."""
    session_id: UUID
    status: str = "IN_PROGRESS"  # IN_PROGRESS, COMPLETED, ABANDONED
    current_stage: int = 0
    questions_answered: int = 0
    charter_status: str = "NOT_STARTED"
    stage_progress: Dict[int, StageProgress] = field(default_factory=dict)
    charter_progress: CharterGenerationProgress = field(
        default_factory=lambda: CharterGenerationProgress(status="NOT_STARTED")
    )
    last_updated: datetime = field(default_factory=datetime.now)


class ProgressService:
    """Service for tracking progress in real-time."""

    def __init__(self, db_manager: Optional["DatabaseManager"] = None):
        """Initialize the progress service.

        Args:
            db_manager: Optional database manager for persistence.
                       If not provided, uses in-memory storage only.
        """
        self.db_manager = db_manager
        # In-memory cache for active sessions
        self.sessions: Dict[UUID, SessionProgress] = {}
        self.events: Dict[UUID, List[ProgressEvent]] = {}

    def initialize_session(self, session_id: UUID) -> SessionProgress:
        """Initialize progress tracking for a new session."""
        progress = SessionProgress(session_id=session_id)
        self.sessions[session_id] = progress
        self.events[session_id] = []
        return progress

    def record_stage_started(self, session_id: UUID, stage_number: int) -> ProgressEvent:
        """Record that a stage has started."""
        event = ProgressEvent(
            event_type=ProgressEventType.STAGE_STARTED,
            session_id=session_id,
            stage_number=stage_number,
            timestamp=datetime.now(),
            data={"stage": stage_number, "status": "STARTED"},
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            self.sessions[session_id].current_stage = stage_number
            self.sessions[session_id].stage_progress[stage_number] = StageProgress(
                stage_number=stage_number,
                status="IN_PROGRESS",
                started_at=datetime.now(),
            )
        
        return event

    def record_question_answered(
        self,
        session_id: UUID,
        stage_number: int,
        question_id: str,
        quality_score: float,
    ) -> ProgressEvent:
        """Record that a question has been answered."""
        event = ProgressEvent(
            event_type=ProgressEventType.QUESTION_ANSWERED,
            session_id=session_id,
            stage_number=stage_number,
            timestamp=datetime.now(),
            data={
                "question_id": question_id,
                "quality_score": quality_score,
                "stage": stage_number,
            },
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            self.sessions[session_id].questions_answered += 1
            if stage_number in self.sessions[session_id].stage_progress:
                self.sessions[session_id].stage_progress[stage_number].questions_answered += 1
                self.sessions[session_id].stage_progress[stage_number].quality_score = quality_score
        
        return event

    def record_stage_completed(
        self,
        session_id: UUID,
        stage_number: int,
        validation_passed: bool,
    ) -> ProgressEvent:
        """Record that a stage has been completed."""
        event = ProgressEvent(
            event_type=ProgressEventType.STAGE_COMPLETED,
            session_id=session_id,
            stage_number=stage_number,
            timestamp=datetime.now(),
            data={
                "stage": stage_number,
                "validation_passed": validation_passed,
                "status": "COMPLETED",
            },
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            if stage_number in self.sessions[session_id].stage_progress:
                self.sessions[session_id].stage_progress[stage_number].status = "COMPLETED"
                self.sessions[session_id].stage_progress[stage_number].validation_passed = validation_passed
                self.sessions[session_id].stage_progress[stage_number].completed_at = datetime.now()
        
        return event

    def record_charter_generation_started(self, session_id: UUID) -> ProgressEvent:
        """Record that charter generation has started."""
        event = ProgressEvent(
            event_type=ProgressEventType.CHARTER_GENERATING,
            session_id=session_id,
            timestamp=datetime.now(),
            data={"status": "STARTED", "progress": 0.0},
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            self.sessions[session_id].charter_status = "GENERATING"
            self.sessions[session_id].charter_progress.status = "GENERATING"
            self.sessions[session_id].charter_progress.started_at = datetime.now()
        
        return event

    def record_charter_generation_progress(
        self,
        session_id: UUID,
        progress: float,
        current_section: str,
    ) -> ProgressEvent:
        """Record charter generation progress."""
        event = ProgressEvent(
            event_type=ProgressEventType.CHARTER_GENERATING,
            session_id=session_id,
            timestamp=datetime.now(),
            data={
                "progress": progress,
                "current_section": current_section,
                "status": "GENERATING",
            },
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            self.sessions[session_id].charter_progress.progress = progress
            self.sessions[session_id].charter_progress.current_section = current_section
        
        return event

    def record_reflection_iteration(
        self,
        session_id: UUID,
        iteration_number: int,
        status: str,
    ) -> ProgressEvent:
        """Record a reflection loop iteration."""
        event = ProgressEvent(
            event_type=ProgressEventType.REFLECTION_ITERATION,
            session_id=session_id,
            timestamp=datetime.now(),
            data={"iteration": iteration_number, "status": status},
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            self.sessions[session_id].charter_progress.reflection_iterations = iteration_number
        
        return event

    def record_error(
        self,
        session_id: UUID,
        error_message: str,
        error_details: str,
    ) -> ProgressEvent:
        """Record an error event."""
        event = ProgressEvent(
            event_type=ProgressEventType.ERROR,
            session_id=session_id,
            timestamp=datetime.now(),
            data={"error": error_message, "details": error_details},
        )
        self._save_event(session_id, event)
        
        # Update session progress
        if session_id in self.sessions:
            self.sessions[session_id].status = "ERROR"
        
        return event

    def get_session_events(self, session_id: UUID) -> List[ProgressEvent]:
        """Get all events for a session."""
        return self.events.get(session_id, [])

    def get_session_progress(self, session_id: UUID) -> Optional[SessionProgress]:
        """Get current progress for a session."""
        return self.sessions.get(session_id)

    def get_stage_progress(self, session_id: UUID, stage_number: int) -> Optional[StageProgress]:
        """Get progress for a specific stage."""
        if session_id in self.sessions:
            return self.sessions[session_id].stage_progress.get(stage_number)
        return None

    def get_event_by_id(self, event_id: UUID) -> Optional[ProgressEvent]:
        """Get a specific event by ID."""
        for events in self.events.values():
            for event in events:
                if event.id == event_id:
                    return event
        return None

    def _save_event(self, session_id: UUID, event: ProgressEvent) -> None:
        """Save an event to the in-memory cache."""
        if session_id not in self.events:
            self.events[session_id] = []
        self.events[session_id].append(event)
        
        # TODO: Persist to database
        # self.db_manager.save_progress_event(event)

