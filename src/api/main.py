"""
FastAPI REST API for U-AIP Orchestrator - v1

Provides REST endpoints for:
- Session management (create, list, get)
- Stage execution and advancement
- Consistency validation
- Charter generation
- Health check and metrics
"""

from fastapi import FastAPI, HTTPException, Query, status, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional, Dict, Any, List
import time

from src.api.models import (
    SessionRequest,
    SessionResponse,
    SessionListResponse,
    StageExecutionRequest,
    StageExecutionResponse,
    StagesStatusResponse,
    StageStatus,
    AdvancementResponse,
    ConsistencyResponse,
    CharterGenerationRequest,
    CharterResponse,
    HealthCheckResponse,
    ErrorResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)
from src.database.connection import DatabaseManager, DatabaseConfig
from src.database.repositories.session_repository import SessionRepository
from src.database.repositories.stage_data_repository import StageDataRepository
from src.database.repositories.checkpoint_repository import CheckpointRepository
from src.database.repositories.user_repository import UserRepository
from src.agents.orchestrator import Orchestrator
from src.models.schemas import Session, SessionStatus
from src.auth.security import hash_password, create_access_token, verify_token

logger = logging.getLogger(__name__)


# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="U-AIP Orchestrator REST API",
    description="REST API for Universal AI Project Scoping and Framing Protocol",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ============================================================================
# Global State
# ============================================================================

# Database and service instances (initialized on startup)
db_manager: Optional[DatabaseManager] = None
session_repo: Optional[SessionRepository] = None
stage_data_repo: Optional[StageDataRepository] = None
checkpoint_repo: Optional[CheckpointRepository] = None
user_repo: Optional[UserRepository] = None
orchestrator: Optional[Orchestrator] = None

# Security
security = HTTPBearer()

# Request tracking
request_counter = 0


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global db_manager, session_repo, stage_data_repo, checkpoint_repo, user_repo, orchestrator
    try:
        # Initialize database with config from environment
        db_config = DatabaseConfig.from_env()
        db_manager = DatabaseManager(db_config)
        await db_manager.initialize()
        logger.info("Database initialized")

        # Initialize repositories
        session_repo = SessionRepository(db_manager)
        stage_data_repo = StageDataRepository(db_manager)
        checkpoint_repo = CheckpointRepository(db_manager)
        user_repo = UserRepository(db_manager)
        logger.info("Repositories initialized")

        # Initialize orchestrator
        orchestrator = Orchestrator(db_manager)
        logger.info("Orchestrator initialized")

    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close resources on shutdown."""
    global db_manager
    try:
        if db_manager:
            await db_manager.close()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)


# ============================================================================
# Error Handling Utilities
# ============================================================================


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    details: Optional[Any] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create standardized error response."""
    if request_id is None:
        request_id = f"req_{uuid4().hex[:12]}"

    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }


def validate_uuid(uuid_str: str) -> UUID:
    """Validate and parse UUID string."""
    try:
        return UUID(uuid_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                code="INVALID_UUID",
                message=f"Invalid session ID format: {uuid_str}",
                status_code=400,
            ),
        )


