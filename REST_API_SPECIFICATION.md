# REST API Specification - U-AIP Backend

**Status**: Specification Draft (RFC)
**Port**: 38937 (unique, verified available)
**Framework**: FastAPI (async, type-safe)
**Python Version**: 3.9+ (compatible)

---

## 1. Overview

The REST API provides programmatic access to the U-AIP orchestrator for managing AI project scoping sessions. It exposes endpoints for session lifecycle management, stage execution, consistency validation, and charter generation.

**Alignment with SWE Spec**: FR-1, FR-4, FR-5, FR-8 (session management, validation, consistency, persistence)

---

## 2. API Endpoints

### 2.1 Session Management

#### POST /api/v1/sessions
Create a new AI project scoping session.

**Request Body**:
```json
{
  "user_id": "user_123",
  "project_name": "Customer Churn Prediction"
}
```

**Response (201 Created)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "project_name": "Customer Churn Prediction",
  "current_stage": 1,
  "status": "IN_PROGRESS",
  "started_at": "2025-10-23T10:30:00Z",
  "last_updated_at": "2025-10-23T10:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Missing required fields
- `500 Internal Server Error`: Database error

---

#### GET /api/v1/sessions/{session_id}
Retrieve session details.

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "project_name": "Customer Churn Prediction",
  "current_stage": 3,
  "status": "IN_PROGRESS",
  "started_at": "2025-10-23T10:30:00Z",
  "last_updated_at": "2025-10-23T11:45:00Z",
  "stage_data": {
    "1": { /* ProblemStatement */ },
    "2": { /* MetricAlignmentMatrix */ },
    "3": { /* DataQualityScorecard */ }
  }
}
```

**Error Responses**:
- `404 Not Found`: Session doesn't exist
- `500 Internal Server Error`: Database error

---

#### GET /api/v1/sessions
List all sessions (paginated).

**Query Parameters**:
- `user_id` (optional): Filter by user
- `status` (optional): Filter by status (IN_PROGRESS, COMPLETED)
- `skip` (default: 0): Pagination offset
- `limit` (default: 10): Items per page

**Response (200 OK)**:
```json
{
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user_123",
      "project_name": "Customer Churn Prediction",
      "current_stage": 3,
      "status": "IN_PROGRESS"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

---

### 2.2 Stage Execution

#### POST /api/v1/sessions/{session_id}/stages/{stage_number}/execute
Run a specific stage of the workflow.

**URL Parameters**:
- `session_id`: UUID of session
- `stage_number`: 1-5

**Request Body**: (Optional) Stage-specific parameters

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "stage_number": 1,
  "status": "COMPLETED",
  "output_type": "ProblemStatement",
  "data": { /* Stage output */ },
  "execution_time_ms": 2340,
  "quality_score": 9.2,
  "completed_at": "2025-10-23T10:32:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid stage number (must be 1-5)
- `404 Not Found`: Session not found
- `409 Conflict`: Stage already completed
- `422 Unprocessable Entity`: Session not at expected stage
- `500 Internal Server Error`: Execution error

---

#### POST /api/v1/sessions/{session_id}/stages/{stage_number}/advance
Validate and advance to the next stage.

**Description**: Runs stage-gate validation (FR-4). Must pass before advancement.

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "previous_stage": 1,
  "current_stage": 2,
  "validation_passed": true,
  "validation_issues": [],
  "checkpoint_created": true,
  "advanced_at": "2025-10-23T10:33:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid transition
- `404 Not Found`: Session not found
- `422 Unprocessable Entity`: Validation failed (returns issues)
- `500 Internal Server Error`: Database error

---

#### GET /api/v1/sessions/{session_id}/stages
Get status of all stages for a session.

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_stage": 3,
  "stages": [
    {
      "stage_number": 1,
      "name": "Problem Statement",
      "status": "COMPLETED",
      "completed_at": "2025-10-23T10:32:00Z",
      "quality_score": 9.2
    },
    {
      "stage_number": 2,
      "name": "Metric Alignment",
      "status": "COMPLETED",
      "completed_at": "2025-10-23T10:40:00Z",
      "quality_score": 8.5
    },
    {
      "stage_number": 3,
      "name": "Data Quality",
      "status": "IN_PROGRESS",
      "completed_at": null
    }
  ]
}
```

---

### 2.3 Consistency & Validation

#### GET /api/v1/sessions/{session_id}/consistency
Run cross-stage consistency validation.

**Description**: Invokes ConsistencyCheckerAgent (FR-5) to validate alignment across all stages.

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_consistent": true,
  "overall_feasibility": "HIGH",
  "analysis_timestamp": "2025-10-23T10:45:00Z",
  "issues": [],
  "recommendations": [
    "Consider real-time inference for Stage 4 requirements"
  ]
}
```

