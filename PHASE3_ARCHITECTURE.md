# Phase 3: API Integration & Progress Tracking Architecture

## Overview

Phase 3 focuses on wiring the frontend to backend APIs and implementing **real-time progress tracking** for the entire questionnaire and charter generation workflow.

---

## 🎯 Key Objectives

1. **API Integration**: Connect frontend buttons to backend endpoints
2. **Progress Tracking**: Real-time visibility into questionnaire, charter generation, and reflection loop
3. **Error Handling**: Detect and display failures with debugging information
4. **User Experience**: Show what's happening behind the scenes

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
├─────────────────────────────────────────────────────────────┤
│  LandingPage → SessionForm → QuestionnaireFlow → Charter    │
│       ↓            ↓              ↓                ↓         │
│  ProgressTracker (Real-time updates via SSE/WebSocket)     │
│       ↓            ↓              ↓                ↓         │
│  API Client (Axios + TanStack Query)                       │
└─────────────────────────────────────────────────────────────┘
                         ↓ HTTP/SSE
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python)                         │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Endpoints:                                         │
│  • POST /sessions (start new)                              │
│  • GET /sessions/{id} (resume)                             │
│  • GET /sessions/{id}/progress (track progress)            │
│  • POST /sessions/{id}/answer (submit answer)              │
│  • GET /sessions/{id}/events (SSE stream)                  │
│                                                             │
│  ProgressService:                                           │
│  • Track stage completion                                  │
│  • Monitor charter generation                              │
│  • Track reflection loop iterations                        │
│  • Emit progress events                                    │
│                                                             │
│  Orchestrator:                                              │
│  • Manage session workflow                                 │
│  • Coordinate stage agents                                 │
│  • Generate charter                                        │
│  • Run reflection loop                                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│  • sessions (id, user_id, status, current_stage)           │
│  • stage_data (session_id, stage, field, value)            │
│  • progress_events (session_id, event_type, data)          │
│  • charter (session_id, content, status)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Progress Tracking States

### Session States
```
CREATED → IN_PROGRESS → CHARTER_GENERATING → REFLECTION_LOOP → COMPLETED
                                                                    ↓
                                                              FAILED (error)
```

### Stage States
```
NOT_STARTED → IN_PROGRESS → COMPLETED → VALIDATED
```

### Charter Generation States
```
QUEUED → GENERATING → VALIDATING → REFLECTION_LOOP → COMPLETED
                                                          ↓
                                                    FAILED (error)
```

### Reflection Loop States
```
ITERATION_1 → ITERATION_2 → ITERATION_3 → ... → COMPLETED
```

---

## 🔌 API Endpoints

### 1. Start New Session
```
POST /sessions
Request: {
  "user_id": "user123",
  "project_name": "AI Project",
  "description": "Project description"
}
Response: {
  "session_id": "uuid",
  "status": "CREATED",
  "current_stage": 1
}
```

### 2. Resume Session
```
GET /sessions/{session_id}
Response: {
  "session_id": "uuid",
  "user_id": "user123",
  "status": "IN_PROGRESS",
  "current_stage": 2,
  "progress": {
    "stage_1": "COMPLETED",
    "stage_2": "IN_PROGRESS",
    "stage_3": "NOT_STARTED"
  }
}
```

### 3. Get Progress
```
GET /sessions/{session_id}/progress
Response: {
  "session_id": "uuid",
  "status": "IN_PROGRESS",
  "current_stage": 2,
  "questions_answered": 15,
  "total_questions": 25,
  "charter_status": "NOT_STARTED",
  "reflection_iterations": 0,
  "last_update": "2025-10-20T12:34:56Z"
}
```

### 4. Submit Answer
```
POST /sessions/{session_id}/answer
Request: {
  "stage": 2,
  "field": "value_proposition",
  "value": "answer text",
  "quality_score": 0.85
}
Response: {
  "success": true,
  "next_question": {...}
}
```

### 5. Real-time Progress Stream (SSE)
```
GET /sessions/{session_id}/events
Response: Server-Sent Events stream
  event: stage_completed
  data: {"stage": 1, "timestamp": "..."}
  
  event: charter_generating
  data: {"status": "GENERATING", "progress": 0.25}
  
  event: reflection_iteration
  data: {"iteration": 1, "status": "IN_PROGRESS"}
  
  event: error
  data: {"error": "...", "details": "..."}
```

---

## 🗄️ Database Schema Extensions