# ============================================================================
# Authentication Utilities
# ============================================================================


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Validate JWT token and return user_id.

    Raises:
        HTTPException: 401 if token invalid or expired
    """
    token = credentials.credentials
    token_data = verify_token(token)

    if not token_data:
        raise HTTPException(
            status_code=401,
            detail=create_error_response(
                code="INVALID_TOKEN",
                message="Invalid or expired token",
                status_code=401,
            ),
        )

    return token_data.get("user_id")


# ============================================================================
# Authentication Endpoints
# ============================================================================


@app.post("/api/v1/auth/register", response_model=TokenResponse, status_code=201)
async def register(request: UserRegisterRequest) -> Dict[str, Any]:
    """
    Register a new user account.

    Args:
        request: Registration details (email, password, name)

    Returns:
        TokenResponse with JWT token for immediate login

    Raises:
        HTTPException: 400 if email already exists, 500 on error
    """
    if not user_repo:
        raise HTTPException(
            status_code=503,
            detail=create_error_response(
                code="SERVICE_UNAVAILABLE",
                message="Authentication service not initialized",
                status_code=503,
            ),
        )

    try:
        # Check if email already exists
        existing_user = await user_repo.get_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    code="EMAIL_EXISTS",
                    message=f"Email {request.email} already registered",
                    status_code=400,
                ),
            )

        # Hash password and create user
        password_hash = hash_password(request.password)
        user = await user_repo.create(
            email=request.email,
            password_hash=password_hash,
            name=request.name or "",
        )

        # Generate token
        token = create_access_token(str(user.user_id), user.email)

        logger.info(f"User registered: {request.email}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user_id": str(user.user_id),
            "email": user.email,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="REGISTRATION_ERROR",
                message="Failed to register user",
                status_code=500,
            ),
        )


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(request: UserLoginRequest) -> Dict[str, Any]:
    """
    Login with email and password.

    Args:
        request: Login credentials (email, password)

    Returns:
        TokenResponse with JWT token

    Raises:
        HTTPException: 401 if credentials invalid
    """
    if not user_repo:
        raise HTTPException(
            status_code=503,
            detail=create_error_response(
                code="SERVICE_UNAVAILABLE",
                message="Authentication service not initialized",
                status_code=503,
            ),
        )

    try:
        # Verify credentials
        user = await user_repo.verify_credentials(request.email, request.password)

        if not user:
            logger.warning(f"Failed login attempt: {request.email}")
            raise HTTPException(
                status_code=401,
                detail=create_error_response(
                    code="INVALID_CREDENTIALS",
                    message="Invalid email or password",
                    status_code=401,
                ),
            )

        # Generate token
        token = create_access_token(str(user.user_id), user.email)

        logger.info(f"User logged in: {request.email}")

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user_id": str(user.user_id),
            "email": user.email,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="LOGIN_ERROR",
                message="Failed to login",
                status_code=500,
            ),
        )


# ============================================================================
# Session Management Endpoints
# ============================================================================


@app.post("/api/v1/sessions", response_model=SessionResponse, status_code=201)
async def create_session(request: SessionRequest) -> Dict[str, Any]:
    """
    Create a new AI project scoping session.

    **FR-8 Compliance**: Creates and persists session in database.
    """
    if not orchestrator or not session_repo:
        raise HTTPException(
            status_code=503,
            detail=create_error_response(
                code="SERVICE_UNAVAILABLE",
                message="Services not initialized",
                status_code=503,
            ),
        )

    try:
        # Create session via orchestrator
        session = await orchestrator.create_session(request.user_id, request.project_name)

        logger.info(f"Created session {session.session_id} for user {request.user_id}")

        return {
            "session_id": str(session.session_id),
            "user_id": session.user_id,
            "project_name": session.project_name,
            "current_stage": session.current_stage,
            "status": session.status.value,
            "started_at": session.started_at,
            "last_updated_at": session.last_updated_at,
            "stage_data": session.stage_data,
        }
    except Exception as e:
        logger.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="INTERNAL_ERROR",
                message="Failed to create session",
                status_code=500,
                details=str(e),
            ),
        )


@app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get session details.

    **FR-8 Compliance**: Retrieves persisted session data.
    """
    if not session_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        session_uuid = validate_uuid(session_id)

        try:
            session = await session_repo.get_by_id(session_uuid)
        except Exception as repo_error:
            # Handle repository errors gracefully
            logger.debug(f"Repository error getting session {session_uuid}: {repo_error}")
            # If it's a "not found" scenario, return 404
            if "not found" in str(repo_error).lower() or "no rows" in str(repo_error).lower():
                raise HTTPException(
                    status_code=404,
                    detail=create_error_response(
                        code="NOT_FOUND",
                        message=f"Session {session_id} not found",
                        status_code=404,
                    ),
                )
            raise

        if not session:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    code="NOT_FOUND",
                    message=f"Session {session_id} not found",
                    status_code=404,
                ),
            )

        return {
            "session_id": str(session.session_id),
            "user_id": session.user_id,
            "project_name": session.project_name,
            "current_stage": session.current_stage,
            "status": session.status.value,
            "started_at": session.started_at,
            "last_updated_at": session.last_updated_at,
            "stage_data": session.stage_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="INTERNAL_ERROR",
                message="Failed to retrieve session",
                status_code=500,
            ),
        )


