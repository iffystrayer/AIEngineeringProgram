"""
U-AIP Scoping Assistant - Core Data Models

This module defines all data structures used throughout the U-AIP system,
including enumerations, stage deliverables, and session management models.

Based on SWE Specification Section 5 - Data Models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

# ============================================================================
# ENUMERATIONS
# ============================================================================


class MLArchetype(Enum):
    """Machine learning task types supported by the system."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    NLP = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series_forecasting"


class QualityDimension(Enum):
    """Data quality assessment dimensions (Stage 3)."""

    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    INTEGRITY = "integrity"


class EthicalPrinciple(Enum):
    """Core ethical principles for AI risk assessment (Stage 5)."""

    FAIRNESS_EQUITY = "fairness_and_equity"
    PRIVACY_PROTECTION = "privacy_and_data_protection"
    TRANSPARENCY_ACCOUNTABILITY = "transparency_and_accountability"
    SAFETY_RESILIENCE = "safety_and_resilience"
    HUMAN_AGENCY = "human_agency_and_oversight"


class RiskLevel(Enum):
    """Risk severity levels for ethical assessment."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class GovernanceDecision(Enum):
    """Automated governance checkpoint decisions."""

    PROCEED = "proceed"
    PROCEED_WITH_MONITORING = "proceed_with_monitoring"
    REVISE = "revise"
    HALT = "halt"
    SUBMIT_TO_COMMITTEE = "submit_to_committee"


class SessionStatus(Enum):
    """Session lifecycle states."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"


class MessageType(Enum):
    """Agent communication message types."""

    QUESTION = "question"
    RESPONSE = "response"
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESULT = "validation_result"
    STAGE_COMPLETE = "stage_complete"
    ERROR = "error"


class AgentType(Enum):
    """Agent identifiers for routing."""

    ORCHESTRATOR = "orchestrator"
    STAGE1 = "stage1_business_translation"
    STAGE2 = "stage2_value_quantification"
    STAGE3 = "stage3_data_feasibility"
    STAGE4 = "stage4_user_centricity"
    STAGE5 = "stage5_ethics"
    RESPONSE_QUALITY = "response_quality"
    STAGE_GATE_VALIDATOR = "stage_gate_validator"
    CONSISTENCY_CHECKER = "consistency_checker"


class FeasibilityLevel(Enum):
    """Overall project feasibility assessment."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFEASIBLE = "infeasible"


class ExportFormat(Enum):
    """Supported export formats for charters."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    JSON = "json"


# ============================================================================
# STAGE 1: BUSINESS TRANSLATION - DELIVERABLES
# ============================================================================


@dataclass
class Feature:
    """Input feature definition with production availability validation."""

    name: str
    data_type: str
    description: str
    source_system: str
    availability_in_production: bool
    access_latency_ms: Optional[int] = None


@dataclass
class OutputDefinition:
    """Target output specification for ML model."""

    name: str
    type: str  # categorical, continuous, probability, etc.
    description: str
    possible_values: Optional[list[str]] = None
    units: Optional[str] = None


@dataclass
class ScopeDefinition:
    """Project scope boundaries."""

    in_scope: list[str]
    out_of_scope: list[str]
    assumptions: list[str]
    constraints: list[str]


@dataclass
class FeatureAccessibilityReport:
    """Validation report for feature availability in production."""

    all_features_available: bool
    unavailable_features: list[str]
    latency_concerns: list[str]
    access_method_issues: list[str]


@dataclass
class ProblemStatement:
    """Stage 1 deliverable: Complete AI problem definition."""

    business_objective: str
    ai_necessity_justification: str
    input_features: list[Feature]
    target_output: OutputDefinition
    ml_archetype: MLArchetype
    ml_archetype_justification: str
    scope_boundaries: ScopeDefinition
    feature_availability: FeatureAccessibilityReport
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


# ============================================================================
# STAGE 2: VALUE QUANTIFICATION - DELIVERABLES
# ============================================================================


@dataclass
class KPI:
    """Business key performance indicator (SMART criteria)."""

    name: str
    description: str
    current_baseline: Optional[float]
    target_value: float
    target_timeframe: str
    measurement_method: str
    business_impact: str  # revenue/cost impact


@dataclass
class TechnicalMetric:
    """ML model evaluation metric."""

    name: str  # e.g., "Precision", "RMSE", "F1 Score"
    description: str
    target_threshold: float
    measurement_method: str


