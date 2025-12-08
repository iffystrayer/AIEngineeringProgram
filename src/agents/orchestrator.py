"""
Orchestrator Agent

Main coordinator for the U-AIP multi-stage interview workflow.
Manages session lifecycle, routes between specialized agents,
enforces stage-gate progression, and generates final AI Project Charter.

Based on SWE Specification Section 7.1 - Orchestrator Agent.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Union
from uuid import UUID, uuid4

# Python 3.9 compatibility - UTC was added in Python 3.11
try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc  # type: ignore

from src.utils.logging_sanitizer import setup_sanitized_logging
from src.exceptions import (
    SessionNotFoundError,
    InvalidStageNumberError,
    StageSkipError,
    CharterGenerationError,
)
from src.agents.stage1_business_translation import Stage1Agent
from src.agents.stage2_agent import Stage2Agent
from src.agents.stage3_agent import Stage3Agent
from src.agents.stage4_agent import Stage4Agent
from src.agents.stage5_agent import Stage5Agent
from src.agents.reflection.response_quality_agent import ResponseQualityAgent
from src.agents.reflection.stage_gate_validator_agent import StageGateValidatorAgent
from src.agents.reflection.consistency_checker_agent import ConsistencyCheckerAgent
from src.database.repositories.session_repository import SessionRepository
from src.database.repositories.checkpoint_repository import CheckpointRepository
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

# M-1 Security Fix: Enable PII sanitization for this logger
setup_sanitized_logging(logger)


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
        llm_router: Union[Any, None] = None,
        config: Union[dict[str, Any], None] = None,
        db_manager: Union[Any, None] = None,
    ):
        """
        Initialize Orchestrator with required dependencies.

        Args:
            db_pool: Database connection pool for persistence
            llm_router: LLM router for agent communication (optional for testing)
            config: Configuration dictionary (optional)
            db_manager: DatabaseManager instance for repository initialization
        """
        self.db_pool = db_pool
        self.db_manager = db_manager
        self.llm_router = llm_router
        self.config = config or {}

        # Initialize repositories for database access
        if db_manager:
            self.session_repo: Union[SessionRepository, None] = SessionRepository(db_manager)
            self.checkpoint_repo: Union[CheckpointRepository, None] = CheckpointRepository(db_manager)
        else:
            self.session_repo: Union[SessionRepository, None] = None
            self.checkpoint_repo: Union[CheckpointRepository, None] = None

        # Agent registries - will be populated when agents are implemented
        self.stage_agents: dict[int, Any] = {}
        self.reflection_agents: dict[str, Any] = {}

        # Initialize registries (placeholder until agents exist)
        self._initialize_agent_registries()

        # Session state tracking
        self.active_sessions: dict[UUID, Session] = {}

        # M-2 Security Fix: Async locks for thread-safe state management
        self._session_locks: dict[UUID, asyncio.Lock] = {}
        self._global_lock: asyncio.Lock = asyncio.Lock()

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

        IMPORTANT: Reflection agents must be initialized before stage agents
        so that the quality_agent can be passed to stage agent factories.
        """
        # Initialize reflection agents FIRST (3 total)
        if self.llm_router:
            self.reflection_agents["quality"] = ResponseQualityAgent(
                llm_router=self.llm_router,
                quality_threshold=7,
                max_reflection_loops=3
            )
            self.reflection_agents["stage_gate"] = StageGateValidatorAgent(
                llm_router=self.llm_router
            )
            self.reflection_agents["consistency"] = ConsistencyCheckerAgent(
                llm_router=self.llm_router
            )
            logger.info("Initialized reflection agents: Quality, StageGate, Consistency")
        else:
            # Placeholder agents if no LLM router (for testing)
            self.reflection_agents["quality"] = None
            self.reflection_agents["stage_gate"] = None
            self.reflection_agents["consistency"] = None
            logger.warning("LLM router not provided - reflection agents not initialized")

        # Get quality agent for stage agents
        quality_agent = self.reflection_agents.get("quality")

        # Stage agent factory functions
        # Each returns a lambda that creates an agent with session context AND quality agent
        # This enables ConversationEngine integration for quality-validated conversations
        self.stage_agents = {
            1: lambda session: Stage1Agent(
                session_context=session,
                llm_router=self.llm_router,
                quality_agent=quality_agent,  # Enable ConversationEngine
                quality_threshold=7.0,
                max_quality_attempts=3
            ),
            2: lambda session: Stage2Agent(
                session_context=session,
                llm_router=self.llm_router,
                quality_agent=quality_agent,  # Enable ConversationEngine
                quality_threshold=7.0,
                max_quality_attempts=3
            ),
            3: lambda session: Stage3Agent(
                session_context=session,
                llm_router=self.llm_router,
                quality_agent=quality_agent,  # Enable ConversationEngine
                quality_threshold=7.0,
                max_quality_attempts=3
            ),
            4: lambda session: Stage4Agent(
                session_context=session,
                llm_router=self.llm_router,
                quality_agent=quality_agent,  # Enable ConversationEngine
                quality_threshold=7.0,
                max_quality_attempts=3
            ),
            5: lambda session: Stage5Agent(
                session_context=session,
                llm_router=self.llm_router,
                quality_agent=quality_agent,  # Enable ConversationEngine
                quality_threshold=7.0,
                max_quality_attempts=3
            ),
        }

        if quality_agent:
            logger.info("Stage agents configured with ConversationEngine integration (quality_agent enabled)")
        else:
            logger.info("Stage agents configured without ConversationEngine (fallback mode)")

    # ========================================================================
    # M-2: LOCK MANAGEMENT HELPERS
    # ========================================================================

    def _get_session_lock(self, session_id: UUID) -> asyncio.Lock:
        """
        Get or create lock for specific session.

        M-2 Security Fix: Prevents race conditions when multiple coroutines
        access same session concurrently.

        Args:
            session_id: Session UUID

        Returns:
            Async lock for the session
        """
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]

    async def _cleanup_session_lock(self, session_id: UUID) -> None:
        """
        Clean up lock for completed/deleted session.

        Args:
            session_id: Session UUID
        """
        if session_id in self._session_locks:
            del self._session_locks[session_id]

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

        M-2 Security Fix: Uses global lock to prevent race conditions during
        session creation (e.g., duplicate session IDs, concurrent registry updates).

        Args:
            user_id: User identifier
            project_name: Name of the AI project

        Returns:
            Session: Newly created session object
        """
        # M-2: Use global lock for session creation
        async with self._global_lock:
            session = Session(
                session_id=uuid4(),
                user_id=user_id,
                project_name=project_name,
                started_at=datetime.utcnow(),
                last_updated_at=datetime.utcnow(),
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

        # Persist to database (outside lock - I/O operation)
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

        # M-3: Use specific exception for better error handling
        raise SessionNotFoundError(str(session_id))

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

        # M-3: Use specific exception
        raise SessionNotFoundError(str(session_id))

    # ========================================================================
    # STAGE EXECUTION
    # ========================================================================

    async def run_stage(self, session: Session, stage_number: int) -> Any:
        """
        Execute a specific stage agent.

        M-2 Security Fix: Uses session-specific lock to prevent concurrent
        execution of same session (e.g., duplicate API calls, race conditions
        in stage_data updates).

        Args:
            session: Current session
            stage_number: Stage number to execute (1-5)

        Returns:
            Stage deliverable output (ProblemStatement, MetricAlignmentMatrix, etc.)

        Raises:
            ValueError: If stage_number is invalid or out of order
        """
        # M-2: Acquire session-specific lock for thread-safe execution
        lock = self._get_session_lock(session.session_id)
        async with lock:
            # M-3: Validate stage progression with specific exceptions
            if stage_number not in range(1, 6):
                raise InvalidStageNumberError(stage_number)

            if stage_number != session.current_stage:
                if stage_number > session.current_stage + 1:
                    raise StageSkipError(
                        requested_stage=stage_number,
                        current_stage=session.current_stage
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

        # Execute stage agent interview (outside lock - long-running operation)
        stage_output = await stage_agent.conduct_interview()

        # Re-acquire lock for state updates
        async with lock:
            # Store stage output in session
            session.stage_data[stage_number] = stage_output
            session.last_updated_at = datetime.utcnow()

            logger.info(
                f"Stage {stage_number} completed for session {session.session_id}. "
                f"Output type: {type(stage_output).__name__}"
            )

        # Persist session updates to database (outside lock - I/O operation)
        if self.session_repo:
            try:
                await self.session_repo.update(session)
                logger.info(f"Persisted stage {stage_number} completion to database")
            except Exception as e:
                logger.error(f"Failed to persist stage completion: {e}", exc_info=True)
                # CRITICAL: Raise the exception to prevent silent data loss
                raise RuntimeError(
                    f"Failed to save stage {stage_number} completion to database. "
                    f"Please retry the operation. Error: {str(e)}"
                ) from e

        return stage_output

    async def advance_to_next_stage(self, session: Session) -> None:
        """
        Advance session to next stage and create checkpoint.

        M-2 Security Fix: Uses lock to ensure atomic stage advancement.

        SWE Spec Compliance: Enforces stage-gate validation before progression (FR-1.2, FR-4).

        Args:
            session: Current session

        Raises:
            ValueError: If stage gate validation fails
        """
        # SWE Spec FR-4: Stage Gate Validation BEFORE advancement
        completed_stage = session.current_stage
        validation = await self.invoke_stage_gate_validator(session, completed_stage)

        if not validation.can_proceed:
            logger.warning(
                f"Stage gate validation failed for stage {completed_stage}. "
                f"Missing items: {validation.missing_items}. "
                f"Concerns: {validation.validation_concerns}"
            )
            raise ValueError(
                f"Cannot advance from stage {completed_stage}: "
                f"Stage gate validation failed. "
                f"Missing: {', '.join(validation.missing_items)}. "
                f"Please complete all required fields before proceeding."
            )

        logger.info(f"Stage gate validation passed for stage {completed_stage} "
                   f"(completeness: {validation.completeness_score:.2f})")

        # M-2: Lock for atomic stage advancement
        lock = self._get_session_lock(session.session_id)
        async with lock:
            session.current_stage += 1
            session.last_updated_at = datetime.utcnow()

            # Mark as completed if past stage 5
            if session.current_stage > 5:
                session.status = SessionStatus.COMPLETED

        # Create checkpoint (has its own locking)
        await self.save_checkpoint(session, session.current_stage - 1)

        # Persist session advancement to database (outside lock - I/O operation)
        if self.session_repo:
            try:
                await self.session_repo.update(session)
                logger.info(f"Persisted stage advancement to database")
            except Exception as e:
                logger.error(f"Failed to persist stage advancement: {e}")

        logger.info(f"Advanced session {session.session_id} to stage {session.current_stage}")

    # ========================================================================
    # REFLECTION AGENT INVOCATION
    # ========================================================================

    async def invoke_quality_agent(
        self,
        question: str,
        response: str,
        session: Session,
    ) -> QualityAssessment:
        """
        Invoke ResponseQualityAgent to evaluate user response.

        Args:
            question: The question that was asked
            response: User response text to evaluate
            session: Current session context

        Returns:
            QualityAssessment: Quality evaluation result
        """
        quality_agent = self.reflection_agents.get("quality")

        if quality_agent is None:
            logger.warning("Quality agent not initialized")
            # Placeholder assessment - accept everything
            return QualityAssessment(
                quality_score=8,
                is_acceptable=True,
                issues=[],
                suggested_followups=[],
                examples_to_provide=[],
            )

        # Track quality attempts
        stage = session.current_stage
        if session.session_id not in self.quality_attempts:
            self.quality_attempts[session.session_id] = {}
        if stage not in self.quality_attempts[session.session_id]:
            self.quality_attempts[session.session_id][stage] = 0

        self.quality_attempts[session.session_id][stage] += 1

        # Check if max attempts exceeded
        if self.quality_attempts[session.session_id][stage] > self.max_quality_attempts:
            logger.warning(
                f"Max quality attempts ({self.max_quality_attempts}) exceeded for "
                f"session {session.session_id} stage {stage}"
            )
            return QualityAssessment(
                quality_score=7,  # Force acceptance after max attempts
                is_acceptable=True,
                issues=[],
                suggested_followups=[],
                examples_to_provide=[],
            )

        # Execute quality agent
        stage_context = {
            "stage": session.current_stage,
            "stage_name": f"Stage {session.current_stage}"
        }

        assessment = await quality_agent.evaluate_response(
            question=question,
            user_response=response,
            stage_context=stage_context
        )

        logger.info(
            f"Quality assessment for session {session.session_id} stage {stage}: "
            f"score={assessment.quality_score}, acceptable={assessment.is_acceptable}"
        )
        return assessment

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
            logger.warning("Stage gate validator not initialized")
            # Placeholder validation - always pass
            return StageValidation(
                can_proceed=True,
                completeness_score=1.0,
                missing_items=[],
                validation_concerns=[],
                recommendations=[],
            )

        # Get stage data from session
        collected_data = session.stage_data.get(stage_number)

        # Execute validator
        validation = await validator.validate_stage(
            stage_number=stage_number,
            collected_data=collected_data
        )

        logger.info(
            f"Stage gate validation for stage {stage_number}: "
            f"can_proceed={validation.can_proceed}, "
            f"completeness={validation.completeness_score:.2f}"
        )
        return validation

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
            logger.warning("Consistency checker not initialized")
            # Placeholder consistency report - always pass
            return ConsistencyReport(
                is_consistent=True,
                overall_feasibility=FeasibilityLevel.HIGH,
                contradictions=[],
                risk_areas=[],
                recommendations=[],
            )

        # Prepare all stages data for consistency checking
        all_stages_data = {
            f"stage{i}": session.stage_data.get(i)
            for i in range(1, 6)
            if session.stage_data.get(i) is not None
        }

        # Execute consistency checker
        report = await checker.check_consistency(all_stages_data)

        logger.info(
            f"Consistency check for session {session.session_id}: "
            f"is_consistent={report.is_consistent}, "
            f"feasibility={report.overall_feasibility.value}, "
            f"contradictions={len(report.contradictions)}"
        )
        return report

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

        SWE Spec Compliance: Performs cross-stage consistency checking before charter generation (FR-5).

        Args:
            session: Completed session with all stage data

        Returns:
            AIProjectCharter: Complete project charter

        Raises:
            ValueError: If session not completed or missing stage data
            CharterGenerationError: If consistency check fails critically
        """
        # M-3: Use specific exceptions for charter generation errors
        if session.status != SessionStatus.COMPLETED:
            raise CharterGenerationError(
                "Session must be completed before generating charter",
                missing_stages=[]
            )

        if len(session.stage_data) < 5:
            missing_stages = [i for i in range(1, 6) if i not in session.stage_data]
            raise CharterGenerationError(
                "All 5 stages must be completed",
                missing_stages=missing_stages
            )

        # SWE Spec FR-5: Cross-Stage Consistency Checking
        logger.info("Running cross-stage consistency check before charter generation...")
        consistency_report = await self.invoke_consistency_checker(session)

        if not consistency_report.is_consistent:
            logger.warning(
                f"Consistency check found issues: "
                f"{len(consistency_report.contradictions)} contradictions, "
                f"{len(consistency_report.risk_areas)} risk areas. "
                f"Feasibility: {consistency_report.overall_feasibility.value}"
            )

            # If feasibility is INFEASIBLE, block charter generation
            if consistency_report.overall_feasibility == FeasibilityLevel.INFEASIBLE:
                raise CharterGenerationError(
                    f"Cannot generate charter: Project has critical inconsistencies. "
                    f"Contradictions: {', '.join(consistency_report.contradictions[:3])}. "
                    f"Please revise stages to resolve conflicts.",
                    missing_stages=[]
                )

            # For other feasibility levels, warn but allow charter generation
            logger.warning(
                f"Generating charter with consistency concerns. "
                f"Recommendations: {', '.join(consistency_report.recommendations[:3])}"
            )
        else:
            logger.info(
                f"Consistency check passed. "
                f"Overall feasibility: {consistency_report.overall_feasibility.value}"
            )

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

        # Extract major risks from Stage 5 (ethical risks from initial_risks dict)
        major_risks = []
        for principle, risks in ethical_report.initial_risks.items():
            for risk in risks:
                major_risks.append(
                    f"{principle.value}: {risk.risk_description} "
                    f"(Severity: {risk.severity.value}/5, Residual: {risk.residual_risk.value}/5)"
                )

        # Create charter
        charter = AIProjectCharter(
            session_id=session.session_id,
            project_name=session.project_name,
            created_at=session.started_at,
            completed_at=datetime.utcnow(),
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

        M-2 Security Fix: Uses lock to prevent concurrent checkpoint creation
        and ensure data consistency.

        Args:
            session: Current session
            stage_number: Stage number that was completed

        Returns:
            Checkpoint: Created checkpoint
        """
        # M-2: Lock for checkpoint creation
        lock = self._get_session_lock(session.session_id)
        async with lock:
            checkpoint = Checkpoint(
                stage_number=stage_number,
                timestamp=datetime.utcnow(),
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

        # Persist to database (outside lock - I/O operation)
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
    # DATABASE PERSISTENCE
    # ========================================================================

    async def _persist_session(self, session: Session) -> None:
        """
        Persist session to database.

        Uses SessionRepository to save session state including stage data,
        conversation history, and checkpoints.
        """
        if not self.session_repo:
            logger.debug("No session repository available, skipping session persistence")
            return

        try:
            await self.session_repo.create(session)
            logger.info(f"Persisted session {session.session_id} to database")
        except Exception as e:
            logger.error(f"Failed to persist session {session.session_id}: {e}")
            # Don't raise - allow session to continue even if persistence fails

    async def _load_session_from_db(self, session_id: UUID) -> Union[Session, None]:
        """
        Load session from database.

        Retrieves session state including stage data, conversation history,
        and checkpoints from the database.

        Args:
            session_id: Session UUID to load

        Returns:
            Session object if found, None otherwise
        """
        if not self.session_repo:
            logger.debug("No session repository available, cannot load session")
            return None

        try:
            session = await self.session_repo.get_by_id(session_id)
            if session:
                logger.info(f"Loaded session {session_id} from database")
            return session
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    async def _persist_checkpoint(self, session: Session, checkpoint: Checkpoint) -> None:
        """
        Persist checkpoint to database.

        Saves checkpoint data including stage data snapshot and validation status.

        Args:
            session: Session object
            checkpoint: Checkpoint to persist
        """
        if not self.checkpoint_repo:
            logger.debug("No checkpoint repository available, skipping checkpoint persistence")
            return

        try:
            await self.checkpoint_repo.create(session.session_id, checkpoint)
            logger.info(f"Persisted checkpoint for stage {checkpoint.stage_number} to database")
        except Exception as e:
            logger.error(f"Failed to persist checkpoint: {e}")

    async def _load_checkpoint_from_db(self, checkpoint_id: str) -> Union[Session, None]:
        """
        Load session from specific checkpoint in database.

        Retrieves the session state as it was at the time of the checkpoint.

        Args:
            checkpoint_id: Checkpoint UUID to load

        Returns:
            Session object if checkpoint found, None otherwise
        """
        if not self.checkpoint_repo:
            logger.debug("No checkpoint repository available, cannot load checkpoint")
            return None

        try:
            session = await self.checkpoint_repo.get_session_from_checkpoint(checkpoint_id)
            if session:
                logger.info(f"Loaded session from checkpoint {checkpoint_id}")
            return session
        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            return None
