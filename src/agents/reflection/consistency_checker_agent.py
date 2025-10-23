#!/usr/bin/env python3
"""
ConsistencyCheckerAgent - Cross-Stage Consistency Validation

This agent validates logical consistency across all 5 stages of the U-AIP process,
detecting contradictions and feasibility issues that could compromise project success.

Per SWE Specification Section 4.3.3:
- Validates alignment between Stage 1 problem and Stage 2 metrics (FR-5.1)
- Verifies Stage 3 data availability supports Stage 2 metrics (FR-5.2)
- Checks Stage 4 user personas align with Stage 3 data access (FR-5.3)
- Ensures Stage 5 ethical risks match project scope from Stages 1-4 (FR-5.4)
- Identifies and reports logical contradictions across stages (FR-5.5)

Cross-Stage Checks:
1. Stage 1 → Stage 2: Do KPIs solve the stated problem?
2. Stage 2 → Stage 3: Is required data available for chosen metrics?
3. Stage 3 → Stage 4: Do users have access to data sources?
4. Stage 1-4 → Stage 5: Do ethical risks match project scope/impact?
5. Overall: Is project feasible given all constraints?

Implementation follows strict TDD methodology with comprehensive test coverage.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FeasibilityLevel(Enum):
    """Overall project feasibility assessment."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Contradiction:
    """
    A logical contradiction detected between stages.

    Attributes:
        stage_from: Source stage number (1-5)
        stage_to: Target stage number (1-5)
        description: Clear description of the contradiction
        severity: CRITICAL/HIGH/MEDIUM/LOW
    """
    stage_from: int
    stage_to: int
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW


@dataclass
class RiskArea:
    """
    A risk area identified during consistency checking.

    Attributes:
        area: Name of the risk area (e.g., "Data Pipeline Latency")
        description: Detailed description of the risk
        impact: Potential impact on project success
    """
    area: str
    description: str
    impact: str


