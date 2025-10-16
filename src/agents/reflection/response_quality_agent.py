#!/usr/bin/env python3
"""
ResponseQualityAgent - LLM-based Response Quality Evaluation

This agent evaluates the quality of user responses on a 0-10 scale based on five
dimensions: specificity, measurability, completeness, coherence, and relevance.

Per SWE Specification Section 4.3.1:
- Evaluates responses on 0-10 scale
- Enforces quality threshold of 7/10
- Identifies vagueness, gaps, and logical issues
- Generates 2-3 targeted follow-up questions
- Provides examples of better responses
- Limits reflection loops to max 3 attempts

Scoring Scale:
- 9-10: Excellent (specific, measurable, complete)
- 7-8: Good (mostly clear, minor gaps acceptable)
- 5-6: Needs improvement (vague or incomplete)
- 0-4: Insufficient (requires complete rework)

Implementation follows strict TDD methodology with comprehensive test coverage.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class QualityAssessment:
    """
    Quality assessment result for a user response.

    Attributes:
        quality_score: Overall quality score (0-10)
        is_acceptable: True if score >= quality_threshold (default 7)
        issues: List of specific problems identified
        suggested_followups: 2-3 targeted follow-up questions
        examples_to_provide: Examples of better responses
    """

    quality_score: int
    is_acceptable: bool
    issues: List[str] = field(default_factory=list)
    suggested_followups: List[str] = field(default_factory=list)
    examples_to_provide: List[str] = field(default_factory=list)


class ResponseQualityAgent:
    """
    LLM-based agent for evaluating response quality.

    This agent uses Claude to perform deep evaluation of user responses across
    five dimensions: specificity, measurability, completeness, coherence, and relevance.

    The agent operates in the reflection layer of the U-AIP system, providing
    quality assurance feedback to Stage Interview Agents.

    Attributes:
        llm_router: Router for LLM API calls (routes to appropriate Claude model)
        quality_threshold: Minimum acceptable score (default: 7)
        max_reflection_loops: Maximum quality improvement attempts (default: 3)
    """

    # System prompt per SWE Spec Section 6.1.3 (Page 24)
    SYSTEM_PROMPT = """You are a strict quality evaluator for AI project scoping responses.

Evaluate each user response on these dimensions:
1. Specificity - Is it concrete or vague?
2. Measurability - Can we quantify this?
3. Completeness - Does it fully answer the question?
4. Coherence - Is it logically consistent?
5. Relevance - Does it stay on topic?

Score 0-10 where:
- 9-10: Excellent (specific, measurable, complete)
- 7-8: Good (mostly clear, minor gaps acceptable)
- 5-6: Needs improvement (vague or incomplete)
- 0-4: Insufficient (requires complete rework)

For scores below 7, provide:
1. Specific issues with the response
2. 2-3 targeted follow-up questions
3. An example of what a better response would include

Be firm but constructive. The goal is to help users provide quality information,
not to frustrate them. Explain WHY specificity matters for AI project success.

Return your evaluation in JSON format:
{
    "quality_score": <int 0-10>,
    "specificity": "<evaluation>",
    "measurability": "<evaluation>",
    "completeness": "<evaluation>",
    "coherence": "<evaluation>",
    "relevance": "<evaluation>",
    "issues": ["<issue 1>", "<issue 2>", ...],
    "suggested_followups": ["<question 1>", "<question 2>", "<question 3>"],
    "examples": ["<example 1>", ...]
}
"""

    def __init__(
        self,
        llm_router: Any,
        quality_threshold: int = 7,
        max_reflection_loops: int = 3
    ):
        """
        Initialize ResponseQualityAgent.

        Args:
            llm_router: Router for LLM API calls
            quality_threshold: Minimum acceptable score (default: 7)
            max_reflection_loops: Max quality improvement attempts (default: 3)

        Raises:
            ValueError: If quality_threshold not in range [0, 10]
            ValueError: If max_reflection_loops < 1
        """
        if not (0 <= quality_threshold <= 10):
            raise ValueError(f"quality_threshold must be in range [0, 10], got {quality_threshold}")

        if max_reflection_loops < 1:
            raise ValueError(f"max_reflection_loops must be >= 1, got {max_reflection_loops}")

        self.llm_router = llm_router
        self.quality_threshold = quality_threshold
        self.max_reflection_loops = max_reflection_loops

        logger.info(
            f"Initialized ResponseQualityAgent with threshold={quality_threshold}, "
            f"max_loops={max_reflection_loops}"
        )

    async def evaluate_response(
        self,
        question: str,
        user_response: str,
        stage_context: Optional[Dict[str, Any]] = None
    ) -> QualityAssessment:
        """
        Evaluate the quality of a user response using LLM.

        This method performs a comprehensive 5-dimension evaluation of the user's
        response and returns a QualityAssessment with score, issues, follow-ups,
        and examples.

        Args:
            question: The question that was asked
            user_response: The user's answer to evaluate
            stage_context: Optional context about current stage (e.g., {"stage": 1})

        Returns:
            QualityAssessment: Evaluation result with score and feedback

        Raises:
            ValueError: If question or user_response is empty/None
            Exception: If LLM API call fails (propagated to caller)
        """
        # Input validation
        if not question or not question.strip():
            raise ValueError("question cannot be empty")

        if user_response is None:
            user_response = ""  # Handle None as empty string

        # Prepare evaluation prompt
        stage_info = ""
        if stage_context and "stage" in stage_context:
            stage_num = stage_context["stage"]
            stage_name = stage_context.get("stage_name", f"Stage {stage_num}")
            stage_info = f"\n\nContext: This is {stage_name} of the U-AIP evaluation process."

        user_prompt = f"""Evaluate the following response to a scoping question.

