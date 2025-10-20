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
from datetime import datetime
from typing import List, Optional
import json

from src.services.progress_service import ProgressService
from src.database.connection import DatabaseManager
from src.database.repositories.session_repository import SessionRepository


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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
progress_service = ProgressService()
# Database manager will be initialized on startup
db_manager = None
session_repo = None

# In-memory session storage for now (will be replaced with database)
_sessions_store: dict = {}


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.post("/api/sessions", status_code=201)
async def create_session(request: CreateSessionRequest):
    """Create a new session."""
    try:
        session_id = uuid4()

        # Initialize progress tracking
        progress_service.initialize_session(session_id)

        # Save session to in-memory store
        session_data = {
            "session_id": str(session_id),
            "user_id": request.user_id,
            "project_name": request.project_name,
            "description": request.description,
            "started_at": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
        }
        _sessions_store[str(session_id)] = session_data

        return session_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Get session from store
        if str(session_uuid) not in _sessions_store:
            raise HTTPException(status_code=404, detail="Session not found")

        return _sessions_store[str(session_uuid)]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions(user_id: str = Query(...)):
    """List sessions for a user."""
    try:
        # Filter sessions by user_id
        user_sessions = [
            session for session in _sessions_store.values()
            if session.get("user_id") == user_id
        ]
        return user_sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        # Validate UUID format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format")

        # Delete from store
        if str(session_uuid) in _sessions_store:
            del _sessions_store[str(session_uuid)]

        return None
    except HTTPException:
        raise
    except Exception as e:
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

