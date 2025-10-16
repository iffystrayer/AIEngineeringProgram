"""
Orchestrator Agent

Main coordinator for the U-AIP multi-stage interview workflow.
Manages session lifecycle, routes between specialized agents,
enforces stage-gate progression, and generates final AI Project Charter.

Based on SWE Specification Section 7.1 - Orchestrator Agent.
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.agents.stage1_business_translation import Stage1Agent
from src.agents.stage2_agent import Stage2Agent
from src.agents.stage3_agent import Stage3Agent
from src.agents.stage4_agent import Stage4Agent
from src.agents.stage5_agent import Stage5Agent
from src.models.schemas import (
    AIProjectCharter,
    AgentType,
    Checkpoint,
    ConsistencyReport,
    DataQualityScorecard,
    EthicalRiskReport,
    FeasibilityLevel,
    GovernanceDecision,
    Message,
    MetricAlignmentMatrix,
    ProblemStatement,
    QualityAssessment,
    Session,
    SessionStatus,
    StageValidation,
    UserContext,
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestration agent coordinating the multi-stage interview workflow.

    Responsibilities:
    - Manage user session lifecycle (create, resume, persist)
    - Route control between specialized agents
    - Enforce stage-gate progression (1→2→3→4→5)
    - Invoke reflection agents at checkpoints
    - Generate final AI Project Charter
    - Make governance decisions based on ethical risk
    """

    def __init__(
        self,
        db_pool: Any,
        llm_router: Any | None = None,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize Orchestrator with required dependencies.

        Args:
            db_pool: Database connection pool for persistence
            llm_router: LLM router for agent communication (optional for testing)
            config: Configuration dictionary (optional)
        """
        self.db_pool = db_pool
        self.llm_router = llm_router
        self.config = config or {}

        # Agent registries - will be populated when agents are implemented
        self.stage_agents: dict[int, Any] = {}
        self.reflection_agents: dict[str, Any] = {}

        # Initialize registries (placeholder until agents exist)
        self._initialize_agent_registries()

        # Session state tracking
        self.active_sessions: dict[UUID, Session] = {}

        # Quality loop tracking
        self.quality_attempts: dict[UUID, dict[int, int]] = {}
        self.max_quality_attempts = 3

        logger.info("Orchestrator initialized")

    def _initialize_agent_registries(self) -> None:
        """
        Initialize agent registries for stage and reflection agents.

        Stage agents are created as factory functions that take session context
        and return configured agent instances. This allows each session to have
        its own agent instances with proper session-specific context.
        """
        # Stage agent factory functions
        # Each returns a lambda that creates an agent with session context
        self.stage_agents = {
            1: lambda session: Stage1Agent(
                session_context=session,
                llm_router=self.llm_router,
            ),
            2: lambda session: Stage2Agent(
                session_context=session,
                llm_router=self.llm_router,
            ),
            3: lambda session: Stage3Agent(
                session_context=session,
                llm_router=self.llm_router,
            ),
            4: lambda session: Stage4Agent(
                session_context=session,
                llm_router=self.llm_router,
            ),
            5: lambda session: Stage5Agent(
                session_context=session,
                llm_router=self.llm_router,
            ),
        }

        # Reflection agents (3 total) - still placeholder
        self.reflection_agents["quality"] = None  # ResponseQualityAgent
        self.reflection_agents["stage_gate"] = None  # StageGateValidatorAgent
        self.reflection_agents["consistency"] = None  # ConsistencyCheckerAgent

    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================

    async def create_session(
        self,
        user_id: str,
        project_name: str,
    ) -> Session:
        """
        Create a new user session.

        Args:
            user_id: User identifier
            project_name: Name of the AI project

        Returns:
            Session: Newly created session object
        """
        session = Session(
            session_id=uuid4(),
            user_id=user_id,
            project_name=project_name,
            started_at=datetime.now(UTC),
            last_updated_at=datetime.now(UTC),
            current_stage=1,
            stage_data={},
            conversation_history=[],
            status=SessionStatus.IN_PROGRESS,
            checkpoints=[],
        )

        # Store in active sessions
        self.active_sessions[session.session_id] = session

        # Initialize quality tracking
        self.quality_attempts[session.session_id] = {}

        # Persist to database
        if self.db_pool:
            await self._persist_session(session)

        logger.info(f"Created session {session.session_id} for user {user_id}")
        return session

    async def resume_session(self, session_id: UUID) -> Session:
        """
        Resume an existing session from checkpoint.

        Args:
            session_id: Session identifier to resume

        Returns:
            Session: Resumed session object

        Raises:
            ValueError: If session not found
        """
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Load from database
        if self.db_pool:
            session = await self._load_session_from_db(session_id)
            if session:
                self.active_sessions[session_id] = session
                logger.info(f"Resumed session {session_id}")
                return session

        raise ValueError(f"Session not found: {session_id}")

    async def get_session_state(self, session_id: UUID) -> Session:
        """
        Get current session state and progress.

        Args:
            session_id: Session identifier

        Returns:
            Session: Current session state
        """
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        raise ValueError(f"Session not found: {session_id}")

    # ========================================================================
    # STAGE EXECUTION
    # ========================================================================

    async def run_stage(self, session: Session, stage_number: int) -> Any:
        """
        Execute a specific stage agent.

        Args:
            session: Current session
            stage_number: Stage number to execute (1-5)

        Returns:
            Stage deliverable output (ProblemStatement, MetricAlignmentMatrix, etc.)

        Raises:
            ValueError: If stage_number is invalid or out of order
        """
        # Validate stage progression
        if stage_number not in range(1, 6):
            raise ValueError(f"Invalid stage number: {stage_number}")

        if stage_number != session.current_stage:
            if stage_number > session.current_stage + 1:
                raise ValueError(
                    f"Cannot skip to stage {stage_number}. "
                    f"Current stage is {session.current_stage}"
                )

        # Get stage agent factory
        agent_factory = self.stage_agents.get(stage_number)
        if agent_factory is None:
            logger.warning(f"Stage {stage_number} agent not implemented yet")
            # For now, create placeholder data
            stage_data = {"stage": stage_number, "completed": True}
            session.stage_data[stage_number] = stage_data
            return stage_data

        # Create agent instance with session context
        logger.info(f"Running stage {stage_number} for session {session.session_id}")
        stage_agent = agent_factory(session)

        # Execute stage agent interview
        stage_output = await stage_agent.conduct_interview()

        # Store stage output in session
        session.stage_data[stage_number] = stage_output
        session.last_updated_at = datetime.now(UTC)

        logger.info(
            f"Stage {stage_number} completed for session {session.session_id}. "
            f"Output type: {type(stage_output).__name__}"
        )

        return stage_output

    async def advance_to_next_stage(self, session: Session) -> None:
        """
        Advance session to next stage and create checkpoint.

        Args:
            session: Current session
        """
        session.current_stage += 1
        session.last_updated_at = datetime.now(UTC)

        # Mark as completed if past stage 5
        if session.current_stage > 5:
            session.status = SessionStatus.COMPLETED

        # Create checkpoint
        await self.save_checkpoint(session, session.current_stage - 1)

        logger.info(f"Advanced session {session.session_id} to stage {session.current_stage}")

    # ========================================================================
    # REFLECTION AGENT INVOCATION
    # ========================================================================

    async def invoke_quality_agent(
        self,
        response: str,
        session: Session,
    ) -> QualityAssessment:
        """
        Invoke ResponseQualityAgent to evaluate user response.

        Args:
            response: User response text to evaluate
            session: Current session context

        Returns:
            QualityAssessment: Quality evaluation result
        """
        quality_agent = self.reflection_agents.get("quality")

        if quality_agent is None:
            logger.warning("Quality agent not implemented yet")
            # Placeholder assessment
            return QualityAssessment(
                quality_score=8,
                is_acceptable=True,
                issues=[],
                suggested_followups=[],
                examples_to_provide=[],
            )

        # Track quality attempts
        stage = session.current_stage
        if stage not in self.quality_attempts.get(session.session_id, {}):
            self.quality_attempts[session.session_id][stage] = 0

        self.quality_attempts[session.session_id][stage] += 1

        # Execute quality agent (will be implemented when agent exists)
        # assessment = await quality_agent.evaluate(response, session)

        logger.info(f"Quality assessment for session {session.session_id}: placeholder")
        return QualityAssessment(
            quality_score=5,
            is_acceptable=False,
            issues=["Response needs more detail"],
            suggested_followups=["Can you provide more specific examples?"],
            examples_to_provide=[],
        )

    async def invoke_stage_gate_validator(
        self,
        session: Session,
        stage_number: int,
    ) -> StageValidation:
        """
        Invoke StageGateValidatorAgent to validate stage completion.

        Args:
            session: Current session
            stage_number: Stage number to validate

        Returns:
            StageValidation: Validation result
        """
        validator = self.reflection_agents.get("stage_gate")

        if validator is None:
            logger.warning("Stage gate validator not implemented yet")
            return StageValidation(
                can_proceed=True,
                completeness_score=1.0,
                missing_items=[],
                validation_concerns=[],
                recommendations=[],
            )

        # Execute validator (will be implemented when agent exists)
        # validation = await validator.validate(session, stage_number)

        logger.info(f"Stage gate validation for stage {stage_number}: placeholder")
        return StageValidation(
            can_proceed=True,
            completeness_score=0.9,
            missing_items=[],
            validation_concerns=[],
            recommendations=[],
        )

    async def invoke_consistency_checker(self, session: Session) -> ConsistencyReport:
        """
        Invoke ConsistencyCheckerAgent for cross-stage validation.

        Args:
            session: Current session with all stage data

        Returns:
            ConsistencyReport: Cross-stage consistency analysis
        """
        checker = self.reflection_agents.get("consistency")

        if checker is None:
            logger.warning("Consistency checker not implemented yet")
            return ConsistencyReport(
                is_consistent=True,
                overall_feasibility=FeasibilityLevel.HIGH,
                contradictions=[],
                risk_areas=[],
                recommendations=[],
            )

        # Execute checker (will be implemented when agent exists)
        # report = await checker.check_consistency(session)

        logger.info(f"Consistency check for session {session.session_id}: placeholder")
        return ConsistencyReport(
            is_consistent=True,
            overall_feasibility=FeasibilityLevel.HIGH,
            contradictions=[],
            risk_areas=[],
            recommendations=[],
        )

    # ========================================================================
    # GOVERNANCE AND CHARTER GENERATION
    # ========================================================================

    async def make_governance_decision(self, risk_report: Any) -> GovernanceDecision:
        """
        Make automated governance decision based on ethical risk assessment.

        Args:
            risk_report: EthicalRiskReport from Stage 5

        Returns:
            GovernanceDecision: Automated governance decision
        """
        # Return the decision from the risk report
        if hasattr(risk_report, "governance_decision"):
            decision = risk_report.governance_decision
            logger.info(f"Governance decision: {decision}")
            return decision

        # Placeholder if risk report doesn't have decision
        return GovernanceDecision.PROCEED_WITH_MONITORING

    async def generate_charter(self, session: Session) -> AIProjectCharter:
        """
        Generate complete AI Project Charter from all stage data.

        Args:
            session: Completed session with all stage data

        Returns:
            AIProjectCharter: Complete project charter

        Raises:
            ValueError: If session not completed or missing stage data
        """
        if session.status != SessionStatus.COMPLETED:
            raise ValueError("Session must be completed before generating charter")

        if len(session.stage_data) < 5:
            raise ValueError("All 5 stages must be completed")

        # Extract stage deliverables
        problem_statement: ProblemStatement = session.stage_data.get(1)  # type: ignore
        metric_alignment: MetricAlignmentMatrix = session.stage_data.get(2)  # type: ignore
        data_quality: DataQualityScorecard = session.stage_data.get(3)  # type: ignore
        user_context: UserContext = session.stage_data.get(4)  # type: ignore
        ethical_report: EthicalRiskReport = session.stage_data.get(5)  # type: ignore

        # Get governance decision from Stage 5
        governance_decision = ethical_report.governance_decision

        # Determine overall feasibility based on ethical risks
        if governance_decision == GovernanceDecision.HALT:
            overall_feasibility = FeasibilityLevel.NOT_FEASIBLE
        elif governance_decision in [
            GovernanceDecision.SUBMIT_TO_COMMITTEE,
            GovernanceDecision.REVISE,
        ]:
            overall_feasibility = FeasibilityLevel.LOW
        elif governance_decision == GovernanceDecision.PROCEED_WITH_MONITORING:
            overall_feasibility = FeasibilityLevel.MEDIUM
        else:
            overall_feasibility = FeasibilityLevel.HIGH

        # Extract critical success factors from Stage 2 (KPIs)
        critical_success_factors = [
            f"{kpi.name}: {kpi.description} (Target: {kpi.target_value})"
            for kpi in metric_alignment.business_kpis
        ]

        # Extract major risks from Stage 5 (ethical risks)
        major_risks = [
            f"{risk.principle.value}: {risk.description} (Severity: {risk.severity}/5, "
            f"Residual: {risk.residual_risk_level.value})"
            for risk in ethical_report.ethical_risks
        ]

        # Create charter
        charter = AIProjectCharter(
            session_id=session.session_id,
            project_name=session.project_name,
            created_at=session.started_at,
            completed_at=datetime.now(UTC),
            problem_statement=problem_statement,
            metric_alignment_matrix=metric_alignment,
            data_quality_scorecard=data_quality,
            user_context=user_context,
            ethical_risk_report=ethical_report,
            governance_decision=governance_decision,
            overall_feasibility=overall_feasibility,
            critical_success_factors=critical_success_factors,
            major_risks=major_risks,
        )

        logger.info(
            f"Generated charter for session {session.session_id}: "
            f"Decision={governance_decision.value}, "
            f"Feasibility={overall_feasibility.value}"
        )

        return charter

    # ========================================================================
    # CHECKPOINT MANAGEMENT
    # ========================================================================

    async def save_checkpoint(self, session: Session, stage_number: int) -> Checkpoint:
        """
        Save checkpoint after stage completion.

        Args:
            session: Current session
            stage_number: Stage number that was completed

        Returns:
            Checkpoint: Created checkpoint
        """
        checkpoint = Checkpoint(
            stage_number=stage_number,
            timestamp=datetime.now(UTC),
            data_snapshot={
                "stage_data": session.stage_data.copy(),
                "conversation_history": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                    for msg in session.conversation_history
                ],
                "current_stage": session.current_stage,
            },
            validation_status=True,
            session_id=session.session_id,
        )

        session.checkpoints.append(checkpoint)

        # Persist to database
        if self.db_pool:
            await self._persist_checkpoint(session, checkpoint)

        logger.info(f"Saved checkpoint for stage {stage_number}")
        return checkpoint

    async def load_checkpoint(self, checkpoint_id: str) -> Session:
        """
        Load session from specific checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Session: Restored session

        Raises:
            ValueError: If checkpoint not found or corrupted
        """
        # Load from database
        if self.db_pool:
            session = await self._load_checkpoint_from_db(checkpoint_id)
            if session:
                self.active_sessions[session.session_id] = session
                logger.info(f"Loaded session from checkpoint {checkpoint_id}")
                return session

        raise ValueError(f"Checkpoint not found: {checkpoint_id}")

    # ========================================================================
    # DATABASE PERSISTENCE (Placeholder implementations)
    # ========================================================================

    async def _persist_session(self, session: Session) -> None:
        """Persist session to database."""
        if not self.db_pool:
            return

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Handle both real pool and mock pool
                conn_context = self.db_pool.acquire()
                # For mocks, acquire() might be a coroutine that needs awaiting
                if asyncio.iscoroutine(conn_context):
                    conn = await conn_context
                    # Database persistence logic (placeholder)
                    logger.debug(f"Persisted session {session.session_id}")
                    return
                else:
                    async with conn_context as conn:
                        # Database persistence logic (placeholder)
                        logger.debug(f"Persisted session {session.session_id}")
                        return
            except ConnectionError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                raise e

    async def _load_session_from_db(self, session_id: UUID) -> Session | None:
        """Load session from database."""
        if not self.db_pool:
            return None

        try:
            conn_context = self.db_pool.acquire()
            if asyncio.iscoroutine(conn_context):
                conn = await conn_context
                # Database query logic (placeholder)
                logger.debug(f"Loaded session {session_id}")
                return None
            else:
                async with conn_context as conn:
                    # Database query logic (placeholder)
                    logger.debug(f"Loaded session {session_id}")
                    return None
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None

    async def _persist_checkpoint(self, session: Session, checkpoint: Checkpoint) -> None:
        """Persist checkpoint to database."""
        if not self.db_pool:
            return

        try:
            conn_context = self.db_pool.acquire()
            if asyncio.iscoroutine(conn_context):
                conn = await conn_context
                # Database persistence logic (placeholder)
                logger.debug(f"Persisted checkpoint for stage {checkpoint.stage_number}")
            else:
                async with conn_context as conn:
                    # Database persistence logic (placeholder)
                    logger.debug(f"Persisted checkpoint for stage {checkpoint.stage_number}")
        except Exception as e:
            logger.error(f"Failed to persist checkpoint: {e}")

    async def _load_checkpoint_from_db(self, checkpoint_id: str) -> Session | None:
        """Load checkpoint from database."""
        if not self.db_pool:
            return None

        try:
            conn_context = self.db_pool.acquire()
            if asyncio.iscoroutine(conn_context):
                conn = await conn_context
                # Database query logic (placeholder)
                logger.debug(f"Loaded checkpoint {checkpoint_id}")
                return None
            else:
                async with conn_context as conn:
                    # Database query logic (placeholder)
                    logger.debug(f"Loaded checkpoint {checkpoint_id}")
                    return None
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