@dataclass
class CausalLink:
    """Causal connection between model metric and business KPI."""

    model_metric: str
    business_kpi: str
    causal_mechanism: str  # How metric improvement → KPI improvement
    assumptions: list[str]
    potential_failure_modes: list[str]


@dataclass
class ValidationPlan:
    """Plan for validating causal impact assumptions."""

    validation_method: str
    data_requirements: list[str]
    timeline: str
    success_criteria: str


@dataclass
class MetricAlignmentMatrix:
    """Stage 2 deliverable: Metric-to-value alignment mapping."""

    business_kpis: list[KPI]
    model_metrics: list[TechnicalMetric]
    causal_pathways: list[CausalLink]
    actionability_window: timedelta
    causal_impact_plan: ValidationPlan
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


# ============================================================================
# STAGE 3: DATA FEASIBILITY - DELIVERABLES
# ============================================================================


@dataclass
class DataSource:
    """Data source inventory with quality assessment."""

    name: str
    type: str  # database, API, file, streaming, etc.
    description: str
    size: str  # e.g., "10M records", "500GB"
    update_frequency: str
    access_method: str
    quality_assessment: dict[QualityDimension, int]  # 0-10 scores
    covered_features: list[dict[str, str]] = field(default_factory=list)  # Features from Stage 1


@dataclass
class LabelingPlan:
    """Data labeling plan with detailed cost and quality analysis."""

    approach: str  # manual, semi-automated, fully automated, hybrid
    num_labels_required: Optional[int] = None
    cost_per_label: Optional[float] = None
    total_budget: Optional[float] = None
    timeline: Optional[str] = None
    quality_assurance: Optional[str] = None
    annotator_requirements: list[str] = field(default_factory=list)


@dataclass
class LabelingStrategy:
    """Data labeling plan and cost analysis."""

    labeling_method: str  # manual, semi-automated, fully automated
    estimated_cost: float
    estimated_time: str
    quality_assurance_process: str
    annotator_requirements: list[str]


@dataclass
class FAIRAssessment:
    """FAIR principles compliance assessment."""

    findable: bool
    accessible: bool
    interoperable: bool
    reusable: bool
    gaps: list[str]
    remediation_plan: str


@dataclass
class InfrastructureReport:
    """Data infrastructure readiness assessment."""

    storage_capacity: str
    compute_resources: str
    pipeline_maturity: str
    gaps: list[str]
    estimated_setup_cost: float


@dataclass
class DataQualityScorecard:
    """Stage 3 deliverable: Comprehensive data assessment."""

    data_sources: list[DataSource]
    quality_scores: dict[QualityDimension, int]  # Aggregated scores
    labeling_strategy: LabelingStrategy
    fair_compliance: FAIRAssessment
    infrastructure_readiness: InfrastructureReport
    overall_feasibility: FeasibilityLevel
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


# ============================================================================
# STAGE 4: USER CENTRICITY - DELIVERABLES
# ============================================================================


@dataclass
class Persona:
    """User persona definition."""

    name: str
    role: str
    goals: list[str]
    pain_points: list[str]
    technical_proficiency: str  # novice, intermediate, expert
    ai_interaction_frequency: str
    decision_authority: str
    research_evidence: Optional[str] = None  # Evidence supporting persona definition
    data_access_level: Optional[str] = None  # full, partial, read-only


@dataclass
class JourneyStage:
    """Single stage in user journey map."""

    stage_name: str  # pre-interaction, during, post-interaction
    user_actions: list[str]
    pain_points: list[str]
    ai_touchpoints: list[str]
    success_criteria: list[str]


@dataclass
class JourneyMap:
    """Complete AI user journey mapping."""

    stages: Optional[list[JourneyStage]] = None
    critical_decision_points: Optional[list[str]] = None
    risk_areas: Optional[list[str]] = None
    # Alternative structure for test compatibility
    pre_ai_stage: Optional[dict[str, Any]] = None
    during_ai_stage: Optional[dict[str, Any]] = None
    post_ai_stage: Optional[dict[str, Any]] = None
    critical_touchpoints: Optional[list[str]] = None


@dataclass
class ExplainabilityRequirements:
    """Model interpretability specifications."""

    required_level: str  # high, medium, low
    explanation_method: str  # SHAP, LIME, attention, etc.
    target_audience: list[str]
    regulatory_requirements: list[str]


