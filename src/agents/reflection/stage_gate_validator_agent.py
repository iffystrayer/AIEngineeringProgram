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

    def _get_field(self, data: Any, field: str, default: Any = None) -> Any:
        """
        Safely get field value from dict or dataclass object.

        Args:
            data: Data object (dict or dataclass)
            field: Field name to retrieve
            default: Default value if field not found

        Returns:
            Field value or default
        """
        from dataclasses import is_dataclass

        if data is None:
            return default

        if is_dataclass(data):
            return getattr(data, field, default)
        elif isinstance(data, dict):
            return data.get(field, default)
        else:
            return default

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
            collected_data: Data collected during stage (deliverable dict or dataclass)

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

        logger.info(f"Validating Stage {stage_number} completion (data type: {type(collected_data).__name__})")

        # Initialize validation tracking
        missing_items = []
        validation_concerns = []
        recommendations = []

        # Get stage requirements
        requirements = self.STAGE_REQUIREMENTS[stage_number]
        mandatory_fields = requirements["mandatory_fields"]
        validation_rules = requirements["validation_rules"]

        # Check mandatory fields
        # Handle both dict and dataclass objects
        from dataclasses import is_dataclass

        for field in mandatory_fields:
            if is_dataclass(collected_data):
                # For dataclass objects, use hasattr and getattr
                if not hasattr(collected_data, field):
                    missing_items.append(f"Missing mandatory field: {field}")
                else:
                    field_value = getattr(collected_data, field)
                    if field_value is None or (isinstance(field_value, (list, dict, str)) and not field_value):
                        missing_items.append(f"Missing mandatory field: {field}")
            else:
                # For dict objects, use dict access
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
        # Check for empty data - handle both dict and dataclass
        from dataclasses import is_dataclass, fields as dataclass_fields

        if not collected_data:
            completeness_score = 0.0
        elif is_dataclass(collected_data):
            # For dataclass, check if any fields have values
            has_data = any(getattr(collected_data, f.name, None) is not None
                          for f in dataclass_fields(collected_data))
            if not has_data:
                completeness_score = 0.0
            else:
                completeness_score = passed_checks / total_checks if total_checks > 0 else 0.0
        elif isinstance(collected_data, dict):
            if len(collected_data) == 0:
                completeness_score = 0.0
            else:
                completeness_score = passed_checks / total_checks if total_checks > 0 else 0.0
        else:
            # Unknown type, assume it has data
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
        ml_archetype_justification = self._get_field(data, "ml_archetype_justification")
        if not ml_archetype_justification:
            missing_items.append("ML archetype justification required")

        # Features defined
        input_features = self._get_field(data, "input_features", [])
        if not input_features or len(input_features) == 0:
            missing_items.append("At least one input feature must be defined")

        # Production availability confirmed
        if input_features:
            for feature in input_features:
                # Handle both dict and dataclass Feature objects
                from dataclasses import is_dataclass
                if is_dataclass(feature):
                    availability = getattr(feature, "availability_in_production", None)
                    feature_name = getattr(feature, "name", "unknown")
                elif isinstance(feature, dict):
                    availability = feature.get("availability_in_production")
                    feature_name = feature.get("name", "unknown")
                else:
                    continue

                if not availability:
                    validation_concerns.append(
                        f"Feature '{feature_name}' not available in production"
                    )

    def _validate_stage2(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 2: Value Quantification."""
        from dataclasses import is_dataclass

        # KPIs are SMART
        business_kpis = self._get_field(data, "business_kpis", [])
        if business_kpis:
            for kpi in business_kpis:
                if is_dataclass(kpi):
                    # Check SMART criteria for dataclass
                    if not all(hasattr(kpi, k) and getattr(kpi, k) is not None
                             for k in ["current_baseline", "target_value", "target_timeframe"]):
                        kpi_name = getattr(kpi, "name", "unknown")
                        validation_concerns.append(
                            f"KPI '{kpi_name}' missing SMART criteria "
                            "(current_baseline, target_value, target_timeframe)"
                        )
                elif isinstance(kpi, dict):
                    # Check SMART criteria for dict
                    if not all(k in kpi for k in ["current_baseline", "target_value", "target_timeframe"]):
                        validation_concerns.append(
                            f"KPI '{kpi.get('name', 'unknown')}' missing SMART criteria "
                            "(current_baseline, target_value, target_timeframe)"
                        )

        # Causal pathway articulated
        causal_pathways = self._get_field(data, "causal_pathways", [])
        if not causal_pathways or len(causal_pathways) == 0:
            missing_items.append("At least one causal pathway must be defined")

        # Metrics aligned (each KPI has linked model metric)
        if business_kpis and causal_pathways:
            linked_kpis = set()
            for p in causal_pathways:
                if is_dataclass(p):
                    biz_kpi = getattr(p, "business_kpi", None)
                    if biz_kpi:
                        linked_kpis.add(biz_kpi)
                elif isinstance(p, dict):
                    biz_kpi = p.get("business_kpi")
                    if biz_kpi:
                        linked_kpis.add(biz_kpi)

            all_kpis = set()
            for k in business_kpis:
                if is_dataclass(k):
                    kpi_name = getattr(k, "name", None)
                    if kpi_name:
                        all_kpis.add(kpi_name)
                elif isinstance(k, dict):
                    kpi_name = k.get("name")
                    if kpi_name:
                        all_kpis.add(kpi_name)

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
        from dataclasses import is_dataclass

        # All 6 quality dimensions scored
        quality_scores = self._get_field(data, "quality_scores", {})
        if quality_scores:
            if isinstance(quality_scores, dict):
                # Convert enum keys to string names for comparison
                scored_dimensions = set()
                for key in quality_scores.keys():
                    if hasattr(key, 'name'):  # Enum object
                        scored_dimensions.add(key.name)
                    else:  # String key
                        scored_dimensions.add(str(key))

                required_dimensions = set(self.QUALITY_DIMENSIONS)

                missing_dimensions = required_dimensions - scored_dimensions
                if missing_dimensions:
                    missing_items.append(
                        f"Missing quality dimension scores: {', '.join(sorted(missing_dimensions))}"
                    )

                # Minimum quality threshold: 6/10 across all dimensions
                for dim, score in quality_scores.items():
                    if isinstance(score, (int, float)) and score < 6:
                        validation_concerns.append(
                            f"Quality dimension '{dim}' score {score} below minimum threshold of 6"
                        )

        # Labeling plan has budget/timeline
        labeling_strategy = self._get_field(data, "labeling_strategy")
        if labeling_strategy:
            if is_dataclass(labeling_strategy):
                if not getattr(labeling_strategy, "estimated_cost", None):
                    missing_items.append("Labeling strategy missing cost estimate")
                if not getattr(labeling_strategy, "estimated_time", None):
                    missing_items.append("Labeling strategy missing timeline")
            elif isinstance(labeling_strategy, dict):
                if "cost_estimate" not in labeling_strategy or not labeling_strategy["cost_estimate"]:
                    missing_items.append("Labeling strategy missing cost estimate")
                if "timeline" not in labeling_strategy or not labeling_strategy["timeline"]:
                    missing_items.append("Labeling strategy missing timeline")

    def _validate_stage4(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 4: User Experience."""
        # Personas research-based
        user_personas = self._get_field(data, "user_personas", [])
        if not user_personas or len(user_personas) == 0:
            missing_items.append("At least one user persona must be defined")

        # Journey map complete
        user_journey_map = self._get_field(data, "user_journey_map")
        if not user_journey_map:
            missing_items.append("User journey map must be defined")

        # Interpretability specified
        interpretability_needs = self._get_field(data, "interpretability_needs")
        if not interpretability_needs:
            missing_items.append("Interpretability requirements must be specified")

    def _validate_stage5(
        self,
        data: Dict[str, Any],
        missing_items: List[str],
        validation_concerns: List[str]
    ) -> None:
        """Validate Stage 5: Ethical Governance."""
        # All ethical principles assessed
        initial_risks = self._get_field(data, "initial_risks", {})
        if initial_risks and isinstance(initial_risks, dict):
            # Convert enum keys to string names for comparison
            assessed_principles = set()
            for key in initial_risks.keys():
                if hasattr(key, 'name'):  # Enum object
                    assessed_principles.add(key.name)
                else:  # String key
                    assessed_principles.add(str(key))

            required_principles = set(self.ETHICAL_PRINCIPLES)

            missing_principles = required_principles - assessed_principles
            if missing_principles:
                missing_items.append(
                    f"Missing ethical principle assessments: {', '.join(sorted(missing_principles))}"
                )

        # Residual risk calculated
        residual_risks = self._get_field(data, "residual_risks", {})
        if not residual_risks:
            missing_items.append("Residual risk calculation required for all principles")

        # Governance decision made
        governance_decision = self._get_field(data, "governance_decision")
        if not governance_decision:
            missing_items.append("Governance decision must be made")