Question: {question}

User Response: {user_response if user_response.strip() else "[No response provided]"}
{stage_info}

Provide your evaluation in the JSON format specified in the system prompt."""

        logger.debug(f"Evaluating response for question: {question[:100]}...")

        # Call LLM for evaluation
        try:
            llm_response = await self.llm_router.route(
                model_preference="haiku",  # Use Haiku for fast, cost-effective evaluation
                system_prompt=self.SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_format="json"
            )

            logger.debug(f"LLM evaluation response: {llm_response}")

            # Parse LLM response
            assessment = self._parse_llm_response(llm_response, user_response)

            logger.info(
                f"Quality assessment complete: score={assessment.quality_score}, "
                f"acceptable={assessment.is_acceptable}"
            )

            return assessment

        except Exception as e:
            logger.error(f"Error during response evaluation: {e}", exc_info=True)
            raise

    def _parse_llm_response(
        self,
        llm_response: Dict[str, Any],
        original_response: str
    ) -> QualityAssessment:
        """
        Parse LLM response into QualityAssessment.

        Handles various response formats and provides sensible defaults for
        missing or malformed data.

        Args:
            llm_response: Response from LLM router
            original_response: Original user response (for empty response handling)

        Returns:
            QualityAssessment: Parsed assessment

        Raises:
            ValueError: If response is completely malformed
        """
        try:
            # Extract quality score (required)
            if "quality_score" not in llm_response:
                # If completely malformed, return default poor assessment
                logger.warning("LLM response missing quality_score, using default")
                return QualityAssessment(
                    quality_score=0,
                    is_acceptable=False,
                    issues=["Response evaluation failed - please rephrase your answer"],
                    suggested_followups=["Could you provide more details?"],
                    examples_to_provide=[]
                )

            quality_score = int(llm_response["quality_score"])

            # Clamp score to valid range [0, 10]
            if quality_score < 0:
                logger.warning(f"Quality score {quality_score} below 0, clamping to 0")
                quality_score = 0
            elif quality_score > 10:
                logger.warning(f"Quality score {quality_score} above 10, clamping to 10")
                quality_score = 10

            # Determine acceptability
            is_acceptable = quality_score >= self.quality_threshold

            # Extract issues
            issues = llm_response.get("issues", [])
            if not isinstance(issues, list):
                issues = [str(issues)] if issues else []

            # Extract suggested follow-ups
            suggested_followups = llm_response.get("suggested_followups", [])
            if not isinstance(suggested_followups, list):
                suggested_followups = [str(suggested_followups)] if suggested_followups else []

            # Extract examples
            examples = llm_response.get("examples", [])
            if not isinstance(examples, list):
                examples = [str(examples)] if examples else []

            # Special handling for empty responses
            if not original_response.strip():
                issues = ["No response provided"]
                suggested_followups = ["Please provide an answer to the question"]
                quality_score = 0
                is_acceptable = False

            return QualityAssessment(
                quality_score=quality_score,
                is_acceptable=is_acceptable,
                issues=issues,
                suggested_followups=suggested_followups,
                examples_to_provide=examples
            )

        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Error parsing LLM response: {e}", exc_info=True)
            # Return default poor assessment if parsing fails
            return QualityAssessment(
                quality_score=0,
                is_acceptable=False,
                issues=[f"Response evaluation error: {str(e)}"],
                suggested_followups=["Could you rephrase your answer?"],
                examples_to_provide=[]
            )
