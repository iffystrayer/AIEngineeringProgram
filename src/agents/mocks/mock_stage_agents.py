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
    FAIRAssessment,
    InfrastructureReport,
    FeasibilityLevel,
    Persona,
    JourneyMap,
    JourneyStage,
    HCISpec,
    ExplainabilityRequirements,
    FeedbackMechanism,
    EthicalRisk,
    EthicalPrinciple,
    RiskLevel,
    MitigationStrategy,
    GovernanceDecision,
    ContinuousMonitoringPlan,
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
                        target_timeframe="12 months",
                        measurement_method="(churned_customers / total_customers) * 100",
                        business_impact="$2M annual revenue retention"
                    )
                ],
                model_metrics=[
                    TechnicalMetric(
                        name="ROC-AUC",
                        description="Area under ROC curve",
                        target_threshold=0.85,
                        measurement_method="scikit-learn roc_auc_score"
                    )
                ],
                causal_pathways=[
                    CausalLink(
                        model_metric="ROC-AUC",
                        business_kpi="Churn Rate Reduction",
                        causal_mechanism="Higher ROC-AUC means better prediction accuracy, enabling earlier intervention by retention team, which reduces actual churn",
                        assumptions=[
                            "Retention team has capacity to act on predictions",
                            "Intervention strategies are effective",
                            "Prediction window is actionable (30 days)"
                        ],
                        potential_failure_modes=[
                            "Model accuracy doesn't translate to business value if retention team is under-resourced",
                            "Prediction-to-action lag exceeds customer decision window",
                            "Intervention strategies may have diminishing returns"
                        ]
                    )
                ],
                actionability_window=timedelta(days=30),
                causal_impact_plan=ValidationPlan(
                    validation_method="A/B testing with control group",
                    data_requirements=[
                        "Historical intervention outcomes",
                        "Customer retention data for treated vs control groups",
                        "Attribution tracking for retention actions"
                    ],
                    timeline="6 months post-deployment",
                    success_criteria="Statistically significant (p<0.05) improvement in retention rate for treated group"
                )
            )
        elif self.stage_number == 3:
            # Return valid DataQualityScorecard object
            return DataQualityScorecard(
                data_sources=[
                    DataSource(
                        name="Customer CRM",
                        type="database",
                        description="Customer master data",
                        size="1M records, 500GB",
                        update_frequency="real-time",
                        access_method="SQL query",
                        quality_assessment={
                            QualityDimension.ACCURACY: 9,
                            QualityDimension.COMPLETENESS: 8,
                            QualityDimension.CONSISTENCY: 9,
                            QualityDimension.TIMELINESS: 10,
                            QualityDimension.VALIDITY: 8,
                            QualityDimension.INTEGRITY: 9
                        },
                        covered_features=[
                            {"feature": "customer_tenure_months", "coverage": "100%"},
                            {"feature": "support_tickets_count", "coverage": "100%"}
                        ]
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
                labeling_strategy=LabelingStrategy(
                    labeling_method="automated from historical data",
                    estimated_cost=5000.0,
                    estimated_time="2 weeks",
                    quality_assurance_process="Validation against known outcomes with 95% accuracy threshold",
                    annotator_requirements=["Domain knowledge of customer behavior", "SQL proficiency"]
                ),
                fair_compliance=FAIRAssessment(
                    findable=True,
                    accessible=True,
                    interoperable=True,
                    reusable=True,
                    gaps=[],
                    remediation_plan="No remediation needed - full FAIR compliance"
                ),
                infrastructure_readiness=InfrastructureReport(
                    storage_capacity="2TB available, sufficient for 3 years",
                    compute_resources="8-core CPU, 32GB RAM, GPU optional",
                    pipeline_maturity="Mature - existing ETL pipelines operational",
                    gaps=["GPU acceleration for model training would improve performance"],
                    estimated_setup_cost=15000.0
                ),
                overall_feasibility=FeasibilityLevel.HIGH
            )
        elif self.stage_number == 4:
            # Return valid UserContext object
            return UserContext(
                user_personas=[
                    Persona(
                        name="Retention Manager",
                        role="Business user managing customer retention",
                        goals=["Reduce customer churn by 25%", "Improve retention team efficiency"],
                        pain_points=["Late detection of at-risk customers", "Overwhelming false positives"],
                        technical_proficiency="intermediate",
                        ai_interaction_frequency="daily",
                        decision_authority="Can approve retention interventions up to $5000",
                        research_evidence="Based on interviews with 5 retention managers",
                        data_access_level="full"
                    )
                ],
                user_journey_map=JourneyMap(
                    stages=[
                        JourneyStage(
                            stage_name="pre-interaction",
                            user_actions=["Login to dashboard", "Review daily churn alerts"],
                            pain_points=["Too many alerts to process", "Unclear prioritization"],
                            ai_touchpoints=["Churn prediction model generates risk scores"],
                            success_criteria=["Clear risk prioritization", "Actionable predictions"]
                        ),
                        JourneyStage(
                            stage_name="during",
                            user_actions=["Review prediction details", "Examine customer history", "Decide on intervention"],
                            pain_points=["Lack of explanation for predictions", "Difficult to validate model output"],
                            ai_touchpoints=["Model explainability interface", "Feature importance display"],
                            success_criteria=["Understanding why customer is at risk", "Confidence in prediction accuracy"]
                        ),
                        JourneyStage(
                            stage_name="post-interaction",
                            user_actions=["Execute retention action", "Track outcome", "Provide feedback"],
                            pain_points=["No feedback loop to model", "Can't track prediction accuracy"],
                            ai_touchpoints=["Outcome tracking", "Model retraining trigger"],
                            success_criteria=["Successful intervention", "Model learns from outcomes"]
                        )
                    ],
                    critical_decision_points=[
                        "Which customers to prioritize for intervention",
                        "What type of retention offer to make",
                        "When to escalate to senior management"
                    ],
                    risk_areas=[
                        "Over-reliance on model without human judgment",
                        "Alert fatigue from too many predictions",
                        "Intervention budget constraints"
                    ]
                ),
                hci_requirements=HCISpec(
                    interface_type="web dashboard with mobile alerts",
                    response_time_requirement="<2 seconds for prediction retrieval, <500ms for filtering",
                    accessibility_requirements=[
                        "WCAG 2.1 Level AA compliance",
                        "Screen reader compatible",
                        "Keyboard navigation support",
                        "Color-blind friendly visualization"
                    ],
                    error_handling_strategy="Graceful degradation with clear error messages and fallback to historical data"
                ),
                interpretability_needs=ExplainabilityRequirements(
                    required_level="high",
                    explanation_method="SHAP values with feature importance visualization",
                    target_audience=["Retention managers", "Customer service team", "Executives"],
                    regulatory_requirements=["GDPR right to explanation", "Internal audit transparency"]
                ),
                feedback_mechanisms=[
                    FeedbackMechanism(
                        feedback_type="explicit",
                        collection_method="Post-intervention survey on prediction accuracy",
                        frequency="after each intervention",
                        integration_plan="Feed back into model retraining pipeline monthly"
                    ),
                    FeedbackMechanism(
                        feedback_type="implicit",
                        collection_method="Track actual churn vs predicted churn",
                        frequency="continuous",
                        integration_plan="Automated alerts for model drift detection"
                    )
                ]
            )
        elif self.stage_number == 5:
            # Return valid EthicalRiskReport object
            return EthicalRiskReport(
                initial_risks={
                    EthicalPrinciple.FAIRNESS_EQUITY: [
                        EthicalRisk(
                            principle=EthicalPrinciple.FAIRNESS_EQUITY,
                            risk_description="Potential bias against certain customer segments (e.g., age, geography)",
                            severity=RiskLevel.MEDIUM,
                            likelihood=RiskLevel.MEDIUM,
                            affected_stakeholders=["Customers", "Company reputation", "Retention team"],
                            mitigation_strategies=[
                                MitigationStrategy(
                                    description="Conduct bias testing across demographic segments",
                                    implementation_method="Statistical parity and equal opportunity analysis on protected attributes",
                                    cost_estimate="$15,000 for external audit",
                                    timeline="3 months",
                                    effectiveness_rating=0.8
                                ),
                                MitigationStrategy(
                                    description="Implement fairness constraints in model training",
                                    implementation_method="Use fairness-aware ML libraries (AIF360, Fairlearn)",
                                    cost_estimate="$10,000 for implementation",
                                    timeline="2 months",
                                    effectiveness_rating=0.7
                                )
                            ],
                            residual_risk=RiskLevel.LOW
                        )
                    ],
                    EthicalPrinciple.PRIVACY_PROTECTION: [
                        EthicalRisk(
                            principle=EthicalPrinciple.PRIVACY_PROTECTION,
                            risk_description="Processing of sensitive personal customer data (PII, behavioral patterns)",
                            severity=RiskLevel.MEDIUM,
                            likelihood=RiskLevel.HIGH,
                            affected_stakeholders=["Customers", "Legal/Compliance team", "Data Protection Officer"],
                            mitigation_strategies=[
                                MitigationStrategy(
                                    description="Implement data anonymization and pseudonymization",
                                    implementation_method="Hash customer IDs, aggregate behavioral data, remove direct identifiers",
                                    cost_estimate="$20,000 for infrastructure",
                                    timeline="4 months",
                                    effectiveness_rating=0.9
                                ),
                                MitigationStrategy(
                                    description="Deploy encryption for data at rest and in transit",
                                    implementation_method="AES-256 encryption, TLS 1.3 for transmission",
                                    cost_estimate="$5,000 for setup",
                                    timeline="1 month",
                                    effectiveness_rating=0.95
                                )
                            ],
                            residual_risk=RiskLevel.LOW
                        )
                    ],
                    EthicalPrinciple.TRANSPARENCY_ACCOUNTABILITY: [
                        EthicalRisk(
                            principle=EthicalPrinciple.TRANSPARENCY_ACCOUNTABILITY,
                            risk_description="Model decisions may not be explainable to customers or auditors",
                            severity=RiskLevel.LOW,
                            likelihood=RiskLevel.MEDIUM,
                            affected_stakeholders=["Customers", "Auditors", "Retention managers"],
                            mitigation_strategies=[
                                MitigationStrategy(
                                    description="Implement SHAP-based model explanations",
                                    implementation_method="Integrate SHAP library, create explanation dashboard",
                                    cost_estimate="$12,000 for development",
                                    timeline="2 months",
                                    effectiveness_rating=0.85
                                )
                            ],
                            residual_risk=RiskLevel.LOW
                        )
                    ],
                    EthicalPrinciple.SAFETY_RESILIENCE: [
                        EthicalRisk(
                            principle=EthicalPrinciple.SAFETY_RESILIENCE,
                            risk_description="Model failure could result in customer dissatisfaction or business losses",
                            severity=RiskLevel.LOW,
                            likelihood=RiskLevel.LOW,
                            affected_stakeholders=["Customers", "Retention team", "Business operations"],
                            mitigation_strategies=[
                                MitigationStrategy(
                                    description="Implement model monitoring and fallback mechanisms",
                                    implementation_method="Deploy canary releases, A/B testing, automated rollback on performance degradation",
                                    cost_estimate="$8,000 for infrastructure",
                                    timeline="1.5 months",
                                    effectiveness_rating=0.9
                                )
                            ],
                            residual_risk=RiskLevel.LOW
                        )
                    ],
                    EthicalPrinciple.HUMAN_AGENCY: [
                        EthicalRisk(
                            principle=EthicalPrinciple.HUMAN_AGENCY,
                            risk_description="Over-automation may reduce human judgment in retention decisions",
                            severity=RiskLevel.MEDIUM,
                            likelihood=RiskLevel.LOW,
                            affected_stakeholders=["Retention managers", "Customers"],
                            mitigation_strategies=[
                                MitigationStrategy(
                                    description="Ensure human-in-the-loop design with override capabilities",
                                    implementation_method="Model provides recommendations, humans make final decisions; audit trail for all automated actions",
                                    cost_estimate="$5,000 for UI development",
                                    timeline="1 month",
                                    effectiveness_rating=0.95
                                )
                            ],
                            residual_risk=RiskLevel.LOW
                        )
                    ]
                },
                mitigation_strategies={
                    "fairness": [
                        MitigationStrategy(
                            description="Conduct bias testing across demographic segments",
                            implementation_method="Statistical parity and equal opportunity analysis",
                            cost_estimate="$15,000",
                            timeline="3 months",
                            effectiveness_rating=0.8
                        )
                    ],
                    "privacy": [
                        MitigationStrategy(
                            description="Data anonymization and encryption",
                            implementation_method="Hash IDs, AES-256 encryption, TLS 1.3",
                            cost_estimate="$25,000",
                            timeline="4 months",
                            effectiveness_rating=0.9
                        )
                    ],
                    "transparency": [
                        MitigationStrategy(
                            description="Model explainability with SHAP",
                            implementation_method="SHAP integration, explanation dashboard",
                            cost_estimate="$12,000",
                            timeline="2 months",
                            effectiveness_rating=0.85
                        )
                    ]
                },
                residual_risks={
                    EthicalPrinciple.FAIRNESS_EQUITY: RiskLevel.LOW,
                    EthicalPrinciple.PRIVACY_PROTECTION: RiskLevel.LOW,
                    EthicalPrinciple.TRANSPARENCY_ACCOUNTABILITY: RiskLevel.LOW,
                    EthicalPrinciple.SAFETY_RESILIENCE: RiskLevel.LOW,
                    EthicalPrinciple.HUMAN_AGENCY: RiskLevel.LOW,
                },
                governance_decision=GovernanceDecision.PROCEED_WITH_MONITORING,
                decision_reasoning="Project demonstrates acceptable risk levels after mitigation. Residual risks are LOW or VERY_LOW across all ethical principles. Benefits of churn reduction ($2M annual revenue retention) outweigh remaining risks. Recommend proceeding with continuous monitoring and quarterly ethics reviews.",
                monitoring_plan=ContinuousMonitoringPlan(
                    metrics_to_monitor=[
                        "Demographic parity difference (monthly)",
                        "Equal opportunity difference (monthly)",
                        "Model prediction distribution by customer segment",
                        "Privacy breach incidents",
                        "Data access audit logs",
                        "Explanation quality scores from user feedback"
                    ],
                    monitoring_frequency="Monthly automated reports, quarterly manual review",
                    alert_thresholds={
                        "demographic_parity_diff": 0.1,
                        "equal_opportunity_diff": 0.1,
                        "privacy_incidents": 0.0,
                        "explanation_satisfaction": 0.7
                    },
                    review_process="Monthly automated dashboard review by ML team, quarterly ethics committee review with stakeholders",
                    escalation_procedure="Threshold violations trigger immediate ML team review. Critical issues (privacy breach, significant bias) escalate to ethics committee within 24 hours and may pause model deployment."
                ),
                requires_committee_review=False
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

