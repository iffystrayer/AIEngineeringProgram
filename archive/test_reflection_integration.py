#!/usr/bin/env python3
"""
Test script for demonstrating reflection agent integration in Orchestrator.

This script demonstrates:
1. ResponseQualityAgent - Evaluating user response quality
2. StageGateValidatorAgent - Validating stage completion
3. ConsistencyCheckerAgent - Cross-stage consistency validation

All integrated through the Orchestrator.
"""

import asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.orchestrator import Orchestrator
from src.models.schemas import Session, SessionStatus
from src.llm.router import LLMRouter
from src.llm.config import LLMConfig


async def main():
    """Demonstrate reflection agent integration."""
    print("=" * 80)
    print("REFLECTION AGENT INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print()

    # Initialize LLM configuration
    print("🔧 Initializing LLM Router...")
    llm_config = LLMConfig()
    llm_router = LLMRouter(config=llm_config)
    print("   ✓ LLM Router initialized")
    print()

    # Initialize Orchestrator with reflection agents
    print("🤖 Initializing Orchestrator with Reflection Agents...")
    orchestrator = Orchestrator(
        db_pool=None,  # No database for this demo
        llm_router=llm_router
    )
    print("   ✓ Orchestrator initialized")
    print("   ✓ ResponseQualityAgent initialized")
    print("   ✓ StageGateValidatorAgent initialized")
    print("   ✓ ConsistencyCheckerAgent initialized")
    print()

    # Create mock session
    print("📝 Creating mock session...")
    session = Session(
        session_id=uuid4(),
        user_id="test_user",
        project_name="Customer Churn Prediction",
        started_at=datetime.now(timezone.utc),
        last_updated_at=datetime.now(timezone.utc),
        current_stage=1,
        stage_data={},
        conversation_history=[],
        status=SessionStatus.IN_PROGRESS,
        checkpoints=[]
    )
    print(f"   ✓ Session created: {session.session_id}")
    print()

    # ==========================================================================
    # DEMONSTRATION 1: ResponseQualityAgent
    # ==========================================================================
    print("=" * 80)
    print("DEMONSTRATION 1: ResponseQualityAgent")
    print("=" * 80)
    print()

    # Test with poor response
    print("📊 Testing poor quality response...")
    question1 = "What is the main business objective for this AI project?"
    poor_response = "Improve stuff"

    print(f"Question: {question1}")
    print(f"Response: {poor_response}")
    print()

    assessment1 = await orchestrator.invoke_quality_agent(
        question=question1,
        response=poor_response,
        session=session
    )

    print("Assessment Results:")
    print(f"  Quality Score: {assessment1.quality_score}/10")
    print(f"  Acceptable: {assessment1.is_acceptable}")
    if assessment1.issues:
        print(f"  Issues: {', '.join(assessment1.issues)}")
    if assessment1.suggested_followups:
        print(f"  Follow-ups: {assessment1.suggested_followups[0]}")
    print()

    # Test with good response
    print("📊 Testing good quality response...")
    question2 = "What is the main business objective for this AI project?"
    good_response = """Reduce customer churn from the current baseline of 15% to 10%
    within 6 months. We'll achieve this by identifying at-risk customers 30 days
    before predicted churn and enabling targeted retention campaigns."""

    print(f"Question: {question2}")
    print(f"Response: {good_response[:100]}...")
    print()

    assessment2 = await orchestrator.invoke_quality_agent(
        question=question2,
        response=good_response,
        session=session
    )

    print("Assessment Results:")
    print(f"  Quality Score: {assessment2.quality_score}/10")
    print(f"  Acceptable: {assessment2.is_acceptable}")
    print()

    # ==========================================================================
    # DEMONSTRATION 2: StageGateValidatorAgent
    # ==========================================================================
    print("=" * 80)
    print("DEMONSTRATION 2: StageGateValidatorAgent")
    print("=" * 80)
    print()

    # Test with incomplete stage data
    print("🚪 Testing incomplete Stage 1 data...")
    session.stage_data[1] = {
        "business_objective": "Reduce customer churn"
        # Missing: ai_necessity_justification, input_features, target_output, ml_archetype
    }

    validation1 = await orchestrator.invoke_stage_gate_validator(
        session=session,
        stage_number=1
    )

    print("Validation Results:")
    print(f"  Can Proceed: {validation1.can_proceed}")
    print(f"  Completeness: {validation1.completeness_score:.1%}")
    if validation1.missing_items:
        print(f"  Missing Items: {len(validation1.missing_items)}")
        for item in validation1.missing_items[:3]:
            print(f"    - {item}")
    print()

    # Test with complete stage data
    print("🚪 Testing complete Stage 1 data...")
    session.stage_data[1] = {
        "business_objective": "Reduce customer churn from 15% to 10%",
        "ai_necessity_justification": "Pattern too complex for rules-based system",
        "input_features": [
            {"name": "customer_lifetime_value", "data_type": "float"},
            {"name": "last_interaction_date", "data_type": "datetime"}
        ],
        "target_output": {"name": "churn_probability", "type": "continuous"},
        "ml_archetype": "CLASSIFICATION",
        "ml_archetype_justification": "Predicting binary outcome (churn/no churn)"
    }

    validation2 = await orchestrator.invoke_stage_gate_validator(
        session=session,
        stage_number=1
    )

    print("Validation Results:")
    print(f"  Can Proceed: {validation2.can_proceed}")
    print(f"  Completeness: {validation2.completeness_score:.1%}")
    print()

    # ==========================================================================
    # DEMONSTRATION 3: ConsistencyCheckerAgent
    # ==========================================================================
    print("=" * 80)
    print("DEMONSTRATION 3: ConsistencyCheckerAgent")
    print("=" * 80)
    print()

    # Add Stage 2 data with intentional inconsistency
    print("🔍 Testing cross-stage consistency with intentional mismatch...")
    session.stage_data[2] = {
        "business_kpis": [
            {
                "name": "Revenue Growth",  # MISMATCH: doesn't solve churn problem
                "current_baseline": 1000000,
                "target_value": 1500000,
                "target_timeframe": "12 months"
            }
        ],
        "model_metrics": [{"name": "Accuracy", "target_threshold": 0.85}],
        "causal_pathways": []
    }

    print("Stage 1: Reduce customer churn")
    print("Stage 2: KPI = Revenue Growth (inconsistent)")
    print()

    consistency_report = await orchestrator.invoke_consistency_checker(session)

    print("Consistency Report:")
    print(f"  Is Consistent: {consistency_report.is_consistent}")
    print(f"  Overall Feasibility: {consistency_report.overall_feasibility.value}")
    if consistency_report.contradictions:
        print(f"  Contradictions: {len(consistency_report.contradictions)}")
        for contradiction in consistency_report.contradictions:
            print(f"    - Stage {contradiction.stage_from} → {contradiction.stage_to}")
            print(f"      {contradiction.description}")
    print()

    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    print("=" * 80)
    print("INTEGRATION DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("✅ All 3 reflection agents successfully integrated:")
    print("   1. ResponseQualityAgent - Evaluated response quality")
    print("   2. StageGateValidatorAgent - Validated stage completion")
    print("   3. ConsistencyCheckerAgent - Checked cross-stage consistency")
    print()
    print("🚀 Ready for CLI conversation workflow implementation!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
