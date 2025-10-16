"""
End-to-End Integration Test: Complete 5-Stage Workflow

Tests the complete workflow from session creation through charter generation,
validating that all stage agents integrate correctly with the orchestrator.

Following TDD methodology:
- Tests the critical path for the entire system
- Validates data flow between all stages
- Ensures charter generation works with real stage data
"""

import sys
from pathlib import Path
from uuid import uuid4

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.orchestrator import Orchestrator
from src.models.schemas import (
    AIProjectCharter,
    DataQualityScorecard,
    EthicalRiskReport,
    GovernanceDecision,
    MetricAlignmentMatrix,
    ProblemStatement,
    SessionStatus,
    UserContext,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_db_pool():
    """Mock database connection pool."""
    from unittest.mock import AsyncMock, MagicMock

    pool = MagicMock()
    # Make acquire() return an async context manager
    pool.acquire = MagicMock(return_value=AsyncMock())
    return pool


@pytest.fixture
def mock_llm_router():
    """Mock LLM router for agent communication."""
    from unittest.mock import AsyncMock, MagicMock

    router = MagicMock()
    # LLM responses for each stage
    router.route = AsyncMock(
        return_value={
            "response": "Mock LLM response with comprehensive details and context"
        }
    )
    return router


@pytest.fixture
async def orchestrator_instance(mock_db_pool, mock_llm_router):
    """Create Orchestrator instance for testing."""
    return Orchestrator(db_pool=mock_db_pool, llm_router=mock_llm_router)


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================


class TestEndToEndWorkflow:
    """Tests for complete 5-stage workflow execution."""

    @pytest.mark.asyncio
    async def test_complete_workflow_session_to_charter(self, orchestrator_instance):
        """
        Test complete workflow from session creation to charter generation.

        Workflow:
        1. Create session
        2. Execute Stage 1 (Business Translation) → ProblemStatement
        3. Execute Stage 2 (Value Quantification) → MetricAlignmentMatrix
        4. Execute Stage 3 (Data Feasibility) → DataQualityScorecard
        5. Execute Stage 4 (User Experience) → UserContext
        6. Execute Stage 5 (Ethical Governance) → EthicalRiskReport
        7. Generate AI Project Charter

        This is the critical path test that validates the entire system works.
        """
        # Step 1: Create session
        session = await orchestrator_instance.create_session(
            user_id="test_user_123", project_name="E2E Test Project"
        )

        assert session is not None
        assert session.session_id is not None
        assert session.user_id == "test_user_123"
        assert session.project_name == "E2E Test Project"
        assert session.current_stage == 1
        assert session.status == SessionStatus.IN_PROGRESS
        assert len(session.stage_data) == 0

        # Step 2: Execute Stage 1
        stage1_output = await orchestrator_instance.run_stage(session, 1)

        assert stage1_output is not None
        assert isinstance(stage1_output, ProblemStatement)
        assert stage1_output.business_objective is not None
        assert stage1_output.ml_archetype is not None
        assert len(stage1_output.input_features) > 0
        assert session.stage_data[1] == stage1_output

        # Advance to Stage 2
        await orchestrator_instance.advance_to_next_stage(session)
        assert session.current_stage == 2
        assert len(session.checkpoints) == 1

        # Step 3: Execute Stage 2
        stage2_output = await orchestrator_instance.run_stage(session, 2)

        assert stage2_output is not None
        assert isinstance(stage2_output, MetricAlignmentMatrix)
        assert len(stage2_output.business_kpis) > 0
        assert len(stage2_output.model_metrics) > 0
        assert len(stage2_output.causal_pathways) > 0
        assert session.stage_data[2] == stage2_output

        # Advance to Stage 3
        await orchestrator_instance.advance_to_next_stage(session)
        assert session.current_stage == 3
        assert len(session.checkpoints) == 2

        # Step 4: Execute Stage 3
        stage3_output = await orchestrator_instance.run_stage(session, 3)

        assert stage3_output is not None
        assert isinstance(stage3_output, DataQualityScorecard)
        assert len(stage3_output.data_sources) > 0
        assert len(stage3_output.quality_scores) > 0
        assert session.stage_data[3] == stage3_output

        # Advance to Stage 4
        await orchestrator_instance.advance_to_next_stage(session)
        assert session.current_stage == 4
        assert len(session.checkpoints) == 3

        # Step 5: Execute Stage 4
        stage4_output = await orchestrator_instance.run_stage(session, 4)

        assert stage4_output is not None
        assert isinstance(stage4_output, UserContext)
        assert len(stage4_output.user_personas) > 0
        assert stage4_output.user_journey_map is not None
        assert stage4_output.interpretability_needs is not None
        assert session.stage_data[4] == stage4_output

        # Advance to Stage 5
        await orchestrator_instance.advance_to_next_stage(session)
        assert session.current_stage == 5
        assert len(session.checkpoints) == 4

        # Step 6: Execute Stage 5
        stage5_output = await orchestrator_instance.run_stage(session, 5)

        assert stage5_output is not None
        assert isinstance(stage5_output, EthicalRiskReport)
        assert len(stage5_output.initial_risks) > 0
        assert stage5_output.governance_decision is not None
        assert session.stage_data[5] == stage5_output

        # Advance to completion
        await orchestrator_instance.advance_to_next_stage(session)
        assert session.current_stage == 6
        assert session.status == SessionStatus.COMPLETED
        assert len(session.checkpoints) == 5

        # Step 7: Generate Charter
        charter = await orchestrator_instance.generate_charter(session)

        assert charter is not None
        assert isinstance(charter, AIProjectCharter)
        assert charter.session_id == session.session_id
        assert charter.project_name == "E2E Test Project"
        assert charter.problem_statement == stage1_output
        assert charter.metric_alignment_matrix == stage2_output
        assert charter.data_quality_scorecard == stage3_output
        assert charter.user_context == stage4_output
        assert charter.ethical_risk_report == stage5_output
        assert charter.governance_decision is not None
        assert charter.overall_feasibility is not None
        assert len(charter.critical_success_factors) > 0
        assert len(charter.major_risks) > 0

    @pytest.mark.asyncio
    async def test_stage_progression_validation(self, orchestrator_instance):
        """Test that stages cannot be skipped."""
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="Test Project"
        )

        # Attempt to skip to Stage 3 without completing Stage 1
        with pytest.raises(ValueError, match="Cannot skip to stage"):
            await orchestrator_instance.run_stage(session, 3)

    @pytest.mark.asyncio
    async def test_checkpoint_recovery(self, orchestrator_instance):
        """Test that session can be recovered from checkpoint."""
        # Create and execute Stage 1
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="Checkpoint Test"
        )
        await orchestrator_instance.run_stage(session, 1)
        await orchestrator_instance.advance_to_next_stage(session)

        # Verify checkpoint was created
        assert len(session.checkpoints) == 1
        checkpoint = session.checkpoints[0]
        assert checkpoint.stage_number == 1
        assert checkpoint.validation_status is True
        assert "stage_data" in checkpoint.data_snapshot
        assert checkpoint.data_snapshot["current_stage"] == 2

    @pytest.mark.asyncio
    async def test_session_state_preservation(self, orchestrator_instance):
        """Test that session state is preserved across stages."""
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="State Test"
        )

        # Execute Stage 1
        stage1_output = await orchestrator_instance.run_stage(session, 1)
        await orchestrator_instance.advance_to_next_stage(session)

        # Execute Stage 2
        stage2_output = await orchestrator_instance.run_stage(session, 2)

        # Verify Stage 1 data is still in session
        assert session.stage_data[1] == stage1_output
        assert session.stage_data[2] == stage2_output

    @pytest.mark.asyncio
    async def test_governance_decision_impacts_feasibility(self, orchestrator_instance):
        """Test that governance decision correctly determines overall feasibility."""
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="Governance Test"
        )

        # Execute all stages
        for stage in range(1, 6):
            await orchestrator_instance.run_stage(session, stage)
            await orchestrator_instance.advance_to_next_stage(session)

        # Generate charter
        charter = await orchestrator_instance.generate_charter(session)

        # Verify governance decision affects feasibility
        ethical_report: EthicalRiskReport = session.stage_data[5]
        governance_decision = ethical_report.governance_decision

        # Check mapping is correct
        if governance_decision == GovernanceDecision.HALT:
            from src.models.schemas import FeasibilityLevel

            assert charter.overall_feasibility == FeasibilityLevel.NOT_FEASIBLE
        elif governance_decision == GovernanceDecision.PROCEED:
            from src.models.schemas import FeasibilityLevel

            assert charter.overall_feasibility == FeasibilityLevel.HIGH

    @pytest.mark.asyncio
    async def test_charter_contains_extracted_data(self, orchestrator_instance):
        """Test that charter correctly extracts data from all stages."""
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="Charter Data Test"
        )

        # Execute all stages
        for stage in range(1, 6):
            await orchestrator_instance.run_stage(session, stage)
            await orchestrator_instance.advance_to_next_stage(session)

        # Generate charter
        charter = await orchestrator_instance.generate_charter(session)

        # Verify critical success factors extracted from Stage 2
        metric_alignment: MetricAlignmentMatrix = session.stage_data[2]
        assert len(charter.critical_success_factors) == len(
            metric_alignment.business_kpis
        )

        # Verify each KPI appears in critical success factors
        for kpi in metric_alignment.business_kpis:
            assert any(kpi.name in csf for csf in charter.critical_success_factors)

        # Verify major risks extracted from Stage 5
        ethical_report: EthicalRiskReport = session.stage_data[5]
        # Count total risks across all principles
        total_risks = sum(len(risks) for risks in ethical_report.initial_risks.values())
        assert len(charter.major_risks) == total_risks

        # Verify each ethical principle appears in major risks
        for principle in ethical_report.initial_risks.keys():
            assert any(principle.value in mr for mr in charter.major_risks)

    @pytest.mark.asyncio
    async def test_stage_data_types(self, orchestrator_instance):
        """Test that each stage returns the correct deliverable type."""
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="Type Test"
        )

        # Stage 1 → ProblemStatement
        stage1_output = await orchestrator_instance.run_stage(session, 1)
        assert isinstance(stage1_output, ProblemStatement)
        await orchestrator_instance.advance_to_next_stage(session)

        # Stage 2 → MetricAlignmentMatrix
        stage2_output = await orchestrator_instance.run_stage(session, 2)
        assert isinstance(stage2_output, MetricAlignmentMatrix)
        await orchestrator_instance.advance_to_next_stage(session)

        # Stage 3 → DataQualityScorecard
        stage3_output = await orchestrator_instance.run_stage(session, 3)
        assert isinstance(stage3_output, DataQualityScorecard)
        await orchestrator_instance.advance_to_next_stage(session)

        # Stage 4 → UserContext
        stage4_output = await orchestrator_instance.run_stage(session, 4)
        assert isinstance(stage4_output, UserContext)
        await orchestrator_instance.advance_to_next_stage(session)

        # Stage 5 → EthicalRiskReport
        stage5_output = await orchestrator_instance.run_stage(session, 5)
        assert isinstance(stage5_output, EthicalRiskReport)

    @pytest.mark.asyncio
    async def test_charter_generation_requires_completion(self, orchestrator_instance):
        """Test that charter generation requires all stages to be completed."""
        session = await orchestrator_instance.create_session(
            user_id="test_user", project_name="Incomplete Test"
        )

        # Try to generate charter without completing any stages
        with pytest.raises(ValueError, match="Session must be completed"):
            await orchestrator_instance.generate_charter(session)

        # Execute only Stages 1-3
        for stage in range(1, 4):
            await orchestrator_instance.run_stage(session, stage)
            await orchestrator_instance.advance_to_next_stage(session)

        # Try to generate charter with incomplete stages
        # Note: Session status is still IN_PROGRESS, so it will fail the status check first
        with pytest.raises(ValueError, match="Session must be completed"):
            await orchestrator_instance.generate_charter(session)