@dataclass
class ConsistencyReport:
    """
    Consistency check result across all stages.

    Attributes:
        is_consistent: True if no critical contradictions found
        overall_feasibility: HIGH/MEDIUM/LOW feasibility assessment
        contradictions: List of contradictions detected
        risk_areas: List of risk areas identified
        recommendations: List of recommended actions
    """
    is_consistent: bool
    overall_feasibility: FeasibilityLevel
    contradictions: List[Contradiction] = field(default_factory=list)
    risk_areas: List[RiskArea] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ConsistencyCheckerAgent:
    """
    LLM-based agent for cross-stage consistency validation.

    This agent performs comprehensive consistency checks across all 5 stages of
    the U-AIP evaluation, detecting logical contradictions and feasibility issues
    that could compromise project success.

    The agent operates in the reflection layer of the U-AIP system, providing
    the final "sanity check" before AI Project Charter generation.

    Attributes:
        llm_router: Router for LLM API calls (routes to appropriate Claude model)
    """

    # System prompt per SWE Spec Section 6.1.3 (Page 25)
    SYSTEM_PROMPT = """You are the Cross-Stage Consistency Checker for U-AIP evaluations.

Your job is to find logical contradictions and feasibility issues across the entire
AI project scope that may have been missed by individual stage validations.

Check these critical alignments:
1. Do Stage 2 KPIs actually solve the Stage 1 problem?
2. Is the Stage 3 data sufficient for Stage 2 metrics?
3. Can Stage 4 users access Stage 3 data sources?
4. Do Stage 5 ethical risks match the project's actual scope and impact?

Look for red flags:
- Claiming to predict rare events but having no data on those events
- Requiring real-time predictions but having batch data pipelines
- Targeting non-technical users but requiring model interpretability expertise
- Low ethical risk rating for high-stakes decisions
- Budget constraints incompatible with data labeling needs

Be the "sanity check" agent. If something seems infeasible, call it out clearly
with specific reasoning.

Return your evaluation in JSON format:
{
    "is_consistent": <bool>,
    "overall_feasibility": "HIGH" | "MEDIUM" | "LOW",
    "contradictions": [
        {
            "stage_from": <int 1-5>,
            "stage_to": <int 1-5>,
            "description": "<clear description>",
            "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
        }
    ],
    "risk_areas": [
        {
            "area": "<risk area name>",
            "description": "<detailed description>",
            "impact": "<potential impact>"
        }
    ],
    "recommendations": ["<action 1>", "<action 2>", ...]
}
"""

    def __init__(self, llm_router: Any):
        """
        Initialize ConsistencyCheckerAgent.

        Args:
            llm_router: Router for LLM API calls
        """
        self.llm_router = llm_router

        logger.info("Initialized ConsistencyCheckerAgent")

    async def check_consistency(
        self,
        all_stages_data: Dict[str, Any]
    ) -> ConsistencyReport:
        """
        Check consistency across all stages.

        This method performs comprehensive cross-stage consistency validation,
        detecting contradictions and feasibility issues that could compromise
        project success.

        Args:
            all_stages_data: Dictionary containing data from all 5 stages
                            Format: {"stage1": {...}, "stage2": {...}, ...}

        Returns:
            ConsistencyReport: Consistency check result with contradictions,
                             risk areas, and recommendations

        Raises:
            Exception: If LLM API call fails (propagated to caller)
        """
        logger.info("Checking cross-stage consistency")

        # Handle empty or None data
        if not all_stages_data or len(all_stages_data) == 0:
            return ConsistencyReport(
                is_consistent=False,
                overall_feasibility=FeasibilityLevel.LOW,
                recommendations=["Insufficient data provided for consistency checking"]
            )

        # Prepare analysis prompt
        user_prompt = f"""Analyze the following AI project data across all 5 stages for
logical consistency and feasibility.

STAGE DATA:
{self._format_stages_for_llm(all_stages_data)}

Perform these specific checks:
1. Stage 1 → Stage 2: Do the business KPIs actually solve the stated problem?
2. Stage 2 → Stage 3: Is the required data available to support the chosen metrics?
3. Stage 3 → Stage 4: Do the user personas have access to the data sources?
4. Stage 1-4 → Stage 5: Do the ethical risks match the project scope and impact?
5. Overall: Is this project feasible given all constraints?

Identify any contradictions, risk areas, and provide recommendations.

Provide your evaluation in the JSON format specified in the system prompt."""

        logger.debug("Analyzing cross-stage consistency with LLM")

        # Call LLM for consistency analysis
        try:
            llm_response = await self.llm_router.route(
                prompt=user_prompt,
                model_preference="sonnet",  # Use Sonnet for complex reasoning
                system_prompt=self.SYSTEM_PROMPT,
                response_format="json"
            )

            logger.debug(f"LLM consistency analysis response: {llm_response}")

            # Parse LLM response
            report = self._parse_llm_response(llm_response, all_stages_data)

            logger.info(
                f"Consistency check complete: is_consistent={report.is_consistent}, "
                f"feasibility={report.overall_feasibility.value}, "
                f"contradictions={len(report.contradictions)}"
            )

            return report

        except Exception as e:
            logger.error(f"Error during consistency checking: {e}", exc_info=True)
            raise

    def _format_stages_for_llm(self, all_stages_data: Dict[str, Any]) -> str:
        """
        Format stage data for LLM analysis.

        Args:
            all_stages_data: Dictionary containing data from all stages

        Returns:
            Formatted string representation of stage data
        """
        formatted = []

        for stage_key in sorted(all_stages_data.keys()):
            stage_data = all_stages_data[stage_key]
            if stage_data:
                formatted.append(f"\n{stage_key.upper()}:")
                formatted.append(self._format_dict(stage_data, indent=2))

        return "\n".join(formatted)

    def _format_dict(self, data: Any, indent: int = 0) -> str:
        """Recursively format dictionary for readable display."""
        if not isinstance(data, dict):
            return str(data)

        lines = []
        prefix = " " * indent

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: [{len(value)} items]")
                if len(value) > 0 and isinstance(value[0], dict):
                    lines.append(f"{prefix}  (showing first item)")
                    lines.append(self._format_dict(value[0], indent + 4))
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)

    def _parse_llm_response(
        self,
        llm_response: Dict[str, Any],
        all_stages_data: Dict[str, Any]
    ) -> ConsistencyReport:
        """
        Parse LLM response into ConsistencyReport.

        Handles various response formats and provides sensible defaults for
        missing or malformed data.

        Args:
            llm_response: Response from LLM router
            all_stages_data: Original stage data (for fallback analysis)

        Returns:
            ConsistencyReport: Parsed consistency report

        Raises:
            ValueError: If response is completely malformed
        """
        try:
            # Extract is_consistent (required)
            if "is_consistent" not in llm_response:
                logger.warning("LLM response missing is_consistent, using default")
                is_consistent = False
            else:
                is_consistent = bool(llm_response["is_consistent"])

            # Extract overall_feasibility
            feasibility_str = llm_response.get("overall_feasibility", "MEDIUM")
            try:
                overall_feasibility = FeasibilityLevel[feasibility_str.upper()]
            except (KeyError, AttributeError):
                logger.warning(f"Invalid feasibility '{feasibility_str}', defaulting to MEDIUM")
                overall_feasibility = FeasibilityLevel.MEDIUM

            # Extract contradictions
            contradictions = []
            for c in llm_response.get("contradictions", []):
                if isinstance(c, dict):
                    contradictions.append(Contradiction(
                        stage_from=int(c.get("stage_from", 0)),
                        stage_to=int(c.get("stage_to", 0)),
                        description=str(c.get("description", "")),
                        severity=str(c.get("severity", "MEDIUM"))
                    ))

            # Extract risk areas
            risk_areas = []
            for r in llm_response.get("risk_areas", []):
                if isinstance(r, dict):
                    risk_areas.append(RiskArea(
                        area=str(r.get("area", "")),
                        description=str(r.get("description", "")),
                        impact=str(r.get("impact", ""))
                    ))

            # Extract recommendations
            recommendations = llm_response.get("recommendations", [])
            if not isinstance(recommendations, list):
                recommendations = [str(recommendations)] if recommendations else []
            recommendations = [str(r) for r in recommendations]

            # If no contradictions found but marked as inconsistent, add general note
            if not is_consistent and len(contradictions) == 0:
                contradictions.append(Contradiction(
                    stage_from=0,
                    stage_to=0,
                    description="General consistency issues detected - review stage alignment",
                    severity="MEDIUM"
                ))

            return ConsistencyReport(
                is_consistent=is_consistent,
                overall_feasibility=overall_feasibility,
                contradictions=contradictions,
                risk_areas=risk_areas,
                recommendations=recommendations
            )

        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Error parsing LLM response: {e}", exc_info=True)

            # Return default "needs review" report if parsing fails
            return ConsistencyReport(
                is_consistent=False,
                overall_feasibility=FeasibilityLevel.MEDIUM,
                contradictions=[
                    Contradiction(
                        stage_from=0,
                        stage_to=0,
                        description=f"Consistency analysis incomplete: {str(e)}",
                        severity="MEDIUM"
                    )
                ],
                recommendations=[
                    "Manual review recommended due to automated analysis error",
                    "Verify alignment between problem statement and success metrics",
                    "Confirm data availability for model requirements"
                ]
            )
