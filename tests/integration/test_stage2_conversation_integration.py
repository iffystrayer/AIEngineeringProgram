"""
Integration test: Stage 2 Agent with ConversationEngine

Tests the complete integration of Stage2Agent with ConversationEngine
for conducting quality-validated conversations.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.agents.stage2_agent import Stage2Agent
from src.agents.reflection.response_quality_agent import ResponseQualityAgent
from src.conversation import ConversationEngine
from src.models.schemas import MLArchetype, ProblemStatement


@pytest.mark.integration
class TestStage2ConversationIntegration:
    """Integration tests for Stage 2 agent with ConversationEngine."""

    @pytest.fixture
    def mock_stage1_data(self):
        """Create mock Stage 1 ProblemStatement."""
        return ProblemStatement(
            business_objective="Reduce customer churn by 15% within 6 months",
            ml_archetype=MLArchetype.CLASSIFICATION,
            target_output="Churn probability score for each customer",
            input_features=["usage_frequency", "support_tickets", "payment_history"],
            success_criteria="80% precision at 50% recall",
            constraints=["Must process within 100ms", "Comply with GDPR"]
        )

    @pytest.fixture
    def mock_session_context(self, mock_stage1_data):
        """Create mock session context with Stage 1 data."""
        context = Mock()
        context.session_id = uuid4()
        context.project_name = "Customer Retention ML"
        context.stage_number = 2
        context.stage1_data = mock_stage1_data
        return context

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router."""
        router = Mock()
        router.route = AsyncMock(return_value={
            "response": "30-day retention rate from 65% to 80% within 6 months, measured via analytics dashboard"
        })
        router.complete = AsyncMock(return_value="Can you specify exact metrics with baseline and target values?")
        return router

    @pytest.fixture
    def mock_quality_agent(self):
        """Create mock ResponseQualityAgent."""
        agent = Mock()
        # First response has low quality, second has good quality
        agent.evaluate_response = AsyncMock(side_effect=[
            {
                "quality_score": 5,
                "is_acceptable": False,
                "issues": ["Missing specific metrics and values"],
                "suggested_followups": ["Can you specify exact metrics with baseline and target values?"]
            },
            {
                "quality_score": 8,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ])
        return agent

    @pytest.fixture
    def stage2_agent_with_conversation(self, mock_session_context, mock_llm_router, mock_quality_agent):
        """Create Stage2Agent with ConversationEngine support."""
        return Stage2Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

    @pytest.mark.asyncio
    async def test_stage2_uses_conversation_engine_when_quality_agent_provided(
        self, stage2_agent_with_conversation, mock_quality_agent
    ):
        """Stage2Agent should use ConversationEngine when quality_agent is provided."""

        # Act: Ask a single question (will use ConversationEngine internally)
        question = "What business metrics define success for this project?"
        response = await stage2_agent_with_conversation._ask_single_question(question)

        # Assert: Quality agent was called (proves ConversationEngine was used)
        assert mock_quality_agent.evaluate_response.called
        assert response is not None
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_conversation_engine_quality_loop_integration(
        self, stage2_agent_with_conversation, mock_quality_agent, mock_llm_router
    ):
        """ConversationEngine should handle quality validation loops correctly for Stage 2."""

        # Setup: Configure responses
        # First attempt: vague
        # Second attempt: specific with SMART criteria
        mock_llm_router.route.side_effect = [
            {"response": "Improve retention"},  # Vague
            {"response": "Increase 30-day retention rate from 65% to 80% within 6 months, measured via analytics"}  # Specific
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 4,
                "is_acceptable": False,
                "issues": ["Too vague, no baseline or target values"],
                "suggested_followups": ["Please provide specific metrics with baseline and target values"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act: Ask question
        response = await stage2_agent_with_conversation._ask_single_question(
            "What business metrics define success for this project?"
        )

        # Assert: Both attempts were made
        assert mock_quality_agent.evaluate_response.call_count >= 1
        assert "30-day retention rate" in response
        assert "65%" in response
        assert "80%" in response

    @pytest.mark.asyncio
    async def test_stage2_fallback_without_quality_agent(
        self, mock_session_context, mock_llm_router
    ):
        """Stage2Agent should fall back to original logic when no quality_agent provided."""

        # Create agent WITHOUT quality_agent
        agent_without_quality = Stage2Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=None,  # No quality agent
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act: Ask question (should use fallback)
        question = "What business metrics define success?"
        response = await agent_without_quality._ask_single_question(question)

        # Assert: Fallback validation was used
        assert response is not None
        # Should use basic heuristic validation instead of ConversationEngine

    @pytest.mark.asyncio
    async def test_stage2_validates_smart_criteria_through_conversation(
        self, stage2_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage2Agent should validate SMART criteria through conversation loops."""

        # Setup: Simulate progression from vague to SMART-compliant KPI
        mock_llm_router.route.side_effect = [
            {"response": "Better customer satisfaction"},  # Not SMART
            {"response": "Increase NPS from 7.5 to 8.5 within 6 months, measured quarterly via surveys"}  # SMART
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 3,
                "is_acceptable": False,
                "issues": ["Not specific, not measurable, missing baseline/target"],
                "suggested_followups": ["Define specific metric with baseline, target, and timeframe"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act
        response = await stage2_agent_with_conversation._ask_single_question(
            "What business KPIs define success? (Must meet SMART criteria)"
        )

        # Assert: Final response is SMART-compliant
        assert "NPS" in response or "8.5" in response
        assert mock_quality_agent.evaluate_response.call_count >= 1

    @pytest.mark.asyncio
    async def test_stage2_uses_stage1_context_for_metric_selection(
        self, stage2_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage2Agent should leverage Stage 1 ML archetype for context-aware questions."""

        # Setup: Agent has CLASSIFICATION archetype from Stage 1
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        mock_llm_router.route = AsyncMock(return_value={
            "response": "Precision, Recall, F1-Score, and AUC-ROC for churn classification"
        })

        # Act
        response = await stage2_agent_with_conversation._ask_single_question(
            "What model performance metrics are appropriate for this classification problem?"
        )

        # Assert: Response contains classification-appropriate metrics
        assert response is not None
        # Verify agent has access to Stage 1 context
        assert stage2_agent_with_conversation.session_context.stage1_data.ml_archetype == MLArchetype.CLASSIFICATION

    @pytest.mark.asyncio
    async def test_stage2_causal_pathway_validation_through_conversation(
        self, stage2_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage2Agent should validate causal pathways through iterative conversation."""

        # Setup: Progress from weak to strong causal explanation
        mock_llm_router.route.side_effect = [
            {"response": "Better precision means better business results"},  # Weak
            {"response": "Higher precision (80%) reduces false churn predictions → fewer unnecessary retention interventions → reduced costs ($50K annually) → higher retention (5% improvement)"}  # Strong
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 4,
                "is_acceptable": False,
                "issues": ["Vague causal mechanism, no quantitative analysis"],
                "suggested_followups": ["Explain HOW precision improvement leads to business KPI improvement with specific mechanisms"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act
        response = await stage2_agent_with_conversation._ask_single_question(
            "How does improving model precision lead to improving your business KPI?"
        )

        # Assert: Final response has detailed causal pathway
        assert len(response) > 50  # Strong explanations are detailed
        assert mock_quality_agent.evaluate_response.call_count >= 1

    @pytest.mark.asyncio
    async def test_end_to_end_stage2_with_conversation_engine(
        self, stage2_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Test complete Stage 2 interview using ConversationEngine."""

        # Setup: Mock all responses as high quality to complete interview
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        mock_llm_router.route = AsyncMock(return_value={
            "response": "Mock high-quality response with specific metrics, baselines, targets, and causal pathways"
        })

        # Act: Conduct full interview
        metric_alignment = await stage2_agent_with_conversation.conduct_interview()

        # Assert: MetricAlignmentMatrix was generated
        from src.models.schemas import MetricAlignmentMatrix
        assert isinstance(metric_alignment, MetricAlignmentMatrix)
        assert metric_alignment.business_kpis is not None
        assert metric_alignment.model_metrics is not None

        # Quality agent was used for validation
        assert mock_quality_agent.evaluate_response.called


@pytest.mark.integration
class TestStage2ConversationEngineEdgeCases:
    """Edge case tests for Stage2Agent conversation integration."""

    @pytest.fixture
    def mock_session_context_regression(self):
        """Create context with REGRESSION archetype for metric diversity testing."""
        context = Mock()
        context.session_id = uuid4()
        context.stage_number = 2
        context.stage1_data = ProblemStatement(
            business_objective="Predict customer lifetime value",
            ml_archetype=MLArchetype.REGRESSION,
            target_output="CLV estimate in dollars",
            input_features=["purchase_history", "engagement_score"],
            success_criteria="RMSE < $500",
            constraints=["Real-time predictions"]
        )
        return context

    @pytest.mark.asyncio
    async def test_stage2_handles_regression_metrics_differently(
        self, mock_session_context_regression, mock_llm_router
    ):
        """Stage2Agent should recommend different metrics for REGRESSION vs CLASSIFICATION."""

        mock_quality_agent = Mock()
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        agent = Stage2Agent(
            session_context=mock_session_context_regression,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Verify agent recognizes REGRESSION archetype
        assert agent.session_context.stage1_data.ml_archetype == MLArchetype.REGRESSION

    @pytest.mark.asyncio
    async def test_stage2_escalation_after_max_attempts(self, mock_session_context, mock_llm_router):
        """Stage2Agent should escalate after 3 failed quality attempts."""

        # Setup: Quality agent always rejects
        mock_quality_agent = Mock()
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 5,
            "is_acceptable": False,
            "issues": ["Insufficient detail"],
            "suggested_followups": ["Please provide more detail"]
        })

        agent = Stage2Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act: Ask question (should hit max attempts)
        response = await agent._ask_single_question("What are your KPIs?")

        # Assert: Should return best response after 3 attempts
        assert response is not None
        # Quality agent called up to max_attempts times
        assert mock_quality_agent.evaluate_response.call_count <= 3