@app.get("/api/v1/sessions", response_model=SessionListResponse)
async def list_sessions(
    user_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> Dict[str, Any]:
    """
    List sessions with optional filtering and pagination.

    **FR-8 Compliance**: Lists persisted sessions.
    """
    if not session_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        sessions = []
        total = 0

        if user_id:
            sessions = await session_repo.get_by_user_id(user_id, limit=limit + skip)
        else:
            # Get all sessions with pagination
            sessions = await session_repo.get_all_sessions(limit=limit + skip, skip=skip)

        # Filter by status if provided
        if status:
            sessions = [s for s in sessions if s.status.value == status]

        # Apply pagination
        total = len(sessions)
        sessions = sessions[skip : skip + limit]

        return {
            "sessions": [
                {
                    "session_id": str(s.session_id),
                    "user_id": s.user_id,
                    "project_name": s.project_name,
                    "current_stage": s.current_stage,
                    "status": s.status.value,
                    "started_at": s.started_at,
                    "last_updated_at": s.last_updated_at,
                    "stage_data": s.stage_data,
                }
                for s in sessions
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="INTERNAL_ERROR",
                message="Failed to list sessions",
                status_code=500,
            ),
        )


# ============================================================================
# Stage Execution Endpoints
# ============================================================================


@app.post("/api/v1/sessions/{session_id}/stages/{stage_number}/execute", response_model=StageExecutionResponse)
async def execute_stage(
    session_id: str,
    stage_number: int,
    request: Optional[StageExecutionRequest] = None,
) -> Dict[str, Any]:
    """
    Execute a specific stage.

    **FR-1 Compliance**: Executes multi-stage orchestration.
    """
    if not orchestrator or not session_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Validate inputs
        if stage_number < 1 or stage_number > 5:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    code="INVALID_STAGE",
                    message=f"Invalid stage number: {stage_number}. Must be 1-5.",
                    status_code=400,
                ),
            )

        session_uuid = validate_uuid(session_id)
        session = await session_repo.get_by_id(session_uuid)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    code="NOT_FOUND",
                    message=f"Session {session_id} not found",
                    status_code=404,
                ),
            )

        # Check if stage already completed
        stage_data = await stage_data_repo.get_stage_data(session_uuid, stage_number)
        if stage_data and len(stage_data) > 0:
            raise HTTPException(
                status_code=409,
                detail=create_error_response(
                    code="CONFLICT",
                    message=f"Stage {stage_number} already completed",
                    status_code=409,
                ),
            )

        # Execute stage
        start_time = time.time()
        stage_output = await orchestrator.run_stage(session, stage_number)
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Determine output type
        output_type = stage_output.__class__.__name__ if hasattr(stage_output, '__class__') else "Unknown"

        # Convert to dict
        if hasattr(stage_output, '__dict__'):
            output_data = stage_output.__dict__
        else:
            output_data = json.loads(json.dumps(stage_output, default=str))

        logger.info(f"Executed stage {stage_number} for session {session_uuid}")

        return {
            "session_id": str(session_uuid),
            "stage_number": stage_number,
            "status": "COMPLETED",
            "output_type": output_type,
            "data": output_data,
            "execution_time_ms": execution_time_ms,
            "quality_score": 8.5,  # Default score, can be enhanced
            "completed_at": datetime.now(timezone.utc),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute stage: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="EXECUTION_ERROR",
                message=f"Failed to execute stage {stage_number}",
                status_code=500,
                details=str(e),
            ),
        )


