"""
FastAPI application for U-AIP Scoping Assistant.

Provides REST API endpoints for:
- Session management (create, get, list, delete)
- Progress tracking (get progress, submit answers)
- Real-time updates (SSE stream)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Optional
import json
import os
import logging

from src.services.progress_service import ProgressService
from src.database.connection import DatabaseManager
from src.database.repositories.session_repository import SessionRepository
from src.models.schemas import Session, SessionStatus

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""
    user_id: str
    project_name: str
    description: Optional[str] = None


class SubmitAnswerRequest(BaseModel):
    """Request model for submitting an answer."""
    stage_number: int
    question_id: str
    answer: str
    quality_score: float


# Initialize FastAPI app
app = FastAPI(
    title="U-AIP Scoping Assistant API",
    description="API for the Universal AI Project Scoping and Framing Protocol",
    version="1.0.0",
)

# Configure CORS with restricted origins
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5173",  # Local development
    "http://localhost:3000",  # Alternative local port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Add CORS middleware with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize services
progress_service = ProgressService()
# Database manager will be initialized on startup
db_manager = None
session_repo = None


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    global db_manager, session_repo
    try:
        from src.database.connection import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        session_repo = SessionRepository(db_manager)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    global db_manager
    try:
        if db_manager:
            await db_manager.close()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.post("/api/sessions", status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new session."""
    try:
        if not session_repo:
            raise HTTPException(status_code=503, detail="Database not initialized")

        # Create session object
        session = Session(
            session_id=uuid4(),
            user_id=request.user_id,
            project_name=request.project_name,
            started_at=datetime.now(timezone.utc),
            last_updated_at=datetime.now(timezone.utc),
            current_stage=1,
            stage_data={},
            conversation_history=[],
            status=SessionStatus.IN_PROGRESS,
            checkpoints=[],
        )

        # Persist to database
        await session_repo.create(session)

        # Initialize progress tracking
        progress_service.initialize_session(session.session_id)

        logger.info(f"Created session {session.session_id} for user {request.user_id}")

        return {
            "session_id": str(session.session_id),
            "user_id": session.user_id,
            "project_name": session.project_name,
            "started_at": session.started_at.isoformat(),
            "status": session.status.value,
            "current_stage": session.current_stage,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    try:
        if not session_repo:
            raise HTTPException(status_code=503, detail="Database not initialized")

        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Get session from database
        session = await session_repo.get(session_uuid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": str(session.session_id),
            "user_id": session.user_id,
            "project_name": session.project_name,
            "started_at": session.started_at.isoformat(),
            "last_updated_at": session.last_updated_at.isoformat(),
            "status": session.status.value,
            "current_stage": session.current_stage,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions(user_id: str = Query(...)):
    """List sessions for a user."""
    try:
        if not session_repo:
            raise HTTPException(status_code=503, detail="Database not initialized")

        # Get sessions from database
        sessions = await session_repo.get_by_user(user_id)

        return [
            {
                "session_id": str(session.session_id),
                "user_id": session.user_id,
                "project_name": session.project_name,
                "started_at": session.started_at.isoformat(),
                "last_updated_at": session.last_updated_at.isoformat(),
                "status": session.status.value,
                "current_stage": session.current_stage,
            }
            for session in sessions
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        if not session_repo:
            raise HTTPException(status_code=503, detail="Database not initialized")

        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Delete from database
        await session_repo.delete(session_uuid)
        logger.info(f"Deleted session {session_uuid}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Progress Tracking Endpoints
# ============================================================================

@app.get("/api/sessions/{session_id}/progress")
async def get_progress(session_id: str):
    """Get session progress."""
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        progress = progress_service.get_session_progress(session_uuid)
        if not progress:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": str(session_uuid),
            "status": progress.status,
            "current_stage": progress.current_stage,
            "questions_answered": progress.questions_answered,
            "charter_status": progress.charter_status,
            "last_updated": progress.last_updated.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/answer")
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    """Submit an answer to a question."""
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Validate stage number
        if request.stage_number < 1 or request.stage_number > 5:
            raise HTTPException(status_code=400, detail="Invalid stage number")

        # Record the answer
        progress_service.record_question_answered(
            session_uuid,
            stage_number=request.stage_number,
            question_id=request.question_id,
            quality_score=request.quality_score,
        )

        return {"status": "RECORDED", "session_id": str(session_uuid)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}/events")
async def get_events(session_id: str):
    """Get all progress events for a session."""
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        events = progress_service.get_session_events(session_uuid)
        return [event.to_dict() for event in events]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Real-Time Updates (SSE)
# ============================================================================

@app.get("/api/sessions/{session_id}/stream")
async def stream_events(session_id: str):
    """Stream progress events in real-time using Server-Sent Events."""
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        async def event_generator():
            """Generate SSE events."""
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'session_id': str(session_uuid)})}\n\n"
            
            # TODO: Implement real-time event streaming
            # For now, just send existing events
            events = progress_service.get_session_events(session_uuid)
            for event in events:
                yield f"data: {json.dumps(event.to_dict())}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

