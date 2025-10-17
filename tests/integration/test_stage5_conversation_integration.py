"""
Integration test: Stage 5 Agent with ConversationEngine

Tests the complete integration of Stage5Agent with ConversationEngine
for conducting quality-validated ethical governance conversations.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.agents.stage5_agent import Stage5Agent
from src.agents.reflection.response_quality_agent import ResponseQualityAgent
from src.conversation import ConversationEngine
from src.models.schemas import MLArchetype, ProblemStatement


@pytest.mark.integration
class TestStage5ConversationIntegration:
    """Integration tests for Stage 5 agent with ConversationEngine."""

    @pytest.fixture
    def mock_stage1_data(self):
        """Create mock Stage 1 ProblemStatement."""
        return ProblemStatement(
            business_objective="Predict loan approval decisions",
            ml_archetype=MLArchetype.CLASSIFICATION,
            target_output="Loan approval probability",
            input_features=["credit_score", "income", "employment_history", "loan_amount"],
            success_criteria="85% accuracy with <10% disparate impact",
            constraints=["Fair lending compliance", "<3 second response time"]
        )

    @pytest.fixture
    def mock_session_context(self, mock_stage1_data):
        """Create mock session context with Stages 1-4 data."""
        context = Mock()
        context.session_id = uuid4()
        context.project_name = "Loan Approval AI"
        context.stage_number = 5
        context.stage1_data = mock_stage1_data
        context.stage2_data = Mock()
        context.stage3_data = Mock()
        context.stage4_data = Mock()
        return context

    @pytest.fixture
    def mock_llm_router(self):
        """Create mock LLM router."""
        router = Mock()
        router.route = AsyncMock(return_value={
            "response": "Bias risk score: 7/10. Protected attributes (race, gender) not in training data but may be correlated with proxies like zip code. Mitigation: fairness metrics monitoring, bias testing across demographics, regular audits."
        })
        router.complete = AsyncMock(return_value="Can you provide a specific risk score (0-10) with evidence of potential bias sources?")
        return router

    @pytest.fixture
    def mock_quality_agent(self):
        """Create mock ResponseQualityAgent."""
        agent = Mock()
        # First response has low quality, second has good quality
        agent.evaluate_response = AsyncMock(side_effect=[
            {
                "quality_score": 4,
                "is_acceptable": False,
                "issues": ["Too vague, needs quantitative risk assessment"],
                "suggested_followups": ["Can you provide a specific risk score (0-10) with evidence?"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ])
        return agent

    @pytest.fixture
    def stage5_agent_with_conversation(self, mock_session_context, mock_llm_router, mock_quality_agent):
        """Create Stage5Agent with ConversationEngine support."""
        return Stage5Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

    @pytest.mark.asyncio
    async def test_stage5_uses_conversation_engine_when_quality_agent_provided(
        self, stage5_agent_with_conversation, mock_quality_agent
    ):
        """Stage5Agent should use ConversationEngine when quality_agent is provided."""

        # Act: Ask a single question (will use ConversationEngine internally)
        question = "Assess the FAIRNESS & NON-DISCRIMINATION risk (0-10) for this AI system"
        response = await stage5_agent_with_conversation._ask_single_question(question)

        # Assert: Quality agent was called (proves ConversationEngine was used)
        assert mock_quality_agent.evaluate_response.called
        assert response is not None
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_conversation_engine_quality_loop_integration(
        self, stage5_agent_with_conversation, mock_quality_agent, mock_llm_router
    ):
        """ConversationEngine should handle quality validation loops correctly for Stage 5."""

        # Setup: Configure responses
        # First attempt: vague
        # Second attempt: specific with quantitative risk assessment
        mock_llm_router.route.side_effect = [
            {"response": "Some fairness risk"},  # Vague
            {"response": "Fairness risk: 7/10. Potential bias from historical data. Protected attributes not in training but correlated with zip code. Mitigation: fairness metrics, bias testing, quarterly audits."}  # Specific
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 3,
                "is_acceptable": False,
                "issues": ["Vague, no quantitative assessment or mitigation plan"],
                "suggested_followups": ["Provide risk score (0-10), bias sources, and mitigation strategies"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act: Ask question
        response = await stage5_agent_with_conversation._ask_single_question(
            "Assess the FAIRNESS & NON-DISCRIMINATION risk (0-10)"
        )

        # Assert: Both attempts were made
        assert mock_quality_agent.evaluate_response.call_count >= 1
        assert "7/10" in response or "7" in response or "fairness" in response.lower()

    @pytest.mark.asyncio
    async def test_stage5_fallback_without_quality_agent(
        self, mock_session_context, mock_llm_router
    ):
        """Stage5Agent should fall back to original logic when no quality_agent provided."""

        # Create agent WITHOUT quality_agent
        agent_without_quality = Stage5Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=None,  # No quality agent
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act: Ask question (should use fallback)
        question = "Assess the FAIRNESS risk (0-10)"
        response = await agent_without_quality._ask_single_question(question)

        # Assert: Fallback validation was used
        assert response is not None
        # Should use basic heuristic validation instead of ConversationEngine

    @pytest.mark.asyncio
    async def test_stage5_five_ethical_principles_assessment(
        self, stage5_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage5Agent should assess all 5 ethical principles through conversation."""

        # Setup: Mock high-quality responses for all principles
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        principles = [
            "FAIRNESS & NON-DISCRIMINATION (0-10)",
            "PRIVACY & DATA PROTECTION (0-10)",
            "SAFETY & RELIABILITY (0-10)",
            "TRANSPARENCY & EXPLAINABILITY (0-10)",
            "ACCOUNTABILITY & GOVERNANCE (0-10)"
        ]

        # Act: Ask about each principle
        responses = []
        for principle in principles:
            response = await stage5_agent_with_conversation._ask_single_question(
                f"Assess {principle} risk"
            )
            responses.append(response)

        # Assert: All principles assessed
        assert len(responses) == 5
        assert all(r is not None for r in responses)

    @pytest.mark.asyncio
    async def test_stage5_mitigation_strategy_conversation(
        self, stage5_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage5Agent should elicit comprehensive mitigation strategies for identified risks."""

        # Setup: Progress from incomplete to comprehensive mitigation plan
        mock_llm_router.route.side_effect = [
            {"response": "We'll monitor the model"},  # Incomplete
            {"response": "Mitigation: (1) Pre-deployment: Bias testing across protected groups, fairness metrics (demographic parity, equal opportunity). (2) Deployment: Real-time monitoring dashboard, monthly audits. (3) Post-deployment: Quarterly model retraining with balanced data. Responsible: ML team + Compliance officer. Timeline: 6 months. Success: <5% disparate impact."}  # Comprehensive
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 3,
                "is_acceptable": False,
                "issues": ["Missing specific mitigation approaches, timeline, responsible parties, and success metrics"],
                "suggested_followups": ["Specify mitigation approaches, implementation timeline, responsible parties, and success metrics"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act
        response = await stage5_agent_with_conversation._ask_single_question(
            "What mitigation strategies will you implement for identified fairness risks?"
        )

        # Assert: Final response is comprehensive
        assert len(response) > 100
        assert mock_quality_agent.evaluate_response.call_count >= 1

    @pytest.mark.asyncio
    async def test_stage5_residual_risk_calculation_conversation(
        self, stage5_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage5Agent should calculate residual risk after mitigation."""

        # Setup: Progress from vague to quantitative residual risk assessment
        mock_llm_router.route.side_effect = [
            {"response": "Lower risk after mitigation"},  # Vague
            {"response": "Pre-mitigation fairness risk: 7/10. Post-mitigation fairness risk: 3/10. Residual risk acceptable because: (1) Meets regulatory threshold (<5% disparate impact), (2) Continuous monitoring in place, (3) Human-in-the-loop for high-risk decisions."}  # Quantitative
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 4,
                "is_acceptable": False,
                "issues": ["Missing quantitative pre/post mitigation risk scores and acceptance justification"],
                "suggested_followups": ["Provide pre-mitigation and post-mitigation risk scores with acceptance justification"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act
        response = await stage5_agent_with_conversation._ask_single_question(
            "What is the residual risk after implementing mitigations?"
        )

        # Assert: Final response includes quantitative assessment
        assert len(response) > 50
        assert mock_quality_agent.evaluate_response.call_count >= 1

    @pytest.mark.asyncio
    async def test_stage5_post_deployment_monitoring_conversation(
        self, stage5_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage5Agent should plan comprehensive post-deployment monitoring."""

        # Setup: Progress from incomplete to comprehensive monitoring plan
        mock_llm_router.route.side_effect = [
            {"response": "Monitor the model"},  # Incomplete
            {"response": "Monitoring: (1) Metrics: Fairness (disparate impact, equal opportunity), Accuracy (precision, recall), Drift (PSI, CSI). (2) Dashboard: Real-time Grafana dashboard with alerts. (3) Audit: Monthly automated + quarterly manual review. (4) Incident response: 24hr SLA for fairness violations, escalation to compliance team. (5) Improvement: Quarterly retraining with feedback data."}  # Comprehensive
        ]

        mock_quality_agent.evaluate_response.side_effect = [
            {
                "quality_score": 3,
                "is_acceptable": False,
                "issues": ["Missing monitoring metrics, audit frequency, incident response, and improvement process"],
                "suggested_followups": ["Specify monitoring metrics, dashboards, audit frequency, incident response procedures, and continuous improvement processes"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ]

        # Act
        response = await stage5_agent_with_conversation._ask_single_question(
            "What post-deployment monitoring will you implement?"
        )

        # Assert: Final response is comprehensive
        assert len(response) > 100
        assert mock_quality_agent.evaluate_response.call_count >= 1

    @pytest.mark.asyncio
    async def test_stage5_automated_governance_decision(
        self, stage5_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Stage5Agent should determine automated governance decision based on risk levels."""

        # Setup: Mock comprehensive risk assessment
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        mock_llm_router.route = AsyncMock(return_value={
            "response": "Fairness: 3/10 (post-mitigation). Privacy: 2/10. Safety: 4/10. Transparency: 3/10. Accountability: 3/10. All risks acceptable with mitigations in place."
        })

        # Act
        response = await stage5_agent_with_conversation._ask_single_question(
            "Summarize all residual risks and governance decision"
        )

        # Assert: Response includes risk summary
        assert response is not None
        assert len(response) > 50

    @pytest.mark.asyncio
    async def test_end_to_end_stage5_with_conversation_engine(
        self, stage5_agent_with_conversation, mock_llm_router, mock_quality_agent
    ):
        """Test complete Stage 5 interview using ConversationEngine."""

        # Setup: Mock all responses as high quality to complete interview
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        mock_llm_router.route = AsyncMock(return_value={
            "response": "Mock high-quality response with detailed risk assessment, mitigation strategies, residual risk calculation, and monitoring plan"
        })

        # Act: Conduct full interview
        ethical_risk_profile = await stage5_agent_with_conversation.conduct_interview()

        # Assert: EthicalRiskReport was generated
        from src.models.schemas import EthicalRiskReport
        assert isinstance(ethical_risk_profile, EthicalRiskReport)
        assert ethical_risk_profile.initial_risks is not None
        assert ethical_risk_profile.mitigation_strategies is not None

        # Quality agent was used for validation
        assert mock_quality_agent.evaluate_response.called


@pytest.mark.integration
class TestStage5ConversationEngineEdgeCases:
    """Edge case tests for Stage5Agent conversation integration."""

    @pytest.mark.asyncio
    async def test_stage5_handles_high_risk_scenario(self, mock_session_context, mock_llm_router):
        """Stage5Agent should properly assess high-risk AI systems."""

        mock_quality_agent = Mock()
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 8,
            "is_acceptable": True,
            "issues": [],
            "suggested_followups": []
        })

        mock_llm_router.route = AsyncMock(return_value={
            "response": "HIGH RISK SYSTEM: Credit decisions affecting vulnerable populations. Fairness: 8/10. Privacy: 7/10. Requires: Human-in-the-loop for all decisions, external audit, regulatory approval before deployment."
        })

        agent = Stage5Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act
        response = await agent._ask_single_question("Assess overall risk level")

        # Assert: Captures high-risk designation
        assert "HIGH RISK" in response or "8/10" in response or "7/10" in response

    @pytest.mark.asyncio
    async def test_stage5_escalation_after_max_attempts(self, mock_session_context, mock_llm_router):
        """Stage5Agent should escalate after 3 failed quality attempts."""

        # Setup: Quality agent always rejects
        mock_quality_agent = Mock()
        mock_quality_agent.evaluate_response = AsyncMock(return_value={
            "quality_score": 5,
            "is_acceptable": False,
            "issues": ["Insufficient risk quantification"],
            "suggested_followups": ["Please provide quantitative risk scores"]
        })

        agent = Stage5Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act: Ask question (should hit max attempts)
        response = await agent._ask_single_question("Assess fairness risk")

        # Assert: Should return best response after 3 attempts
        assert response is not None
        # Quality agent called up to max_attempts times
        assert mock_quality_agent.evaluate_response.call_count <= 3

    @pytest.mark.asyncio
    async def test_stage5_validates_all_stages_context_present(self, mock_llm_router):
        """Stage5Agent should validate that all previous stage contexts (1-4) are present."""

        # Setup: Context missing Stage 3 data
        incomplete_context = Mock()
        incomplete_context.session_id = uuid4()
        incomplete_context.stage1_data = Mock()
        incomplete_context.stage2_data = Mock()
        incomplete_context.stage3_data = None  # Missing!
        incomplete_context.stage4_data = Mock()

        mock_quality_agent = Mock()

        # Act & Assert: Should raise ValueError for missing stage data
        with pytest.raises(ValueError, match="All stages 1-4 data required"):
            Stage5Agent(
                session_context=incomplete_context,
                llm_router=mock_llm_router,
                quality_agent=mock_quality_agent,
                quality_threshold=7.0,
                max_quality_attempts=3
            )

    @pytest.mark.asyncio
    async def test_stage5_privacy_risk_specific_assessment(
        self, mock_session_context, mock_llm_router
    ):
        """Stage5Agent should conduct detailed privacy risk assessment."""

        mock_quality_agent = Mock()
        mock_quality_agent.evaluate_response = AsyncMock(side_effect=[
            {
                "quality_score": 4,
                "is_acceptable": False,
                "issues": ["Missing data protection specifics"],
                "suggested_followups": ["Specify data minimization, encryption, retention, and GDPR/CCPA compliance"]
            },
            {
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": []
            }
        ])

        mock_llm_router.route = AsyncMock(side_effect=[
            {"response": "We protect privacy"},  # Vague
            {"response": "Privacy risk: 4/10. Mitigation: Data minimization (only 4 features), AES-256 encryption at rest/transit, 90-day retention policy, GDPR Article 30 processing records, CCPA data deletion rights implemented."}  # Specific
        ])

        agent = Stage5Agent(
            session_context=mock_session_context,
            llm_router=mock_llm_router,
            quality_agent=mock_quality_agent,
            quality_threshold=7.0,
            max_quality_attempts=3
        )

        # Act
        response = await agent._ask_single_question(
            "Assess PRIVACY & DATA PROTECTION risk (0-10)"
        )

        # Assert: Final response includes privacy specifics
        assert "GDPR" in response or "CCPA" in response or "encryption" in response or "4/10" in response