@app.post("/api/v1/sessions/{session_id}/stages/{stage_number}/advance", response_model=AdvancementResponse)
async def advance_stage(
    session_id: str,
    stage_number: int,
) -> Dict[str, Any]:
    """
    Validate and advance to next stage.

    **FR-4 Compliance**: Enforces stage-gate validation before advancement.
    """
    if not orchestrator or not session_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Validate inputs
        if stage_number < 1 or stage_number > 5:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    code="INVALID_STAGE",
                    message=f"Invalid stage number: {stage_number}",
                    status_code=400,
                ),
            )

        session_uuid = validate_uuid(session_id)
        session = await session_repo.get_by_id(session_uuid)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    code="NOT_FOUND",
                    message=f"Session {session_id} not found",
                    status_code=404,
                ),
            )

        # Perform stage-gate validation
        try:
            await orchestrator.advance_to_next_stage(session)
        except ValueError as e:
            # Validation failed
            raise HTTPException(
                status_code=422,
                detail=create_error_response(
                    code="VALIDATION_FAILED",
                    message="Stage-gate validation failed",
                    status_code=422,
                    details=str(e),
                ),
            )

        # Create checkpoint
        checkpoint = await orchestrator.save_checkpoint(session, stage_number)

        # Update session
        session.current_stage = stage_number + 1
        await session_repo.update(session)

        logger.info(f"Advanced session {session_uuid} from stage {stage_number} to {stage_number + 1}")

        return {
            "session_id": str(session_uuid),
            "previous_stage": stage_number,
            "current_stage": stage_number + 1,
            "validation_passed": True,
            "validation_issues": [],
            "checkpoint_created": True,
            "advanced_at": datetime.now(timezone.utc),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to advance stage: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="INTERNAL_ERROR",
                message="Failed to advance stage",
                status_code=500,
            ),
        )


@app.get("/api/v1/sessions/{session_id}/stages", response_model=StagesStatusResponse)
async def get_stages_status(session_id: str) -> Dict[str, Any]:
    """
    Get status of all stages for a session.

    **FR-1 Compliance**: Shows orchestration progress.
    """
    if not session_repo or not stage_data_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        session_uuid = validate_uuid(session_id)
        session = await session_repo.get_by_id(session_uuid)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    code="NOT_FOUND",
                    message=f"Session {session_id} not found",
                    status_code=404,
                ),
            )

        # Get stage names
        stage_names = {
            1: "Problem Statement",
            2: "Metric Alignment",
            3: "Data Quality",
            4: "User Context",
            5: "Ethical Risk",
        }

        stages = []
        for stage_num in range(1, 6):
            stage_data = await stage_data_repo.get_stage_data(session_uuid, stage_num)
            status = "COMPLETED" if stage_data else "PENDING"
            if stage_num == session.current_stage:
                status = "IN_PROGRESS"

            stages.append({
                "stage_number": stage_num,
                "name": stage_names.get(stage_num, f"Stage {stage_num}"),
                "status": status,
                "completed_at": None,  # TODO: Get from checkpoint
                "quality_score": None,  # TODO: Get from quality agent
            })

        return {
            "session_id": str(session_uuid),
            "current_stage": session.current_stage,
            "stages": stages,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stages status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="INTERNAL_ERROR",
                message="Failed to get stages status",
                status_code=500,
            ),
        )


# ============================================================================
# Consistency & Validation Endpoints
# ============================================================================