**Error Responses**:
- `404 Not Found`: Session not found
- `422 Unprocessable Entity`: Incomplete stages (can't validate)
- `500 Internal Server Error`: LLM or validation error

---

### 2.4 Charter Generation

#### POST /api/v1/sessions/{session_id}/charter/generate
Generate the AI Project Charter.

**Request Body** (Optional):
```json
{
  "format": "json",  // json, markdown, or pdf
  "include_governance": true
}
```

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "charter_id": "charter_123",
  "governance_decision": "PROCEED_WITH_CONDITIONS",
  "conditions": [
    "Monthly fairness audits required",
    "Real-time inference capacity must be implemented"
  ],
  "generated_at": "2025-10-23T11:00:00Z",
  "formats_available": {
    "json": "/api/v1/charters/charter_123/download?format=json",
    "markdown": "/api/v1/charters/charter_123/download?format=markdown",
    "pdf": "/api/v1/charters/charter_123/download?format=pdf"
  }
}
```

**Error Responses**:
- `404 Not Found`: Session not found
- `422 Unprocessable Entity`: Workflow not complete
- `500 Internal Server Error`: Charter generation error

---

#### GET /api/v1/charters/{charter_id}/download
Download generated charter.

**Query Parameters**:
- `format`: json, markdown, or pdf (default: json)

**Response**: Binary or text file (appropriate MIME type)

---

### 2.5 Health & Status

#### GET /api/v1/health
Health check endpoint.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T11:05:00Z",
  "components": {
    "database": "healthy",
    "ollama": "healthy",
    "uptime_seconds": 3600
  }
}
```

---

#### GET /metrics
Prometheus metrics endpoint.

**Response**: Prometheus-formatted metrics
```
# HELP uaip_sessions_total Total sessions created
# TYPE uaip_sessions_total counter
uaip_sessions_total{status="completed"} 5
uaip_sessions_total{status="in_progress"} 2

# HELP uaip_stage_duration_seconds Stage execution duration
# TYPE uaip_stage_duration_seconds histogram
uaip_stage_duration_seconds_bucket{stage="1",le="5"} 10
```

---

## 3. Request/Response Standards

### 3.1 Headers

**Request Headers**:
```
Content-Type: application/json
Accept: application/json
```

**Response Headers**:
```
Content-Type: application/json
X-Request-ID: <uuid>
X-Response-Time-Ms: <integer>
```

---

### 3.2 Error Response Format

All errors follow this standard format:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Stage gate validation failed for stage 1",
    "details": {
      "stage": 1,
      "missing_fields": ["business_objective", "target_output"]
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-23T11:05:00Z"
  }
}
```

**HTTP Status Codes**:
- `200 OK`: Successful GET/POST
- `201 Created`: Resource created
- `202 Accepted`: Async operation started
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `409 Conflict`: State conflict (already completed)
- `422 Unprocessable Entity`: Validation failed
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Dependency unavailable

---

## 4. Authentication & Authorization

**Phase 1** (MVP): No authentication (internal/trusted use)

**Phase 2** (Future):
- JWT token-based authentication
- Role-based access control (RBAC)
- API key support for CI/CD

---

## 5. Rate Limiting

**Phase 1**: No rate limiting

**Phase 2** (Future):
- 100 requests per minute per user
- 10 concurrent sessions per user
- Graceful degradation when approaching limits

---

## 6. Pagination

List endpoints support pagination with:
- `skip`: Offset (default: 0)
- `limit`: Maximum items (default: 10, max: 100)

---

## 7. Async Operations

Long-running operations may return `202 Accepted` with a status URL:

```json
{
  "status": "processing",
  "status_url": "/api/v1/operations/op_123",
  "estimated_completion_ms": 30000
}
```

Poll the status URL to check completion.

---

## 8. Versioning

- API Version: `v1`
- All endpoints use `/api/v1/` prefix
- Future breaking changes will use `/api/v2/`

---

## 9. Implementation Notes

### Technology Stack
- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn (ASGI)
- **Type Safety**: Pydantic v2
- **Async**: AsyncIO
- **Testing**: pytest + httpx

### Database Integration
- Uses existing `DatabaseManager`
- Async PostgreSQL via asyncpg
- Connection pooling via `asyncpg.Pool`

### LLM Integration
- Uses existing `LLMRouter`
- Ollama-backed (local, no API costs)
- Async LLM calls with timeouts

### Monitoring
- Prometheus metrics exposure on `/metrics`
- Request/response logging to Loki
- Structured logging for observability

---

## 10. Deployment

**Container Port**: 38937 (5-digit unique port)
**Health Check**: GET `/api/v1/health`
**Graceful Shutdown**: 30-second timeout
**Hot Reload**: Disabled in production

---

## 11. SWE Spec Alignment

| FR | Requirement | API Coverage | Status |
|----|-------------|--------------|--------|
| FR-1 | Multi-stage orchestration | `/stages/{n}/execute`, `/stages/{n}/advance` | ✅ |
| FR-4 | Stage-gate validation | `/stages/{n}/advance` (validates) | ✅ |
| FR-5 | Consistency checking | `/sessions/{id}/consistency` | ✅ |
| FR-8 | Session persistence | All endpoints persist to DB | ✅ |
| NFR-1 | API availability | 99.9% uptime (production) | ✅ |
| NFR-2 | Response time | <5s p95 for most endpoints | ✅ |
| NFR-3 | Concurrent sessions | 100+ concurrent via AsyncIO | ✅ |

---

## 12. Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] GraphQL interface as alternative to REST
- [ ] OpenAPI/Swagger auto-documentation
- [ ] Request/response caching
- [ ] Bulk operations
- [ ] Export to multiple formats
- [ ] Webhook notifications
- [ ] Rate limiting & quotas
- [ ] API key management
- [ ] RBAC & fine-grained permissions

---

**Status**: Ready for implementation with TDD
**Next**: Create test suite before implementation
**Target Completion**: 3-4 hours