# ============================================================================
# SESSION LIFECYCLE TESTS
# ============================================================================


class TestSessionLifecycle:
    """Tests for session management and lifecycle."""

    @pytest.mark.asyncio
    async def test_create_session_initializes_correctly(self, orchestrator_instance):
        """Test that create_session initializes all fields correctly."""
        session = await orchestrator_instance.create_session(
            user_id="user123", project_name="Test Project"
        )

        assert session.user_id == "user123"
        assert session.project_name == "Test Project"
        assert session.current_stage == 1
        assert session.status == SessionStatus.IN_PROGRESS
        assert len(session.stage_data) == 0
        assert len(session.conversation_history) == 0
        assert len(session.checkpoints) == 0
        assert session.started_at is not None
        assert session.last_updated_at is not None

    @pytest.mark.asyncio
    async def test_resume_session_retrieves_active_session(self, orchestrator_instance):
        """Test that resume_session retrieves active session."""
        # Create session
        session = await orchestrator_instance.create_session(
            user_id="user123", project_name="Test Project"
        )

        session_id = session.session_id

        # Resume session
        resumed_session = await orchestrator_instance.resume_session(session_id)

        assert resumed_session.session_id == session_id
        assert resumed_session.user_id == "user123"
        assert resumed_session.project_name == "Test Project"

    @pytest.mark.asyncio
    async def test_get_session_state_returns_current_state(self, orchestrator_instance):
        """Test that get_session_state returns current session state."""
        session = await orchestrator_instance.create_session(
            user_id="user123", project_name="Test Project"
        )

        # Execute Stage 1
        await orchestrator_instance.run_stage(session, 1)
        await orchestrator_instance.advance_to_next_stage(session)

        # Get session state
        current_state = await orchestrator_instance.get_session_state(session.session_id)

        assert current_state.current_stage == 2
        assert 1 in current_state.stage_data
        assert len(current_state.checkpoints) == 1