@dataclass
class FeedbackMechanism:
    """User feedback collection plan."""

    feedback_type: str  # implicit, explicit
    collection_method: str
    frequency: str
    integration_plan: str


@dataclass
class HCISpec:
    """Human-computer interaction requirements."""

    interface_type: str  # CLI, web, API, etc.
    response_time_requirement: str
    accessibility_requirements: list[str]
    error_handling_strategy: str


@dataclass
class UserContext:
    """Stage 4 deliverable: User-centric design specification."""

    user_personas: list[Persona]
    user_journey_map: JourneyMap
    hci_requirements: HCISpec
    interpretability_needs: ExplainabilityRequirements
    feedback_mechanisms: list[FeedbackMechanism]
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


# ============================================================================
# STAGE 5: ETHICS - DELIVERABLES
# ============================================================================


@dataclass
class MitigationStrategy:
    """Ethical risk mitigation plan."""

    description: str
    implementation_method: str
    cost_estimate: Optional[str] = None
    timeline: Optional[str] = None
    effectiveness_rating: float = 0.0  # 0.0-1.0


@dataclass
class EthicalRisk:
    """Ethical risk assessment for specific principle."""

    principle: EthicalPrinciple
    risk_description: str
    severity: RiskLevel
    likelihood: RiskLevel
    affected_stakeholders: list[str]
    mitigation_strategies: list[MitigationStrategy]
    residual_risk: RiskLevel


@dataclass
class ContinuousMonitoringPlan:
    """Post-deployment ethical monitoring strategy."""

    metrics_to_monitor: list[str]
    monitoring_frequency: str
    alert_thresholds: dict[str, float]
    review_process: str
    escalation_procedure: str


@dataclass
class EthicalRiskReport:
    """Stage 5 deliverable: Comprehensive ethical assessment."""

    initial_risks: dict[EthicalPrinciple, list[EthicalRisk]]
    mitigation_strategies: dict[str, list[MitigationStrategy]]
    residual_risks: dict[EthicalPrinciple, RiskLevel]
    governance_decision: GovernanceDecision
    decision_reasoning: str
    monitoring_plan: ContinuousMonitoringPlan
    requires_committee_review: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"


# ============================================================================
# CITATION AND DOCUMENTATION
# ============================================================================


@dataclass
class Citation:
    """APA 7th Edition citation."""

    citation_type: str  # journal, book, website, report, conference
    authors: list[str]
    year: int
    title: str
    source: str
    url: Optional[str] = None
    doi: Optional[str] = None
    access_date: Optional[datetime] = None


# ============================================================================
# COMPLETE AI PROJECT CHARTER
# ============================================================================


@dataclass
class AIProjectCharter:
    """Complete AI Project Charter aggregating all stage deliverables."""

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
    overall_feasibility: FeasibilityLevel
    critical_success_factors: list[str]
    major_risks: list[str]

    # Metadata
    approver: Optional[str] = None
    approval_date: Optional[datetime] = None
    version: str = "1.0"
    citations: list[Citation] = field(default_factory=list)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================


