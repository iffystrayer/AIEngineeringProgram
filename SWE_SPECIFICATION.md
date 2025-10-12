# Software Engineering Specification: U-AIP Scoping Assistant

**Project Name:** U-AIP Scoping Assistant
**Version:** 1.0.0
**Date:** 2025-10-12
**Status:** Design Phase
**Document Owner:** Technical Architecture Team

---

## Executive Summary

The U-AIP Scoping Assistant is an intelligent, conversational agent system built on the Claude Agent SDK that guides users through the Universal AI Project Scoping and Framing Protocol (U-AIP). The system conducts structured interviews across five evaluation stages, validates responses through self-reflection agents, and generates comprehensive AI Project Charter documents that ensure strategic alignment, technical feasibility, and ethical compliance.

**Key Differentiators:**
- Autonomous quality assurance through self-reflection agents
- Rigorous stage-gate validation preventing premature progression
- Dynamic follow-up questioning based on response quality
- Automated ethical risk assessment with governance decisions
- APA 7th Edition compliant documentation generation

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Requirements](#2-requirements)
3. [System Architecture](#3-system-architecture)
4. [Component Specifications](#4-component-specifications)
5. [Data Models](#5-data-models)
6. [Agent Specifications](#6-agent-specifications)
7. [Tool Specifications](#7-tool-specifications)
8. [Conversation Flow](#8-conversation-flow)
9. [Quality Assurance & Validation](#9-quality-assurance--validation)
10. [Output Specifications](#10-output-specifications)
11. [Technology Stack](#11-technology-stack)
12. [Development Phases](#12-development-phases)
13. [Testing Strategy](#13-testing-strategy)
14. [Deployment Architecture](#14-deployment-architecture)
15. [Security & Compliance](#15-security--compliance)
16. [Performance Requirements](#16-performance-requirements)
17. [Monitoring & Observability](#17-monitoring--observability)
18. [Risks & Mitigations](#18-risks--mitigations)
19. [Future Enhancements](#19-future-enhancements)

---

## 1. System Overview

### 1.1 Purpose

The U-AIP Scoping Assistant automates the rigorous evaluation process defined in the Universal AI Project Scoping and Framing Protocol, transforming a multi-week manual documentation process into a 30-45 minute guided conversational experience.

### 1.2 Scope

**In Scope:**
- Interactive interview system for all 5 U-AIP stages
- Real-time response quality validation
- Stage-gate enforcement mechanisms
- Cross-stage consistency checking
- Automated AI Project Charter generation
- APA 7th Edition citation formatting
- Ethical risk calculation and governance decision automation
- Session state persistence and resumption
- Export to multiple formats (Markdown, PDF, JSON)

**Out of Scope (v1.0):**
- Multi-stakeholder collaborative editing
- Integration with project management tools (Jira, Confluence)
- Visual dashboard/analytics
- Mobile application interface
- Real-time collaboration features
- External data source integration for automatic data quality assessment

### 1.3 Users

**Primary Users:**
- AI Product Managers
- Data Science Team Leads
- ML Engineers
- AI Strategy Consultants

**Secondary Users:**
- Ethics Officers (reviewing Stage 5 outputs)
- Executive Stakeholders (reviewing final charters)
- Compliance Teams (auditing governance decisions)

### 1.4 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session completion rate | >80% | % of started sessions that produce final charter |
| Time to complete full protocol | <60 minutes | Average session duration |
| Charter quality score (expert review) | >8/10 | Independent expert evaluation |
| Response quality improvement | >50% reduction in vague responses | Comparison vs. unguided interviews |
| Ethical governance accuracy | 100% correct Proceed/Revise/Halt decisions | Validation against expert review |
| User satisfaction (NPS) | >40 | Post-session survey |

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-1: Multi-Stage Interview Orchestration
- **FR-1.1:** System SHALL conduct structured interviews across 5 sequential stages
- **FR-1.2:** System SHALL prevent progression to next stage until current stage validation passes
- **FR-1.3:** System SHALL allow users to revisit and edit previous stage responses
- **FR-1.4:** System SHALL maintain conversation context across all stages

#### FR-2: Dynamic Question Management
- **FR-2.1:** System SHALL ask all mandatory questions defined in U-AIP protocol
- **FR-2.2:** System SHALL generate contextual follow-up questions based on user responses
- **FR-2.3:** System SHALL provide examples and clarifications when user requests help
- **FR-2.4:** System SHALL adapt question phrasing based on user's domain expertise level

#### FR-3: Response Quality Validation
- **FR-3.1:** System SHALL evaluate response quality on 10-point scale
- **FR-3.2:** System SHALL reject responses scoring below quality threshold (score < 7)
- **FR-3.3:** System SHALL provide specific feedback on why response is insufficient
- **FR-3.4:** System SHALL suggest targeted follow-up questions to improve response quality
- **FR-3.5:** System SHALL limit follow-up loops to maximum 3 attempts before escalating

#### FR-4: Stage Gate Validation
- **FR-4.1:** System SHALL verify all mandatory fields are populated before stage completion
- **FR-4.2:** System SHALL validate logical consistency within each stage
- **FR-4.3:** System SHALL check for missing information against stage requirements
- **FR-4.4:** System SHALL produce stage-specific deliverable (Problem Statement, Metric Alignment Matrix, etc.)

#### FR-5: Cross-Stage Consistency Checking
- **FR-5.1:** System SHALL validate alignment between Stage 1 problem and Stage 2 metrics
- **FR-5.2:** System SHALL verify Stage 3 data availability supports Stage 2 metrics
- **FR-5.3:** System SHALL check Stage 4 user personas align with Stage 3 data access
- **FR-5.4:** System SHALL ensure Stage 5 ethical risks match project scope from Stages 1-4
- **FR-5.5:** System SHALL identify and report logical contradictions across stages

#### FR-6: Ethical Risk Assessment Automation
- **FR-6.1:** System SHALL calculate residual risk scores for each ethical principle
- **FR-6.2:** System SHALL automatically determine governance decision (Proceed/Revise/Halt)
- **FR-6.3:** System SHALL generate mandatory ethical risk assessment report
- **FR-6.4:** System SHALL flag projects requiring AI Review Committee submission

#### FR-7: Document Generation
- **FR-7.1:** System SHALL generate complete AI Project Charter in APA 7 format
- **FR-7.2:** System SHALL include all 8 required charter sections
- **FR-7.3:** System SHALL support export to Markdown, PDF, and JSON formats
- **FR-7.4:** System SHALL generate interim deliverables for each stage
- **FR-7.5:** System SHALL maintain citation bibliography in APA 7 format

#### FR-8: Session Management
- **FR-8.1:** System SHALL save session state after each completed stage
- **FR-8.2:** System SHALL allow users to resume interrupted sessions
- **FR-8.3:** System SHALL provide session history and version control
- **FR-8.4:** System SHALL support exporting partial progress reports

### 2.2 Non-Functional Requirements

#### NFR-1: Performance
- **NFR-1.1:** System SHALL respond to user input within 3 seconds (95th percentile)
- **NFR-1.2:** System SHALL support concurrent sessions without degradation
- **NFR-1.3:** System SHALL handle sessions up to 120 minutes in duration
- **NFR-1.4:** System SHALL generate final charter document within 10 seconds

#### NFR-2: Reliability
- **NFR-2.1:** System SHALL have 99.5% uptime during business hours
- **NFR-2.2:** System SHALL automatically recover from transient API failures
- **NFR-2.3:** System SHALL persist session state to prevent data loss on crashes
- **NFR-2.4:** System SHALL provide graceful degradation if reflection agents fail

#### NFR-3: Usability
- **NFR-3.1:** Users SHALL be able to start sessions without training
- **NFR-3.2:** System SHALL provide clear progress indicators
- **NFR-3.3:** System SHALL use plain language avoiding technical jargon
- **NFR-3.4:** System SHALL provide contextual help throughout session

#### NFR-4: Maintainability
- **NFR-4.1:** Code SHALL follow PEP 8 Python style guidelines
- **NFR-4.2:** All components SHALL have >80% test coverage
- **NFR-4.3:** System SHALL use configuration files for U-AIP question templates
- **NFR-4.4:** Architecture SHALL support adding new stages without core code changes

#### NFR-5: Security
- **NFR-5.1:** System SHALL encrypt session data at rest
- **NFR-5.2:** System SHALL not log sensitive business information
- **NFR-5.3:** System SHALL validate and sanitize all user inputs
- **NFR-5.4:** System SHALL implement rate limiting to prevent abuse

#### NFR-6: Scalability
- **NFR-6.1:** System SHALL support 100 concurrent users
- **NFR-6.2:** System SHALL be containerized for horizontal scaling
- **NFR-6.3:** Session storage SHALL support distributed deployment

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  - CLI Interface (v1.0)                                      │
│  - Web Interface (future)                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  Application Layer                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Orchestrator Agent                          │    │
│  │  - Session management                               │    │
│  │  - Stage progression control                        │    │
│  │  - Agent coordination                               │    │
│  │  - Output synthesis                                 │    │
│  └──────────┬──────────────────────────┬───────────────┘    │
│             │                          │                     │
│  ┌──────────▼──────────┐    ┌─────────▼──────────────┐     │
│  │  Stage Interview     │    │  Reflection Agent      │     │
│  │  Agents (5)          │    │  System                │     │
│  │                      │    │                        │     │
│  │  - Stage 1: Business │    │  - Response Quality    │     │
│  │  - Stage 2: Value    │◄───┤  - Stage Gate          │     │
│  │  - Stage 3: Data     │    │  - Consistency Check   │     │
│  │  - Stage 4: User     │    │                        │     │
│  │  - Stage 5: Ethics   │    │                        │     │
│  └──────────┬───────────┘    └────────────────────────┘     │
│             │                                                │
│  ┌──────────▼───────────────────────────────────────────┐   │
│  │              Tool System                              │   │
│  │  - Validators         - Calculators                   │   │
│  │  - Document Generator - Citation Formatter            │   │
│  │  - Risk Assessor      - Metric Aligner                │   │
│  └───────────────────────────────────────────────────────┘   │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                   Data & Persistence Layer                    │
│  - Session Store (PostgreSQL)                                │
│  - Document Store (File System)                              │
│  - Configuration Store (YAML/JSON)                           │
└───────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                   External Services Layer                     │
│  - Claude API (Anthropic)                                    │
│  - PDF Generation Service                                    │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 Agent Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  UAIPOrchestrator                         │
│  Responsibilities:                                        │
│  - Initialize stage sequence                              │
│  - Coordinate agent communication                         │
│  - Enforce stage-gate progression                         │
│  - Trigger reflection loops                               │
│  - Synthesize final charter                               │
└─────────┬────────────────────────────────────────────────┘
          │
          ├──► Stage Interview Agents (Specialized Sub-Agents)
          │    │
          │    ├─► Stage1BusinessTranslationAgent
          │    │   - Ask 4 question groups
          │    │   - Map ML archetype
          │    │   - Validate AI suitability
          │    │   - Output: ProblemStatement
          │    │
          │    ├─► Stage2ValueQuantificationAgent
          │    │   - Define KPIs
          │    │   - Select model metrics
          │    │   - Establish causal pathways
          │    │   - Output: MetricAlignmentMatrix
          │    │
          │    ├─► Stage3DataFeasibilityAgent
          │    │   - Inventory data sources
          │    │   - Assess 6 quality dimensions
          │    │   - Plan labeling strategy
          │    │   - Output: DataQualityScorecard
          │    │
          │    ├─► Stage4UserCentricityAgent
          │    │   - Define personas
          │    │   - Map user journey
          │    │   - Specify HCI requirements
          │    │   - Output: UserContext
          │    │
          │    └─► Stage5EthicsAgent
          │        - Conduct risk self-assessment
          │        - Calculate residual risk
          │        - Determine governance decision
          │        - Output: EthicalRiskReport
          │
          └──► Reflection Agents (Quality Assurance)
               │
               ├─► ResponseQualityAgent
               │   - Score response quality (0-10)
               │   - Identify vagueness/gaps
               │   - Generate targeted follow-ups
               │
               ├─► StageGateValidatorAgent
               │   - Check mandatory field completion
               │   - Validate stage-specific logic
               │   - Approve/reject stage progression
               │
               └─► ConsistencyCheckerAgent
                   - Verify cross-stage alignment
                   - Detect logical contradictions
                   - Flag feasibility concerns
```

### 3.3 Component Interaction Flow

```
User Request
     │
     ▼
┌────────────────┐
│ CLI Interface  │
└────────┬───────┘
         │
         ▼
┌─────────────────────┐
│ Orchestrator        │──────────┐
│ - Load Stage Config │          │
│ - Initialize Agent  │          │
└──────────┬──────────┘          │
           │                     │
           ▼                     │
┌─────────────────────┐          │
│ Stage Agent         │          │
│ - Ask Question      │          │
└──────────┬──────────┘          │
           │                     │
           ▼                     │
    User Provides Answer         │
           │                     │
           ▼                     ▼
┌──────────────────────┐  ┌──────────────────┐
│ Response Quality     │  │ Tool System      │
│ Agent                │  │ - Validators     │
│ - Score response     │  │ - Calculators    │
│ - Check specificity  │  └──────────────────┘
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │ Score >= 7? │
    └──────┬──────┘
           │
    ┌──────┴──────────────┐
    │                     │
   YES                   NO
    │                     │
    │              ┌──────▼──────────┐
    │              │ Request         │
    │              │ Clarification   │
    │              └──────┬──────────┘
    │                     │
    │              ┌──────▼──────────┐
    │              │ Loop (max 3x)   │
    │              └─────────────────┘
    │
    ▼
┌─────────────────────┐
│ Store Response      │
└──────────┬──────────┘
           │
    ┌──────▼──────────┐
    │ More Questions? │
    └──────┬──────────┘
           │
    ┌──────┴──────────────┐
    │                     │
   YES                   NO
    │                     │
    │              ┌──────▼──────────┐
    │              │ Stage Gate      │
    │              │ Validation      │
    │              └──────┬──────────┘
    │                     │
    │              ┌──────▼──────────┐
    │              │ Can Proceed?    │
    │              └──────┬──────────┘
    │                     │
    │              ┌──────┴──────────┐
    │              │                 │
    │             YES               NO
    │              │                 │
    │              │          ┌──────▼──────┐
    │              │          │ Address     │
    │              │          │ Gaps        │
    │              │          └─────────────┘
    │              │
    │              ▼
    │    ┌─────────────────────┐
    │    │ Generate Stage      │
    │    │ Deliverable         │
    │    └──────────┬──────────┘
    │               │
    │        ┌──────▼──────────┐
    │        │ More Stages?    │
    │        └──────┬──────────┘
    │               │
    │        ┌──────┴──────────┐
    │        │                 │
    │       YES               NO
    └────────┘                 │
                               ▼
                    ┌─────────────────────┐
                    │ Consistency Check   │
                    │ (Cross-Stage)       │
                    └──────────┬──────────┘
                               │
                        ┌──────▼──────────┐
                        │ Consistent?     │
                        └──────┬──────────┘
                               │
                        ┌──────┴──────────┐
                        │                 │
                       YES               NO
                        │                 │
                        │          ┌──────▼──────┐
                        │          │ Resolve     │
                        │          │ Issues      │
                        │          └─────────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │ Generate Final      │
             │ AI Project Charter  │
             └──────────┬──────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Export       │
                 │ (MD/PDF/JSON)│
                 └──────────────┘
```

---

## 4. Component Specifications

### 4.1 Orchestrator Component

**Class:** `UAIPOrchestrator`

**Responsibilities:**
- Session lifecycle management
- Stage sequence coordination
- Agent initialization and communication
- Context propagation across stages
- Final synthesis and document generation

**Key Methods:**

```python
class UAIPOrchestrator:
    async def initialize_session(self, user_context: dict) -> SessionID
    async def conduct_full_protocol(self) -> AIProjectCharter
    async def conduct_stage(self, stage_num: int) -> StageDeliverable
    async def save_checkpoint(self, stage_num: int) -> None
    async def resume_session(self, session_id: SessionID) -> None
    async def export_charter(self, format: ExportFormat) -> Path
```

**Configuration:**
```yaml
orchestrator:
  max_session_duration_minutes: 120
  auto_save_interval_seconds: 60
  max_reflection_loops: 3
  quality_threshold: 7
```

### 4.2 Stage Interview Agents

#### 4.2.1 Stage1BusinessTranslationAgent

**Purpose:** Translate business needs into precise AI problem statements

**Question Groups:**
1. Core Business Objective (1 primary, 2-3 follow-ups)
2. AI Suitability Assessment (1 primary, 1-2 follow-ups)
3. Problem Statement Definition (3 primary: inputs/outputs/archetype, 2-3 follow-ups each)
4. Scope & Boundaries (2 primary, 2 follow-ups)

**Deliverable:** `ProblemStatement` object containing:
- business_objective: str
- ai_justification: str
- input_features: List[Feature]
- target_output: OutputDefinition
- ml_archetype: MLArchetype
- scope_boundaries: ScopeDefinition
- feature_availability_validation: FeatureAccessibilityReport

**Validation Logic:**
- ML archetype must map correctly to inputs/outputs
- All features must be accessible in production
- AI necessity must be justified vs. simpler alternatives

#### 4.2.2 Stage2ValueQuantificationAgent

**Purpose:** Establish measurable success criteria and causal linkages

**Question Groups:**
1. Business KPIs (SMART criteria)
2. Technical Metrics Selection
3. Causal Connection Mapping
4. Prediction Actionability Window

**Deliverable:** `MetricAlignmentMatrix` containing:
- business_kpis: List[KPI]
- model_metrics: List[TechnicalMetric]
- causal_pathways: List[CausalLink]
- actionability_window: TimeDelta
- causal_impact_plan: ValidationPlan

**Validation Logic:**
- Each KPI must have at least one linked model metric
- Causal pathway must be logically coherent
- Actionability window must exceed prediction latency

#### 4.2.3 Stage3DataFeasibilityAgent

**Purpose:** Assess data availability, quality, and governance readiness

**Question Groups:**
1. Data Source Inventory
2. Six-Dimension Quality Assessment
3. Labeling Strategy & Cost Analysis
4. FAIR Principles Adherence

**Deliverable:** `DataQualityScorecard` containing:
- data_sources: List[DataSource]
- quality_scores: Dict[QualityDimension, Score]
- labeling_strategy: LabelingPlan
- fair_compliance: FAIRAssessment
- infrastructure_readiness: InfrastructureReport

**Validation Logic:**
- All six quality dimensions must be scored
- Labeling cost must be within budget constraints
- Minimum quality threshold: 6/10 across all dimensions

#### 4.2.4 Stage4UserCentricityAgent

**Purpose:** Ensure user-centric design and workflow integration

**Question Groups:**
1. User Persona Definition
2. AI User Journey Mapping
3. Interpretability Requirements
4. Feedback Mechanisms

**Deliverable:** `UserContext` containing:
- user_personas: List[Persona]
- user_journey_map: JourneyMap
- hci_requirements: HCISpec
- interpretability_needs: ExplainabilityRequirements
- feedback_mechanisms: FeedbackPlan

**Validation Logic:**
- At least one primary persona required
- User journey must include pre/during/post AI interaction
- Interpretability level must match decision criticality

#### 4.2.5 Stage5EthicsAgent

**Purpose:** Identify, assess, and mitigate ethical risks with governance decisions

**Question Groups:**
1. Risk Self-Assessment (RMF-based)
2. Principle-Specific Risk Mapping
3. Mitigation Strategy Planning
4. Residual Risk Calculation
5. Post-Deployment Monitoring

**Deliverable:** `EthicalRiskReport` containing:
- initial_risks: Dict[EthicalPrinciple, List[Risk]]
- mitigation_strategies: Dict[Risk, MitigationPlan]
- residual_risks: Dict[EthicalPrinciple, RiskLevel]
- governance_decision: GovernanceDecision  # Proceed/Revise/Halt
- monitoring_plan: ContinuousMonitoringPlan

**Validation Logic:**
- All core ethical principles must be assessed
- Residual risk HIGH → HALT or Submit to Committee
- Residual risk MEDIUM → PROCEED with monitoring
- Residual risk LOW → PROCEED

**Critical Business Logic:**
```python
def determine_governance_decision(residual_risks: Dict[EthicalPrinciple, RiskLevel]) -> GovernanceDecision:
    max_risk = max(residual_risks.values())

    if max_risk >= RiskLevel.HIGH:
        return GovernanceDecision.HALT
    elif max_risk == RiskLevel.MEDIUM:
        return GovernanceDecision.PROCEED_WITH_MONITORING
    else:
        return GovernanceDecision.PROCEED
```

### 4.3 Reflection Agent System

#### 4.3.1 ResponseQualityAgent

**Purpose:** Evaluate individual response quality and generate improvement suggestions

**Inputs:**
- question: str
- user_response: str
- stage_context: StageContext

**Outputs:**
```python
@dataclass
class QualityAssessment:
    quality_score: int  # 0-10
    is_acceptable: bool  # score >= 7
    issues: List[str]
    suggested_followups: List[str]
    examples_to_provide: List[str]
```

**Evaluation Criteria:**
- Specificity (vs. vagueness)
- Measurability (quantifiable data)
- Completeness (answers full question)
- Coherence (logically consistent)
- Relevance (on-topic)

**System Prompt:**
```
You are a strict quality evaluator for AI project scoping.
Evaluate responses based on specificity, measurability, and completeness.
Score 0-10 where:
- 9-10: Excellent - specific, measurable, complete
- 7-8: Good - mostly clear with minor gaps
- 5-6: Needs improvement - vague or incomplete
- 0-4: Insufficient - requires complete rework

Provide concrete follow-up questions to address gaps.
```

#### 4.3.2 StageGateValidatorAgent

**Purpose:** Validate stage completion before allowing progression

**Inputs:**
- stage_number: int
- collected_data: Dict[str, Any]
- stage_requirements: StageRequirements

**Outputs:**
```python
@dataclass
class StageValidation:
    can_proceed: bool
    completeness_score: float  # 0.0-1.0
    missing_items: List[str]
    validation_concerns: List[str]
    recommendations: List[str]
```

**Stage-Specific Validation Rules:**

| Stage | Critical Validations |
|-------|---------------------|
| 1 | ML archetype justified, all features defined, production availability confirmed |
| 2 | KPIs are SMART, causal pathway articulated, metrics aligned |
| 3 | All 6 quality dimensions scored, labeling plan has budget/timeline |
| 4 | Personas research-based, journey map complete, interpretability specified |
| 5 | All ethical principles assessed, residual risk calculated, governance decision made |

#### 4.3.3 ConsistencyCheckerAgent

**Purpose:** Validate logical consistency across all stages

**Inputs:**
- all_stages_data: AllStagesData

**Outputs:**
```python
@dataclass
class ConsistencyReport:
    is_consistent: bool
    overall_feasibility: FeasibilityLevel
    contradictions: List[Contradiction]
    risk_areas: List[RiskArea]
    recommendations: List[str]
```

**Cross-Stage Checks:**

1. **Stage 1 → Stage 2:** Do KPIs solve the stated problem?
2. **Stage 2 → Stage 3:** Is required data available for chosen metrics?
3. **Stage 3 → Stage 4:** Do users have access to data sources?
4. **Stage 1-4 → Stage 5:** Do ethical risks match project scope/impact?
5. **Overall:** Is project feasible given all constraints?

---

## 5. Data Models

### 5.1 Core Domain Models

```python
# Enumerations
class MLArchetype(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    NLP = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series_forecasting"

class QualityDimension(Enum):
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    INTEGRITY = "integrity"

class EthicalPrinciple(Enum):
    FAIRNESS_EQUITY = "fairness_and_equity"
    PRIVACY_PROTECTION = "privacy_and_data_protection"
    TRANSPARENCY_ACCOUNTABILITY = "transparency_and_accountability"
    SAFETY_RESILIENCE = "safety_and_resilience"
    HUMAN_AGENCY = "human_agency_and_oversight"

class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class GovernanceDecision(Enum):
    PROCEED = "proceed"
    PROCEED_WITH_MONITORING = "proceed_with_monitoring"
    REVISE = "revise"
    HALT = "halt"
    SUBMIT_TO_COMMITTEE = "submit_to_committee"

# Stage Deliverables
@dataclass
class ProblemStatement:
    business_objective: str
    ai_necessity_justification: str
    input_features: List[Feature]
    target_output: OutputDefinition
    ml_archetype: MLArchetype
    ml_archetype_justification: str
    scope_boundaries: ScopeDefinition
    feature_availability: FeatureAccessibilityReport
    created_at: datetime
    version: str

@dataclass
class Feature:
    name: str
    data_type: str
    description: str
    source_system: str
    availability_in_production: bool
    access_latency_ms: Optional[int]

@dataclass
class OutputDefinition:
    name: str
    type: str  # categorical, continuous, probability, etc.
    description: str
    possible_values: Optional[List[str]]
    units: Optional[str]

@dataclass
class KPI:
    name: str
    description: str
    current_baseline: Optional[float]
    target_value: float
    target_timeframe: str
    measurement_method: str
    business_impact: str  # revenue/cost impact

@dataclass
class TechnicalMetric:
    name: str  # e.g., "Precision", "RMSE"
    description: str
    target_threshold: float
    measurement_method: str

@dataclass
class CausalLink:
    model_metric: str
    business_kpi: str
    causal_mechanism: str  # Explanation of how metric improvement → KPI improvement
    assumptions: List[str]
    potential_failure_modes: List[str]

@dataclass
class DataSource:
    name: str
    type: str  # database, API, file, etc.
    description: str
    size: str
    update_frequency: str
    access_method: str
    quality_assessment: Dict[QualityDimension, int]  # 0-10 scores

@dataclass
class Persona:
    name: str
    role: str
    goals: List[str]
    pain_points: List[str]
    technical_proficiency: str  # novice, intermediate, expert
    ai_interaction_frequency: str
    decision_authority: str

@dataclass
class EthicalRisk:
    principle: EthicalPrinciple
    risk_description: str
    severity: RiskLevel
    likelihood: RiskLevel
    affected_stakeholders: List[str]
    mitigation_strategies: List[MitigationStrategy]
    residual_risk: RiskLevel

@dataclass
class MitigationStrategy:
    description: str
    implementation_method: str
    cost_estimate: Optional[str]
    timeline: Optional[str]
    effectiveness_rating: float  # 0.0-1.0

# Complete Charter
@dataclass
class AIProjectCharter:
    session_id: UUID
    project_name: str
    created_at: datetime
    completed_at: datetime

    # Stage deliverables
    problem_statement: ProblemStatement
    metric_alignment_matrix: MetricAlignmentMatrix
    data_quality_scorecard: DataQualityScorecard
    user_context: UserContext
    ethical_risk_report: EthicalRiskReport

    # Final assessments
    governance_decision: GovernanceDecision
    overall_feasibility: str
    critical_success_factors: List[str]
    major_risks: List[str]

    # Metadata
    approver: Optional[str]
    approval_date: Optional[datetime]
    version: str
    citations: List[Citation]
```

### 5.2 Session Management Models

```python
@dataclass
class Session:
    session_id: UUID
    user_id: str
    project_name: str
    started_at: datetime
    last_updated_at: datetime
    current_stage: int
    stage_data: Dict[int, Any]
    conversation_history: List[Message]
    status: SessionStatus
    checkpoints: List[Checkpoint]

class SessionStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"

@dataclass
class Checkpoint:
    stage_number: int
    timestamp: datetime
    data_snapshot: Dict[str, Any]
    validation_status: bool
```

### 5.3 Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    project_name VARCHAR(500) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    last_updated_at TIMESTAMP NOT NULL,
    current_stage INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_sessions (user_id, started_at),
    INDEX idx_status (status)
);

-- Stage data table
CREATE TABLE stage_data (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    field_value JSONB NOT NULL,
    quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, stage_number, field_name)
);

-- Conversation history
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    stage_number INTEGER,
    metadata JSONB,
    INDEX idx_session_messages (session_id, timestamp)
);

-- Checkpoints
CREATE TABLE checkpoints (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL,
    checkpoint_timestamp TIMESTAMP NOT NULL,
    data_snapshot JSONB NOT NULL,
    validation_passed BOOLEAN NOT NULL
);

-- Generated charters
CREATE TABLE project_charters (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    charter_content JSONB NOT NULL,
    governance_decision VARCHAR(50) NOT NULL,
    generated_at TIMESTAMP NOT NULL,
    markdown_path VARCHAR(500),
    pdf_path VARCHAR(500),
    version VARCHAR(50) NOT NULL
);
```

---

## 6. Agent Specifications

### 6.1 Agent System Prompts

#### 6.1.1 Orchestrator Agent

```
You are the U-AIP Orchestrator, responsible for guiding users through a rigorous
5-stage AI project evaluation process. Your role is to:

1. Explain the overall process and set expectations (30-45 minute session)
2. Coordinate stage progression, ensuring no stage is skipped
3. Enforce quality standards through reflection agent feedback
4. Maintain professional, clear communication throughout
5. Synthesize all information into a comprehensive AI Project Charter

Communication style:
- Professional but conversational
- Clear progress updates ("We're now in Stage 2 of 5...")
- Transparent about validation requirements
- Encouraging when users provide quality responses
- Firm but helpful when responses need improvement

You must NEVER allow progression to the next stage until the current stage
passes validation. You are the gatekeeper of rigor and quality.
```

#### 6.1.2 Stage Interview Agents (Example: Stage 1)

```
You are the Stage 1 Business Translation specialist. Your goal is to translate
a business need into a precise, technically feasible AI problem statement.

You will ask questions in 4 groups:
1. Core Business Objective - What problem are we solving?
2. AI Suitability - Is AI/ML really needed, or would simpler methods work?
3. Problem Definition - What are the exact inputs, outputs, and ML task type?
4. Scope & Boundaries - What will this project NOT do?

Your questioning style:
- Start open-ended, then narrow to specifics
- Ask "why" and "how" to uncover true requirements
- Challenge assumptions respectfully ("Have you considered that...")
- Provide examples from similar projects when users seem uncertain
- Detect vague language and request concrete details

RED FLAGS to catch:
- "Improve efficiency" without defining what metric measures efficiency
- Claiming AI is needed without justifying why rules-based logic won't work
- Undefined target variables ("predict customer behavior" - which behavior?)
- Features that won't be available at inference time

You work closely with the Response Quality Agent who will evaluate each answer.
If responses are too vague, you will receive feedback to ask more targeted follow-ups.
```

#### 6.1.3 Reflection Agents

**ResponseQualityAgent:**
```
You are a strict quality evaluator for AI project scoping responses.

Evaluate each user response on these dimensions:
1. Specificity - Is it concrete or vague?
2. Measurability - Can we quantify this?
3. Completeness - Does it fully answer the question?
4. Coherence - Is it logically consistent?
5. Relevance - Does it stay on topic?

Score 0-10:
- 9-10: Excellent (specific, measurable, complete)
- 7-8: Good (mostly clear, minor gaps acceptable)
- 5-6: Needs improvement (vague or incomplete)
- 0-4: Insufficient (requires complete rework)

For scores below 7, provide:
1. Specific issues with the response
2. 2-3 targeted follow-up questions
3. An example of what a better response would include

Be firm but constructive. The goal is to help users provide quality information,
not to frustrate them. Explain WHY specificity matters for AI project success.
```

**StageGateValidatorAgent:**
```
You are the Stage Gate Validator. You determine if a stage is complete enough
to proceed to the next stage.

For each stage, check:
- Are ALL mandatory fields populated?
- Does the information meet quality standards?
- Are stage-specific requirements satisfied?
- Are there logical inconsistencies within this stage?

Stage-specific critical checks:
- Stage 1: ML archetype mapping justified, feature production availability validated
- Stage 2: Clear causal link between model metrics and business KPIs
- Stage 3: All 6 data quality dimensions scored, labeling plan has budget
- Stage 4: User personas research-based, interpretability requirements specified
- Stage 5: Residual risk calculated, governance decision determined

Return a clear PASS/FAIL decision with specific gaps if failing.
U-AIP is a stage-gated process - be strict. Incomplete stages lead to project failures.
```

**ConsistencyCheckerAgent:**
```
You are the Cross-Stage Consistency Checker. Your job is to find logical
contradictions and feasibility issues across the entire project scope.

Check these critical alignments:
1. Do Stage 2 KPIs actually solve the Stage 1 problem?
2. Is the Stage 3 data sufficient for Stage 2 metrics?
3. Can Stage 4 users access Stage 3 data sources?
4. Do Stage 5 ethical risks match the project's actual scope and impact?

Look for red flags:
- Claiming to predict rare events but having no data on those events
- Requiring real-time predictions but having batch data pipelines
- Targeting non-technical users but requiring model interpretability expertise
- Low ethical risk rating for high-stakes decisions
- Budget constraints incompatible with data labeling needs

Be the "sanity check" agent. If something seems infeasible, call it out clearly
with specific reasoning.
```

### 6.2 Agent Communication Protocol

```python
# Agent-to-Agent Message Structure
@dataclass
class AgentMessage:
    sender: AgentType
    receiver: AgentType
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: UUID

class MessageType(Enum):
    QUESTION = "question"
    RESPONSE = "response"
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESULT = "validation_result"
    STAGE_COMPLETE = "stage_complete"
    ERROR = "error"

# Example validation flow
orchestrator.send(AgentMessage(
    sender=AgentType.STAGE1,
    receiver=AgentType.RESPONSE_QUALITY,
    message_type=MessageType.VALIDATION_REQUEST,
    payload={
        "question": "What is your business objective?",
        "response": "Improve customer satisfaction",
        "context": {"stage": 1, "question_id": "S1Q1"}
    }
))

response_quality_agent.send(AgentMessage(
    sender=AgentType.RESPONSE_QUALITY,
    receiver=AgentType.STAGE1,
    message_type=MessageType.VALIDATION_RESULT,
    payload={
        "quality_score": 4,
        "is_acceptable": False,
        "issues": ["Too vague - satisfaction needs a metric"],
        "suggested_followups": [
            "What specific metric defines satisfaction? (e.g., NPS, CSAT, retention rate)",
            "How do you currently measure customer satisfaction?"
        ]
    }
))
```

---

## 7. Tool Specifications

### 7.1 Validation Tools

#### 7.1.1 ML Archetype Validator

```python
class MLArchetypeValidator:
    """Validates that ML archetype matches problem definition"""

    def validate(self,
                 inputs: List[Feature],
                 output: OutputDefinition,
                 claimed_archetype: MLArchetype) -> ValidationResult:
        """
        Logic:
        - Classification: Categorical output with fixed classes
        - Regression: Continuous numerical output
        - Clustering: No predefined output, grouping task
        - etc.
        """
        pass
```

#### 7.1.2 SMART KPI Validator

```python
class SMARTKPIValidator:
    """Validates KPIs meet SMART criteria"""

    def validate(self, kpi: KPI) -> ValidationResult:
        """
        Check:
        - Specific: Clear, unambiguous definition
        - Measurable: Quantifiable metric defined
        - Achievable: Baseline and target are reasonable
        - Relevant: Tied to business value
        - Time-bound: Has target timeframe
        """
        pass
```

### 7.2 Calculator Tools

#### 7.2.1 Residual Risk Calculator

```python
class ResidualRiskCalculator:
    """Calculates residual risk after mitigation"""

    def calculate(self,
                  initial_risk: Risk,
                  mitigations: List[MitigationStrategy]) -> RiskLevel:
        """
        Formula:
        residual_risk = initial_risk * (1 - Σ(mitigation.effectiveness))

        Constrain to RiskLevel enum values
        """
        total_mitigation_effectiveness = sum(
            m.effectiveness_rating for m in mitigations
        )

        # Cap at 95% mitigation effectiveness
        total_mitigation_effectiveness = min(total_mitigation_effectiveness, 0.95)

        residual_score = initial_risk.severity.value * initial_risk.likelihood.value
        residual_score *= (1 - total_mitigation_effectiveness)

        return self._map_to_risk_level(residual_score)
```

#### 7.2.2 Governance Decision Engine

```python
class GovernanceDecisionEngine:
    """Determines Proceed/Revise/Halt decision"""

    def decide(self,
               residual_risks: Dict[EthicalPrinciple, RiskLevel]) -> GovernanceDecision:
        """
        Rules (per U-AIP protocol):
        - Any HIGH or CRITICAL residual risk → HALT or SUBMIT_TO_COMMITTEE
        - All MEDIUM → PROCEED_WITH_MONITORING
        - All LOW → PROCEED
        """
        max_risk = max(residual_risks.values(), key=lambda x: x.value)

        if max_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return GovernanceDecision.HALT
        elif max_risk == RiskLevel.MEDIUM:
            return GovernanceDecision.PROCEED_WITH_MONITORING
        else:
            return GovernanceDecision.PROCEED
```

### 7.3 Document Generation Tools

#### 7.3.1 APA Citation Formatter

```python
class APACitationFormatter:
    """Formats citations in APA 7th Edition style"""

    def format_citation(self, citation: Citation) -> str:
        """
        Format based on citation type:
        - Journal article
        - Book
        - Website
        - Report
        - Conference paper
        """
        pass

    def generate_reference_list(self, citations: List[Citation]) -> str:
        """Generate complete APA 7 reference list"""
        pass
```

#### 7.3.2 Charter Document Generator

```python
class CharterDocumentGenerator:
    """Generates AI Project Charter in multiple formats"""

    def __init__(self):
        self.templates = self._load_templates()
        self.citation_formatter = APACitationFormatter()

    async def generate_markdown(self, charter: AIProjectCharter) -> str:
        """Generate structured markdown document"""
        pass

    async def generate_pdf(self, charter: AIProjectCharter) -> bytes:
        """Generate PDF from markdown using pandoc or weasyprint"""
        pass

    async def generate_json(self, charter: AIProjectCharter) -> str:
        """Generate structured JSON export"""
        pass
```

**Charter Template Structure:**
```markdown
# AI Project Charter: {project_name}

**Date:** {created_at}
**Session ID:** {session_id}
**Governance Decision:** {governance_decision}

---

## Executive Summary

{auto_generated_summary}

---

## 1. Strategic Alignment

### Business Goals
{stage2.business_kpis}

### Financial Impact
{calculated_roi}

---

## 2. Problem Definition

{stage1.problem_statement}

### ML Archetype Mapping
**Archetype:** {stage1.ml_archetype}
**Justification:** {stage1.ml_archetype_justification}

### Input Features
{stage1.input_features_table}

### Target Output
{stage1.target_output}

---

## 3. Technical Feasibility Assessment

{stage3.data_quality_scorecard}

### Data Quality Scores
{stage3.quality_dimension_scores_table}

### Labeling Strategy
{stage3.labeling_strategy}

---

## 4. User Context and Interaction

{stage4.user_personas}

### AI User Journey Map
{stage4.journey_map_visualization}

### Interpretability Requirements
{stage4.interpretability_requirements}

---

## 5. Metric Alignment Matrix

{stage2.metric_alignment_matrix_table}

### Causal Connection Analysis
{stage2.causal_pathways}

---

## 6. Ethical Risk Assessment

{stage5.ethical_risk_report}

### Residual Risk Summary
{stage5.residual_risk_table}

### Governance Checkpoint Decision
**Decision:** {stage5.governance_decision}
**Reasoning:** {stage5.decision_reasoning}

---

## 7. Operational Strategy

{stage5.continuous_monitoring_plan}

---

## 8. References

{apa7_reference_list}

---

**Document generated by U-AIP Scoping Assistant v{version}**
**Charter approval pending:** [Signature line]
```

---

## 8. Conversation Flow

### 8.1 Session Initialization

```
Assistant: Welcome to the U-AIP Scoping Assistant! I'll guide you through a
comprehensive 5-stage evaluation process for your AI project. This typically
takes 30-45 minutes.

We'll cover:
1. Business Translation - Defining your problem
2. Value Quantification - Setting success metrics
3. Data Feasibility - Assessing your data readiness
4. User Context - Understanding your users
5. Ethics & Risk - Evaluating ethical considerations

At the end, you'll receive a complete AI Project Charter document.

Before we begin, a few housekeeping items:
- Your session will auto-save after each stage
- You can pause and resume anytime
- I'll challenge vague responses - this rigor ensures project success
- Be as specific as possible in your answers

Ready to start? First, what would you like to name this project?

[User provides project name]

Perfect! Let's begin Stage 1: Business Translation...
```

### 8.2 Stage 1 Example Flow (Complete Interaction with Quality Loops)

This section demonstrates exactly how users interact with the system, including reflection loops.

```
=== STAGE 1: BUSINESS TRANSLATION (Question Group 1 of 4) ===
Progress: [████░░░░░░░░░░░░] Stage 1: 0% complete