# ============================================================================
# STAGE AGENT INTEGRATION TESTS
# ============================================================================


class TestStageAgentIntegration:
    """Tests for stage agent integration with orchestrator."""

    @pytest.mark.asyncio
    async def test_stage1_agent_integration(self, orchestrator_instance):
        """Test Stage 1 (Business Translation) integration."""
        session = await orchestrator_instance.create_session(
            user_id="test", project_name="Stage 1 Test"
        )

        output = await orchestrator_instance.run_stage(session, 1)

        assert isinstance(output, ProblemStatement)
        assert output.business_objective is not None
        assert output.ml_archetype is not None
        assert len(output.input_features) > 0

    @pytest.mark.asyncio
    async def test_stage2_agent_integration(self, orchestrator_instance):
        """Test Stage 2 (Value Quantification) integration."""
        session = await orchestrator_instance.create_session(
            user_id="test", project_name="Stage 2 Test"
        )

        # Execute Stage 1 first (required)
        await orchestrator_instance.run_stage(session, 1)
        await orchestrator_instance.advance_to_next_stage(session)

        # Execute Stage 2
        output = await orchestrator_instance.run_stage(session, 2)

        assert isinstance(output, MetricAlignmentMatrix)
        assert len(output.business_kpis) > 0
        assert len(output.model_metrics) > 0

    @pytest.mark.asyncio
    async def test_stage3_agent_integration(self, orchestrator_instance):
        """Test Stage 3 (Data Feasibility) integration."""
        session = await orchestrator_instance.create_session(
            user_id="test", project_name="Stage 3 Test"
        )

        # Execute Stages 1-2 first
        await orchestrator_instance.run_stage(session, 1)
        await orchestrator_instance.advance_to_next_stage(session)
        await orchestrator_instance.run_stage(session, 2)
        await orchestrator_instance.advance_to_next_stage(session)

        # Execute Stage 3
        output = await orchestrator_instance.run_stage(session, 3)

        assert isinstance(output, DataQualityScorecard)
        assert len(output.data_sources) > 0
        assert len(output.quality_scores) > 0

    @pytest.mark.asyncio
    async def test_stage4_agent_integration(self, orchestrator_instance):
        """Test Stage 4 (User Experience) integration."""
        session = await orchestrator_instance.create_session(
            user_id="test", project_name="Stage 4 Test"
        )

        # Execute Stages 1-3 first
        for stage in range(1, 4):
            await orchestrator_instance.run_stage(session, stage)
            await orchestrator_instance.advance_to_next_stage(session)

        # Execute Stage 4
        output = await orchestrator_instance.run_stage(session, 4)

        assert isinstance(output, UserContext)
        assert len(output.user_personas) > 0
        assert output.interpretability_needs is not None

    @pytest.mark.asyncio
    async def test_stage5_agent_integration(self, orchestrator_instance):
        """Test Stage 5 (Ethical Governance) integration."""
        session = await orchestrator_instance.create_session(
            user_id="test", project_name="Stage 5 Test"
        )

        # Execute Stages 1-4 first
        for stage in range(1, 5):
            await orchestrator_instance.run_stage(session, stage)
            await orchestrator_instance.advance_to_next_stage(session)

        # Execute Stage 5
        output = await orchestrator_instance.run_stage(session, 5)

        assert isinstance(output, EthicalRiskReport)
        assert len(output.initial_risks) > 0
        assert output.governance_decision is not None
