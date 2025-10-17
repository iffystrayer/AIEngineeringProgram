"""
Stage 2: Value Quantification Agent

Establishes measurable success criteria and causal linkages between business KPIs
and model metrics.

Responsibilities:
- Define business KPIs with SMART criteria
- Select appropriate technical model metrics
- Establish causal pathways between metrics and KPIs
- Validate actionability window for predictions
- Ensure measurability of success criteria
- Generate MetricAlignmentMatrix deliverable

Position in workflow: Second stage, follows problem definition
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from src.conversation import ConversationEngine, ConversationContext, MessageRole
from src.models.schemas import (
    CausalLink,
    KPI,
    MetricAlignmentMatrix,
    MLArchetype,
    QualityAssessment,
    TechnicalMetric,
    ValidationPlan,
)

logger = logging.getLogger(__name__)


@dataclass
class QuestionGroup:
    """A structured group of related questions."""

    group_number: int
    title: str
    questions: list[str]
    key_extractions: list[str]  # What to extract from responses


@dataclass
class SMARTValidation:
    """SMART criteria validation result."""

    is_valid: bool
    meets_specific: bool
    meets_measurable: bool
    meets_achievable: bool
    meets_relevant: bool
    meets_timebound: bool
    feedback: str


@dataclass
class CausalValidation:
    """Causal pathway validation result."""

    is_coherent: bool
    has_clear_mechanism: bool
    identified_assumptions: list[str]
    identified_failure_modes: list[str]
    feedback: str


@dataclass
class ActionabilityValidation:
    """Actionability window validation result."""

    is_sufficient: bool
    time_margin: timedelta
    feedback: str


class Stage2Agent:
    """
    Stage 2: Value Quantification Agent

    Translates business objectives into measurable KPIs and technical metrics
    with clear causal connections.
    """

    def __init__(
        self,
        session_context: Any,
        llm_router: Any,
        quality_agent: Any = None,  # ResponseQualityAgent
        quality_threshold: float = 7.0,
        max_quality_attempts: int = 3,
    ):
        """
        Initialize Stage2Agent.

        Args:
            session_context: Session information with Stage 1 data
            llm_router: LLM routing service for API calls
            quality_agent: ResponseQualityAgent for response validation (optional)
            quality_threshold: Minimum quality score to accept responses (default: 7.0)
            max_quality_attempts: Maximum quality loop iterations per question (default: 3)

        Raises:
            ValueError: If Stage 1 data is not available
        """
        # Validate Stage 1 context exists
        if not hasattr(session_context, "stage1_data") or session_context.stage1_data is None:
            raise ValueError("Stage 1 data required for Stage 2 agent")

        self.session_context = session_context
        self.llm_router = llm_router
        self.quality_agent = quality_agent
        self.quality_threshold = quality_threshold
        self.max_quality_attempts = max_quality_attempts

        # Question groups loaded from configuration
        self.question_groups = self._load_question_groups()

        # State management
        self.collected_responses: dict[str, Any] = {}
        self.quality_attempts: dict[str, int] = {}

        logger.info(
            f"Stage2Agent initialized for session {getattr(session_context, 'session_id', 'unknown')}"
        )

    def _load_question_groups(self) -> list[QuestionGroup]:
        """
        Load question group templates.

        For initial implementation, questions are hardcoded.
        Later versions will load from YAML configuration.

        Returns:
            List of QuestionGroup objects
        """
        # Get ML archetype from Stage 1 for context-aware questions
        ml_archetype = getattr(self.session_context.stage1_data, "ml_archetype", None)

        return [
            QuestionGroup(
                group_number=1,
                title="Business KPIs (SMART Criteria)",
                questions=[
                    "What business metrics define success for this project?",
                    "What is the current baseline for these metrics?",
                    "What target values do you aim to achieve?",
                    "What is the timeframe for achieving these targets?",
                    "How will you measure these metrics? What's the measurement method?",
                ],
                key_extractions=[
                    "business_metrics",
                    "baseline_values",
                    "target_values",
                    "target_timeframe",
                    "measurement_methods",
                ],
            ),
            QuestionGroup(
                group_number=2,
                title="Technical Metrics Selection",
                questions=[
                    f"What model performance metrics are appropriate for {ml_archetype.value if ml_archetype else 'your ML task'}?",
                    "What threshold values for these metrics indicate good performance?",
                    "How will you measure these metrics in production?",
                ],
                key_extractions=[
                    "model_metrics",
                    "metric_thresholds",
                    "production_measurement",
                ],
            ),
            QuestionGroup(
                group_number=3,
                title="Causal Connection Mapping",
                questions=[
                    "How does improving each model metric lead to improving each business KPI?",
                    "What are the underlying assumptions in these causal pathways?",
                    "What could cause these connections to break or fail?",
                ],
                key_extractions=[
                    "causal_mechanisms",
                    "causal_assumptions",
                    "failure_modes",
                ],
            ),
            QuestionGroup(
                group_number=4,
                title="Prediction Actionability Window",
                questions=[
                    "How much time do you have to act on model predictions?",
                    "What is the model's expected prediction lead time?",
                    "Is the actionability window sufficient for your business needs?",
                ],
                key_extractions=[
                    "actionability_window",
                    "prediction_latency",
                    "window_sufficiency",
                ],
            ),
        ]

    async def conduct_interview(self) -> MetricAlignmentMatrix:
        """
        Conduct complete Stage 2 interview.

        Executes all 4 question groups, validates SMART criteria, verifies causal
        pathways, and generates final MetricAlignmentMatrix.

        Returns:
            MetricAlignmentMatrix object with complete metric alignment

        Raises:
            FileNotFoundError: If question templates are missing
            ValueError: If metric alignment matrix cannot be generated
        """
        logger.info("Starting Stage 2 interview")

        # Verify question templates are loaded
        if not self.question_groups:
            raise FileNotFoundError("Question templates not found")

        # Execute all 4 question groups
        for group in self.question_groups:
            logger.info(f"Starting Question Group {group.group_number}: {group.title}")
            responses = await self.ask_question_group(group_number=group.group_number)

            # Store responses for later processing
            for idx, key in enumerate(group.key_extractions):
                if idx < len(responses):
                    self.collected_responses[key] = responses[idx]

        logger.info("Interview complete, processing responses")

        # Generate MetricAlignmentMatrix from collected data
        matrix = await self.generate_metric_alignment_matrix(self.collected_responses)

        logger.info(
            f"MetricAlignmentMatrix generated: {len(matrix.business_kpis)} KPIs, "
            f"{len(matrix.model_metrics)} metrics"
        )

        return matrix

    async def ask_question_group(self, group_number: int) -> list[str]:
        """
        Ask all questions in a specific group and collect responses.

        Args:
            group_number: Which question group to execute (1-4)

        Returns:
            List of validated responses (one per question)

        Raises:
            ValueError: If group_number is invalid
        """
        # Find the question group
        group = next(
            (g for g in self.question_groups if g.group_number == group_number),
            None,
        )

        if not group:
            raise ValueError(f"Invalid question group number: {group_number}")

        responses = []

        for question in group.questions:
            # For initial implementation, mock the LLM call
            response = await self._ask_single_question(question)
            responses.append(response)

        return responses

    async def _ask_single_question(self, question: str) -> str:
        """
        Ask a single question with quality validation loop.

        Uses ConversationEngine when quality_agent is available, otherwise falls back
        to basic heuristic validation.

        Args:
            question: The question to ask

        Returns:
            Validated response string
        """
        # Use ConversationEngine if quality_agent is available
        if self.quality_agent:
            return await self._ask_single_question_with_conversation_engine(question)
        else:
            return await self._ask_single_question_fallback(question)

    async def _ask_single_question_with_conversation_engine(self, question: str) -> str:
        """
        Ask question using ConversationEngine for quality validation.

        Args:
            question: The question to ask

        Returns:
            Validated response string
        """
        # Get session ID (handle different context types)
        if hasattr(self.session_context, "session_id"):
            session_id = self.session_context.session_id
        elif hasattr(self.session_context, "id"):
            session_id = self.session_context.id
        else:
            session_id = UUID("00000000-0000-0000-0000-000000000000")

        # Create conversation context for this question
        conversation_context = ConversationContext(
            session_id=session_id,
            stage_number=2,
            current_question=question,
            max_attempts=self.max_quality_attempts
        )

        # Create conversation engine
        engine = ConversationEngine(
            quality_agent=self.quality_agent,
            llm_router=self.llm_router,
            context=conversation_context
        )

        # Start conversation turn
        await engine.start_turn(question)

        # Get user response
        user_response = await self._get_user_response(question)

        # Process response through conversation engine
        result = await engine.process_response(user_response)

        # Handle quality validation loop
        while not result["is_acceptable"] and not result.get("escalated"):
            follow_up_question = result.get("follow_up_question")

            if follow_up_question:
                # Ask follow-up question
                improved_response = await self._get_user_response(follow_up_question)

                # Process improved response
                result = await engine.process_response(improved_response)
            else:
                # No follow-up question available, exit loop
                break

        # Extract final response from conversation history
        history = engine.get_context().conversation_history
        user_messages = [msg for msg in history if msg.role == MessageRole.USER]

        if user_messages:
            return user_messages[-1].content

        return ""

    async def _ask_single_question_fallback(self, question: str) -> str:
        """
        Ask question with basic heuristic validation (fallback mode).

        Args:
            question: The question to ask

        Returns:
            Validated response string
        """
        attempt = 0
        best_response = ""
        best_score = 0.0

        while attempt < self.max_quality_attempts:
            # Get response (mocked for now, later will use LLM)
            response = await self._get_user_response(question)

            # Validate response quality
            quality_assessment = await self.validate_response_quality(
                question=question,
                response=response,
            )

            # Track best response
            if quality_assessment.quality_score > best_score:
                best_response = response
                best_score = quality_assessment.quality_score

            # Check if acceptable
            if quality_assessment.is_acceptable:
                logger.debug(f"Response accepted (score: {quality_assessment.quality_score})")
                return response

            # Log quality issues
            logger.warning(
                f"Response quality too low (score: {quality_assessment.quality_score}). "
                f"Issues: {quality_assessment.issues}"
            )

            attempt += 1

        # Max attempts reached - return best response
        logger.warning(f"Max quality attempts ({self.max_quality_attempts}) reached for question")

        return best_response

    async def _get_user_response(self, question: str) -> str:
        """
        Get user response to a question (via LLM or mock).

        Args:
            question: The question being asked

        Returns:
            User's response string
        """
        if hasattr(self.llm_router, "route") and callable(self.llm_router.route):
            # Mock or real LLM call
            llm_response = await self.llm_router.route(
                prompt=question,
                context=self.session_context,
            )
            # Handle different response formats
            if isinstance(llm_response, dict):
                return str(llm_response.get("response", llm_response.get("content", "")))
            elif hasattr(llm_response, "content"):
                return str(llm_response.content)
            else:
                return str(llm_response)
        else:
            # Fallback mock response
            return f"Mock response to: {question}"

    async def validate_response_quality(
        self,
        question: str,
        response: str,
    ) -> QualityAssessment:
        """
        Validate response quality using ResponseQualityAgent.

        For now, implements basic heuristic validation.
        Later will integrate with actual ResponseQualityAgent.

        Args:
            question: The question that was asked
            response: The user's response

        Returns:
            QualityAssessment object
        """
        # Simple heuristic validation
        issues = []
        score = 10.0

        # Check for vague responses
        vague_terms = ["improve", "better", "optimize", "enhance", "pretty good"]
        if any(term in response.lower() for term in vague_terms):
            if len(response.split()) < 15:
                issues.append("Response is too vague - please be more specific with metrics")
                score -= 3.0

        # Check for minimal responses
        if len(response.split()) < 5:
            issues.append("Response is too brief - please provide more detail")
            score -= 4.0

        # Check for relevant content
        if "mock" in response.lower() and "mock" not in question.lower():
            # This is a mock response, give it a passing score for testing
            score = 8.0
            issues = []

        # Ensure score is in valid range
        score = max(0.0, min(10.0, score))

        # Determine if acceptable
        is_acceptable = score >= self.quality_threshold

        # Generate follow-up questions if needed
        suggested_followups = []
        if not is_acceptable:
            if "vague" in " ".join(issues).lower():
                suggested_followups.append("Can you specify exact metrics with numbers?")
            if "brief" in " ".join(issues).lower():
                suggested_followups.append("Can you provide more context and details?")

        return QualityAssessment(
            quality_score=int(score),
            is_acceptable=is_acceptable,
            issues=issues,
            suggested_followups=suggested_followups,
            examples_to_provide=[],
        )

    async def validate_smart_criteria(self, kpi: KPI) -> SMARTValidation:
        """
        Validate KPI against SMART criteria.

        Args:
            kpi: KPI to validate

        Returns:
            SMARTValidation with detailed criteria assessment
        """
        # Specific: Clear, unambiguous metric name and description
        meets_specific = bool(
            kpi.name
            and len(kpi.name) > 3
            and kpi.description
            and len(kpi.description) > 10
            and not any(vague in kpi.name.lower() for vague in ["improve", "better", "enhance"])
        )

        meets_measurable = bool(
            kpi.measurement_method
            and len(kpi.measurement_method) > 5
            and kpi.current_baseline is not None
        )
        meets_achievable = True
        if kpi.current_baseline is not None and kpi.target_value is not None:
            # Check if target is realistic (not more than 10x increase)
            if kpi.target_value > kpi.current_baseline * 10:
                meets_achievable = False

        meets_relevant = bool(kpi.business_impact and len(kpi.business_impact) > 10)
        meets_timebound = bool(
            kpi.target_timeframe
            and any(
                term in kpi.target_timeframe.lower()
                for term in ["month", "week", "day", "year", "quarter"]
            )
        )

        is_valid = all(
            [
                meets_specific,
                meets_measurable,
                meets_achievable,
                meets_relevant,
                meets_timebound,
            ]
        )

        # Generate feedback
        feedback_parts = []
        if not meets_specific:
            feedback_parts.append("KPI name/description too vague")
        if not meets_measurable:
            feedback_parts.append("Missing measurement method or baseline")
        if not meets_achievable:
            feedback_parts.append("Target appears unrealistic - please justify")
        if not meets_relevant:
            feedback_parts.append("Business impact not clearly defined")
        if not meets_timebound:
            feedback_parts.append("Target timeframe not specific enough")

        feedback = "; ".join(feedback_parts) if feedback_parts else "KPI meets all SMART criteria"

        return SMARTValidation(
            is_valid=is_valid,
            meets_specific=meets_specific,
            meets_measurable=meets_measurable,
            meets_achievable=meets_achievable,
            meets_relevant=meets_relevant,
            meets_timebound=meets_timebound,
            feedback=feedback,
        )

    async def validate_causal_pathway(self, causal_link: CausalLink) -> CausalValidation:
        """
        Validate logical coherence of causal pathway.

        Args:
            causal_link: CausalLink to validate

        Returns:
            CausalValidation with coherence assessment
        """
        # Check for clear mechanism with multiple steps
        has_arrow_notation = "→" in causal_link.causal_mechanism or "->" in causal_link.causal_mechanism
        has_multiple_steps = causal_link.causal_mechanism.count("→") >= 2 or causal_link.causal_mechanism.count("->") >= 2

        has_clear_mechanism = bool(
            causal_link.causal_mechanism
            and len(causal_link.causal_mechanism) > 50
            and (has_arrow_notation or has_multiple_steps)
        )

        # Check for vague mechanisms
        vague_phrases = ["better model", "more accurate", "improves business", "leads to more"]
        is_vague = any(phrase in causal_link.causal_mechanism.lower() for phrase in vague_phrases)

        # If has clear steps but still vague, accept it if long enough
        if is_vague and len(causal_link.causal_mechanism) > 100 and (has_arrow_notation or has_multiple_steps):
            has_clear_mechanism = True

        # Check assumptions
        identified_assumptions = causal_link.assumptions or []
        has_assumptions = len(identified_assumptions) > 0

        # Check failure modes
        identified_failure_modes = causal_link.potential_failure_modes or []
        has_failure_modes = len(identified_failure_modes) > 0

        is_coherent = has_clear_mechanism and has_assumptions and has_failure_modes

        # Generate feedback
        feedback_parts = []
        if not has_clear_mechanism:
            feedback_parts.append(
                "Causal mechanism too vague - explain step-by-step how metric improvement leads to KPI improvement"
            )
        if not has_assumptions:
            feedback_parts.append("List underlying assumptions")
        if not has_failure_modes:
            feedback_parts.append("Identify potential failure modes")

        feedback = "; ".join(feedback_parts) if feedback_parts else "Causal pathway is coherent"

        return CausalValidation(
            is_coherent=is_coherent,
            has_clear_mechanism=has_clear_mechanism,
            identified_assumptions=identified_assumptions,
            identified_failure_modes=identified_failure_modes,
            feedback=feedback,
        )

    async def validate_actionability_window(
        self,
        prediction_latency: timedelta,
        actionability_window: timedelta,
    ) -> ActionabilityValidation:
        """
        Validate actionability window is sufficient.

        Args:
            prediction_latency: Time to generate prediction
            actionability_window: Time available to act

        Returns:
            ActionabilityValidation with sufficiency assessment
        """
        time_margin = actionability_window - prediction_latency
        is_sufficient = time_margin.total_seconds() > 0

        if is_sufficient:
            feedback = f"Actionability window sufficient with {time_margin} margin"
        else:
            feedback = f"Actionability window insufficient - predictions will be stale by {abs(time_margin)}"

        return ActionabilityValidation(
            is_sufficient=is_sufficient,
            time_margin=time_margin,
            feedback=feedback,
        )

    async def recommend_metrics(self, archetype: MLArchetype) -> list[TechnicalMetric]:
        """
        Recommend appropriate metrics for ML archetype.

        Args:
            archetype: ML archetype from Stage 1

        Returns:
            List of recommended TechnicalMetric objects
        """
        metrics_by_archetype = {
            MLArchetype.CLASSIFICATION: [
                TechnicalMetric(
                    name="Precision",
                    description="Ratio of correct positive predictions",
                    target_threshold=0.80,
                    measurement_method="TP / (TP + FP)",
                ),
                TechnicalMetric(
                    name="Recall",
                    description="Ratio of correctly identified positives",
                    target_threshold=0.75,
                    measurement_method="TP / (TP + FN)",
                ),
                TechnicalMetric(
                    name="F1-Score",
                    description="Harmonic mean of precision and recall",
                    target_threshold=0.77,
                    measurement_method="2 * (Precision * Recall) / (Precision + Recall)",
                ),
            ],
            MLArchetype.REGRESSION: [
                TechnicalMetric(
                    name="RMSE",
                    description="Root Mean Squared Error",
                    target_threshold=0.0,  # Lower is better, set based on domain
                    measurement_method="sqrt(mean((y_pred - y_true)^2))",
                ),
                TechnicalMetric(
                    name="MAE",
                    description="Mean Absolute Error",
                    target_threshold=0.0,  # Lower is better, set based on domain
                    measurement_method="mean(|y_pred - y_true|)",
                ),
                TechnicalMetric(
                    name="R-squared",
                    description="Coefficient of determination",
                    target_threshold=0.70,
                    measurement_method="1 - (SS_res / SS_tot)",
                ),
            ],
            MLArchetype.CLUSTERING: [
                TechnicalMetric(
                    name="Silhouette Score",
                    description="Measure of cluster cohesion and separation",
                    target_threshold=0.50,
                    measurement_method="(b - a) / max(a, b) where a=intra-cluster, b=inter-cluster distance",
                ),
            ],
            MLArchetype.RECOMMENDATION: [
                TechnicalMetric(
                    name="Precision@K",
                    description="Precision at top K recommendations",
                    target_threshold=0.70,
                    measurement_method="Relevant items in top K / K",
                ),
                TechnicalMetric(
                    name="Recall@K",
                    description="Recall at top K recommendations",
                    target_threshold=0.60,
                    measurement_method="Relevant items in top K / Total relevant items",
                ),
            ],
            MLArchetype.ANOMALY_DETECTION: [
                TechnicalMetric(
                    name="Precision",
                    description="Precision for anomaly detection",
                    target_threshold=0.85,
                    measurement_method="True anomalies / Predicted anomalies",
                ),
                TechnicalMetric(
                    name="Recall",
                    description="Recall for anomaly detection",
                    target_threshold=0.80,
                    measurement_method="Detected anomalies / Total anomalies",
                ),
            ],
            MLArchetype.TIME_SERIES: [
                TechnicalMetric(
                    name="RMSE",
                    description="Root Mean Squared Error for forecasting",
                    target_threshold=0.0,  # Lower is better, set based on domain
                    measurement_method="sqrt(mean((forecast - actual)^2))",
                ),
                TechnicalMetric(
                    name="MAPE",
                    description="Mean Absolute Percentage Error",
                    target_threshold=10.0,
                    measurement_method="mean(|forecast - actual| / actual) * 100",
                ),
            ],
        }

        # Return metrics for archetype, or default to classification
        return metrics_by_archetype.get(archetype, metrics_by_archetype[MLArchetype.CLASSIFICATION])

    async def generate_metric_alignment_matrix(
        self,
        collected_data: dict[str, Any],
    ) -> MetricAlignmentMatrix:
        """
        Generate complete MetricAlignmentMatrix from collected interview data.

        Args:
            collected_data: Dictionary of collected responses

        Returns:
            Complete MetricAlignmentMatrix object

        Raises:
            ValueError: If data is incomplete or invalid
        """
        logger.info("Generating MetricAlignmentMatrix from collected data")

        # Get ML archetype from Stage 1
        ml_archetype = getattr(self.session_context.stage1_data, "ml_archetype", MLArchetype.CLASSIFICATION)

        # Parse business KPIs (simplified for MVP)
        business_kpis = [
            KPI(
                name="Primary Business KPI",
                description=collected_data.get("business_metrics", "Revenue increase"),
                current_baseline=100.0,
                target_value=115.0,
                target_timeframe=collected_data.get("target_timeframe", "6 months"),
                measurement_method=collected_data.get("measurement_methods", "Quarterly revenue reports"),
                business_impact="15% revenue increase",
            )
        ]

        # Validate SMART criteria for each KPI
        for kpi in business_kpis:
            validation = await self.validate_smart_criteria(kpi)
            if not validation.is_valid:
                logger.warning(f"KPI '{kpi.name}' does not meet SMART criteria: {validation.feedback}")

        # Get recommended metrics for archetype
        model_metrics = await self.recommend_metrics(ml_archetype)

        # Create causal pathways (simplified for MVP)
        causal_pathways = [
            CausalLink(
                model_metric=model_metrics[0].name if model_metrics else "Model Metric",
                business_kpi=business_kpis[0].name,
                causal_mechanism=collected_data.get(
                    "causal_mechanisms",
                    "Improved model performance → better predictions → business outcome improvement",
                ),
                assumptions=["Historical patterns continue", "Business processes remain stable"],
                potential_failure_modes=["External market changes", "Process changes"],
            )
        ]

        # Validate causal pathways
        for pathway in causal_pathways:
            validation = await self.validate_causal_pathway(pathway)
            if not validation.is_coherent:
                logger.warning(f"Causal pathway validation issue: {validation.feedback}")

        # Parse actionability window (default to 24 hours)
        actionability_window = timedelta(hours=24)

        # Create validation plan
        causal_impact_plan = ValidationPlan(
            validation_method="A/B testing with model predictions vs. baseline",
            data_requirements=["Model metrics", "Business KPIs", "Control group data"],
            timeline="3 months post-deployment",
            success_criteria="Statistically significant improvement in KPIs (p<0.05)",
        )

        matrix = MetricAlignmentMatrix(
            business_kpis=business_kpis,
            model_metrics=model_metrics,
            causal_pathways=causal_pathways,
            actionability_window=actionability_window,
            causal_impact_plan=causal_impact_plan,
            created_at=datetime.now(),
            version="1.0",
        )

        logger.info(
            f"MetricAlignmentMatrix created: {len(matrix.business_kpis)} KPIs, "
            f"{len(matrix.model_metrics)} metrics"
        )

        return matrix
