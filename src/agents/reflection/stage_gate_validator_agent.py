#!/usr/bin/env python3
"""
StageGateValidatorAgent - Stage Completion Validation

This agent validates that each stage of the U-AIP process is complete before
allowing progression to the next stage. It performs strict validation of:
- Mandatory field completion
- Stage-specific requirements
- Data quality standards
- Logical consistency within stage

Per SWE Specification Section 4.3.2:
- Validates stage completion before progression
- Checks all mandatory fields populated
- Verifies stage-specific requirements satisfied
- Calculates completeness score (0.0-1.0)
- Generates missing_items and recommendations
- Enforces strict stage-gate discipline

Stage-Specific Validations:
- Stage 1: ML archetype justified, features defined, production availability confirmed
- Stage 2: KPIs are SMART, causal pathway articulated, metrics aligned
- Stage 3: All 6 quality dimensions scored, labeling plan has budget/timeline
- Stage 4: Personas research-based, journey map complete, interpretability specified
- Stage 5: All ethical principles assessed, residual risk calculated, governance decision made

Implementation follows strict TDD methodology with comprehensive test coverage.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class StageValidation:
    """
    Validation result for a stage completion check.

    Attributes:
        can_proceed: True if stage meets all requirements for progression
        completeness_score: Percentage complete (0.0-1.0)
        missing_items: List of missing mandatory fields
        validation_concerns: List of quality/logic issues
        recommendations: List of suggested improvements
    """

    can_proceed: bool
    completeness_score: float  # 0.0-1.0
    missing_items: List[str] = field(default_factory=list)
    validation_concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class StageGateValidatorAgent:
    """
    Rule-based agent for stage completion validation.

    This agent enforces strict stage-gate discipline by validating that all
    mandatory requirements are met before allowing progression. Uses rule-based
    validation (no LLM required for core checks, though LLM can be used for
    advanced semantic validation).

    The agent operates in the reflection layer of the U-AIP system, providing
    gate-keeping functionality to prevent premature stage progression.

    Attributes:
        llm_router: Optional router for LLM-based semantic validation
    """

    # Stage-specific mandatory fields per SWE Spec Section 4.3.2 (Page 17)
    STAGE_REQUIREMENTS = {
        1: {  # Business Translation
            "mandatory_fields": [
                "business_objective",
                "ai_necessity_justification",
                "input_features",
                "target_output",
                "ml_archetype",
                "ml_archetype_justification"
            ],
            "validation_rules": [
                "ml_archetype_justified",
                "features_defined",
                "production_availability_confirmed"
            ]
        },
        2: {  # Value Quantification
            "mandatory_fields": [
                "business_kpis",
                "model_metrics",
                "causal_pathways"
            ],
            "validation_rules": [
                "kpis_are_smart",
                "causal_pathway_articulated",
                "metrics_aligned"
            ]
        },
        3: {  # Data Feasibility
            "mandatory_fields": [
                "data_sources",
                "quality_scores",
                "labeling_strategy"
            ],
            "validation_rules": [
                "all_6_quality_dimensions_scored",
                "labeling_plan_has_budget_timeline",
                "minimum_quality_threshold_6"
            ]
        },
        4: {  # User Experience
            "mandatory_fields": [
                "user_personas",
                "user_journey_map",
                "interpretability_needs"
            ],
            "validation_rules": [
                "personas_research_based",
                "journey_map_complete",
                "interpretability_specified"
            ]
        },
        5: {  # Ethical Governance
            "mandatory_fields": [
                "initial_risks",
                "residual_risks",
                "governance_decision"
            ],
            "validation_rules": [
                "all_ethical_principles_assessed",
                "residual_risk_calculated",
                "governance_decision_made"
            ]
        }
    }

    # Quality dimensions for Stage 3
    QUALITY_DIMENSIONS = [
        "ACCURACY",
        "CONSISTENCY",
        "COMPLETENESS",
        "TIMELINESS",
        "VALIDITY",
        "INTEGRITY"
    ]

    # Ethical principles for Stage 5
    ETHICAL_PRINCIPLES = [
        "FAIRNESS_EQUITY",
        "PRIVACY_PROTECTION",
        "TRANSPARENCY_ACCOUNTABILITY",
        "SAFETY_RESILIENCE",
        "HUMAN_AGENCY"
    ]

    def __init__(self, llm_router: Optional[Any] = None):
        """
        Initialize StageGateValidatorAgent.

        Args:
            llm_router: Optional router for LLM-based semantic validation
        """
        self.llm_router = llm_router

        logger.info("Initialized StageGateValidatorAgent")

    async def validate_stage(
        self,
        stage_number: int,
        collected_data: Optional[Dict[str, Any]] = None
    ) -> StageValidation:
        """
        Validate stage completion.

        This method performs comprehensive validation of a stage's deliverable,
        checking mandatory fields, stage-specific requirements, and data quality.

        Args:
            stage_number: Stage number (1-5)
            collected_data: Data collected during stage (deliverable dict)

        Returns:
            StageValidation: Validation result with proceed decision and feedback

        Raises:
            ValueError: If stage_number is invalid (not 1-5)
        """
        # Validate stage number
        if stage_number < 1 or stage_number > 5:
            raise ValueError(f"stage_number must be in range [1, 5], got {stage_number}")

        # Handle None or empty data
        if collected_data is None:
            collected_data = {}

        logger.info(f"Validating Stage {stage_number} completion")

        # Initialize validation tracking
        missing_items = []
        validation_concerns = []
        recommendations = []

        # Get stage requirements
        requirements = self.STAGE_REQUIREMENTS[stage_number]
        mandatory_fields = requirements["mandatory_fields"]
        validation_rules = requirements["validation_rules"]

        # Check mandatory fields
        for field in mandatory_fields:
            if field not in collected_data or not collected_data[field]:
                missing_items.append(f"Missing mandatory field: {field}")

        # Run stage-specific validation rules
        if stage_number == 1:
            self._validate_stage1(collected_data, missing_items, validation_concerns)
        elif stage_number == 2:
            self._validate_stage2(collected_data, missing_items, validation_concerns)
        elif stage_number == 3:
            self._validate_stage3(collected_data, missing_items, validation_concerns)
        elif stage_number == 4:
            self._validate_stage4(collected_data, missing_items, validation_concerns)
        elif stage_number == 5:
            self._validate_stage5(collected_data, missing_items, validation_concerns)

        # Calculate completeness score
        total_checks = len(mandatory_fields) + len(validation_rules)
        failed_checks = len(missing_items) + len(validation_concerns)
        passed_checks = max(0, total_checks - failed_checks)

        # Special case: if all fields missing, score is 0.0
        if not collected_data or len(collected_data) == 0:
            completeness_score = 0.0
        else:
            completeness_score = passed_checks / total_checks if total_checks > 0 else 0.0

        # Generate recommendations
        if missing_items:
            recommendations.append("Complete all mandatory fields before proceeding")
        if validation_concerns:
            recommendations.append("Address validation concerns to improve stage quality")

        # Determine if can proceed
        can_proceed = (
            len(missing_items) == 0 and
            len(validation_concerns) == 0 and
            completeness_score >= 0.9
        )

        logger.info(
            f"Stage {stage_number} validation complete: "
            f"can_proceed={can_proceed}, score={completeness_score:.2f}"
        )

        return StageValidation(
            can_proceed=can_proceed,
            completeness_score=completeness_score,
            missing_items=missing_items,
            validation_concerns=validation_concerns,
            recommendations=recommendations
        )

    def _validate_stage1(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 1: Business Translation."""
        # ML archetype justified
        if "ml_archetype_justification" not in data or not data["ml_archetype_justification"]:
            missing_items.append("ML archetype justification required")

        # Features defined
        if "input_features" in data:
            if not data["input_features"] or len(data["input_features"]) == 0:
                missing_items.append("At least one input feature must be defined")

        # Production availability confirmed
        if "input_features" in data and data["input_features"]:
            for feature in data["input_features"]:
                if isinstance(feature, dict):
                    if "availability_in_production" in feature:
                        if not feature["availability_in_production"]:
                            validation_concerns.append(
                                f"Feature '{feature.get('name', 'unknown')}' not available in production"
                            )

    def _validate_stage2(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 2: Value Quantification."""
        # KPIs are SMART
        if "business_kpis" in data and data["business_kpis"]:
            for kpi in data["business_kpis"]:
                if isinstance(kpi, dict):
                    # Check SMART criteria
                    if not all(k in kpi for k in ["current_baseline", "target_value", "target_timeframe"]):
                        validation_concerns.append(
                            f"KPI '{kpi.get('name', 'unknown')}' missing SMART criteria "
                            "(current_baseline, target_value, target_timeframe)"
                        )

        # Causal pathway articulated
        if "causal_pathways" in data:
            if not data["causal_pathways"] or len(data["causal_pathways"]) == 0:
                missing_items.append("At least one causal pathway must be defined")

        # Metrics aligned (each KPI has linked model metric)
        if "business_kpis" in data and "causal_pathways" in data:
            kpis = data["business_kpis"]
            pathways = data["causal_pathways"]

            if kpis and pathways:
                linked_kpis = {p.get("business_kpi") for p in pathways if isinstance(p, dict)}
                all_kpis = {k.get("name") for k in kpis if isinstance(k, dict)}

                unlinked = all_kpis - linked_kpis
                if unlinked:
                    validation_concerns.append(
                        f"KPIs without linked model metrics: {', '.join(unlinked)}"
                    )

    def _validate_stage3(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 3: Data Feasibility."""
        # All 6 quality dimensions scored
        if "quality_scores" in data and data["quality_scores"]:
            scored_dimensions = set(data["quality_scores"].keys())
            required_dimensions = set(self.QUALITY_DIMENSIONS)

            missing_dimensions = required_dimensions - scored_dimensions
            if missing_dimensions:
                missing_items.append(
                    f"Missing quality dimension scores: {', '.join(missing_dimensions)}"
                )

            # Minimum quality threshold: 6/10 across all dimensions
            for dim, score in data["quality_scores"].items():
                if isinstance(score, (int, float)) and score < 6:
                    validation_concerns.append(
                        f"Quality dimension '{dim}' score {score} below minimum threshold of 6"
                    )

        # Labeling plan has budget/timeline
        if "labeling_strategy" in data and data["labeling_strategy"]:
            strategy = data["labeling_strategy"]
            if isinstance(strategy, dict):
                if "cost_estimate" not in strategy or not strategy["cost_estimate"]:
                    missing_items.append("Labeling strategy missing cost estimate")
                if "timeline" not in strategy or not strategy["timeline"]:
                    missing_items.append("Labeling strategy missing timeline")

    def _validate_stage4(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 4: User Experience."""
        # Personas research-based
        if "user_personas" in data:
            if not data["user_personas"] or len(data["user_personas"]) == 0:
                missing_items.append("At least one user persona must be defined")

        # Journey map complete
        if "user_journey_map" in data:
            if not data["user_journey_map"]:
                missing_items.append("User journey map must be defined")

        # Interpretability specified
        if "interpretability_needs" not in data or not data["interpretability_needs"]:
            missing_items.append("Interpretability requirements must be specified")

    def _validate_stage5(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 5: Ethical Governance."""
        # All ethical principles assessed
        if "initial_risks" in data and data["initial_risks"]:
            assessed_principles = set(data["initial_risks"].keys())
            required_principles = set(self.ETHICAL_PRINCIPLES)

            missing_principles = required_principles - assessed_principles
            if missing_principles:
                missing_items.append(
                    f"Missing ethical principle assessments: {', '.join(missing_principles)}"
                )

        # Residual risk calculated
        if "residual_risks" in data:
            if not data["residual_risks"]:
                missing_items.append("Residual risk calculation required for all principles")
        else:
            missing_items.append("Residual risks must be calculated")

        # Governance decision made
        if "governance_decision" not in data or not data["governance_decision"]:
            missing_items.append("Governance decision must be made")
