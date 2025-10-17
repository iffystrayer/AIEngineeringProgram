"""
Stage 5: Ethical Governance Agent

Conducts comprehensive ethical risk assessment across five ethical principles,
proposes mitigation strategies, calculates residual risk, and determines
automated governance decisions.

Responsibilities:
- Assess risks across 5 ethical principles (Fairness, Privacy, Transparency, Safety, Human Agency)
- Calculate initial risk scores (severity × likelihood)
- Validate mitigation strategies and their effectiveness
- Calculate residual risk after mitigation
- Determine governance decision (Proceed/Revise/Halt/Committee)
- Generate EthicalRiskReport deliverable

Position in workflow: Final stage (5), concludes interview process
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from src.conversation import ConversationEngine, ConversationContext, MessageRole
from src.models.schemas import (
    ContinuousMonitoringPlan,
    EthicalPrinciple,
    EthicalRisk,
    EthicalRiskReport,
    GovernanceDecision,
    MitigationStrategy,
    QualityAssessment,
    RiskLevel,
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
class MitigationValidation:
    """Mitigation strategy validation result."""

    is_realistic: bool
    is_specific: bool
    has_timeline: bool
    has_cost_estimate: bool
    effectiveness_reasonable: bool
    feedback: str


class Stage5Agent:
    """
    Stage 5: Ethical Governance Agent

    Conducts comprehensive ethical risk assessment and determines governance decisions.
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
        Initialize Stage5Agent.

        Args:
            session_context: Session information with Stage 1-4 data
            llm_router: LLM routing service for API calls
            quality_agent: ResponseQualityAgent for response validation (optional)
            quality_threshold: Minimum quality score to accept responses (default: 7.0)
            max_quality_attempts: Maximum quality loop iterations per question (default: 3)

        Raises:
            ValueError: If any Stage 1-4 data is not available
        """
        # Validate all previous stage contexts exist
        required_stages = ["stage1_data", "stage2_data", "stage3_data", "stage4_data"]
        missing_stages = []
        for stage_attr in required_stages:
            if not hasattr(session_context, stage_attr) or getattr(session_context, stage_attr) is None:
                missing_stages.append(stage_attr)

        if missing_stages:
            raise ValueError(f"All stages 1-4 data required for Stage 5 agent. Missing: {missing_stages}")

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
            f"Stage5Agent initialized for session {getattr(session_context, 'session_id', 'unknown')}"
        )

    def _load_question_groups(self) -> list[QuestionGroup]:
        """
        Load question group templates.

        For initial implementation, questions are hardcoded.
        Later versions will load from YAML configuration.

        Returns:
            List of QuestionGroup objects
        """
        return [
            QuestionGroup(
                group_number=1,
                title="Risk Self-Assessment",
                questions=[
                    "Have you completed a preliminary ethical risk assessment for this project?",
                    "What ethical risks have been identified so far?",
                    "What stakeholders could be negatively affected by this AI system?",
                ],
                key_extractions=[
                    "preliminary_assessment",
                    "identified_risks",
                    "affected_stakeholders",
                ],
            ),
            QuestionGroup(
                group_number=2,
                title="Principle-Specific Risk Mapping",
                questions=[
                    "FAIRNESS & EQUITY: What risks exist regarding bias, discrimination, or disparate impact?",
                    "PRIVACY & DATA PROTECTION: What risks exist regarding data leakage, re-identification, or consent?",
                    "TRANSPARENCY & ACCOUNTABILITY: What risks exist regarding black-box decisions or auditability?",
                    "SAFETY & RESILIENCE: What risks exist regarding model failures, adversarial attacks, or robustness?",
                    "HUMAN AGENCY & OVERSIGHT: What risks exist regarding automation bias, deskilling, or override capability?",
                ],
                key_extractions=[
                    "fairness_risks",
                    "privacy_risks",
                    "transparency_risks",
                    "safety_risks",
                    "human_agency_risks",
                ],
            ),
            QuestionGroup(
                group_number=3,
                title="Mitigation Strategy Planning",
                questions=[
                    "For each identified risk, what mitigation strategy will reduce it?",
                    "How will each mitigation be implemented?",
                    "What is the estimated cost and timeline for each mitigation?",
                    "What is the expected effectiveness of each mitigation (0-100%)?",
                ],
                key_extractions=[
                    "mitigation_strategies",
                    "implementation_methods",
                    "cost_timeline",
                    "effectiveness_ratings",
                ],
            ),
            QuestionGroup(
                group_number=4,
                title="Residual Risk Calculation",
                questions=[
                    "After mitigation, what risk level remains for each principle?",
                    "Are residual risks acceptable for deployment?",
                    "What monitoring will track residual risks post-deployment?",
                ],
                key_extractions=[
                    "residual_risk_levels",
                    "risk_acceptability",
                    "monitoring_plan",
                ],
            ),
            QuestionGroup(
                group_number=5,
                title="Post-Deployment Monitoring",
                questions=[
                    "What metrics will monitor ethical performance?",
                    "How often will ethics audits occur?",
                    "What triggers escalation or model shutdown?",
                ],
                key_extractions=[
                    "monitoring_metrics",
                    "audit_frequency",
                    "escalation_triggers",
                ],
            ),
        ]

    async def conduct_interview(self) -> EthicalRiskReport:
        """
        Conduct complete Stage 5 interview.

        Executes all 5 question groups, validates responses, calculates residual risks,
        and generates final EthicalRiskReport with governance decision.

        Returns:
            EthicalRiskReport object with complete ethical assessment

        Raises:
            FileNotFoundError: If question templates are missing
            ValueError: If ethical risk report cannot be generated
        """
        logger.info("Starting Stage 5 interview")

        # Verify question templates are loaded
        if not self.question_groups:
            raise FileNotFoundError("Question templates not found")

        # Execute all 5 question groups
        for group in self.question_groups:
            logger.info(f"Starting Question Group {group.group_number}: {group.title}")
            responses = await self.ask_question_group(group_number=group.group_number)

            # Store responses for later processing
            for idx, key in enumerate(group.key_extractions):
                if idx < len(responses):
                    self.collected_responses[key] = responses[idx]

        logger.info("Interview complete, processing responses")

        # Generate EthicalRiskReport from collected data
        report = await self.generate_ethical_risk_report(self.collected_responses)

        logger.info(
            f"EthicalRiskReport generated: {len(report.initial_risks)} risk categories, "
            f"decision: {report.governance_decision.value}"
        )

        return report

    async def ask_question_group(self, group_number: int) -> list[str]:
        """
        Ask all questions in a specific group and collect responses.

        Args:
            group_number: Which question group to execute (1-5)

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
            stage_number=5,
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

        # Get actual user response via interactive CLI
        from src.cli.interactive import ask_user_question

        user_response = await ask_user_question(
            question=question,
            stage_number=5,
            context=f"Session: {getattr(self.session_context, 'project_name', 'Unknown')}"
        )

        # Process response through conversation engine
        result = await engine.process_response(user_response)

        # Handle quality validation loop
        while not result["is_acceptable"] and not result.get("escalated"):
            follow_up_question = result.get("follow_up_question")

            if follow_up_question:
                # Display quality feedback and get improved response
                from src.cli.interactive import display_follow_up

                quality_score = result.get("quality_score", 0)
                issues = result.get("issues", [])

                improved_response = await display_follow_up(
                    follow_up_question=follow_up_question,
                    quality_score=quality_score,
                    issues=issues
                )

                # Process improved response
                result = await engine.process_response(improved_response)
            else:
                # No follow-up question available, exit loop
                break

        # Display success message
        from src.cli.interactive import display_quality_success
        final_score = result.get("quality_score", 10)
        display_quality_success(final_score)

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

        For now, implements ethics-specific heuristic validation.
        Later will integrate with actual ResponseQualityAgent.

        Args:
            question: The question that was asked
            response: The user's response

        Returns:
            QualityAssessment object
        """
        # Ethics-specific validation
        issues = []
        score = 10.0

        # Check for dismissive responses
        dismissive_terms = [
            "no concerns",
            "no risks",
            "don't have any",
            "not applicable",
            "n/a",
            "everything is fine",
        ]
        if any(term in response.lower() for term in dismissive_terms) and len(response.split()) < 20:
            issues.append("Response appears dismissive - please provide thorough ethical assessment")
            score -= 5.0

        # Check for vague mitigation strategies
        if "mitigation" in question.lower():
            vague_terms = ["be careful", "we'll try", "monitor closely", "do our best"]
            if any(term in response.lower() for term in vague_terms):
                issues.append("Mitigation strategy too vague - please be specific")
                score -= 3.0

        # Check for minimal responses
        if len(response.split()) < 10:
            issues.append("Response is too brief - please provide more detail")
            score -= 3.0

        # Check for mock responses
        if "mock" in response.lower() and "mock" not in question.lower():
            score = 8.0
            issues = []

        # Ensure score is in valid range
        score = max(0.0, min(10.0, score))

        # Determine if acceptable
        is_acceptable = score >= self.quality_threshold

        # Generate follow-up questions if needed
        suggested_followups = []
        if not is_acceptable:
            if "dismissive" in " ".join(issues).lower():
                suggested_followups.append("Can you identify at least one potential ethical risk?")
            if "vague" in " ".join(issues).lower():
                suggested_followups.append("Can you specify the exact implementation method?")

        return QualityAssessment(
            quality_score=int(score),
            is_acceptable=is_acceptable,
            issues=issues,
            suggested_followups=suggested_followups,
            examples_to_provide=[],
        )

    async def assess_risk_per_principle(
        self,
        principle: EthicalPrinciple,
        project_context: dict[str, Any],
    ) -> list[EthicalRisk]:
        """
        Assess ethical risks for a specific principle.

        Args:
            principle: The ethical principle to assess
            project_context: Context from previous stages

        Returns:
            List of EthicalRisk objects for this principle
        """
        # Mock implementation - in production would use LLM to analyze context
        risks = []

        # Create a sample risk for each principle
        if principle == EthicalPrinciple.FAIRNESS_EQUITY:
            risk = EthicalRisk(
                principle=principle,
                risk_description="Potential bias in model decisions",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                affected_stakeholders=["End users", "Protected groups"],
                mitigation_strategies=[],
                residual_risk=RiskLevel.MEDIUM,
            )
            risks.append(risk)

        return risks

    async def calculate_residual_risk(
        self,
        initial_risk: EthicalRisk,
        mitigations: list[MitigationStrategy],
    ) -> RiskLevel:
        """
        Calculate residual risk after applying mitigation strategies.

        Formula: residual_risk = initial_risk × (1 - Σ(mitigation effectiveness))
        Mitigation effectiveness capped at 0.95 (cannot reduce to zero).

        Args:
            initial_risk: Initial risk assessment
            mitigations: List of mitigation strategies

        Returns:
            RiskLevel enum for residual risk
        """
        # Calculate initial risk score (severity × likelihood)
        initial_score = initial_risk.severity.value * initial_risk.likelihood.value

        # Sum mitigation effectiveness
        total_effectiveness = sum(m.effectiveness_rating for m in mitigations)

        # Cap at 0.95 (95% reduction max)
        total_effectiveness = min(0.95, total_effectiveness)

        # Calculate residual risk
        residual_score = initial_score * (1 - total_effectiveness)

        # Map to RiskLevel enum
        if residual_score >= 8:
            return RiskLevel.CRITICAL
        elif residual_score >= 4:
            return RiskLevel.HIGH if residual_score >= 6 else RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def validate_mitigation_strategy(
        self,
        mitigation: MitigationStrategy,
    ) -> MitigationValidation:
        """
        Validate mitigation strategy for realism and specificity.

        Args:
            mitigation: MitigationStrategy to validate

        Returns:
            MitigationValidation with assessment
        """
        issues = []

        # Check for realistic effectiveness (< 100%)
        effectiveness_reasonable = mitigation.effectiveness_rating < 1.0
        if not effectiveness_reasonable:
            issues.append("100% effectiveness is unrealistic")

        # Check for specific description
        is_specific = len(mitigation.description) > 20
        if not is_specific:
            issues.append("Description too brief")

        # Check for timeline
        has_timeline = mitigation.timeline is not None and len(mitigation.timeline) > 0
        if not has_timeline:
            issues.append("Timeline not specified")

        # Check for cost estimate
        has_cost_estimate = mitigation.cost_estimate is not None and len(mitigation.cost_estimate) > 0
        if not has_cost_estimate:
            issues.append("Cost estimate not specified")

        is_realistic = effectiveness_reasonable and is_specific

        feedback = "; ".join(issues) if issues else "Mitigation strategy is realistic"

        return MitigationValidation(
            is_realistic=is_realistic,
            is_specific=is_specific,
            has_timeline=has_timeline,
            has_cost_estimate=has_cost_estimate,
            effectiveness_reasonable=effectiveness_reasonable,
            feedback=feedback,
        )

    async def determine_governance_decision(
        self,
        residual_risks: dict[EthicalPrinciple, RiskLevel],
    ) -> GovernanceDecision:
        """
        Determine automated governance decision based on residual risk levels.

        Decision rules:
        - HALT: Any CRITICAL risk OR multiple HIGH risks (3+) OR Safety at HIGH/CRITICAL
        - SUBMIT_TO_COMMITTEE: Multiple HIGH risks (2) OR HIGH in Fairness/Privacy
        - REVISE: Single HIGH risk OR insufficient mitigation
        - PROCEED_WITH_MONITORING: All MEDIUM or below with strong mitigation
        - PROCEED: All LOW risks

        Args:
            residual_risks: Dict mapping principles to their residual risk levels

        Returns:
            GovernanceDecision enum
        """
        # Count risk levels
        critical_count = sum(1 for level in residual_risks.values() if level == RiskLevel.CRITICAL)
        high_count = sum(1 for level in residual_risks.values() if level == RiskLevel.HIGH)
        medium_count = sum(1 for level in residual_risks.values() if level == RiskLevel.MEDIUM)

        # HALT: Any critical risk
        if critical_count > 0:
            return GovernanceDecision.HALT

        # HALT: Multiple HIGH risks (3+)
        if high_count >= 3:
            return GovernanceDecision.HALT

        # HALT: Safety at HIGH or CRITICAL
        if residual_risks.get(EthicalPrinciple.SAFETY_RESILIENCE) in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return GovernanceDecision.HALT

        # SUBMIT_TO_COMMITTEE: Multiple HIGH risks (2)
        if high_count >= 2:
            return GovernanceDecision.SUBMIT_TO_COMMITTEE

        # REVISE: Single HIGH risk (check this before specific principle checks)
        if high_count >= 1:
            return GovernanceDecision.REVISE

        # PROCEED_WITH_MONITORING: Any MEDIUM risks
        if medium_count > 0:
            return GovernanceDecision.PROCEED_WITH_MONITORING

        # PROCEED: All LOW risks
        return GovernanceDecision.PROCEED

    async def generate_ethical_risk_report(
        self,
        collected_data: dict[str, Any],
    ) -> EthicalRiskReport:
        """
        Generate complete EthicalRiskReport from collected interview data.

        Args:
            collected_data: Dictionary of collected responses

        Returns:
            Complete EthicalRiskReport object

        Raises:
            ValueError: If data is incomplete or invalid
        """
        logger.info("Generating EthicalRiskReport from collected data")

        # Create sample risks for each principle (simplified for MVP)
        initial_risks: dict[EthicalPrinciple, list[EthicalRisk]] = {}

        for principle in EthicalPrinciple:
            # Create a sample risk
            risk = EthicalRisk(
                principle=principle,
                risk_description=f"Risk identified for {principle.value}",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                affected_stakeholders=["Users", "Stakeholders"],
                mitigation_strategies=[
                    MitigationStrategy(
                        description="Implement appropriate controls",
                        implementation_method="Technical and process controls",
                        cost_estimate="$10K",
                        timeline="4 weeks",
                        effectiveness_rating=0.6,
                    )
                ],
                residual_risk=RiskLevel.LOW,
            )
            initial_risks[principle] = [risk]

        # Create mitigation strategies mapping
        mitigation_strategies: dict[str, list[MitigationStrategy]] = {}
        for principle, risks in initial_risks.items():
            for risk in risks:
                key = f"{principle.value}_{risk.risk_description[:20]}"
                mitigation_strategies[key] = risk.mitigation_strategies

        # Calculate residual risks for each principle
        residual_risks: dict[EthicalPrinciple, RiskLevel] = {}
        for principle, risks in initial_risks.items():
            if risks:
                # Calculate residual risk for the first risk in each principle
                residual_risk = await self.calculate_residual_risk(
                    initial_risk=risks[0],
                    mitigations=risks[0].mitigation_strategies,
                )
                residual_risks[principle] = residual_risk
            else:
                residual_risks[principle] = RiskLevel.LOW

        # Determine governance decision
        governance_decision = await self.determine_governance_decision(residual_risks)

        # Generate decision reasoning
        decision_reasoning = self._generate_decision_reasoning(governance_decision, residual_risks)

        # Create monitoring plan
        monitoring_plan = ContinuousMonitoringPlan(
            metrics_to_monitor=["Fairness metrics", "Privacy compliance", "Safety incidents"],
            monitoring_frequency="Weekly",
            alert_thresholds={"fairness_deviation": 0.1, "privacy_breaches": 0.0},
            review_process="Monthly ethics review",
            escalation_procedure="Immediate escalation to ethics committee",
        )

        # Determine if committee review required
        requires_committee_review = governance_decision in [
            GovernanceDecision.SUBMIT_TO_COMMITTEE,
            GovernanceDecision.HALT,
        ]

        report = EthicalRiskReport(
            initial_risks=initial_risks,
            mitigation_strategies=mitigation_strategies,
            residual_risks=residual_risks,
            governance_decision=governance_decision,
            decision_reasoning=decision_reasoning,
            monitoring_plan=monitoring_plan,
            requires_committee_review=requires_committee_review,
            created_at=datetime.now(),
            version="1.0",
        )

        logger.info(
            f"EthicalRiskReport created: {len(report.initial_risks)} risk categories, "
            f"decision: {report.governance_decision.value}"
        )

        return report

    def _generate_decision_reasoning(
        self,
        decision: GovernanceDecision,
        residual_risks: dict[EthicalPrinciple, RiskLevel],
    ) -> str:
        """
        Generate human-readable reasoning for governance decision.

        Args:
            decision: The governance decision made
            residual_risks: The residual risk levels by principle

        Returns:
            String explaining the decision
        """
        risk_summary = ", ".join(
            f"{principle.value}: {level.name}" for principle, level in residual_risks.items()
        )

        if decision == GovernanceDecision.HALT:
            return f"Project cannot proceed due to unacceptable risk levels. Residual risks: {risk_summary}. Critical risks must be addressed before deployment."

        elif decision == GovernanceDecision.SUBMIT_TO_COMMITTEE:
            return f"Project requires AI Review Committee evaluation due to elevated risk levels. Residual risks: {risk_summary}. Awaiting committee decision."

        elif decision == GovernanceDecision.REVISE:
            return f"Project requires design revisions to reduce ethical risks. Residual risks: {risk_summary}. Address high risks before proceeding."

        elif decision == GovernanceDecision.PROCEED_WITH_MONITORING:
            return f"Project approved with mandatory ongoing monitoring. Residual risks: {risk_summary}. Comprehensive oversight required."

        else:  # PROCEED
            return f"Project approved to proceed with standard monitoring. Residual risks: {risk_summary}. All risks at acceptable levels."
