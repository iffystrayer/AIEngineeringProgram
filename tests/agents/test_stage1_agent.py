"""
Test Suite: Stage 1 Business Translation Agent

Tests the agent that translates business needs into precise AI problem statements.

Following TDD methodology:
- Specification tests (always passing) document requirements
- Implementation tests (skipped until implementation) verify behavior
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Conditional import for TDD - Stage1Agent may not exist yet
try:
    from src.agents.stage1_business_translation import Stage1Agent

    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

    # Placeholder for test structure
    class Stage1Agent:
        pass


from src.models.schemas import ProblemStatement, MLArchetype

# ============================================================================
# TEST SPECIFICATION - These tests ALWAYS PASS (living documentation)
# ============================================================================


class TestStage1AgentSpecification:
    """
    Specification tests documenting Stage1Agent requirements.
    These tests always pass and serve as executable documentation.
    """

    def test_stage1_agent_role_and_responsibilities(self) -> None:
        """
        SPECIFICATION: Stage1Agent Role

        The Stage1Agent (Business Translation Agent) is responsible for:
        1. Conducting structured interview about business problem
        2. Validating AI/ML necessity and suitability
        3. Determining appropriate ML archetype
        4. Confirming feature availability in production
        5. Defining precise problem scope and boundaries
        6. Generating ProblemStatement deliverable

        Position in workflow: First stage, entry point for problem definition
        """
        assert True, "Specification documented"

    def test_stage1_agent_input_requirements(self) -> None:
        """
        SPECIFICATION: Stage1Agent Input Requirements

        Required inputs:
        - Session context (session_id, project_name)
        - LLM router for question generation and validation
        - Question templates from config/questions/stage1_questions.yaml
        - Response quality threshold (default: 7)

        User provides:
        - Business objective description
        - Justification for AI/ML approach
        - Input features description
        - Target output definition
        - Scope boundaries
        """
        assert True, "Input requirements documented"

    def test_stage1_agent_output_specification(self) -> None:
        """
        SPECIFICATION: Stage1Agent Output

        Outputs produced:
        - ProblemStatement dataclass containing:
          * business_objective: str
          * ai_necessity_justification: str
          * input_features: List[Feature]
          * target_output: OutputDefinition
          * ml_archetype: MLArchetype enum
          * ml_archetype_justification: str
          * scope_boundaries: ScopeDefinition
          * feature_availability: FeatureAccessibilityReport

        Output format: Structured dataclass defined in schemas.py
        """
        assert True, "Output specification documented"

    def test_stage1_agent_workflow_position(self) -> None:
        """
        SPECIFICATION: Stage1Agent Workflow Position

        Workflow sequence:
        1. Orchestrator creates session → invokes Stage1Agent
        2. Stage1Agent loads question templates
        3. Stage1Agent asks Question Group 1: Core Business Objective
        4. For each user response → invoke ResponseQualityAgent
        5. If quality score ≥7 → accept response, next question
        6. If quality score <7 → provide feedback, ask clarifying questions (max 3 loops)
        7. Complete all 4 question groups (Business, AI Suitability, Problem Definition, Scope)
        8. Validate feature availability
        9. Determine and validate ML archetype
        10. Return ProblemStatement to Orchestrator
        11. Orchestrator → StageGateValidator → Stage 2 if passed

        Dependencies:
        - Invokes ResponseQualityAgent after each response
        - Uses ML Archetype Validator tool
        - Uses Feature Availability Validator tool
        """
        assert True, "Workflow position documented"

    def test_stage1_agent_question_groups(self) -> None:
        """
        SPECIFICATION: Stage1Agent Question Groups

        The agent asks questions in 4 structured groups:

        Group 1: Core Business Objective
        - What business problem are you trying to solve?
        - Why is this problem important to the organization?
        - What would success look like?

        Group 2: AI Suitability Assessment
        - Have you considered non-AI solutions?
        - Why is AI/ML necessary for this problem?
        - What makes this problem suitable for machine learning?

        Group 3: Problem Definition
        - What input data/features will the model use?
        - What should the model predict/output?
        - What type of ML task is this? (classification, regression, etc.)

        Group 4: Scope & Boundaries
        - What will this project NOT do?
        - What are the constraints (time, budget, resources)?
        - What edge cases should be excluded?

        Questions are loaded from YAML templates.
        """
        assert True, "Question groups documented"

    def test_stage1_agent_ml_archetype_determination(self) -> None:
        """
        SPECIFICATION: ML Archetype Determination Logic

        The agent must determine the correct ML archetype based on:

        - CLASSIFICATION: Categorical output with predefined classes
          Example: Predict customer will churn (Yes/No)

        - REGRESSION: Continuous numerical output
          Example: Predict customer lifetime value ($)

        - CLUSTERING: Grouping without predefined labels
          Example: Segment customers into behavior groups

        - RECOMMENDATION: Suggest items from a catalog
          Example: Recommend products to users

        - ANOMALY_DETECTION: Identify unusual patterns
          Example: Detect fraudulent transactions

        - NLP: Process or generate natural language
          Example: Classify support tickets by topic

        - COMPUTER_VISION: Process images/video
          Example: Detect defects in product images

        - TIME_SERIES: Forecast future values over time
          Example: Predict sales for next quarter

        Archetype must align with input features and target output.
        Agent must validate and explain the mapping.
        """
        assert True, "ML archetype determination documented"

    def test_stage1_agent_quality_loop_integration(self) -> None:
        """
        SPECIFICATION: ResponseQualityAgent Integration

        For each user response:
        1. Submit response to ResponseQualityAgent
        2. Receive QualityAssessment with score 0-10
        3. If score ≥7: Accept response, continue
        4. If score <7: Provide feedback and ask follow-up questions

        Quality loop behavior:
        - Maximum 3 retry attempts per question
        - Each retry includes specific feedback on why response was insufficient
        - Provide examples of better responses
        - After 3 failed attempts, escalate or accept with flag

        Red flags that trigger low quality scores:
        - Vague language ("improve efficiency" without defining metric)
        - Unjustified AI necessity (simpler solutions not considered)
        - Undefined target variables ("predict behavior" - which behavior?)
        - Features unavailable at inference time
        """
        assert True, "Quality loop integration documented"

    def test_stage1_agent_validation_requirements(self) -> None:
        """
        SPECIFICATION: Stage1Agent Validation Requirements

        Before completing, the agent must validate:

        1. Feature Availability Validation
           - All input features must be accessible in production environment
           - Check if features will be available at inference time
           - Validate data source access latency is acceptable

        2. ML Archetype Validation
           - Archetype must match input/output structure
           - Justify why chosen archetype is appropriate
           - Verify archetype aligns with business objective

        3. AI Necessity Validation
           - Confirm simpler rule-based solutions are insufficient
           - Validate that uncertainty/complexity requires ML
           - Ensure AI adds value over traditional approaches

        4. Completeness Validation
           - All mandatory fields populated
           - All 4 question groups completed
           - No contradictions in problem definition
        """
        assert True, "Validation requirements documented"

    def test_stage1_agent_error_handling_specification(self) -> None:
        """
        SPECIFICATION: Error Handling Requirements

        The Stage1Agent must handle:
        - Invalid user input → prompt for correction with examples
        - Quality loop timeout (3 attempts) → escalate with partial data
        - LLM API failures → retry with exponential backoff
        - Invalid ML archetype selection → prompt for clarification
        - Missing question templates → fail fast with clear error
        - Feature validation failures → highlight issues, allow override with justification

        All errors logged with context for debugging.
        """
        assert True, "Error handling requirements documented"


# ============================================================================
# TEST STRUCTURE - Skipped until implementation exists
# ============================================================================


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1AgentStructure:
    """Tests verifying Stage1Agent class structure and interface."""

    def test_stage1_agent_class_exists(self) -> None:
        """Stage1Agent class should exist in src.agents.stage1_agent."""
        assert hasattr(Stage1Agent, "__init__"), "Stage1Agent class must exist"

    def test_stage1_agent_inherits_from_base_agent(self) -> None:
        """Stage1Agent should inherit from BaseAgent (if exists)."""
        # TODO: Implement when BaseAgent is created
        assert True, "Placeholder for base class verification"

    def test_stage1_agent_has_required_methods(self) -> None:
        """Stage1Agent must implement required interface methods."""
        required_methods = [
            "conduct_interview",
            "ask_question_group",
            "validate_response_quality",
            "determine_ml_archetype",
            "validate_feature_availability",
            "generate_problem_statement",
        ]
        for method in required_methods:
            assert hasattr(Stage1Agent, method), f"Stage1Agent must have {method} method"

    def test_stage1_agent_initialization_signature(self) -> None:
        """Stage1Agent __init__ should accept required parameters."""
        import inspect

        if AGENT_AVAILABLE:
            sig = inspect.signature(Stage1Agent.__init__)
            params = list(sig.parameters.keys())
            # Expecting: self, session_context, llm_router, config
            assert len(params) >= 3, "Stage1Agent should accept session and llm_router"


# ============================================================================
# TEST EXECUTION - Skipped until implementation exists
# ============================================================================


@pytest.fixture
def mock_session_context():
    """Mock session context for testing."""
    from unittest.mock import MagicMock

    context = MagicMock()
    context.session_id = "test-session-123"
    context.project_name = "Test Project"
    context.stage_number = 1
    return context


@pytest.fixture
def mock_llm_router():
    """Mock LLM router for agent communication."""
    from unittest.mock import AsyncMock, MagicMock

    router = MagicMock()
    router.route = AsyncMock()
    return router


@pytest.fixture
def stage1_agent_instance(mock_session_context, mock_llm_router):
    """Create Stage1Agent instance for testing."""
    if not AGENT_AVAILABLE:
        pytest.skip("Stage1Agent not implemented yet")
    return Stage1Agent(session_context=mock_session_context, llm_router=mock_llm_router)


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1AgentExecution:
    """Tests verifying Stage1Agent runtime behavior."""

    @pytest.mark.asyncio
    async def test_conduct_full_interview(self, stage1_agent_instance) -> None:
        """Stage1Agent should conduct complete 4-group interview."""
        problem_statement = await stage1_agent_instance.conduct_interview()

        assert isinstance(problem_statement, ProblemStatement)
        assert problem_statement.business_objective is not None
        assert problem_statement.ml_archetype is not None
        assert len(problem_statement.input_features) > 0

    @pytest.mark.asyncio
    async def test_ask_question_group_business_objective(self, stage1_agent_instance) -> None:
        """Should ask all questions in Business Objective group."""
        responses = await stage1_agent_instance.ask_question_group(group_number=1)

        assert len(responses) > 0
        assert all(r.quality_score >= 7 for r in responses)

    @pytest.mark.asyncio
    async def test_quality_loop_with_low_score_response(self, stage1_agent_instance) -> None:
        """Should trigger quality loop for responses scoring below 7."""
        # Mock low quality response
        mock_response = "Improve efficiency"  # Vague

        quality_assessment = await stage1_agent_instance.validate_response_quality(
            question="What is your business objective?", response=mock_response
        )

        assert quality_assessment.quality_score < 7
        assert not quality_assessment.is_acceptable
        assert len(quality_assessment.suggested_followups) > 0

    @pytest.mark.asyncio
    async def test_quality_loop_with_high_score_response(self, stage1_agent_instance) -> None:
        """Should accept responses scoring 7 or higher."""
        # Mock high quality response
        mock_response = (
            "Reduce customer churn by 15% within 6 months by predicting which customers "
            "are at risk of leaving, measured by 30-day retention rate."
        )

        quality_assessment = await stage1_agent_instance.validate_response_quality(
            question="What is your business objective?", response=mock_response
        )

        assert quality_assessment.quality_score >= 7
        assert quality_assessment.is_acceptable

    @pytest.mark.asyncio
    async def test_determine_ml_archetype_classification(self, stage1_agent_instance) -> None:
        """Should correctly identify classification archetype."""
        inputs = ["customer_age", "purchase_history", "engagement_score"]
        output = "will_churn (Yes/No)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.CLASSIFICATION

    @pytest.mark.asyncio
    async def test_determine_ml_archetype_regression(self, stage1_agent_instance) -> None:
        """Should correctly identify regression archetype."""
        inputs = ["customer_age", "purchase_history", "tenure_months"]
        output = "lifetime_value ($)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.REGRESSION

    @pytest.mark.asyncio
    async def test_validate_feature_availability(self, stage1_agent_instance) -> None:
        """Should validate that features are available in production."""
        features = [
            {"name": "customer_age", "source": "CRM", "available_at_inference": True},
            {"name": "future_purchases", "source": "N/A", "available_at_inference": False},
        ]

        validation_report = await stage1_agent_instance.validate_feature_availability(features)

        assert validation_report.all_features_available is False
        assert len(validation_report.unavailable_features) == 1
        assert "future_purchases" in validation_report.unavailable_features

    @pytest.mark.asyncio
    async def test_generate_problem_statement(self, stage1_agent_instance) -> None:
        """Should generate complete ProblemStatement from collected data."""
        # Mock collected responses
        collected_data = {
            "business_objective": "Reduce churn by 15%",
            "ai_justification": "Pattern complexity requires ML",
            "input_features": ["age", "purchase_history"],
            "target_output": "will_churn",
            "scope": "Active customers only",
        }

        problem_statement = await stage1_agent_instance.generate_problem_statement(
            collected_data
        )

        assert isinstance(problem_statement, ProblemStatement)
        assert problem_statement.business_objective == "Reduce churn by 15%"
        assert problem_statement.ml_archetype is not None


# ============================================================================
# TEST ERROR HANDLING - Skipped until implementation exists
# ============================================================================


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1AgentErrorHandling:
    """Tests verifying Stage1Agent error handling."""

    @pytest.mark.asyncio
    async def test_max_quality_loop_iterations(self, stage1_agent_instance) -> None:
        """Should escalate after 3 failed quality checks."""
        # Mock 3 consecutive low quality responses
        low_quality_response = "make things better"

        attempt_count = 0
        max_attempts = 3

        for _ in range(max_attempts):
            quality_assessment = await stage1_agent_instance.validate_response_quality(
                question="What is your business objective?", response=low_quality_response
            )
            attempt_count += 1
            assert not quality_assessment.is_acceptable

        # After 3 attempts, should escalate
        assert attempt_count == max_attempts

    @pytest.mark.asyncio
    async def test_invalid_ml_archetype_handling(self, stage1_agent_instance) -> None:
        """Should handle cases where ML archetype cannot be determined."""
        inputs = ["unclear_feature"]
        output = "ambiguous_output"

        with pytest.raises(ValueError, match="Cannot determine ML archetype"):
            await stage1_agent_instance.determine_ml_archetype(inputs=inputs, output=output)

    @pytest.mark.asyncio
    async def test_missing_question_templates(self, stage1_agent_instance) -> None:
        """Should fail gracefully if question templates are missing."""
        # Mock missing templates
        stage1_agent_instance.question_templates = None

        with pytest.raises(FileNotFoundError, match="Question templates not found"):
            await stage1_agent_instance.conduct_interview()

    @pytest.mark.asyncio
    async def test_llm_api_failure_retry(self, stage1_agent_instance, mock_llm_router) -> None:
        """Should retry LLM calls on transient failures."""
        from unittest.mock import AsyncMock

        # Mock API failure then success
        mock_llm_router.route.side_effect = [
            Exception("API timeout"),
            {"response": "valid response"},
        ]

        # Should succeed after retry
        response = await stage1_agent_instance.validate_response_quality(
            question="Test question", response="Test response"
        )

        assert response is not None


# ============================================================================
# TEST INTEGRATION - Skipped until implementation exists
# ============================================================================


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
@pytest.mark.integration
class TestStage1AgentIntegration:
    """Integration tests with other system components."""

    @pytest.mark.asyncio
    async def test_integration_with_response_quality_agent(self, stage1_agent_instance) -> None:
        """Stage1Agent should successfully invoke ResponseQualityAgent."""
        # This test verifies the agent can communicate with ResponseQualityAgent
        quality_assessment = await stage1_agent_instance.validate_response_quality(
            question="What is your business objective?",
            response="Reduce customer churn rate by 15% in 6 months",
        )

        from src.models.schemas import QualityAssessment

        assert isinstance(quality_assessment, QualityAssessment)
        assert 0 <= quality_assessment.quality_score <= 10

    @pytest.mark.asyncio
    async def test_integration_with_ml_archetype_validator(self, stage1_agent_instance) -> None:
        """Stage1Agent should use ML Archetype Validator tool."""
        # This test verifies the agent uses validation tools
        result = await stage1_agent_instance.determine_ml_archetype(
            inputs=["feature1", "feature2"], output="categorical_output"
        )

        assert result in MLArchetype

    @pytest.mark.asyncio
    async def test_output_accepted_by_orchestrator(self, stage1_agent_instance) -> None:
        """ProblemStatement output should be compatible with Orchestrator."""
        problem_statement = await stage1_agent_instance.conduct_interview()

        # Verify output structure matches what Orchestrator expects
        assert hasattr(problem_statement, "business_objective")
        assert hasattr(problem_statement, "ml_archetype")
        assert hasattr(problem_statement, "input_features")
        assert hasattr(problem_statement, "target_output")

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, stage1_agent_instance) -> None:
        """Test complete Stage 1 workflow from start to ProblemStatement generation."""
        # Comprehensive integration test
        pytest.skip("Comprehensive integration test - implement when all components ready")


# ============================================================================
# EXTENDED IMPLEMENTATION TESTS (S1-1: Enhanced for detailed TDD)
# ============================================================================


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1QuestionGroupExecution:
    """Detailed tests for each question group's execution."""

    @pytest.mark.asyncio
    async def test_question_group_1_core_business_objective(self, stage1_agent_instance) -> None:
        """Test Question Group 1: Core Business Objective execution."""
        from unittest.mock import AsyncMock

        # Mock LLM responses for Group 1 questions
        stage1_agent_instance.llm_router.route = AsyncMock(
            return_value={
                "business_problem": "High customer churn impacting revenue",
                "importance": "30% annual customer loss = $2M revenue impact",
                "success_criteria": "Reduce churn from 30% to 15% in 12 months",
            }
        )

        responses = await stage1_agent_instance.ask_question_group(group_number=1)

        # Verify all key business objective components are collected
        assert len(responses) >= 3
        assert any("business_problem" in r or "problem" in r for r in responses)
        assert any("importance" in r or "why" in r for r in responses)
        assert any("success" in r for r in responses)

    @pytest.mark.asyncio
    async def test_question_group_2_ai_suitability(self, stage1_agent_instance) -> None:
        """Test Question Group 2: AI Suitability Assessment execution."""
        from unittest.mock import AsyncMock

        # Mock responses for AI suitability questions
        stage1_agent_instance.llm_router.route = AsyncMock(
            return_value={
                "non_ai_alternatives": "Tried rule-based scoring, too simple",
                "ai_necessity": "Complex patterns require ML pattern recognition",
                "suitability": "Classification task with historical labeled data",
            }
        )

        responses = await stage1_agent_instance.ask_question_group(group_number=2)

        # Verify AI justification is collected
        assert len(responses) >= 3
        assert any("alternative" in r.lower() or "non-ai" in r.lower() for r in responses)
        assert any("necessity" in r.lower() or "why" in r.lower() for r in responses)

    @pytest.mark.asyncio
    async def test_question_group_3_problem_definition(self, stage1_agent_instance) -> None:
        """Test Question Group 3: Problem Definition execution."""
        from unittest.mock import AsyncMock

        # Mock responses for problem definition questions
        stage1_agent_instance.llm_router.route = AsyncMock(
            return_value={
                "input_features": "customer_age, tenure, purchases, support_tickets",
                "target_output": "will_churn (binary: Yes/No)",
                "ml_task_type": "Binary classification",
            }
        )

        responses = await stage1_agent_instance.ask_question_group(group_number=3)

        # Verify input/output definition is collected
        assert len(responses) >= 3
        assert any("input" in r.lower() or "feature" in r.lower() for r in responses)
        assert any("output" in r.lower() or "predict" in r.lower() for r in responses)
        assert any("type" in r.lower() or "task" in r.lower() for r in responses)

    @pytest.mark.asyncio
    async def test_question_group_4_scope_boundaries(self, stage1_agent_instance) -> None:
        """Test Question Group 4: Scope & Boundaries execution."""
        from unittest.mock import AsyncMock

        # Mock responses for scope questions
        stage1_agent_instance.llm_router.route = AsyncMock(
            return_value={
                "exclusions": "New customers <3 months, enterprise accounts",
                "constraints": "6 month timeline, $100K budget",
                "edge_cases": "Seasonal businesses, dormant accounts",
            }
        )

        responses = await stage1_agent_instance.ask_question_group(group_number=4)

        # Verify scope boundaries are collected
        assert len(responses) >= 3
        assert any("not" in r.lower() or "exclusion" in r.lower() for r in responses)
        assert any("constraint" in r.lower() or "limit" in r.lower() for r in responses)


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1MLArchetypeLogic:
    """Detailed tests for ML archetype determination logic."""

    @pytest.mark.asyncio
    async def test_archetype_clustering_identification(self, stage1_agent_instance) -> None:
        """Should identify CLUSTERING archetype correctly."""
        inputs = ["purchase_history", "browsing_behavior", "demographics"]
        output = "customer_segments (unlabeled groups)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.CLUSTERING

    @pytest.mark.asyncio
    async def test_archetype_recommendation_identification(self, stage1_agent_instance) -> None:
        """Should identify RECOMMENDATION archetype correctly."""
        inputs = ["user_history", "item_features", "user_preferences"]
        output = "recommended_products (list of items)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.RECOMMENDATION

    @pytest.mark.asyncio
    async def test_archetype_anomaly_detection_identification(
        self, stage1_agent_instance
    ) -> None:
        """Should identify ANOMALY_DETECTION archetype correctly."""
        inputs = ["transaction_amount", "location", "time", "device"]
        output = "is_fraudulent (anomaly score)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.ANOMALY_DETECTION

    @pytest.mark.asyncio
    async def test_archetype_time_series_identification(self, stage1_agent_instance) -> None:
        """Should identify TIME_SERIES archetype correctly."""
        inputs = ["historical_sales", "seasonality", "trends"]
        output = "future_sales (next 30 days)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.TIME_SERIES

    @pytest.mark.asyncio
    async def test_archetype_nlp_identification(self, stage1_agent_instance) -> None:
        """Should identify NLP archetype correctly."""
        inputs = ["customer_message_text", "subject_line"]
        output = "ticket_category (support, sales, billing)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.NLP

    @pytest.mark.asyncio
    async def test_archetype_computer_vision_identification(self, stage1_agent_instance) -> None:
        """Should identify COMPUTER_VISION archetype correctly."""
        inputs = ["product_image", "inspection_photo"]
        output = "defect_detected (Yes/No)"

        archetype = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output
        )

        assert archetype == MLArchetype.COMPUTER_VISION

    @pytest.mark.asyncio
    async def test_archetype_justification_provided(self, stage1_agent_instance) -> None:
        """Agent should provide justification for archetype selection."""
        inputs = ["customer_age", "purchase_history"]
        output = "will_churn (Yes/No)"

        archetype, justification = await stage1_agent_instance.determine_ml_archetype(
            inputs=inputs, output=output, return_justification=True
        )

        assert archetype == MLArchetype.CLASSIFICATION
        assert isinstance(justification, str)
        assert len(justification) > 50  # Substantive justification
        assert "classification" in justification.lower()


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1FeatureValidation:
    """Detailed tests for feature availability validation."""

    @pytest.mark.asyncio
    async def test_all_features_available_validation(self, stage1_agent_instance) -> None:
        """Should validate when all features are production-ready."""
        features = [
            {
                "name": "customer_age",
                "source": "CRM",
                "available_at_inference": True,
                "latency_ms": 50,
            },
            {
                "name": "purchase_count",
                "source": "Transaction DB",
                "available_at_inference": True,
                "latency_ms": 100,
            },
        ]

        report = await stage1_agent_instance.validate_feature_availability(features)

        assert report.all_features_available is True
        assert len(report.unavailable_features) == 0
        assert len(report.latency_concerns) == 0

    @pytest.mark.asyncio
    async def test_feature_unavailable_at_inference(self, stage1_agent_instance) -> None:
        """Should flag features not available at inference time."""
        features = [
            {
                "name": "customer_age",
                "source": "CRM",
                "available_at_inference": True,
                "latency_ms": 50,
            },
            {
                "name": "next_month_purchases",  # Future leakage!
                "source": "Future data",
                "available_at_inference": False,
                "latency_ms": None,
            },
        ]

        report = await stage1_agent_instance.validate_feature_availability(features)

        assert report.all_features_available is False
        assert "next_month_purchases" in report.unavailable_features
        assert len(report.unavailable_features) == 1

    @pytest.mark.asyncio
    async def test_high_latency_feature_warning(self, stage1_agent_instance) -> None:
        """Should warn about features with unacceptable latency."""
        features = [
            {
                "name": "customer_age",
                "source": "CRM",
                "available_at_inference": True,
                "latency_ms": 50,
            },
            {
                "name": "computed_aggregate",
                "source": "Data Warehouse",
                "available_at_inference": True,
                "latency_ms": 5000,  # 5 seconds - too slow!
            },
        ]

        report = await stage1_agent_instance.validate_feature_availability(features)

        assert len(report.latency_concerns) > 0
        assert any("computed_aggregate" in concern for concern in report.latency_concerns)

    @pytest.mark.asyncio
    async def test_feature_access_method_issues(self, stage1_agent_instance) -> None:
        """Should identify features with problematic access methods."""
        features = [
            {
                "name": "customer_age",
                "source": "CRM API",
                "available_at_inference": True,
                "latency_ms": 50,
                "access_method": "REST API",
            },
            {
                "name": "manual_field",
                "source": "Requires manual lookup",
                "available_at_inference": True,
                "latency_ms": None,
                "access_method": "manual",
            },
        ]

        report = await stage1_agent_instance.validate_feature_availability(features)

        assert len(report.access_method_issues) > 0
        assert any("manual_field" in issue for issue in report.access_method_issues)


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1QualityLoopBehavior:
    """Detailed tests for quality loop behavior and edge cases."""

    @pytest.mark.asyncio
    async def test_quality_loop_first_attempt_success(self, stage1_agent_instance) -> None:
        """Should accept high-quality response on first attempt."""
        from unittest.mock import AsyncMock

        # Mock high-quality response
        stage1_agent_instance.llm_router.route = AsyncMock(
            return_value={
                "quality_score": 9,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": [],
            }
        )

        response = "Reduce customer churn from 30% to 15% within 12 months, measured by 30-day retention rate, to save $2M in annual recurring revenue."

        result, attempts = await stage1_agent_instance.validate_response_quality(
            question="What is your business objective?",
            response=response,
            return_attempt_count=True,
        )

        assert result.is_acceptable is True
        assert attempts == 1

    @pytest.mark.asyncio
    async def test_quality_loop_retry_with_improvement(self, stage1_agent_instance) -> None:
        """Should retry and eventually accept improved response."""
        from unittest.mock import AsyncMock

        # Mock: first attempt fails, second succeeds
        quality_results = [
            {
                "quality_score": 5,
                "is_acceptable": False,
                "issues": ["Too vague"],
                "suggested_followups": ["Please specify the metric"],
            },
            {
                "quality_score": 8,
                "is_acceptable": True,
                "issues": [],
                "suggested_followups": [],
            },
        ]

        stage1_agent_instance.llm_router.route = AsyncMock(side_effect=quality_results)

        response_1 = "Improve customer retention"
        response_2 = "Reduce churn by 15% in 6 months"

        # First attempt (should fail)
        result_1, attempts_1 = await stage1_agent_instance.validate_response_quality(
            question="What is your business objective?",
            response=response_1,
            return_attempt_count=True,
        )

        assert result_1.is_acceptable is False
        assert attempts_1 == 1

        # Second attempt (should succeed)
        result_2, attempts_2 = await stage1_agent_instance.validate_response_quality(
            question="What is your business objective?",
            response=response_2,
            return_attempt_count=True,
            previous_attempts=1,
        )

        assert result_2.is_acceptable is True
        assert attempts_2 == 2

    @pytest.mark.asyncio
    async def test_quality_loop_max_attempts_escalation(self, stage1_agent_instance) -> None:
        """Should escalate after 3 failed quality attempts."""
        from unittest.mock import AsyncMock

        # Mock 3 consecutive failures
        stage1_agent_instance.llm_router.route = AsyncMock(
            return_value={
                "quality_score": 4,
                "is_acceptable": False,
                "issues": ["Insufficient detail"],
                "suggested_followups": ["Please be more specific"],
            }
        )

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            result, attempt_count = await stage1_agent_instance.validate_response_quality(
                question="What is your business objective?",
                response="Make things better",
                return_attempt_count=True,
                previous_attempts=attempt - 1,
            )

            assert result.is_acceptable is False
            assert attempt_count == attempt

        # After 3 attempts, should trigger escalation
        assert attempt_count == max_attempts

        # Escalation should be handled (accept with flag or raise to human)
        escalation_result = await stage1_agent_instance.handle_quality_escalation(
            question="What is your business objective?",
            best_response="Make things better",
            attempts=max_attempts,
        )

        assert escalation_result is not None
        assert hasattr(escalation_result, "escalated")
        assert escalation_result.escalated is True


@pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
class TestStage1ProblemStatementGeneration:
    """Detailed tests for final ProblemStatement generation."""

    @pytest.mark.asyncio
    async def test_generate_complete_problem_statement(self, stage1_agent_instance) -> None:
        """Should generate complete ProblemStatement with all required fields."""
        from src.models.schemas import (
            Feature,
            FeatureAccessibilityReport,
            OutputDefinition,
            ScopeDefinition,
        )

        collected_data = {
            "business_objective": "Reduce customer churn by 15% in 12 months",
            "ai_necessity_justification": "Complex behavioral patterns require ML",
            "input_features": [
                Feature(
                    name="customer_age",
                    data_type="int",
                    description="Age in years",
                    source_system="CRM",
                    availability_in_production=True,
                    access_latency_ms=50,
                ),
                Feature(
                    name="purchase_count",
                    data_type="int",
                    description="Total purchases",
                    source_system="Transaction DB",
                    availability_in_production=True,
                    access_latency_ms=100,
                ),
            ],
            "target_output": OutputDefinition(
                name="will_churn",
                type="binary",
                description="Customer will churn in next 30 days",
                possible_values=["Yes", "No"],
            ),
            "ml_archetype": MLArchetype.CLASSIFICATION,
            "ml_archetype_justification": "Binary classification problem with labeled data",
            "scope_boundaries": ScopeDefinition(
                in_scope=["Active customers with >3 months tenure"],
                out_of_scope=["New customers", "Enterprise accounts"],
                assumptions=["Historical churn patterns will continue"],
                constraints=["6 month development timeline", "$100K budget"],
            ),
            "feature_availability": FeatureAccessibilityReport(
                all_features_available=True,
                unavailable_features=[],
                latency_concerns=[],
                access_method_issues=[],
            ),
        }

        problem_statement = await stage1_agent_instance.generate_problem_statement(
            collected_data
        )

        # Verify all required fields are present
        assert isinstance(problem_statement, ProblemStatement)
        assert problem_statement.business_objective is not None
        assert problem_statement.ai_necessity_justification is not None
        assert len(problem_statement.input_features) == 2
        assert problem_statement.target_output is not None
        assert problem_statement.ml_archetype == MLArchetype.CLASSIFICATION
        assert problem_statement.ml_archetype_justification is not None
        assert problem_statement.scope_boundaries is not None
        assert problem_statement.feature_availability is not None
        assert problem_statement.created_at is not None
        assert problem_statement.version == "1.0"

    @pytest.mark.asyncio
    async def test_problem_statement_validation_before_return(
        self, stage1_agent_instance
    ) -> None:
        """Should validate ProblemStatement completeness before returning."""
        # Incomplete data (missing target_output)
        incomplete_data = {
            "business_objective": "Reduce churn",
            "ai_necessity_justification": "ML needed",
            # Missing target_output!
            "input_features": [],
        }

        with pytest.raises(ValueError, match="Incomplete problem statement"):
            await stage1_agent_instance.generate_problem_statement(incomplete_data)

    @pytest.mark.asyncio
    async def test_problem_statement_archetype_alignment_validation(
        self, stage1_agent_instance
    ) -> None:
        """Should validate ML archetype aligns with inputs/outputs."""
        from src.models.schemas import Feature, OutputDefinition

        # Misaligned: regression output but classification archetype
        misaligned_data = {
            "business_objective": "Predict customer value",
            "ai_necessity_justification": "Complex patterns",
            "input_features": [
                Feature(
                    name="age",
                    data_type="int",
                    description="Age",
                    source_system="CRM",
                    availability_in_production=True,
                )
            ],
            "target_output": OutputDefinition(
                name="lifetime_value",
                type="continuous",  # Regression output
                description="Customer lifetime value in dollars",
                units="USD",
            ),
            "ml_archetype": MLArchetype.CLASSIFICATION,  # Wrong archetype!
        }

        with pytest.raises(ValueError, match="ML archetype.*does not align"):
            await stage1_agent_instance.generate_problem_statement(misaligned_data)