@dataclass
class Message:
    """Conversation message in session history."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    stage_number: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Checkpoint:
    """Stage completion checkpoint for session recovery."""

    stage_number: int
    timestamp: datetime
    data_snapshot: dict[str, Any]
    validation_status: bool
    checkpoint_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: Optional[UUID] = None  # Optional session reference
    checksum: Optional[str] = None  # Checksum for data integrity validation
    cross_stage_issues: list[str] = field(default_factory=list)  # Issues identified across stages

    # Compatibility properties for accessing nested data
    @property
    def stage_data(self) -> dict[int, Any]:
        """Extract stage_data from data_snapshot."""
        return self.data_snapshot.get("stage_data", {})

    @property
    def conversation_history(self) -> list[dict[str, Any]]:
        """Extract conversation_history from data_snapshot."""
        return self.data_snapshot.get("conversation_history", [])


@dataclass
class Session:
    """User session managing multi-stage conversation flow."""

    session_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    project_name: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)
    current_stage: int = 1
    stage_data: dict[int, Any] = field(default_factory=dict)
    conversation_history: list[Message] = field(default_factory=list)
    status: SessionStatus = SessionStatus.IN_PROGRESS
    checkpoints: list[Checkpoint] = field(default_factory=list)
    progress_percentage: float = 0.0  # 0-100% progress through workflow
    data_hash: Optional[str] = None  # Hash for data integrity validation

    # Compatibility properties for test API
    @property
    def created_at(self) -> datetime:
        """Alias for started_at to match test expectations."""
        return self.started_at

    @property
    def updated_at(self) -> datetime:
        """Alias for last_updated_at to match test expectations."""
        return self.last_updated_at

    def calculate_progress_percentage(self) -> float:
        """Calculate progress percentage based on current stage and status."""
        if self.status == SessionStatus.COMPLETED:
            return 100.0
        elif self.status == SessionStatus.ABANDONED:
            return 0.0
        else:
            # Progress is based on current stage (1-5)
            # Each stage is 20% of the workflow
            return (self.current_stage - 1) * 20.0

    # Dynamic stage data accessors for agent compatibility
    @property
    def stage1_data(self) -> Optional[Any]:
        """Access Stage 1 deliverable (ProblemStatement)."""
        return self.stage_data.get(1)

    @property
    def stage2_data(self) -> Optional[Any]:
        """Access Stage 2 deliverable (MetricAlignmentMatrix)."""
        return self.stage_data.get(2)

    @property
    def stage3_data(self) -> Optional[Any]:
        """Access Stage 3 deliverable (DataQualityScorecard)."""
        return self.stage_data.get(3)

    @property
    def stage4_data(self) -> Optional[Any]:
        """Access Stage 4 deliverable (UserContext)."""
        return self.stage_data.get(4)

    @property
    def stage5_data(self) -> Optional[Any]:
        """Access Stage 5 deliverable (EthicalRiskReport)."""
        return self.stage_data.get(5)


# ============================================================================
# REFLECTION AGENT OUTPUTS
# ============================================================================


@dataclass
class QualityAssessment:
    """Response quality evaluation from ResponseQualityAgent."""

    quality_score: int  # 0-10
    is_acceptable: bool  # score >= 7
    issues: list[str]
    suggested_followups: list[str]
    examples_to_provide: list[str]


@dataclass
class StageValidation:
    """Stage gate validation result from StageGateValidatorAgent."""

    can_proceed: bool
    completeness_score: float  # 0.0-1.0
    missing_items: list[str]
    validation_concerns: list[str]
    recommendations: list[str]


@dataclass
class Contradiction:
    """Logical contradiction identified across stages."""

    stage1: int
    stage2: int
    description: str
    severity: str  # "minor", "major", "critical"


@dataclass
class RiskArea:
    """Feasibility risk identified in consistency check."""

    area: str
    description: str
    affected_stages: list[int]
    mitigation_recommendation: str


@dataclass
class ConsistencyReport:
    """Cross-stage consistency check from ConsistencyCheckerAgent."""

    is_consistent: bool
    overall_feasibility: FeasibilityLevel
    contradictions: list[Contradiction]
    risk_areas: list[RiskArea]
    recommendations: list[str]


# ============================================================================
# AGENT COMMUNICATION
# ============================================================================


@dataclass
class AgentMessage:
    """Message structure for agent-to-agent communication."""

    sender: AgentType
    receiver: AgentType
    message_type: MessageType
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: UUID = field(default_factory=uuid4)


# ============================================================================
# VALIDATION RESULTS
# ============================================================================


@dataclass
class ValidationResult:
    """Generic validation result from tool validators."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


# ============================================================================
# STAGE 3 VALIDATION RESULTS
# ============================================================================


@dataclass
class DimensionScore:
    """Quality dimension assessment result."""

    dimension: QualityDimension
    score: int  # 0-10
    evidence: str
    concerns: list[str] = field(default_factory=list)


@dataclass
class ThresholdValidation:
    """Quality threshold validation result."""

    meets_threshold: bool
    average_score: float
    blocking_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class LabelingValidation:
    """Labeling strategy validation result."""

    is_adequate: bool
    has_budget: bool
    has_timeline: bool
    has_quality_plan: bool
    missing_elements: list[str] = field(default_factory=list)
    feedback: str = ""


@dataclass
class FAIRCompliance:
    """FAIR principles compliance assessment."""

    findable_score: str  # Full, Partial, None
    accessible_score: str
    interoperable_score: str
    reusable_score: str
    overall_maturity: str  # High, Medium, Low
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
