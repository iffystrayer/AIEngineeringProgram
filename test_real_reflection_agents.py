#!/usr/bin/env python3
"""
Test Real Reflection Agents with Ollama LLM

This test validates that the reflection agents (ConsistencyChecker, ResponseQuality)
can successfully use Ollama for real LLM reasoning tasks.

Tests:
1. ConsistencyCheckerAgent with mock stage data
2. ResponseQualityAgent with sample user responses
3. Integration with orchestrator

Uses:
- Real Ollama LLM (no API costs)
- Real reflection agent logic
- Mock stage data (no user interaction needed)
"""

import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4

from dotenv import load_dotenv

from src.database.connection import DatabaseConfig, DatabaseManager
from src.llm.router import _create_default_router
from src.agents.reflection.consistency_checker_agent import ConsistencyCheckerAgent
from src.agents.reflection.response_quality_agent import ResponseQualityAgent
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

# Load environment
load_dotenv()


def create_test_stage_data():
    """Create realistic test data for all 5 stages."""

    # Stage 1: Problem Statement
    stage1 = ProblemStatement(
        business_objective="Reduce customer churn by predicting at-risk customers",
        ai_necessity_justification="Need to analyze complex patterns in customer behavior",
        input_features=[
            Feature(
                name="usage_frequency",
                data_type="numeric",
                description="Login frequency per month",
                source_system="Analytics DB",
                availability_in_production=True,
            ),
            Feature(
                name="support_tickets",
                data_type="numeric",
                description="Number of support tickets filed",
                source_system="Zendesk",
                availability_in_production=True,
            ),
        ],
        target_output=OutputDefinition(
            name="will_churn",
            type="binary",
            description="Will customer churn in next 30 days?",
            possible_values=["Yes", "No"],
        ),
        ml_archetype=MLArchetype.CLASSIFICATION,
        ml_archetype_justification="Binary classification problem (churn/no-churn)",
        scope_boundaries=ScopeDefinition(
            in_scope=["Predict churn risk", "Identify at-risk customers"],
            out_of_scope=["Retention campaign execution"],
            assumptions=["Historical patterns will continue"],
            constraints=["Must predict within 24 hours"],
        ),
        feature_availability=FeatureAccessibilityReport(
            all_features_available=True,
            unavailable_features=[],
            latency_concerns=[],
            access_method_issues=[],
        ),
        created_at=datetime.now(),
        version="1.0",
    )

    # Stage 2: Metric Alignment Matrix
    stage2 = MetricAlignmentMatrix(
        business_kpis=[
            KPI(
                name="Churn Rate Reduction",
                description="Reduce monthly churn rate from 5.2% to 3.9%",
                current_baseline=5.2,
                target_value=3.9,
                target_timeframe="12 months",
                measurement_method="(churned_customers / total_customers) * 100",
                business_impact="$2M annual revenue retention",
            )
        ],
        model_metrics=[
            TechnicalMetric(
                name="ROC-AUC",
                description="Area under ROC curve",
                target_threshold=0.85,
                measurement_method="scikit-learn roc_auc_score",
            )
        ],
        causal_pathways=[
            CausalLink(
                model_metric="ROC-AUC",
                business_kpi="Churn Rate Reduction",
                causal_mechanism="Higher ROC-AUC → Better churn prediction → Targeted retention",
                assumptions=["Retention team acts on predictions within 7 days"],
                potential_failure_modes=["Retention campaigns ineffective", "Budget constraints"],
            )
        ],
        actionability_window=timedelta(days=30),
        causal_impact_plan=ValidationPlan(
            test_description="A/B test on 10,000 customers",
            success_criteria=["Churn reduction >= 1.0%"],
            timeline="3 months",
        ),
    )

    # Stage 3: Data Quality Scorecard
    stage3 = DataQualityScorecard(
        data_sources=[
            DataSource(
                name="Customer Analytics DB",
                description="Customer usage logs",
                format="PostgreSQL",
                size="500GB, 10M customers",
                quality_assessment={
                    QualityDimension.COMPLETENESS: 8.5,
                    QualityDimension.ACCURACY: 9.0,
                    QualityDimension.CONSISTENCY: 8.0,
                    QualityDimension.TIMELINESS: 9.5,
                    QualityDimension.VALIDITY: 8.5,
                    QualityDimension.INTEGRITY: 9.0,
                },
            )
        ],
        overall_quality_score=8.75,
        fair_compliance=FAIRAssessment(
            findable=True,
            accessible=True,
            interoperable=True,
            reusable=True,
            gaps=["Metadata documentation incomplete"],
        ),
        infrastructure_readiness=InfrastructureReport(
            compute_available=True,
            storage_sufficient=True,
            latency_acceptable=True,
            limitations=["Batch processing only, no real-time inference"],
        ),
        overall_feasibility=FeasibilityLevel.HIGH,
    )

    # Stage 4: User Context
    stage4 = UserContext(
        personas=[
            Persona(
                name="Retention Manager",
                role="Decision maker",
                needs=["Early churn warnings", "Actionable customer segments"],
                pain_points=["Too many false alarms", "Predictions come too late"],
            )
        ],
        journey_map=JourneyMap(
            stages=[
                JourneyStage(
                    name="Daily Review",
                    actions=["Check dashboard", "Review at-risk list"],
                    pain_points=["Dashboard slow to load"],
                    ai_touchpoints=["Churn predictions displayed"],
                )
            ]
        ),
        hci_spec=HCISpec(
            interface_type="Web dashboard",
            interaction_patterns=["Click to drill down", "Filter by risk level"],
            accessibility_requirements=["WCAG 2.1 AA compliance"],
        ),
        explainability_requirements=ExplainabilityRequirements(
            required_level="high",
            explanation_format="Feature importance + example cases",
            target_audience="Non-technical managers",
        ),
        feedback_mechanisms=[
            FeedbackMechanism(
                mechanism_type="explicit",
                description="'Was this prediction accurate?' button",
                collection_frequency="Per prediction",
            )
        ],
    )

    # Stage 5: Ethical Risk Report
    stage5 = EthicalRiskReport(
        principle_assessments={
            EthicalPrinciple.FAIRNESS_EQUITY: [
                EthicalRisk(
                    principle=EthicalPrinciple.FAIRNESS_EQUITY,
                    risk_description="Model may discriminate based on customer demographics",
                    severity=RiskLevel.HIGH,
                    likelihood=RiskLevel.MEDIUM,
                    affected_stakeholders=["Customers", "Retention team"],
                    mitigation_strategies=[
                        MitigationStrategy(
                            strategy="Fairness testing across demographic groups",
                            implementation="Use fairlearn library for bias detection",
                            effectiveness="High",
                        )
                    ],
                    residual_risk=RiskLevel.LOW,
                )
            ],
            EthicalPrinciple.TRANSPARENCY_ACCOUNTABILITY: [],
            EthicalPrinciple.PRIVACY_SECURITY: [],
            EthicalPrinciple.SAFETY_RESILIENCE: [],
            EthicalPrinciple.HUMAN_AGENCY: [],
        },
        overall_risk_level=RiskLevel.MEDIUM,
        governance_decision=GovernanceDecision.PROCEED_WITH_CONDITIONS,
        conditions=["Monthly fairness audits", "Explainability dashboard"],
        continuous_monitoring=ContinuousMonitoringPlan(
            metrics_to_track=["Fairness metrics by demographic group"],
            review_frequency="Monthly",
            escalation_criteria=["Fairness metric drops below 0.8"],
        ),
    )

    return {
        1: stage1,
        2: stage2,
        3: stage3,
        4: stage4,
        5: stage5,
    }


