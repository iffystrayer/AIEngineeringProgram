"""Mock stage agents for Phase 2 testing.

Provides mock implementations of Stage1Agent through Stage5Agent
for testing orchestrator stage progression and context passing.

SWE Spec Compliance: Mocks now return proper stage deliverable dataclasses
to pass stage-gate validation (FR-4).
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from datetime import timedelta
from src.models.schemas import (
    ProblemStatement,
    MetricAlignmentMatrix,
    DataQualityScorecard,
    UserContext,
    EthicalRiskReport,
    Feature,
    OutputDefinition,
    ScopeDefinition,
    FeatureAccessibilityReport,
    MLArchetype,
    KPI,
    TechnicalMetric,
    CausalLink,
    ValidationPlan,
    DataSource,
    QualityDimension,
    LabelingStrategy,
    Persona,
    JourneyMap,
    HCISpec,
    ExplainabilityRequirements,
    FeedbackMechanism,
    EthicalRisk,
    EthicalPrinciple,
    RiskLevel,
    MitigationStrategy,
    GovernanceDecision,
)


@dataclass
class MockStageResponse:
    """Response from a mock stage agent."""

    stage_number: int
    output: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    context_received: Optional[Dict[str, Any]] = None


class MockStageAgent:
    """Base mock stage agent for testing."""

    def __init__(self, stage_number: int, session_id: str):
        """Initialize mock stage agent.

        Args:
            stage_number: Stage number (1-5)
            session_id: Session ID for context
        """
        self.stage_number = stage_number
        self.session_id = session_id
        self.execution_count = 0
        self.last_response: Optional[MockStageResponse] = None

    async def run_stage(
        self, context: Optional[Dict[str, Any]] = None
    ) -> MockStageResponse:
        """Run mock stage with optional context.

        Args:
            context: Context from previous stages

        Returns:
            MockStageResponse with stage output
        """
        self.execution_count += 1

        # Generate mock output based on stage
        output = self._generate_stage_output()

        response = MockStageResponse(
            stage_number=self.stage_number,
            output=output,
            context_received=context,
        )

        self.last_response = response
        return response

    async def conduct_interview(self) -> Dict[str, Any]:
        """Conduct mock interview for this stage.

        Returns:
            Mock stage output
        """
        self.execution_count += 1
        output = self._generate_stage_output()

        response = MockStageResponse(
            stage_number=self.stage_number,
            output=output,
        )

        self.last_response = response
        return output

    def _generate_stage_output(self) -> Any:
        """Generate mock output for this stage.

        SWE Spec Compliance: Returns proper dataclass objects that pass
        stage-gate validation (FR-4).
        """
        if self.stage_number == 1:
            # Return valid ProblemStatement object
            return ProblemStatement(
                business_objective="Reduce customer churn by 25% within 12 months",
                ai_necessity_justification="ML needed to predict churn risk in real-time",
                input_features=[
                    Feature(
                        name="customer_tenure_months",
                        data_type="integer",
                        description="Months as customer",
                        source_system="CRM",
                        availability_in_production=True,
                        access_latency_ms=50
                    ),
                    Feature(
                        name="support_tickets_count",
                        data_type="integer",
                        description="Number of support tickets",
                        source_system="SupportDB",
                        availability_in_production=True,
                        access_latency_ms=100
                    ),
                ],
                target_output=OutputDefinition(
                    name="churn_probability",
                    type="probability",
                    description="Probability of churn in next 30 days",
                    possible_values=None,
                    units="percentage"
                ),
                ml_archetype=MLArchetype.CLASSIFICATION,
                ml_archetype_justification="Binary classification problem - churn vs no churn",
                scope_boundaries=ScopeDefinition(
                    in_scope=["Existing customers", "30-day prediction window"],
                    out_of_scope=["New customer acquisition", "90+ day predictions"],
                    assumptions=["Historical data is representative"],
                    constraints=["Must run in <100ms", "Privacy compliance required"]
                ),
                feature_availability=FeatureAccessibilityReport(
                    all_features_available=True,
                    unavailable_features=[],
                    latency_concerns=[],
                    access_method_issues=[]
                )
            )
        elif self.stage_number == 2:
            # Return valid MetricAlignmentMatrix object
            return MetricAlignmentMatrix(
                business_kpis=[
                    KPI(
                        name="Churn Rate Reduction",
                        description="Reduce monthly churn rate",
                        current_baseline=5.2,
                        target_value=3.9,
                        measurement_frequency="monthly",
                        measurement_method="(churned_customers / total_customers) * 100"
                    )
                ],
                technical_metrics=[
                    TechnicalMetric(
                        name="ROC-AUC",
                        description="Area under ROC curve",
                        target_value=0.85,
                        measurement_method="scikit-learn roc_auc_score"
                    )
                ],
                causal_pathways=[
                    CausalPathway(
                        model_metric="ROC-AUC",
                        business_kpi="Churn Rate Reduction",
                        causal_chain=["Model predicts churn", "Retention team intervenes", "Churn reduced"],
                        strength_of_evidence="strong"
                    )
                ]
            )
        elif self.stage_number == 3:
            # Return valid DataQualityScorecard object
            return DataQualityScorecard(
                data_sources=[
                    DataSource(
                        name="Customer CRM",
                        type="database",
                        description="Customer master data",
                        access_method="SQL query",
                        update_frequency="real-time",
                        estimated_row_count=1000000
                    )
                ],
                quality_scores={
                    QualityDimension.ACCURACY: 9,
                    QualityDimension.COMPLETENESS: 8,
                    QualityDimension.CONSISTENCY: 9,
                    QualityDimension.TIMELINESS: 10,
                    QualityDimension.VALIDITY: 8,
                    QualityDimension.INTEGRITY: 9
                },
                fair_principles_compliance={
                    "findable": True,
                    "accessible": True,
                    "interoperable": True,
                    "reusable": True
                },
                labeling_strategy=LabelingStrategy(
                    method="automated",
                    description="Churn labels from historical data",
                    quality_assurance="Validation against known outcomes",
                    estimated_cost=5000,
                    estimated_timeline_weeks=2
                )
            )
        elif self.stage_number == 4:
            # Return valid UserContext object
            return UserContext(
                user_personas=[
                    UserPersona(
                        name="Retention Manager",
                        role="Business user",
                        goals=["Reduce churn", "Improve retention"],
                        pain_points=["Late churn detection"],
                        technical_proficiency="Medium"
                    )
                ],
                user_journeys=[
                    UserJourney(
                        persona="Retention Manager",
                        stages=["Login", "View churn dashboard", "Review predictions", "Take action"],
                        interactions=["View predictions", "Filter by risk level", "Export list"],
                        pain_points=["Too many false positives"],
                        opportunities=["Automated intervention triggering"]
                    )
                ],
                interpretability_requirements=[
                    InterpretabilityRequirement(
                        stakeholder="Retention Manager",
                        need_level="High",
                        rationale="Must explain why customer is at risk",
                        proposed_method="SHAP values for feature importance"
                    )
                ],
                feedback_mechanisms=["Weekly accuracy reports", "User satisfaction surveys"]
            )
        elif self.stage_number == 5:
            # Return valid EthicalRiskReport object
            return EthicalRiskReport(
                initial_risks={
                    EthicalPrinciple.FAIRNESS_EQUITY: [
                        EthicalRisk(
                            principle=EthicalPrinciple.FAIRNESS_EQUITY,
                            risk_description="Potential bias against certain customer segments",
                            severity=RiskLevel.MEDIUM,
                            affected_stakeholders=["Customers", "Company reputation"],
                            likelihood="Medium"
                        )
                    ],
                    EthicalPrinciple.PRIVACY_PROTECTION: [
                        EthicalRisk(
                            principle=EthicalPrinciple.PRIVACY_PROTECTION,
                            risk_description="Processing of personal customer data",
                            severity=RiskLevel.MEDIUM,
                            affected_stakeholders=["Customers"],
                            likelihood="High"
                        )
                    ],
                },
                mitigation_strategies={
                    EthicalPrinciple.FAIRNESS_EQUITY: [
                        MitigationStrategy(
                            principle=EthicalPrinciple.FAIRNESS_EQUITY,
                            strategy="Bias testing across demographics",
                            implementation_effort="Medium",
                            expected_risk_reduction=RiskLevel.LOW,
                            responsible_party="ML Team"
                        )
                    ],
                    EthicalPrinciple.PRIVACY_PROTECTION: [
                        MitigationStrategy(
                            principle=EthicalPrinciple.PRIVACY_PROTECTION,
                            strategy="Data anonymization and encryption",
                            implementation_effort="High",
                            expected_risk_reduction=RiskLevel.LOW,
                            responsible_party="Security Team"
                        )
                    ],
                },
                residual_risks={
                    EthicalPrinciple.FAIRNESS_EQUITY: RiskLevel.LOW,
                    EthicalPrinciple.PRIVACY_PROTECTION: RiskLevel.LOW,
                },
                governance_decision=GovernanceDecision.PROCEED_WITH_MONITORING,
                monitoring_requirements=["Monthly bias audits", "Quarterly privacy reviews"]
            )
        else:
            return {
                "error": f"Unknown stage: {self.stage_number}",
                "stage_data": {}
            }

    async def validate_stage(self) -> bool:
        """Validate stage completion."""
        return self.last_response is not None

    def get_execution_history(self) -> int:
        """Get number of times this stage was executed."""
        return self.execution_count


class MockStage1Agent(MockStageAgent):
    """Mock Stage 1 agent - Problem Statement."""

    def __init__(self, session_id: str):
        super().__init__(1, session_id)


class MockStage2Agent(MockStageAgent):
    """Mock Stage 2 agent - Scope Definition."""

    def __init__(self, session_id: str):
        super().__init__(2, session_id)


class MockStage3Agent(MockStageAgent):
    """Mock Stage 3 agent - Technical Approach."""

    def __init__(self, session_id: str):
        super().__init__(3, session_id)


class MockStage4Agent(MockStageAgent):
    """Mock Stage 4 agent - Resource Planning."""

    def __init__(self, session_id: str):
        super().__init__(4, session_id)


class MockStage5Agent(MockStageAgent):
    """Mock Stage 5 agent - Risk Assessment."""

    def __init__(self, session_id: str):
        super().__init__(5, session_id)


def create_mock_stage_agent(stage_number: int, session_id: str) -> MockStageAgent:
    """Factory function to create mock stage agents.

    Args:
        stage_number: Stage number (1-5)
        session_id: Session ID

    Returns:
        Appropriate mock stage agent

    Raises:
        ValueError: If stage_number is not 1-5
    """
    if stage_number == 1:
        return MockStage1Agent(session_id)
    elif stage_number == 2:
        return MockStage2Agent(session_id)
    elif stage_number == 3:
        return MockStage3Agent(session_id)
    elif stage_number == 4:
        return MockStage4Agent(session_id)
    elif stage_number == 5:
        return MockStage5Agent(session_id)
    else:
        raise ValueError(f"Invalid stage number: {stage_number}")

