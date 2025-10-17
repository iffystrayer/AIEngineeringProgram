"""
Helper fixtures for integration tests.

Provides minimal valid schema objects for testing.
"""

from datetime import timedelta, datetime
from src.models.schemas import (
    ProblemStatement,
    MetricAlignmentMatrix,
    DataQualityScorecard,
    MLArchetype,
    Feature,
    OutputDefinition,
    ScopeDefinition,
    FeatureAccessibilityReport,
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
)


def create_minimal_problem_statement() -> ProblemStatement:
    """Create minimal valid ProblemStatement for testing."""
    return ProblemStatement(
        business_objective="Reduce customer churn by 15% within 6 months",
        ai_necessity_justification="Manual analysis cannot scale to millions of customers",
        input_features=[
            Feature(
                name="usage_frequency",
                data_type="float",
                description="Daily login frequency",
                source_system="analytics_db",
                availability_in_production=True,
                access_latency_ms=50
            ),
            Feature(
                name="support_tickets",
                data_type="int",
                description="Number of support tickets",
                source_system="zendesk",
                availability_in_production=True,
                access_latency_ms=100
            )
        ],
        target_output=OutputDefinition(
            name="churn_probability",
            type="probability",
            description="Probability of customer churning in next 30 days",
            possible_values=None,
            units="percentage"
        ),
        ml_archetype=MLArchetype.CLASSIFICATION,
        ml_archetype_justification="Binary classification problem: churn vs no churn",
        scope_boundaries=ScopeDefinition(
            in_scope=["Existing customers", "B2C segment"],
            out_of_scope=["New signups", "Enterprise customers"],
            assumptions=["Historical data representative of future"],
            constraints=["Must process within 100ms", "GDPR compliance required"]
        ),
        feature_availability=FeatureAccessibilityReport(
            all_features_available=True,
            unavailable_features=[],
            latency_concerns=[],
            access_method_issues=[]
        )
    )


def create_minimal_metric_alignment_matrix() -> MetricAlignmentMatrix:
    """Create minimal valid MetricAlignmentMatrix for testing."""
    return MetricAlignmentMatrix(
        business_kpis=[
            KPI(
                name="30-day retention rate",
                description="Percentage of customers active after 30 days",
                current_baseline=65.0,
                target_value=80.0,
                target_timeframe="6 months",
                measurement_method="Analytics dashboard",
                business_impact="15% increase = $500K annual revenue"
            )
        ],
        model_metrics=[
            TechnicalMetric(
                name="Precision",
                description="Precision at 50% recall",
                target_threshold=0.80,
                measurement_method="sklearn.metrics.precision_score"
            ),
            TechnicalMetric(
                name="Recall",
                description="Recall score",
                target_threshold=0.50,
                measurement_method="sklearn.metrics.recall_score"
            )
        ],
        causal_pathways=[
            CausalLink(
                model_metric="Precision",
                business_kpi="30-day retention rate",
                causal_mechanism="Higher precision → fewer false churn predictions → better resource allocation → improved retention",
                assumptions=["Team acts on predictions", "Interventions are effective"],
                potential_failure_modes=["Recall drops too low", "Intervention timing issues"]
            )
        ],
        actionability_window=timedelta(hours=24),
        causal_impact_plan=ValidationPlan(
            validation_method="A/B test",
            data_requirements=["Historical predictions", "Intervention outcomes"],
            timeline="3 months",
            success_criteria="Statistical significance p<0.05"
        )
    )


def create_minimal_data_quality_scorecard() -> DataQualityScorecard:
    """Create minimal valid DataQualityScorecard for testing."""
    return DataQualityScorecard(
        data_sources=[
            DataSource(
                name="Analytics Database",
                type="database",
                description="User behavior data",
                size="10M records",
                update_frequency="hourly",
                access_method="SQL",
                quality_assessment={
                    QualityDimension.ACCURACY: 9,
                    QualityDimension.CONSISTENCY: 8,
                    QualityDimension.COMPLETENESS: 7,
                    QualityDimension.TIMELINESS: 9,
                    QualityDimension.VALIDITY: 8,
                    QualityDimension.INTEGRITY: 9
                },
                covered_features=[]
            )
        ],
        quality_scores={
            QualityDimension.ACCURACY: 9,
            QualityDimension.CONSISTENCY: 8,
            QualityDimension.COMPLETENESS: 7,
            QualityDimension.TIMELINESS: 9,
            QualityDimension.VALIDITY: 8,
            QualityDimension.INTEGRITY: 9
        },
        labeling_strategy=LabelingStrategy(
            labeling_method="manual",
            estimated_cost=50000.0,
            estimated_time="3 months",
            quality_assurance_process="Double-blind annotation",
            annotator_requirements=["Domain expertise", "Training certification"]
        ),
        fair_compliance=FAIRAssessment(
            findable=True,
            accessible=True,
            interoperable=True,
            reusable=True,
            gaps=[],
            remediation_plan="No remediation needed"
        ),
        infrastructure_readiness=InfrastructureReport(
            storage_capacity="Sufficient (100TB available)",
            compute_resources="GPU cluster with 8x V100",
            pipeline_maturity="Production-ready",
            gaps=[],
            estimated_setup_cost=0.0
        ),
        overall_feasibility=FeasibilityLevel.HIGH
    )