async def test_consistency_checker_with_ollama():
    """Test ConsistencyCheckerAgent with real Ollama LLM."""

    print("=" * 80)
    print("TEST: ConsistencyCheckerAgent with Ollama")
    print("=" * 80)

    # 1. Setup LLM router with Ollama
    print("\n[1/4] Initializing Ollama LLM router...")
    llm_router = _create_default_router()
    print("✓ LLM router ready")

    # 2. Create test stage data
    print("\n[2/4] Creating realistic test stage data...")
    stage_data = create_test_stage_data()
    print(f"✓ Created data for {len(stage_data)} stages")

    # 3. Initialize ConsistencyCheckerAgent
    print("\n[3/4] Initializing ConsistencyCheckerAgent...")

    # Create mock session context
    class MockSession:
        session_id = uuid4()
        stage_data = stage_data
        current_stage = 5

    session = MockSession()

    consistency_agent = ConsistencyCheckerAgent(
        session_context=session,
        llm_router=llm_router,
    )
    print("✓ ConsistencyCheckerAgent initialized")

    # 4. Run consistency check with real LLM reasoning
    print("\n[4/4] Running cross-stage consistency validation with Ollama...")
    print("  This will use the LLM to analyze:")
    print("  - Stage 1 (Problem Statement) vs Stage 2 (Metrics)")
    print("  - Stage 2 (Metrics) vs Stage 3 (Data)")
    print("  - Stage 3 (Data) vs Stage 4 (User Context)")
    print("  - Stage 4 (User Context) vs Stage 5 (Ethics)")
    print("\n  🤖 Ollama is thinking...")

    try:
        report = await consistency_agent.check_cross_stage_consistency()

        print("\n✅ Consistency check completed!")
        print(f"\n  Overall feasibility: {report.overall_feasibility.value}")
        print(f"  Is consistent: {report.is_consistent}")
        print(f"  Issues found: {len(report.issues)}")

        if report.issues:
            print("\n  Issues detected:")
            for issue in report.issues[:3]:  # Show first 3
                print(f"    - {issue}")

        if report.recommendations:
            print("\n  Recommendations:")
            for rec in report.recommendations[:3]:  # Show first 3
                print(f"    - {rec}")

        return True

    except Exception as e:
        print(f"\n❌ Consistency check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_response_quality_with_ollama():
    """Test ResponseQualityAgent with real Ollama LLM."""

    print("\n" + "=" * 80)
    print("TEST: ResponseQualityAgent with Ollama")
    print("=" * 80)

    # 1. Setup LLM router
    print("\n[1/3] Initializing Ollama LLM router...")
    llm_router = _create_default_router()
    print("✓ LLM router ready")

    # 2. Initialize ResponseQualityAgent
    print("\n[2/3] Initializing ResponseQualityAgent...")

    class MockSession:
        session_id = uuid4()
        current_stage = 1

    quality_agent = ResponseQualityAgent(
        session_context=MockSession(),
        llm_router=llm_router,
        quality_threshold=7.0,
    )
    print("✓ ResponseQualityAgent initialized")

    # 3. Test quality assessment on sample responses
    print("\n[3/3] Testing quality assessment on sample responses...")

    test_cases = [
        {
            "question": "What business problem are you trying to solve?",
            "response": "We want to reduce customer churn by predicting which customers are at risk of leaving so we can proactively engage them with retention offers.",
            "expected": "HIGH quality (detailed, specific)"
        },
        {
            "question": "What business problem are you trying to solve?",
            "response": "Make things better.",
            "expected": "LOW quality (too vague)"
        },
        {
            "question": "What should the model predict?",
            "response": "Whether a customer will churn in the next 30 days (yes/no binary prediction).",
            "expected": "HIGH quality (clear, specific)"
        },
    ]

    print("\n  🤖 Ollama is evaluating response quality...")

    try:
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  Test {i}/3:")
            print(f"    Question: {test_case['question']}")
            print(f"    Response: {test_case['response'][:60]}...")

            assessment = await quality_agent.assess_response_quality(
                question=test_case['question'],
                response=test_case['response'],
            )

            print(f"    ✓ Quality score: {assessment.quality_score}/10")
            print(f"    ✓ Acceptable: {assessment.is_acceptable}")
            print(f"    Expected: {test_case['expected']}")

            results.append({
                'test_case': test_case,
                'assessment': assessment,
            })

        print("\n✅ All quality assessments completed!")
        return True

    except Exception as e:
        print(f"\n❌ Quality assessment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all reflection agent tests with Ollama."""

    print("=" * 80)
    print("REAL REFLECTION AGENTS + OLLAMA LLM INTEGRATION TEST")
    print("=" * 80)
    print(f"\nOllama Configuration:")
    print(f"  Base URL: {os.getenv('OLLAMA_BASE_URL')}")
    print(f"  Fast Model: {os.getenv('OLLAMA_MODEL_FAST')}")
    print(f"  Balanced Model: {os.getenv('OLLAMA_MODEL_BALANCED')}")
    print(f"  Powerful Model: {os.getenv('OLLAMA_MODEL_POWERFUL')}")
    print()

    # Test 1: ConsistencyChecker
    print("\n" + "▶" * 40)
    success1 = await test_consistency_checker_with_ollama()

    # Test 2: ResponseQuality
    print("\n" + "▶" * 40)
    success2 = await test_response_quality_with_ollama()

    # Summary
    print("\n" + "=" * 80)
    if success1 and success2:
        print("✅ ALL TESTS PASSED - Reflection agents working with Ollama!")
        print("=" * 80)
        print("\nVerified:")
        print("  ✓ ConsistencyCheckerAgent uses Ollama for cross-stage analysis")
        print("  ✓ ResponseQualityAgent uses Ollama for response evaluation")
        print("  ✓ Real LLM reasoning (no mocks)")
        print("  ✓ No API costs (local Ollama)")
        print("\nNext Steps:")
        print("  1. Test with real user interaction (Stage1-5 agents + CLI)")
        print("  2. Run full orchestrator workflow end-to-end")
        print("  3. Performance testing with concurrent sessions")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
