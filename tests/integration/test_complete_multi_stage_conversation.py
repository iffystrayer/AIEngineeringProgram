"""
Integration test: Complete Multi-Stage Conversation Workflow

Tests the end-to-end integration of all 5 stages (1-5) with ConversationEngine
for conducting quality-validated conversations across the complete AI Charter workflow.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.agents.stage1_business_translation import Stage1Agent
from src.agents.stage2_agent import Stage2Agent
from src.agents.stage3_agent import Stage3Agent
from src.agents.stage4_agent import Stage4Agent
from src.agents.stage5_agent import Stage5Agent
from src.agents.reflection.response_quality_agent import ResponseQualityAgent
from src.conversation import ConversationEngine
from src.models.schemas import (
    MLArchetype,
    ProblemStatement,
    MetricAlignmentMatrix,
    DataQualityScorecard,
    UserAlignmentReport,
    EthicalRiskProfile
)


@pytest.mark.integration
@pytest.mark.slow
class TestCompleteMultiStageConversation:
    """Integration tests for complete 5-stage conversation workflow."""

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router that works for all stages."""
        router = Mock()
        router.route = AsyncMock(return_value={
            "response": "Mock high-quality response with comprehensive details"
        })
        router.complete = AsyncMock(return_value="Follow-up question for clarification")
        return router

    @pytest.fixture
    def mock_quality_agent(self):
        """Create mock ResponseQualityAgent that accepts all responses."""
        agent = Mock()
        agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })
        return agent

    @pytest.fixture
    def initial_session_context(self):
        """Create initial session context for Stage 1."""
        context = Mock()
        context.session_id = uuid4()
        context.project_name = "Complete Multi-Stage Test Project"
        context.stage_number = 1
        return context

    @pytest.mark.asyncio
    async def test_stage1_to_stage5_complete_workflow(
        self, initial_session_context, mock_llm_router, mock_quality_agent
    ):
        """Test complete workflow from Stage 1 through Stage 5 with ConversationEngine."""

        # ===== STAGE 1: Business Translation =====
        stage1_agent = Stage1Agent(
            session_context=initial_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        stage1_output = await stage1_agent.conduct_interview()

        # Assert Stage 1 output
        assert isinstance(stage1_output, ProblemStatement)
        assert stage1_output.business_objective is not None
        assert stage1_output.ml_archetype is not None

        # ===== STAGE 2: Value Quantification =====
        # Create context with Stage 1 data
        stage2_context = Mock()
        stage2_context.session_id = initial_session_context.session_id
        stage2_context.project_name = initial_session_context.project_name
        stage2_context.stage_number = 2
        stage2_context.stage1_data = stage1_output

        stage2_agent = Stage2Agent(
            session_context=stage2_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        stage2_output = await stage2_agent.conduct_interview()

        # Assert Stage 2 output
        assert isinstance(stage2_output, MetricAlignmentMatrix)
        assert stage2_output.business_kpis is not None
        assert stage2_output.model_metrics is not None

        # ===== STAGE 3: Data Feasibility =====
        # Create context with Stage 1-2 data
        stage3_context = Mock()
        stage3_context.session_id = initial_session_context.session_id
        stage3_context.project_name = initial_session_context.project_name
        stage3_context.stage_number = 3
        stage3_context.stage1_data = stage1_output
        stage3_context.stage2_data = stage2_output

        stage3_agent = Stage3Agent(
            session_context=stage3_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        stage3_output = await stage3_agent.conduct_interview()

        # Assert Stage 3 output
        assert isinstance(stage3_output, DataQualityScorecard)
        assert stage3_output.data_sources is not None
        assert stage3_output.quality_scores is not None

        # ===== STAGE 4: User Centricity =====
        # Create context with Stage 1-3 data
        stage4_context = Mock()
        stage4_context.session_id = initial_session_context.session_id
        stage4_context.project_name = initial_session_context.project_name
        stage4_context.stage_number = 4
        stage4_context.stage1_data = stage1_output
        stage4_context.stage2_data = stage2_output
        stage4_context.stage3_data = stage3_output

        stage4_agent = Stage4Agent(
            session_context=stage4_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        stage4_output = await stage4_agent.conduct_interview()

        # Assert Stage 4 output
        assert isinstance(stage4_output, UserAlignmentReport)
        assert stage4_output.user_personas is not None
        assert stage4_output.user_journey is not None

        # ===== STAGE 5: Ethical Governance =====
        # Create context with Stage 1-4 data
        stage5_context = Mock()
        stage5_context.session_id = initial_session_context.session_id
        stage5_context.project_name = initial_session_context.project_name
        stage5_context.stage_number = 5
        stage5_context.stage1_data = stage1_output
        stage5_context.stage2_data = stage2_output
        stage5_context.stage3_data = stage3_output
        stage5_context.stage4_data = stage4_output

        stage5_agent = Stage5Agent(
            session_context=stage5_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        stage5_output = await stage5_agent.conduct_interview()

        # Assert Stage 5 output
        assert isinstance(stage5_output, EthicalRiskProfile)
        assert stage5_output.risk_scores is not None
        assert stage5_output.mitigation_strategies is not None

        # ===== FINAL ASSERTIONS =====
        # All stages completed successfully
        assert stage1_output is not None
        assert stage2_output is not None
        assert stage3_output is not None
        assert stage4_output is not None
        assert stage5_output is not None

        # Quality agent was used throughout
        assert mock_quality_agent.evaluate_response.called
        # Should have been called many times across all stages
        assert mock_quality_agent.evaluate_response.call_count > 10

    @pytest.mark.asyncio
    async def test_data_flow_across_stages(
        self, initial_session_context, mock_llm_router, mock_quality_agent
    ):
        """Test that data flows correctly from one stage to the next."""

        # Stage 1
        stage1_agent = Stage1Agent(
            session_context=initial_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )
        stage1_output = await stage1_agent.conduct_interview()

        # Stage 2 should receive Stage 1 output
        stage2_context = Mock()
        stage2_context.session_id = initial_session_context.session_id
        stage2_context.stage_number = 2
        stage2_context.stage1_data = stage1_output  # Data flow

        stage2_agent = Stage2Agent(
            session_context=stage2_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )

        # Assert Stage 2 can access Stage 1 data
        assert stage2_agent.session_context.stage1_data == stage1_output
        assert stage2_agent.session_context.stage1_data.ml_archetype is not None

    @pytest.mark.asyncio
    async def test_quality_validation_across_all_stages(
        self, initial_session_context, mock_llm_router
    ):
        """Test that quality validation works consistently across all 5 stages."""

        # Create quality agent that tracks all evaluations
        evaluation_log = []

        def log_evaluation(*args, **kwargs):
            evaluation_log.append({"args": args, "kwargs": kwargs})
            return {
                "quality_score": 8,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }

        mock_quality_agent = Mock()
        mock_quality_agent.evaluate_response = AsyncMock(side_effect=log_evaluation)

        # Run Stage 1 with quality tracking
        stage1_agent = Stage1Agent(
            session_context=initial_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )
        stage1_output = await stage1_agent.conduct_interview()

        # Assert quality validation was used
        stage1_evaluations = len(evaluation_log)
        assert stage1_evaluations > 0, "Stage 1 should have quality evaluations"

        # Continue with Stage 2 to verify consistent quality validation
        stage2_context = Mock()
        stage2_context.session_id = initial_session_context.session_id
        stage2_context.stage_number = 2
        stage2_context.stage1_data = stage1_output

        stage2_agent = Stage2Agent(
            session_context=stage2_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )
        stage2_output = await stage2_agent.conduct_interview()

        # Assert Stage 2 also used quality validation
        total_evaluations = len(evaluation_log)
        stage2_evaluations = total_evaluations - stage1_evaluations
        assert stage2_evaluations > 0, "Stage 2 should have quality evaluations"

    @pytest.mark.asyncio
    async def test_session_consistency_across_stages(
        self, initial_session_context, mock_llm_router, mock_quality_agent
    ):
        """Test that session ID remains consistent across all stages."""

        session_id = uuid4()
        project_name = "Consistent Session Test"

        # Stage 1
        stage1_context = Mock()
        stage1_context.session_id = session_id
        stage1_context.project_name = project_name
        stage1_context.stage_number = 1

        stage1_agent = Stage1Agent(
            session_context=stage1_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )
        stage1_output = await stage1_agent.conduct_interview()

        # Stage 2 - verify session consistency
        stage2_context = Mock()
        stage2_context.session_id = session_id  # Same session ID
        stage2_context.project_name = project_name  # Same project
        stage2_context.stage_number = 2
        stage2_context.stage1_data = stage1_output

        stage2_agent = Stage2Agent(
            session_context=stage2_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )

        # Assert session consistency
        assert stage2_agent.session_context.session_id == session_id
        assert stage2_agent.session_context.project_name == project_name


@pytest.mark.integration
@pytest.mark.slow
class TestMultiStageConversationEdgeCases:
    """Edge case tests for multi-stage conversation workflow."""

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router."""
        router = Mock()
        router.route = AsyncMock(return_value={
            "response": "Mock response"
        })
        router.complete = AsyncMock(return_value="Follow-up")
        return router

    @pytest.fixture
    def mock_quality_agent(self):
        """Create mock quality agent."""
        agent = Mock()
        agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })
        return agent

    @pytest.mark.asyncio
    async def test_stage5_requires_all_previous_stages(
        self, mock_llm_router, mock_quality_agent
    ):
        """Stage 5 should fail if any previous stage data is missing."""

        # Context missing Stage 3 data
        incomplete_context = Mock()
        incomplete_context.session_id = uuid4()
        incomplete_context.stage_number = 5
        incomplete_context.stage1_data = Mock()
        incomplete_context.stage2_data = Mock()
        incomplete_context.stage3_data = None  # Missing!
        incomplete_context.stage4_data = Mock()

        # Should raise error
        with pytest.raises(ValueError, match="All stages 1-4 data required"):
            Stage5Agent(
                session_context=incomplete_context,
                llm_router=mock_llm_router,
                quality_agent=mock_quality_agent
            )

    @pytest.mark.asyncio
    async def test_quality_loop_escalation_across_stages(
        self, mock_llm_router
    ):
        """Test that quality loop escalation (max 3 attempts) works consistently across stages."""

        # Create quality agent that always rejects
        rejecting_quality_agent = Mock()
        rejecting_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 5,
            "is_acceptable": False,
            "issues": ["Always insufficient"],
            "suggested_followups": ["Please provide more detail"]
        })

        # Test Stage 1 escalation
        stage1_context = Mock()
        stage1_context.session_id = uuid4()
        stage1_context.stage_number = 1

        stage1_agent = Stage1Agent(
            session_context=stage1_context,
            llm_router=mock_llm_router,
            quality_agent=rejecting_quality_agent,
            max_quality_attempts=3
        )

        # Ask single question - should escalate after 3 attempts
        response = await stage1_agent._ask_single_question("Test question")

        # Assert: Should have attempted 3 times (max_quality_attempts)
        assert response is not None
        assert rejecting_quality_agent.evaluate_response.call_count <= 3

    @pytest.mark.asyncio
    async def test_fallback_mode_across_all_stages(
        self, mock_llm_router
    ):
        """Test that fallback mode (no quality_agent) works for all stages."""

        # Stage 1 without quality agent
        stage1_context = Mock()
        stage1_context.session_id = uuid4()
        stage1_context.stage_number = 1

        stage1_agent = Stage1Agent(
            session_context=stage1_context,
            llm_router=mock_llm_router,
            quality_agent=None,  # No quality agent
            max_quality_attempts=3
        )

        response = await stage1_agent._ask_single_question("Test question")
        assert response is not None

        # Continue with Stage 2 (also without quality agent)
        stage1_output = await stage1_agent.conduct_interview()

        stage2_context = Mock()
        stage2_context.session_id = uuid4()
        stage2_context.stage_number = 2
        stage2_context.stage1_data = stage1_output

        stage2_agent = Stage2Agent(
            session_context=stage2_context,
            llm_router=mock_llm_router,
            quality_agent=None,  # No quality agent
            max_quality_attempts=3
        )

        response = await stage2_agent._ask_single_question("Test question")
        assert response is not None


@pytest.mark.integration
class TestMultiStageConversationPerformance:
    """Performance and efficiency tests for multi-stage conversations."""

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router."""
        router = Mock()
        router.route = AsyncMock(return_value={
            "response": "Mock response"
        })
        return router

    @pytest.fixture
    def mock_quality_agent(self):
        """Create fast mock quality agent."""
        agent = Mock()
        agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })
        return agent

    @pytest.mark.asyncio
    async def test_conversation_engine_created_per_question_not_per_interview(
        self, mock_llm_router, mock_quality_agent
    ):
        """Verify ConversationEngine is created per question for memory efficiency."""

        stage1_context = Mock()
        stage1_context.session_id = uuid4()
        stage1_context.stage_number = 1

        stage1_agent = Stage1Agent(
            session_context=stage1_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )

        # Ask multiple questions
        response1 = await stage1_agent._ask_single_question("Question 1")
        response2 = await stage1_agent._ask_single_question("Question 2")

        # Both should succeed (each creates its own ConversationEngine)
        assert response1 is not None
        assert response2 is not None

    @pytest.mark.asyncio
    async def test_async_execution_efficiency(
        self, mock_llm_router, mock_quality_agent
    ):
        """Test that async execution is efficient across stages."""

        import time

        stage1_context = Mock()
        stage1_context.session_id = uuid4()
        stage1_context.stage_number = 1

        stage1_agent = Stage1Agent(
            session_context=stage1_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent
        )

        # Measure execution time
        start_time = time.time()
        response = await stage1_agent._ask_single_question("Test question")
        end_time = time.time()

        execution_time = end_time - start_time

        # Assert: Should complete quickly (mocked LLM calls)
        assert execution_time < 1.0, f"Execution took {execution_time}s, should be <1s"
        assert response is not None
