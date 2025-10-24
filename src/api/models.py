"""
Pydantic models for REST API requests and responses.

Provides type-safe request/response validation and serialization
for all REST API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============================================================================
# Request Models
# ============================================================================


class UserRegisterRequest(BaseModel):
    """Request body for user registration."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    name: Optional[str] = Field(None, description="User full name")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """Request body for user login."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class TokenResponse(BaseModel):
    """Response model for authentication endpoints."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(86400, description="Token expiration in seconds")
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com"
            }
        }


class SessionRequest(BaseModel):
    """Request body for creating a session."""
    user_id: str = Field(..., min_length=1, description="User identifier")
    project_name: str = Field(..., min_length=1, description="Name of the AI project")
    description: Optional[str] = Field(None, description="Project description")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_123",
                "project_name": "Customer Churn Prediction",
                "description": "ML model to predict customer churn risk"
            }
        }


class StageExecutionRequest(BaseModel):
    """Request body for executing a stage."""
    parameters: Optional[Dict[str, Any]] = Field(None, description="Stage-specific parameters")

    class Config:
        schema_extra = {
            "example": {
                "parameters": {}
            }
        }


class CharterGenerationRequest(BaseModel):
    """Request body for generating charter."""
    format: str = Field("json", description="Output format: json, markdown, or pdf")
    include_governance: bool = Field(True, description="Include governance decision")

    class Config:
        schema_extra = {
            "example": {
                "format": "json",
                "include_governance": True
            }
        }


# ============================================================================
# Response Models
# ============================================================================


class SessionResponse(BaseModel):
    """Response model for session details."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    project_name: str = Field(..., description="Project name")
    current_stage: int = Field(..., ge=1, le=6, description="Current stage (1-6)")
    status: str = Field(..., description="Session status: IN_PROGRESS, COMPLETED, ABANDONED, PAUSED")
    started_at: datetime = Field(..., description="Session start timestamp")
    last_updated_at: datetime = Field(..., description="Last update timestamp")
    stage_data: Optional[Dict[int, Dict[str, Any]]] = Field(None, description="Stage-specific data")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "project_name": "Customer Churn Prediction",
                "current_stage": 1,
                "status": "IN_PROGRESS",
                "started_at": "2025-10-23T10:30:00Z",
                "last_updated_at": "2025-10-23T10:30:00Z",
                "stage_data": {}
            }
        }


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionResponse] = Field(..., description="List of sessions")
    total: int = Field(..., ge=0, description="Total count of sessions")
    skip: int = Field(0, ge=0, description="Number of items skipped")
    limit: int = Field(10, ge=1, description="Items per page")

    class Config:
        schema_extra = {
            "example": {
                "sessions": [],
                "total": 0,
                "skip": 0,
                "limit": 10
            }
        }


class StageExecutionResponse(BaseModel):
    """Response model for stage execution."""
    session_id: str = Field(..., description="Session identifier")
    stage_number: int = Field(..., ge=1, le=5, description="Stage number (1-5)")
    status: str = Field(..., description="Execution status: COMPLETED, FAILED")
    output_type: str = Field(..., description="Type of stage output")
    data: Dict[str, Any] = Field(..., description="Stage-specific deliverable data")
    execution_time_ms: int = Field(..., ge=0, description="Execution time in milliseconds")
    quality_score: Optional[float] = Field(None, ge=0, le=10, description="Quality score 0-10")
    completed_at: datetime = Field(..., description="Completion timestamp")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "stage_number": 1,
                "status": "COMPLETED",
                "output_type": "ProblemStatement",
                "data": {},
                "execution_time_ms": 2340,
                "quality_score": 9.2,
                "completed_at": "2025-10-23T10:32:00Z"
            }
        }


class StageStatus(BaseModel):
    """Status of a single stage."""
    stage_number: int = Field(..., ge=1, le=5, description="Stage number")
    name: str = Field(..., description="Stage name")
    status: str = Field(..., description="Status: COMPLETED, IN_PROGRESS, PENDING")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    quality_score: Optional[float] = Field(None, ge=0, le=10, description="Quality score")


class StagesStatusResponse(BaseModel):
    """Response model for listing all stages status."""
    session_id: str = Field(..., description="Session identifier")
    current_stage: int = Field(..., ge=1, le=6, description="Current stage")
    stages: List[StageStatus] = Field(..., description="Status of all stages")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "current_stage": 1,
                "stages": []
            }
        }


class AdvancementResponse(BaseModel):
    """Response model for advancing to next stage."""
    session_id: str = Field(..., description="Session identifier")
    previous_stage: int = Field(..., ge=1, le=5, description="Previous stage")
    current_stage: int = Field(..., ge=1, le=6, description="New current stage")
    validation_passed: bool = Field(..., description="Whether validation passed")
    validation_issues: List[str] = Field(default_factory=list, description="Validation issues if any")
    checkpoint_created: bool = Field(..., description="Whether checkpoint was created")
    advanced_at: datetime = Field(..., description="Advancement timestamp")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "previous_stage": 1,
                "current_stage": 2,
                "validation_passed": True,
                "validation_issues": [],
                "checkpoint_created": True,
                "advanced_at": "2025-10-23T10:33:00Z"
            }
        }


class ConsistencyResponse(BaseModel):
    """Response model for consistency check."""
    session_id: str = Field(..., description="Session identifier")
    is_consistent: bool = Field(..., description="Whether stages are consistent")
    overall_feasibility: str = Field(..., description="Feasibility: HIGH, MEDIUM, LOW")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp")
    issues: List[str] = Field(default_factory=list, description="Consistency issues")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_consistent": True,
                "overall_feasibility": "HIGH",
                "analysis_timestamp": "2025-10-23T10:45:00Z",
                "issues": [],
                "recommendations": []
            }
        }


class CharterResponse(BaseModel):
    """Response model for charter generation."""
    session_id: str = Field(..., description="Session identifier")
    charter_id: str = Field(..., description="Charter identifier")
    governance_decision: str = Field(..., description="Decision: PROCEED, PROCEED_WITH_CONDITIONS, REJECT")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment details")
    generated_at: datetime = Field(..., description="Generation timestamp")
    format: str = Field("json", description="Output format")
    content: Optional[str] = Field(None, description="Charter content for json/markdown formats")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "charter_id": "charter_123",
                "governance_decision": "PROCEED",
                "risk_assessment": {},
                "generated_at": "2025-10-23T10:50:00Z",
                "format": "json",
                "content": None
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Overall status: healthy, degraded, unhealthy")
    timestamp: datetime = Field(..., description="Check timestamp")
    components: Dict[str, str] = Field(..., description="Component status")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-23T10:50:00Z",
                "components": {
                    "database": "healthy",
                    "ollama": "healthy",
                    "cache": "healthy"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    error: Dict[str, Any] = Field(
        ...,
        description="Error details including code, message, request_id, timestamp"
    )

    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Missing required field: user_id",
                    "details": None,
                    "request_id": "req_123abc",
                    "timestamp": "2025-10-23T10:50:00Z"
                }
            }
        }
