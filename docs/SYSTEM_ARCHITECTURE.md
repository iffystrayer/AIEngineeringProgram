# U-AIP System Architecture

**Universal AI Project Charter Generator - Technical Architecture**
Version 1.0 | Last Updated: October 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Patterns](#architectural-patterns)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Agent Architecture](#agent-architecture)
6. [Security Architecture](#security-architecture)
7. [Scalability and Performance](#scalability-and-performance)
8. [Integration Points](#integration-points)
9. [Technology Stack](#technology-stack)
10. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │   CLI        │     │   Web API    │     │   Future:    │       │
│  │   Interface  │     │   (FastAPI)  │     │   Web UI     │       │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│         │                     │                     │               │
└─────────┼─────────────────────┼─────────────────────┼───────────────┘
          │                     │                     │
┌─────────┴─────────────────────┴─────────────────────┴───────────────┐
│                      Orchestration Layer                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │              Orchestrator Agent                            │      │
│  │  - Session lifecycle management                            │      │
│  │  - Stage routing and coordination                          │      │
│  │  - Checkpoint management                                   │      │
│  │  - Governance decision application                         │      │
│  └─────┬──────────────────────────────────────────┬──────────┘      │
│        │                                           │                  │
│        ▼                                           ▼                  │
│  ┌──────────────────────┐           ┌───────────────────────┐       │
│  │   Stage Agents       │           │  Reflection Agents    │       │
│  │   (Stages 1-5)       │           │  (Quality, StageGate, │       │
│  │                      │◀──────────│   Consistency)        │       │
│  └──────────────────────┘           └───────────────────────┘       │
│        │                                           │                  │
└────────┼───────────────────────────────────────────┼──────────────────┘
         │                                           │
┌────────┴───────────────────────────────────────────┴──────────────────┐
│                    Conversation Engine Layer                          │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────┐         │
│  │         Conversation Engine (Quality Validation)         │         │
│  │  - Question management                                   │         │
│  │  - Response quality validation                           │         │
│  │  - Follow-up question generation                         │         │
│  │  - Quality loop orchestration                            │         │
│  │  - Security: Injection detection, input sanitization     │         │
│  └─────┬────────────────────────────────────────────┬───────┘         │
│        │                                            │                  │
└────────┼────────────────────────────────────────────┼──────────────────┘
         │                                            │
┌────────┴────────────────────────────────────────────┴──────────────────┐
│                        Integration Layer                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌───────────────┐    ┌──────────────┐    ┌────────────────────┐    │
│  │  LLM Router   │    │  Database    │    │   Observability    │    │
│  │  - Provider   │    │  Manager     │    │   - Prometheus     │    │
│  │    abstraction│    │  - asyncpg   │    │   - Loki           │    │
│  │  - Failover   │    │  - Migrations│    │   - Metrics        │    │
│  └───────┬───────┘    └──────┬───────┘    └─────────┬──────────┘    │
│          │                   │                       │                │
└──────────┼───────────────────┼───────────────────────┼────────────────┘
           │                   │                       │
    ┌──────┴──────┐    ┌──────┴──────┐        ┌───────┴────────┐
    │  External   │    │  PostgreSQL │        │    Monitoring  │
    │  LLM APIs   │    │  Database   │        │    Stack       │
    │  (OpenAI,   │    │  - Sessions │        │  - Prometheus  │
    │   Claude,   │    │  - Charters │        │  - Grafana     │
    │   etc.)     │    │  - Checkpts │        │  - Loki        │
    └─────────────┘    └─────────────┘        └────────────────┘
```

### Design Principles

1. **Agent-Based Architecture**
   - Specialized agents for each stage
   - Reflection agents for validation
   - Clear separation of concerns

2. **Conversation-Driven**
   - Natural language interaction
   - Quality-validated responses
   - Adaptive follow-up questions

3. **Fail-Safe and Recoverable**
   - Checkpoint-based recovery
   - Automatic retry with exponential backoff
   - Graceful degradation

4. **Security-First**
   - Input validation and sanitization
   - Prompt injection detection
   - Privacy-preserving (no session ID leakage)

5. **Observable and Monitorable**
   - Comprehensive metrics
   - Structured logging
   - Distributed tracing

6. **Cloud-Native**
   - Containerized deployment
   - Stateless application layer
   - Horizontal scalability

---

## Architectural Patterns

### 1. Multi-Agent System Pattern

**Intent**: Decompose complex interview workflow into specialized, autonomous agents.

**Structure**:
```
Orchestrator (Coordinator)
    ├── Stage1Agent (Problem Definition)
    ├── Stage2Agent (Success Criteria)
    ├── Stage3Agent (Data Assessment)
    ├── Stage4Agent (User Impact)
    ├── Stage5Agent (Ethical Risk)
    ├── ResponseQualityAgent (Reflection)
    ├── StageGateValidatorAgent (Reflection)
    └── ConsistencyCheckerAgent (Reflection)
```

**Benefits**:
- **Modularity**: Each agent can evolve independently
- **Testability**: Agents tested in isolation
- **Maintainability**: Clear boundaries and responsibilities
- **Extensibility**: New agents easily added

**Implementation**:
```python
class Orchestrator:
    """
    Main coordinator managing agent lifecycle and routing.
    """
    def __init__(self, db_pool, llm_router):
        self.stage_agents: Dict[int, Callable] = {}
        self.reflection_agents: Dict[str, BaseAgent] = {}
        self._initialize_agent_registries()

    async def run_stage(self, session: Session, stage_number: int):
        """Route to appropriate stage agent."""
        agent_factory = self.stage_agents[stage_number]
        agent = agent_factory(session)  # Create instance with context
        return await agent.conduct_interview()

    async def invoke_quality_agent(self, question, response, session):
        """Delegate to quality validation agent."""
        return await self.reflection_agents["quality"].evaluate_response(
            question=question,
            user_response=response,
            stage_context={"stage": session.current_stage}
        )
```

### 2. Conversation Engine Pattern

**Intent**: Decouple quality validation from interview logic, enabling reusable conversation flows.

**Structure**:
```
ConversationEngine
    ├── ConversationContext (State management)
    ├── ResponseQualityAgent (Validation)
    ├── LLMRouter (Follow-up generation)
    └── Security (Sanitization, injection detection)
```

**Workflow**:
```
1. start_turn(question) → Initialize conversation
2. process_response(user_input) → Validate quality
3. IF quality < threshold:
     generate_follow_up() → Ask clarification
     GOTO 2
4. ELSE:
     return validated response
```

**Benefits**:
- **Reusability**: Same engine across all 5 stages
- **Consistency**: Uniform quality standards
- **Security**: Centralized input sanitization
- **Maintainability**: Quality logic in one place

**Implementation**:
```python
class ConversationEngine:
    """
    Manages quality-validated conversation loops.
    """
    async def start_turn(self, question: str):
        """Begin new question-answer cycle."""
        # Input validation
        if len(question) > MAX_QUESTION_LENGTH:
            raise ValueError("Question too long")

        self.context.update_current_question(question)
        self.state = ConversationState.WAITING_FOR_RESPONSE

    async def process_response(self, user_response: str) -> Dict[str, Any]:
        """Validate response quality and loop if needed."""
        # Security: Sanitize and detect injection
        if self._detect_injection(user_response):
            raise ValueError("Potential security issue detected")

        sanitized = self._sanitize_for_prompt(user_response)

        # Quality validation
        result = await asyncio.wait_for(
            self.quality_agent.evaluate_response(
                question=self.context.current_question,
                response=sanitized,
                context={
                    "stage_number": self.context.stage_number,
                    "attempt": self.context.attempt_count
                }
            ),
            timeout=TIMEOUT_SECONDS
        )

        if not result["is_acceptable"]:
            # Generate follow-up
            follow_up = await self._generate_follow_up(
                question=self.context.current_question,
                response=sanitized,
                issues=result["issues"]
            )
            return {
                "is_acceptable": False,
                "follow_up_question": follow_up,
                **result
            }

        return {"is_acceptable": True, **result}
```

### 3. Checkpoint-Based Recovery Pattern

**Intent**: Enable session recovery from any point in workflow.

**Structure**:
```
Checkpoint
    ├── stage_number (int)
    ├── timestamp (datetime)
    ├── data_snapshot (dict)
    │   ├── stage_data (dict)
    │   ├── conversation_history (list)
    │   └── current_stage (int)
    ├── validation_status (bool)
    └── session_id (UUID)
```

**Workflow**:
```
After each stage completion:
1. Create checkpoint snapshot
2. Persist to database
3. Add to session.checkpoints list

On session resume:
1. Load latest checkpoint
2. Restore session state
3. Continue from next stage
```

**Benefits**:
- **Fault Tolerance**: Recover from crashes
- **User Convenience**: Resume multi-day sessions
- **Audit Trail**: Complete history of session evolution

**Implementation**:
```python
async def save_checkpoint(self, session: Session, stage_number: int) -> Checkpoint:
    """Create immutable checkpoint after stage completion."""
    checkpoint = Checkpoint(
        stage_number=stage_number,
        timestamp=datetime.now(UTC),
        data_snapshot={
            "stage_data": deep_copy(session.stage_data),
            "conversation_history": [
                serialize_message(msg) for msg in session.conversation_history
            ],
            "current_stage": session.current_stage,
        },
        validation_status=True,
        session_id=session.session_id,
    )

    session.checkpoints.append(checkpoint)
    await self._persist_checkpoint(session, checkpoint)
    return checkpoint

async def resume_session(self, session_id: UUID) -> Session:
    """Restore session from latest checkpoint."""
    session = await self._load_session_from_db(session_id)

    if session.checkpoints:
        latest = session.checkpoints[-1]
        # Restore state from snapshot
        session.stage_data = latest.data_snapshot["stage_data"]
        session.current_stage = latest.data_snapshot["current_stage"]
        session.conversation_history = deserialize_messages(
            latest.data_snapshot["conversation_history"]
        )

    return session
```

### 4. LLM Router Pattern

**Intent**: Abstract LLM provider details, enabling multi-provider support and failover.

**Structure**:
```
LLMRouter
    ├── PrimaryProvider (OpenAI, Anthropic, etc.)
    ├── FallbackProvider (Alternative LLM)
    ├── ProviderConfig (API keys, models, timeouts)
    └── RequestLogger (Metrics, cost tracking)
```

**Workflow**:
```
1. route(prompt, context) → Select provider
2. TRY:
     call_primary_provider()
3. EXCEPT ProviderError:
     call_fallback_provider()
4. Log metrics (latency, tokens, cost)
```

**Benefits**:
- **Provider Agnostic**: Swap providers without code changes
- **Reliability**: Automatic failover
- **Cost Optimization**: Route to cheapest provider
- **Vendor Lock-in Avoidance**

**Implementation**:
```python
class LLMRouter:
    """
    Route LLM requests to appropriate provider with failover.
    """
    def __init__(self, primary_provider, fallback_provider=None):
        self.primary = primary_provider
        self.fallback = fallback_provider

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion with automatic failover."""
        try:
            start_time = time.time()
            response = await asyncio.wait_for(
                self.primary.complete(prompt, **kwargs),
                timeout=LLM_TIMEOUT_SECONDS
            )
            latency = time.time() - start_time

            # Metrics
            metrics.llm_requests_total.labels(
                provider=self.primary.name,
                model=kwargs.get("model", "default")
            ).inc()

            metrics.llm_latency_seconds.labels(
                provider=self.primary.name,
                model=kwargs.get("model", "default")
            ).observe(latency)

            return response

        except (asyncio.TimeoutError, ProviderError) as e:
            if self.fallback:
                logger.warning(f"Primary LLM failed, using fallback: {e}")
                return await self.fallback.complete(prompt, **kwargs)
            raise
```

### 5. Stage-Gate Validation Pattern

**Intent**: Enforce quality gates between stages to ensure deliverable completeness.

**Structure**:
```
Stage Execution → Stage Output → Stage Gate Validator → Proceed/Retry

StageGateValidatorAgent
    ├── validate_stage(stage_number, collected_data)
    ├── check_completeness()
    ├── check_quality()
    └── generate_recommendations()
```

**Validation Criteria**:
```python
STAGE_REQUIREMENTS = {
    1: {  # Problem Statement
        "required_fields": [
            "business_objective",
            "ai_necessity_justification",
            "input_features",
            "target_output",
            "ml_archetype"
        ],
        "min_features": 2,
        "ml_archetype_valid": True,
    },
    2: {  # Success Criteria
        "required_fields": ["business_kpis", "ml_metrics"],
        "min_kpis": 1,
        "min_ml_metrics": 2,
        "metric_alignment_exists": True,
    },
    # ... stages 3-5
}
```

**Benefits**:
- **Quality Assurance**: Ensure deliverables meet standards
- **Early Error Detection**: Catch issues before later stages
- **User Guidance**: Provide feedback on what's missing

---

## Component Architecture

### Orchestrator Agent

**Responsibilities**:
1. Session lifecycle management (create, resume, persist)
2. Route control between stage agents
3. Enforce stage-gate progression (1→2→3→4→5)
4. Invoke reflection agents at checkpoints
5. Generate final AI Project Charter
6. Make governance decisions

**Key Methods**:
```python
class Orchestrator:
    async def create_session(user_id, project_name) -> Session
    async def resume_session(session_id) -> Session
    async def run_stage(session, stage_number) -> StageOutput
    async def invoke_quality_agent(question, response, session) -> QualityAssessment
    async def invoke_stage_gate_validator(session, stage_number) -> StageValidation
    async def invoke_consistency_checker(session) -> ConsistencyReport
    async def generate_charter(session) -> AIProjectCharter
    async def save_checkpoint(session, stage_number) -> Checkpoint
```

**State Management**:
```python
self.active_sessions: Dict[UUID, Session] = {}
self.quality_attempts: Dict[UUID, Dict[int, int]] = {}
self.stage_agents: Dict[int, Callable] = {1: Stage1Factory, ...}
self.reflection_agents: Dict[str, BaseAgent] = {
    "quality": ResponseQualityAgent,
    "stage_gate": StageGateValidatorAgent,
    "consistency": ConsistencyCheckerAgent
}
```

### Stage Agents (1-5)

**Common Interface**:
```python
class BaseStageAgent(ABC):
    """Abstract base class for all stage agents."""

    def __init__(
        self,
        session_context: Session,
        llm_router: LLMRouter,
        quality_agent: ResponseQualityAgent = None,
        quality_threshold: float = 7.0,
        max_quality_attempts: int = 3
    ):
        self.session_context = session_context
        self.llm_router = llm_router
        self.quality_agent = quality_agent
        self.quality_threshold = quality_threshold
        self.max_quality_attempts = max_quality_attempts

    @abstractmethod
    async def conduct_interview(self) -> StageDeliverable:
        """Execute stage-specific interview and return deliverable."""
        pass

    async def ask_question_group(self, group_number: int) -> List[str]:
        """Common pattern for question group execution."""
        pass
```

**Stage-Specific Implementations**:

| Stage | Agent Class | Deliverable | Key Methods |
|-------|------------|-------------|-------------|
| 1 | Stage1Agent | ProblemStatement | `determine_ml_archetype()`, `validate_feature_availability()` |
| 2 | Stage2Agent | MetricAlignmentMatrix | `define_business_kpis()`, `align_ml_metrics()` |
| 3 | Stage3Agent | DataQualityScorecard | `assess_data_quality()`, `calculate_dimension_scores()` |
| 4 | Stage4Agent | UserContext | `identify_primary_users()`, `analyze_unintended_consequences()` |
| 5 | Stage5Agent | EthicalRiskReport | `evaluate_ethical_risks()`, `determine_governance_decision()` |

### Reflection Agents

**1. ResponseQualityAgent**

**Purpose**: Evaluate quality of user responses on 0-10 scale

**Evaluation Criteria**:
```python
{
    "specificity": "Contains concrete details vs vague statements",
    "completeness": "Addresses all parts of question",
    "relevance": "On-topic and contextually appropriate",
    "clarity": "Unambiguous and well-structured",
    "evidence": "Includes examples, metrics, or data"
}
```

**Output**:
```python
QualityAssessment(
    quality_score: int,  # 0-10
    is_acceptable: bool,  # score >= threshold
    issues: List[str],  # e.g., ["Too vague", "Missing metrics"]
    suggested_followups: List[str],  # Clarification questions
    examples_to_provide: List[str]  # Optional: example good answers
)
```

**2. StageGateValidatorAgent**

**Purpose**: Validate stage deliverable completeness before progression

**Validation Logic**:
```python
async def validate_stage(
    self,
    stage_number: int,
    collected_data: Dict[str, Any]
) -> StageValidation:
    """
    Check:
    1. All required fields present
    2. Data types correct
    3. Cross-field consistency
    4. Domain-specific rules
    """
    requirements = STAGE_REQUIREMENTS[stage_number]
    missing_items = []
    validation_concerns = []

    # Check required fields
    for field in requirements["required_fields"]:
        if field not in collected_data:
            missing_items.append(field)

    # Domain-specific validation
    if stage_number == 1:
        # Validate ML archetype aligns with input/output
        if not self._validate_archetype_alignment(collected_data):
            validation_concerns.append("ML archetype doesn't match I/O")

    completeness_score = 1.0 - (len(missing_items) / len(requirements["required_fields"]))

    return StageValidation(
        can_proceed=completeness_score >= 0.9,
        completeness_score=completeness_score,
        missing_items=missing_items,
        validation_concerns=validation_concerns,
        recommendations=self._generate_recommendations(missing_items)
    )
```

**3. ConsistencyCheckerAgent**

**Purpose**: Cross-validate data across all 5 stages for contradictions

**Consistency Checks**:
```python
{
    "metric_alignment": "Stage 2 metrics match Stage 1 problem type",
    "data_feasibility": "Stage 3 data supports Stage 1 features",
    "user_technical_fit": "Stage 4 users can interpret Stage 2 metrics",
    "ethical_scope_match": "Stage 5 risks align with Stage 1 scope",
    "cross_stage_timeline": "Timelines consistent across stages"
}
```

**Output**:
```python
ConsistencyReport(
    is_consistent: bool,
    overall_feasibility: FeasibilityLevel,
    contradictions: List[Contradiction],  # What conflicts
    risk_areas: List[str],  # What needs attention
    recommendations: List[str]  # How to resolve
)
```

### Conversation Engine

**Core Components**:

```python
class ConversationEngine:
    """
    Quality-validated conversation manager.
    """
    def __init__(
        self,
        quality_agent: ResponseQualityAgent,
        llm_router: LLMRouter,
        context: ConversationContext
    ):
        self.quality_agent = quality_agent
        self.llm_router = llm_router
        self.context = context
        self.state = ConversationState.IDLE

class ConversationContext:
    """
    Stateful conversation context.
    """
    session_id: UUID
    stage_number: int
    current_question: str
    attempt_count: int
    max_attempts: int
    conversation_history: List[Message]

    def update_current_question(self, question: str):
        """Update question and reset attempt counter."""
        self.current_question = question
        self.attempt_count = 0
        self.conversation_history.append(
            Message(role=MessageRole.ASSISTANT, content=question)
        )

    def add_user_message(self, content: str):
        """Add user response to history."""
        self.conversation_history.append(
            Message(role=MessageRole.USER, content=content)
        )
        self.attempt_count += 1

enum ConversationState:
    IDLE
    WAITING_FOR_RESPONSE
    VALIDATING_RESPONSE
    GENERATING_FOLLOW_UP
    COMPLETE
    ERROR
```

**Security Features (H-1, H-2, H-3)**:

```python
# H-1: Prompt Injection Detection
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior)\s+instructions',
    r'new\s+instruction',
    r'system\s+prompt',
    r'forget\s+(everything|all|previous)',
    r'you\s+are\s+now',
    r'disregard\s+(all|previous)',
    r'override\s+',
]

def _detect_injection(self, text: str) -> bool:
    """Detect potential prompt injection attempts."""
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"Potential injection detected: {pattern}")
            return True
    return False

# H-2: Denial of Service Prevention
MAX_QUESTION_LENGTH = 500
MAX_RESPONSE_LENGTH = 10000
MAX_FOLLOW_UP_LENGTH = 2000

async def start_turn(self, question: str):
    """Validate input size before processing."""
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(f"Question exceeds {MAX_QUESTION_LENGTH} chars")

# H-3: Session Context Data Leakage Prevention
# session_id REMOVED from external API calls
result = await self.quality_agent.evaluate_response(
    question=self.context.current_question,
    response=user_response,
    context={
        # ✅ session_id NOT included
        "stage_number": self.context.stage_number,
        "attempt": self.context.attempt_count
    }
)
```

---

## Data Flow

### End-to-End Session Flow

```
1. User initiates session
   │
   ├─ CLI: python -m src.cli.main start --project-name "My Project"
   │  OR
   └─ API: POST /api/sessions {user_id, project_name}
   │
   ▼
2. Orchestrator creates session
   │
   ├─ Generate UUID
   ├─ Initialize session object
   ├─ Persist to PostgreSQL
   └─ Return session_id
   │
   ▼
3. Execute Stage 1 (Problem Definition)
   │
   ├─ Orchestrator.run_stage(session, 1)
   ├─ Create Stage1Agent instance with ConversationEngine
   └─ Stage1Agent.conduct_interview()
       │
       ├─ Question Group 1: Core Business Objective
       │   ├─ For each question in group:
       │   │   ├─ ConversationEngine.start_turn(question)
       │   │   ├─ Get user response (via CLI/API)
       │   │   ├─ ConversationEngine.process_response(response)
       │   │   │   ├─ Security: Detect injection, sanitize
       │   │   │   ├─ Quality: Call ResponseQualityAgent
       │   │   │   ├─ IF quality < 7: Generate follow-up, loop
       │   │   │   └─ ELSE: Accept response
       │   │   └─ Store response in collected_responses
       │   │
       │   ├─ Question Group 2: AI Suitability
       │   ├─ Question Group 3: Problem Definition
       │   └─ Question Group 4: Scope & Boundaries
       │
       ├─ Generate ProblemStatement from collected_responses
       │   ├─ Determine ML archetype
       │   ├─ Validate feature availability
       │   └─ Create ProblemStatement object
       │
       └─ Return ProblemStatement
   │
   ▼
4. Stage Gate Validation
   │
   ├─ Orchestrator.invoke_stage_gate_validator(session, 1)
   ├─ StageGateValidatorAgent.validate_stage(1, problem_statement)
   │   ├─ Check required fields
   │   ├─ Validate ML archetype alignment
   │   └─ Return can_proceed=True/False
   │
   ├─ IF can_proceed:
   │   ├─ session.stage_data[1] = problem_statement
   │   └─ Orchestrator.advance_to_next_stage(session)
   │       ├─ session.current_stage = 2
   │       └─ Orchestrator.save_checkpoint(session, 1)
   │           ├─ Create checkpoint snapshot
   │           └─ Persist to database
   │
   └─ ELSE:
       └─ Retry Stage 1 or escalate
   │
   ▼
5. Repeat for Stages 2-5
   │
   ├─ Stage 2: Success Criteria → MetricAlignmentMatrix
   ├─ Stage 3: Data Assessment → DataQualityScorecard
   ├─ Stage 4: User Impact → UserContext
   └─ Stage 5: Ethical Risk → EthicalRiskReport
       └─ Governance decision made here
   │
   ▼
6. Consistency Check
   │
   ├─ Orchestrator.invoke_consistency_checker(session)
   ├─ ConsistencyCheckerAgent.check_consistency(all_stage_data)
   │   ├─ Cross-validate stages 1-5
   │   ├─ Identify contradictions
   │   └─ Return ConsistencyReport
   │
   └─ IF not consistent:
       └─ Flag issues in final charter
   │
   ▼
7. Charter Generation
   │
   ├─ Orchestrator.generate_charter(session)
   ├─ Extract all stage deliverables
   ├─ Apply governance decision
   ├─ Calculate overall feasibility
   ├─ Compile critical success factors
   ├─ Compile major risks
   └─ Create AIProjectCharter object
   │
   ▼
8. Session Completion
   │
   ├─ session.status = COMPLETED
   ├─ Save final checkpoint
   ├─ Persist charter to database
   └─ Return charter to user
       │
       ├─ CLI: Display charter + export options
       └─ API: Return JSON charter
```

### Data Storage Schema

```sql
-- Session management
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    project_name VARCHAR(500) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    current_stage INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL,  -- IN_PROGRESS, COMPLETED, FAILED
    stage_data JSONB NOT NULL DEFAULT '{}',
    conversation_history JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_started_at ON sessions(started_at DESC);

-- Checkpoints for recovery
CREATE TABLE checkpoints (
    checkpoint_id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    data_snapshot JSONB NOT NULL,
    validation_status BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkpoints_session_id ON checkpoints(session_id);
CREATE INDEX idx_checkpoints_timestamp ON checkpoints(timestamp DESC);

-- Final charters
CREATE TABLE ai_project_charters (
    charter_id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    project_name VARCHAR(500) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    governance_decision VARCHAR(100) NOT NULL,
    overall_feasibility VARCHAR(50) NOT NULL,
    problem_statement JSONB NOT NULL,
    metric_alignment_matrix JSONB NOT NULL,
    data_quality_scorecard JSONB NOT NULL,
    user_context JSONB NOT NULL,
    ethical_risk_report JSONB NOT NULL,
    critical_success_factors JSONB NOT NULL,
    major_risks JSONB NOT NULL,
    charter_version VARCHAR(20) NOT NULL DEFAULT '1.0'
);

CREATE INDEX idx_charters_session_id ON ai_project_charters(session_id);
CREATE INDEX idx_charters_governance ON ai_project_charters(governance_decision);
CREATE INDEX idx_charters_created_at ON ai_project_charters(created_at DESC);

-- User management
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Audit logs
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
```

---

## Agent Architecture

### Agent Communication Protocol

**Message Format**:
```python
@dataclass
class AgentMessage:
    """Standardized message format for agent communication."""
    sender: str  # Agent name
    receiver: str  # Target agent or "orchestrator"
    message_type: str  # REQUEST, RESPONSE, ERROR, NOTIFICATION
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: UUID  # For tracking related messages
```

**Communication Patterns**:

1. **Orchestrator → Stage Agent** (Synchronous)
```python
# Orchestrator sends
request = AgentMessage(
    sender="orchestrator",
    receiver="stage1_agent",
    message_type="REQUEST",
    payload={"session_id": session.session_id, "action": "conduct_interview"},
    correlation_id=uuid4()
)

# Stage Agent responds
response = await stage1_agent.handle_message(request)
# response.payload contains ProblemStatement
```

2. **Stage Agent → Quality Agent** (via ConversationEngine)
```python
# Indirect call through ConversationEngine
quality_result = await conversation_engine.process_response(user_input)
# ConversationEngine internally calls ResponseQualityAgent
```

3. **Orchestrator → Reflection Agents** (Synchronous validation)
```python
# Stage gate validation
validation = await orchestrator.invoke_stage_gate_validator(session, stage_num)

# Consistency check
consistency = await orchestrator.invoke_consistency_checker(session)
```

### Agent State Management

Each agent maintains internal state during execution:

```python
class Stage1Agent:
    def __init__(self, session_context, llm_router, quality_agent):
        # Immutable context
        self.session_context = session_context  # Read-only session info

        # Mutable state
        self.collected_responses: Dict[str, Any] = {}
        self.quality_attempts: Dict[str, int] = {}
        self.current_group: Optional[QuestionGroup] = None
        self.conversation_engine: Optional[ConversationEngine] = None

    async def conduct_interview(self) -> ProblemStatement:
        """
        Stateful interview execution.
        State transitions: IDLE → QUESTIONING → PROCESSING → COMPLETE
        """
        for group in self.question_groups:
            self.current_group = group  # State update
            responses = await self.ask_question_group(group.group_number)
            self._store_responses(group, responses)

        return await self.generate_problem_statement(self.collected_responses)
```

**State Persistence**:
- **In-Memory**: Active session state in Orchestrator
- **Database**: Checkpoints after each stage
- **Recovery**: Restore from latest checkpoint on resume

---

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────┐
│                  Application Security                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Layer 1: Input Validation & Sanitization               │
│  ┌───────────────────────────────────────────────────┐  │
│  │ - Size limits (500/10000/2000 char)               │  │
│  │ - Type validation (string, int, enum)             │  │
│  │ - Sanitize special characters                     │  │
│  │ - Remove triple quotes (prompt escape)            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Layer 2: Prompt Injection Detection                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ - Pattern matching (regex)                        │  │
│  │ - Suspicious phrase detection                     │  │
│  │ - Logging and blocking                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Layer 3: Data Minimization (Privacy)                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │ - Remove session_id from external API calls       │  │
│  │ - Anonymize logs (user_id hashed)                 │  │
│  │ - Encrypt PII at rest                             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Layer 4: Rate Limiting & Throttling                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ - 60 requests/minute per user                     │  │
│  │ - 10 burst size                                    │  │
│  │ - Backoff on repeated violations                  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Layer 5: Authentication & Authorization                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ - JWT tokens (RS256, 1-hour expiry)               │  │
│  │ - API keys (bcrypt hashed)                        │  │
│  │ - RBAC (User, Reviewer, Admin, SuperAdmin)        │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                Infrastructure Security                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  - TLS 1.3 (HTTPS only)                                  │
│  - Firewall rules (block direct database access)         │
│  - Container isolation (Docker networks)                 │
│  - Secrets management (Vault, Docker Secrets)            │
│  - Vulnerability scanning (docker scan, safety)          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Security Implementation Details

**Implemented Fixes (H-1, H-2, H-3)**:

| Fix | Vulnerability | Implementation | Location |
|-----|--------------|----------------|----------|
| **H-1** | Prompt Injection | Regex pattern matching + sanitization | `src/conversation/engine.py:_detect_injection()` |
| **H-2** | Denial of Service | Input size limits (500/10000/2000) | `src/conversation/engine.py:start_turn()`, `process_response()` |
| **H-3** | Session Leakage | Remove session_id from external calls | `src/conversation/engine.py:_validate_quality()` |
| **Bonus** | Timeout Hanging | 30-second timeout on async LLM calls | `src/conversation/engine.py` (asyncio.wait_for) |

**Pending Security Work (M-1 through M-4)**:

| Priority | Issue | Description | Effort |
|----------|-------|-------------|--------|
| **M-1** | PII Logging | Sanitize logs to remove user emails, session IDs | 4-6 hours |
| **M-2** | State Management | Add async locks for concurrent session access | 4-6 hours |
| **M-3** | Error Handling | Granular exception types, better error messages | 4-6 hours |
| **M-4** | Type Validation | Runtime Pydantic validation for all inputs | 4-6 hours |

---

## Scalability and Performance

### Scalability Patterns

**1. Stateless Application Tier**
```
┌────────────┐  ┌────────────┐  ┌────────────┐
│  U-AIP     │  │  U-AIP     │  │  U-AIP     │
│  Instance  │  │  Instance  │  │  Instance  │
│     1      │  │     2      │  │     3      │
└────────────┘  └────────────┘  └────────────┘
       │               │               │
       └───────────────┴───────────────┘
                       │
                ┌──────┴──────┐
                │  PostgreSQL │
                │  (Shared)   │
                └─────────────┘
```

- No session affinity required
- Horizontal scaling via load balancer
- Session state in database, not in-memory

**2. Database Connection Pooling**
```python
DB_POOL_CONFIG = {
    "min_size": 5,         # Minimum connections per instance
    "max_size": 20,        # Maximum connections per instance
    "max_queries": 50000,  # Recycle after N queries
    "max_inactive_connection_lifetime": 3600,  # 1 hour
}
```

**3. Async I/O for Concurrency**
```python
# Asyncio enables high concurrency
async def run_stage(self, session: Session, stage_number: int):
    """Non-blocking stage execution."""
    stage_agent = self.stage_agents[stage_number](session)
    return await stage_agent.conduct_interview()

# Multiple sessions can run concurrently
await asyncio.gather(
    orchestrator.run_stage(session1, 1),
    orchestrator.run_stage(session2, 1),
    orchestrator.run_stage(session3, 2)
)
```

**4. LLM Request Batching (Future)**
```python
# Batch multiple questions to LLM in single API call
questions = [q1, q2, q3, q4]
responses = await llm_router.batch_complete(questions)  # One API call

# Reduces latency and API costs
```

### Performance Metrics

**Target Performance**:

| Metric | Target | Notes |
|--------|--------|-------|
| Session creation | < 100ms | Database write + init |
| Question-answer cycle | < 3s | NFR-1.1 compliance |
| Stage completion | < 5 min | Depends on user response time |
| Complete workflow | < 60 min | All 5 stages |
| API response (p95) | < 500ms | Non-LLM endpoints |
| Database query (p95) | < 50ms | With proper indexes |
| LLM API call (p95) | < 2s | External dependency |

**Performance Optimizations**:

1. **Database Indexes**
```sql
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_checkpoints_session_id ON checkpoints(session_id);
```

2. **Query Optimization**
```python
# Use JSONB operators for efficient queries
SELECT * FROM sessions WHERE stage_data @> '{"1": {"ml_archetype": "CLASSIFICATION"}}';

# Limit result sets
SELECT * FROM sessions ORDER BY created_at DESC LIMIT 100;
```

3. **Caching (Optional)**
```python
# Cache LLM responses for identical questions (testing/dev)
@lru_cache(maxsize=1000)
def get_llm_response(prompt_hash: str) -> str:
    return llm_router.complete(prompt)
```

---

## Integration Points

### External LLM APIs

**Supported Providers**:

```python
LLM_PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "azure": AzureOpenAIProvider,
    "gemini": GeminiProvider,
    "custom": CustomLLMProvider
}
```

**Provider Interface**:
```python
class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate completion from prompt."""
        pass

    @abstractmethod
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate chat completion from messages."""
        pass
```

**OpenAI Implementation**:
```python
class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def complete(self, prompt: str, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7)
        )
        return response.choices[0].message.content
```

### API Endpoints

**REST API (FastAPI)**:

```python
# Session management
POST   /api/sessions                    # Create session
GET    /api/sessions/{session_id}       # Get session
GET    /api/sessions                    # List user's sessions
DELETE /api/sessions/{session_id}       # Delete session

# Stage execution
POST   /api/sessions/{session_id}/stages/{stage_num}/start
POST   /api/sessions/{session_id}/stages/{stage_num}/response
GET    /api/sessions/{session_id}/stages/{stage_num}/status

# Charter management
GET    /api/sessions/{session_id}/charter
POST   /api/sessions/{session_id}/charter/export  # PDF/JSON/Markdown

# Health and monitoring
GET    /health
GET    /metrics  # Prometheus format
GET    /api/docs  # OpenAPI/Swagger UI
```

**WebSocket (Future - Real-time Updates)**:
```python
# Connect to session for real-time updates
ws://localhost:10000/ws/sessions/{session_id}

# Server sends:
{
  "event": "stage_started",
  "data": {"stage_number": 1, "title": "Problem Definition"}
}

{
  "event": "question_asked",
  "data": {"question": "What business problem are you solving?"}
}

{
  "event": "quality_feedback",
  "data": {"score": 6, "follow_up": "Can you be more specific?"}
}
```

### Monitoring Integration

**Prometheus Exporter**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics defined in src/observability/metrics.py
sessions_created = Counter(
    'uaip_sessions_created_total',
    'Total sessions created',
    ['user_id', 'project_name']
)

session_duration = Histogram(
    'uaip_session_duration_seconds',
    'Session completion time',
    buckets=[60, 300, 600, 1800, 3600]  # 1m, 5m, 10m, 30m, 1h
)

# Expose at /metrics endpoint
app.add_route("/metrics", generate_latest)
```

**Structured Logging (Loki)**:
```python
import structlog

logger = structlog.get_logger()

# Logs automatically formatted as JSON
logger.info(
    "session_created",
    session_id=str(session.session_id),
    user_id=session.user_id,
    project_name=session.project_name
)

# Output:
# {
#   "timestamp": "2025-10-17T10:30:00Z",
#   "level": "info",
#   "event": "session_created",
#   "session_id": "550e8400-...",
#   "user_id": "user@example.com",
#   "project_name": "Customer Churn"
# }
```

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Application logic |
| **Web Framework** | FastAPI | 0.104+ | REST API |
| **Async Runtime** | asyncio | stdlib | Concurrency |
| **Database** | PostgreSQL | 15+ | Persistent storage |
| **DB Driver** | asyncpg | 0.29+ | Async Postgres client |
| **Migrations** | Alembic | 1.12+ | Schema versioning |
| **Data Validation** | Pydantic | 2.5+ | Type safety |
| **HTTP Client** | httpx | 0.25+ | Async HTTP |

### Deployment Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Containerization** | Docker | 24.0+ | Packaging |
| **Orchestration** | Docker Compose | 2.20+ | Local/dev deployment |
| **Production** | Kubernetes | 1.28+ | Cloud deployment |
| **Reverse Proxy** | Nginx | 1.25+ | SSL termination |
| **Load Balancer** | HAProxy / ALB | Latest | Traffic distribution |

### Monitoring Stack

| Tool | Purpose | Port |
|------|---------|------|
| **Prometheus** | Metrics collection | 60090 |
| **Grafana** | Dashboards | 60001 |
| **Loki** | Log aggregation | 60100 |
| **Alertmanager** | Alert routing | 60093 |

### Development Tools

| Tool | Purpose |
|------|---------|
| **uv** | Python package management |
| **pytest** | Testing framework |
| **black** | Code formatting |
| **ruff** | Linting |
| **mypy** | Type checking |
| **pre-commit** | Git hooks |

---

## Deployment Architecture

### Local Development

```bash
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "10000:10000"
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    volumes:
      - ./src:/app/src  # Hot reload
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    ports:
      - "60543:5432"
    environment:
      - POSTGRES_DB=uaip_dev
    volumes:
      - postgres-dev:/var/lib/postgresql/data
```

### Production (Kubernetes)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: uaip-app
  namespace: uaip
spec:
  replicas: 3
  selector:
    matchLabels:
      app: uaip
  template:
    metadata:
      labels:
        app: uaip
    spec:
      containers:
      - name: uaip
        image: uaip:1.0.0
        ports:
        - containerPort: 10000
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: uaip-secrets
              key: postgres-password
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 10000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 10000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: uaip-service
spec:
  selector:
    app: uaip
  ports:
  - port: 80
    targetPort: 10000
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: uaip-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: uaip-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Cloud Deployment Options

**AWS ECS:**
- Fargate for serverless containers
- RDS for PostgreSQL
- ALB for load balancing
- CloudWatch for monitoring

**Google Cloud Run:**
- Fully managed container platform
- Cloud SQL for PostgreSQL
- Cloud Load Balancing
- Cloud Monitoring

**Azure Container Instances:**
- ACI for container hosting
- Azure Database for PostgreSQL
- Application Gateway
- Azure Monitor

---

**Document Version**: 1.0
**Last Updated**: October 2025
**For Support**: support@uaip.io
**Documentation**: [https://docs.uaip.io](https://docs.uaip.io)