### progress_events Table
```sql
CREATE TABLE progress_events (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES sessions(id),
  event_type VARCHAR(50),  -- stage_completed, charter_generating, etc.
  data JSONB,
  timestamp TIMESTAMP DEFAULT NOW(),
  INDEX (session_id, timestamp)
);
```

### charter Table
```sql
CREATE TABLE charter (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES sessions(id),
  content TEXT,
  status VARCHAR(50),  -- GENERATING, VALIDATING, COMPLETED, FAILED
  reflection_iterations INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎨 Frontend Components

### ProgressTracker Component
```
┌─────────────────────────────────────┐
│  Session Progress                   │
├─────────────────────────────────────┤
│  Status: IN_PROGRESS                │
│  Current Stage: 2 / 5               │
│  Questions: 15 / 25                 │
│                                     │
│  ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  60% Complete                       │
│                                     │
│  Stage 1: ✓ COMPLETED               │
│  Stage 2: ⟳ IN_PROGRESS             │
│  Stage 3: ○ NOT_STARTED             │
│  Stage 4: ○ NOT_STARTED             │
│  Stage 5: ○ NOT_STARTED             │
│                                     │
│  Charter Generation: NOT_STARTED    │
│  Reflection Loop: 0 iterations      │
│                                     │
│  Last Update: 2 seconds ago         │
└─────────────────────────────────────┘
```

### Error Display Component
```
┌─────────────────────────────────────┐
│  ⚠️ Error Occurred                   │
├─────────────────────────────────────┤
│  Error: Stage 2 validation failed   │
│  Details: Missing required field    │
│  Timestamp: 2025-10-20 12:34:56     │
│                                     │
│  [Retry] [View Logs] [Contact Help] │
└─────────────────────────────────────┘
```

---

## 🔄 Data Flow Example

### Start New Questionnaire Flow
```
1. User clicks "Start New Questionnaire"
   ↓
2. SessionForm component opens
   ↓
3. User fills form and submits
   ↓
4. API Client: POST /sessions
   ↓
5. Backend: Create session, emit event
   ↓
6. Frontend: Receive session_id, subscribe to SSE
   ↓
7. Navigate to QuestionnaireFlow
   ↓
8. ProgressTracker subscribes to /sessions/{id}/events
   ↓
9. Display first question from Stage 1
   ↓
10. User answers question
    ↓
11. API Client: POST /sessions/{id}/answer
    ↓
12. Backend: Save answer, emit progress event
    ↓
13. Frontend: Receive event, update ProgressTracker
    ↓
14. Display next question or move to next stage
```

---

## 🛡️ Error Handling Strategy

### Error Types
1. **Validation Errors**: Invalid input, missing fields
2. **Stage Errors**: Stage agent failures, LLM errors
3. **Charter Errors**: Generation failures, reflection loop issues
4. **Network Errors**: Connection timeouts, server errors
5. **Database Errors**: Persistence failures

### Error Recovery
- Retry mechanism with exponential backoff
- Checkpoint system to resume from last valid state
- Detailed error logging for debugging
- User-friendly error messages

---

## 📈 Monitoring & Logging

### Frontend Logging
- API call tracking
- Error tracking
- User interaction tracking
- Performance metrics

### Backend Logging
- Session lifecycle events
- Stage agent execution
- Charter generation progress
- Reflection loop iterations
- Error details with stack traces

### Centralized Monitoring
- Send logs to backend for aggregation
- Dashboard for real-time monitoring
- Alert system for critical errors

---

## 🚀 Implementation Order

1. **Backend Progress Service** (Task 2)
2. **Backend API Endpoints** (Task 3)
3. **SSE/WebSocket Implementation** (Task 4)
4. **Frontend API Client** (Task 5)
5. **SessionForm Component** (Task 6)
6. **ProgressTracker Component** (Task 8)
7. **QuestionnaireFlow Component** (Task 9)
8. **Error Handling** (Task 10)
9. **Charter Display** (Task 11)
10. **End-to-End Testing** (Task 13)

---

## 📊 Success Criteria

- ✅ All API endpoints working
- ✅ Real-time progress updates visible
- ✅ Errors detected and displayed
- ✅ Complete questionnaire flow working
- ✅ Charter generation tracked
- ✅ Reflection loop visible
- ✅ 100% test coverage for new code
- ✅ End-to-end flow tested

---

*Architecture Document for Phase 3*
*Status: Planning Phase*
*Next: Implement Backend Progress Service*