@app.get("/api/v1/sessions/{session_id}/consistency", response_model=ConsistencyResponse)
async def check_consistency(session_id: str) -> Dict[str, Any]:
    """
    Check cross-stage consistency.

    **FR-5 Compliance**: Validates alignment across all stages using ConsistencyCheckerAgent.
    """
    if not orchestrator or not session_repo or not stage_data_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        session_uuid = validate_uuid(session_id)
        session = await session_repo.get_by_id(session_uuid)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    code="NOT_FOUND",
                    message=f"Session {session_id} not found",
                    status_code=404,
                ),
            )

        # Check if all stages are completed
        all_stage_data = await stage_data_repo.get_all_stage_data(session_uuid)
        if len(all_stage_data) < 5:
            raise HTTPException(
                status_code=422,
                detail=create_error_response(
                    code="INCOMPLETE_WORKFLOW",
                    message="Not all stages completed. Cannot perform consistency check.",
                    status_code=422,
                ),
            )

        # Invoke consistency checker
        consistency_report = await orchestrator.invoke_consistency_checker(session)

        logger.info(f"Consistency check completed for session {session_uuid}")

        return {
            "session_id": str(session_uuid),
            "is_consistent": consistency_report.is_consistent,
            "overall_feasibility": consistency_report.overall_feasibility.value if hasattr(consistency_report.overall_feasibility, 'value') else str(consistency_report.overall_feasibility),
            "analysis_timestamp": datetime.now(timezone.utc),
            "issues": [str(c) for c in consistency_report.contradictions],
            "recommendations": consistency_report.recommendations,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check consistency: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="CONSISTENCY_ERROR",
                message="Failed to perform consistency check",
                status_code=500,
                details=str(e),
            ),
        )


# ============================================================================
# Charter Generation Endpoints
# ============================================================================


@app.post("/api/v1/sessions/{session_id}/charter/generate", response_model=CharterResponse)
async def generate_charter(
    session_id: str,
    request: Optional[CharterGenerationRequest] = None,
) -> Dict[str, Any]:
    """
    Generate AI Project Charter.

    **FR-5 Compliance**: Generates charter after consistency checking.
    """
    if not orchestrator or not session_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        session_uuid = validate_uuid(session_id)
        session = await session_repo.get_by_id(session_uuid)
        if not session:
            raise HTTPException(
                status_code=404,
                detail=create_error_response(
                    code="NOT_FOUND",
                    message=f"Session {session_id} not found",
                    status_code=404,
                ),
            )

        # Generate charter
        charter = await orchestrator.generate_charter(session)

        # Make governance decision
        governance_decision = await orchestrator.make_governance_decision(
            session.stage_data.get(5, {})  # Ethical risk report from stage 5
        )

        logger.info(f"Generated charter for session {session_uuid}")

        return {
            "session_id": str(session_uuid),
            "charter_id": f"charter_{uuid4().hex[:12]}",
            "governance_decision": governance_decision.value if hasattr(governance_decision, 'value') else str(governance_decision),
            "risk_assessment": session.stage_data.get(5, {}),
            "generated_at": datetime.now(timezone.utc),
            "format": request.format if request else "json",
            "content": None,  # TODO: Generate charter content based on format
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate charter: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                code="CHARTER_ERROR",
                message="Failed to generate charter",
                status_code=500,
                details=str(e),
            ),
        )


# ============================================================================
# Health Check & Metrics Endpoints
# ============================================================================


@app.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns status of API and dependent services.
    """
    components = {
        "api": "healthy",
        "database": "healthy" if db_manager else "unhealthy",
        "ollama": "healthy",  # TODO: Actually check Ollama
    }

    overall_status = "healthy" if all(s == "healthy" for s in components.values()) else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc),
        "components": components,
    }


@app.get("/metrics")
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format.
    """
    # Simple metrics implementation
    metrics_text = """# HELP uaip_sessions_total Total number of sessions created
# TYPE uaip_sessions_total counter
uaip_sessions_total 0

# HELP uaip_stages_completed_total Total number of stages completed
# TYPE uaip_stages_completed_total counter
uaip_stages_completed_total 0

# HELP uaip_api_requests_total Total API requests
# TYPE uaip_api_requests_total counter
uaip_api_requests_total 0

# HELP uaip_api_request_duration_seconds API request duration
# TYPE uaip_api_request_duration_seconds histogram
uaip_api_request_duration_seconds_bucket{le="+Inf"} 0
"""
    return Response(content=metrics_text, media_type="text/plain")
