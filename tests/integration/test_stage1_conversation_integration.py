"""
Integration test: Stage 1 Agent with ConversationEngine

Tests the complete integration of Stage1Agent with ConversationEngine
for conducting quality-validated conversations.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.agents.stage1_business_translation import Stage1Agent
from src.agents.reflection.response_quality_agent import ResponseQualityAgent
from src.conversation import ConversationEngine


@pytest.mark.integration
class TestStage1ConversationIntegration:
    """Integration tests for Stage 1 agent with ConversationEngine."""

    @pytest.fixture
    def mock_session_context(self):
        """Create mock session context."""
        context = Mock()
        context.session_id = uuid4()
        context.project_name = "Test Project"
        context.stage_number = 1
        return context

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router."""
        router = Mock()
        router.route = AsyncMock(return_value={
            "response": "Reduce customer churn by 15% within 6 months"
        })
        router.complete = AsyncMock(return_value="What specific metric defines customer retention?")
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
                "issues": ["Too vague - needs specific metrics"],
                "suggested_followups": ["What specific metric defines customer retention?"]
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
    def stage1_agent_with_conversation(self, mock_session_context, mock_llm_router, mock_quality_agent):
        """Create Stage1Agent with ConversationEngine support."""
        return Stage1Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

    @pytest.mark.asyncio
    async def test_stage1_uses_conversation_engine_when_quality_agent_provided(
        self, stage1_agent_with_conversation, mock_quality_agent
    ):
        """Stage1Agent should use ConversationEngine when quality_agent is provided."""

        # Act: Ask a single question (will use ConversationEngine internally)
        question = "What is your business objective?"
        response = await stage1_agent_with_conversation._ask_single_question(question)

        # Assert: Quality agent was called (proves ConversationEngine was used)
        assert mock_quality_agent.evaluate_response.called
        assert response is not None
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_conversation_engine_quality_loop_integration(
        self, stage1_agent_with_conversation, mock_quality_agent, mock_llm_router
    ):
        """ConversationEngine should handle quality validation loops correctly."""

        # Setup: Configure responses
        # First attempt: low quality
        # Second attempt: good quality
        mock_llm_router.route.side_effect = [
            {"response": "Improve retention"},  # Vague
            {"response": "Reduce churn by 15% in 6 months"}  # Specific
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 5,
                "is_acceptable": False,
                "issues": ["Too vague"],
                "suggested_followups": ["Be more specific"]
            },
            {
                "quality_score": 8,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act: Ask question
        response = await stage1_agent_with_conversation._ask_single_question(
            "What is your business objective?"
        )

        # Assert: Both attempts were made
        assert mock_quality_agent.evaluate_response.call_count >= 1
        assert response == "Reduce churn by 15% in 6 months"

    @pytest.mark.asyncio
    async def test_stage1_fallback_without_quality_agent(
        self, mock_session_context, mock_llm_router
    ):
        """Stage1Agent should fall back to original logic when no quality_agent provided."""

        # Create agent WITHOUT quality_agent
        agent_without_quality = Stage1Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=None,  # No quality agent
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act: Ask question (should use fallback)
        question = "What is your business objective?"
        response = await agent_without_quality._ask_single_question(question)

        # Assert: Fallback validation was used
        assert response is not None
        # Should use basic heuristic validation instead of ConversationEngine

    @pytest.mark.asyncio
    async def test_end_to_end_stage1_with_conversation_engine(
        self, stage1_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Test complete Stage 1 interview using ConversationEngine."""

        # Setup: Mock all responses as high quality to avoid loops
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        mock_llm_router.route = AsyncMock(return_value={
            "response": "Mock high-quality response with sufficient detail and specificity"
        })

        # Act: Conduct full interview
        problem_statement = await stage1_agent_with_conversation.conduct_interview()

        # Assert: ProblemStatement was generated
        from src.models.schemas import ProblemStatement
        assert isinstance(problem_statement, ProblemStatement)
        assert problem_statement.business_objective is not None
        assert problem_statement.ml_archetype is not None

        # Quality agent was used for validation
        assert mock_quality_agent.evaluate_response.called


@pytest.mark.integration
class TestConversationEngineStandalone:
    """Standalone tests for ConversationEngine functionality."""

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

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router."""
        router = Mock()
        router.complete = AsyncMock(return_value="Follow-up question")
        return router

    @pytest.mark.asyncio
    async def test_conversation_engine_basic_flow(self, mock_quality_agent, mock_llm_router):
        """Test basic ConversationEngine conversation flow."""
        from src.conversation import ConversationEngine, ConversationContext

        # Create context
        context = ConversationContext(
            session_id=uuid4(),
            stage_number=1,
            current_question="What is your goal?",
            max_attempts=3
        )

        # Create engine
        engine = ConversationEngine(
            quality_agent=mock_quality_agent,
            llm_router=mock_llm_router,
            context=context
        )

        # Start turn
        await engine.start_turn("What is your goal?")

        # Process response
        result = await engine.process_response("Increase revenue by 20%")

        # Verify
        assert result["is_acceptable"] is True
        assert result["quality_score"] == 8
        assert mock_quality_agent.evaluate_response.called
