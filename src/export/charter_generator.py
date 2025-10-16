#!/usr/bin/env python3
"""
CharterDocumentGenerator - Multi-Format AI Project Charter Export

This module implements charter document generation per SWE Specification Section 7.3 (FR-7).

Capabilities:
- FR-7.1: Generate complete AI Project Charter in APA 7 format
- FR-7.2: Include all 8 required charter sections
- FR-7.3: Support export to Markdown, PDF, and JSON formats
- FR-7.5: Maintain citation bibliography in APA 7 format

Charter Template Structure (per SWE Spec lines 1291-1393):
1. Executive Summary (auto-generated)
2. Strategic Alignment (Stage 2 KPIs)
3. Problem Definition (Stage 1)
4. Technical Feasibility Assessment (Stage 3)
5. User Context and Interaction (Stage 4)
6. Metric Alignment Matrix (Stage 2)
7. Ethical Risk Assessment (Stage 5)
8. Operational Strategy (Stage 5 monitoring)
9. References (APA 7)
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.schemas import (
    AIProjectCharter,
    Citation,
    QualityDimension,
)

logger = logging.getLogger(__name__)


class APACitationFormatter:
    """
    APA 7th Edition citation formatter.

    Supports formatting citations for:
    - Journal articles
    - Books
    - Websites
    - Reports
    - Conference papers

    Per SWE Specification Section 7.3.1 (FR-7.5).
    """

    def format_citation(self, citation: Citation) -> str:
        """
        Format a single citation in APA 7th Edition style.

        Args:
            citation: Citation object to format

        Returns:
            Formatted citation string

        Format by type:
        - Journal: Author(s). (Year). Title. Source. DOI/URL
        - Book: Author(s). (Year). Title. Publisher.
        - Website: Author(s). (Year). Title. URL
        - Report: Author(s). (Year). Title. Organization.
        - Conference: Author(s). (Year). Title. Conference. DOI/URL
        """
        # Format authors
        if len(citation.authors) == 1:
            author_str = citation.authors[0]
        elif len(citation.authors) == 2:
            author_str = f"{citation.authors[0]}, & {citation.authors[1]}"
        else:
            # More than 2 authors: First, Second, & Third
            author_str = ", ".join(citation.authors[:-1]) + f", & {citation.authors[-1]}"

        # Base citation
        formatted = f"{author_str} ({citation.year}). {citation.title}. {citation.source}."

        # Add DOI or URL if available
        if citation.doi:
            formatted += f" https://doi.org/{citation.doi}"
        elif citation.url:
            formatted += f" {citation.url}"

        return formatted

    def generate_reference_list(self, citations: List[Citation]) -> str:
        """
        Generate complete APA 7 reference list, alphabetically sorted.

        Args:
            citations: List of Citation objects

        Returns:
            Formatted reference list as markdown string (without section header)
        """
        if not citations:
            return "*No citations available.*"

        # Sort citations alphabetically by first author's last name
        sorted_citations = sorted(citations, key=lambda c: c.authors[0] if c.authors else "")

        # Format each citation
        formatted_citations = [self.format_citation(c) for c in sorted_citations]

        # Build reference list (without header - will be added by caller)
        reference_list = "\n\n".join(formatted_citations)

        return reference_list


class CharterDocumentGenerator:
    """
    Generates AI Project Charter in multiple formats.

    Implements SWE Specification Section 7.3.2:
    - generate_markdown(): Structured markdown document
    - generate_pdf(): PDF document from markdown
    - generate_json(): Structured JSON export

    All exports follow the charter template structure defined in
    SWE Specification lines 1291-1393.
    """

    def __init__(self, citation_formatter: Optional[APACitationFormatter] = None):
        """
        Initialize CharterDocumentGenerator.

        Args:
            citation_formatter: Optional APACitationFormatter instance.
                              If None, creates default formatter.
        """
        self.citation_formatter = citation_formatter or APACitationFormatter()
        logger.info("Initialized CharterDocumentGenerator")

    async def generate_markdown(self, charter: AIProjectCharter) -> str:
        """
        Generate structured Markdown charter document.

        Implements FR-7.1, FR-7.2, FR-7.3 (Markdown format).

        Args:
            charter: Complete AIProjectCharter object

        Returns:
            Markdown-formatted charter as string

        Raises:
            ValueError: If charter is None or invalid
        """
        if charter is None:
            raise ValueError("Charter cannot be None")

        logger.info(f"Generating markdown charter for project: {charter.project_name}")

        # Build charter sections following SWE Spec template (lines 1291-1393)
        sections = []

        # Header
        sections.append(f"# AI Project Charter: {charter.project_name}")
        sections.append("")
        sections.append(f"**Date:** {charter.created_at.strftime('%Y-%m-%d')}")
        sections.append(f"**Session ID:** {charter.session_id}")
        sections.append(f"**Governance Decision:** {charter.governance_decision.value}")
        sections.append("")
        sections.append("---")
        sections.append("")

        # Executive Summary
        sections.append("## Executive Summary")
        sections.append("")
        sections.append(self._generate_executive_summary(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 1. Strategic Alignment
        sections.append("## 1. Strategic Alignment")
        sections.append("")
        sections.append(self._generate_strategic_alignment(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 2. Problem Definition
        sections.append("## 2. Problem Definition")
        sections.append("")
        sections.append(self._generate_problem_definition(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 3. Technical Feasibility Assessment
        sections.append("## 3. Technical Feasibility Assessment")
        sections.append("")
        sections.append(self._generate_technical_feasibility(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 4. User Context and Interaction
        sections.append("## 4. User Context and Interaction")
        sections.append("")
        sections.append(self._generate_user_context(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 5. Metric Alignment Matrix
        sections.append("## 5. Metric Alignment Matrix")
        sections.append("")
        sections.append(self._generate_metric_alignment(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 6. Ethical Risk Assessment
        sections.append("## 6. Ethical Risk Assessment")
        sections.append("")
        sections.append(self._generate_ethical_risk_assessment(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 7. Operational Strategy
        sections.append("## 7. Operational Strategy")
        sections.append("")
        sections.append(self._generate_operational_strategy(charter))
        sections.append("")
        sections.append("---")
        sections.append("")

        # 8. References
        sections.append("## 8. References")
        sections.append("")
        sections.append(self.citation_formatter.generate_reference_list(charter.citations))
        sections.append("")
        sections.append("---")
        sections.append("")

        # Footer
        sections.append(f"**Document generated by U-AIP Scoping Assistant v{charter.version}**")
        sections.append("**Charter approval pending:** [Signature line]")

        markdown = "\n".join(sections)
        logger.info(f"Generated {len(markdown)} character markdown document")

        return markdown

    async def generate_pdf(self, charter: AIProjectCharter) -> bytes:
        """
        Generate PDF charter document.

        Implements FR-7.3 (PDF format).

        Uses xhtml2pdf (pisa) to convert Markdown to PDF with professional formatting.
        This library is pure Python and doesn't require system dependencies.

        Args:
            charter: Complete AIProjectCharter object

        Returns:
            PDF document as bytes

        Raises:
            ImportError: If xhtml2pdf is not installed
            ValueError: If charter is None or invalid
        """
        logger.info(f"Generating PDF charter for project: {charter.project_name}")

        # First generate markdown
        markdown_content = await self.generate_markdown(charter)

        # Convert markdown to HTML
        try:
            import markdown2
        except ImportError:
            raise ImportError(
                "markdown2 package required for PDF generation. "
                "Install with: pip install markdown2"
            )

        html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks"])

        # Add basic CSS for professional formatting
        styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: letter;
            margin: 2cm;
        }}
        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            font-size: 20pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            color: #000;
        }}
        h2 {{
            font-size: 16pt;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #000;
        }}
        h3 {{
            font-size: 13pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            color: #000;
        }}
        p {{
            margin-bottom: 0.5em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 2em 0;
        }}
        strong {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

        # Convert HTML to PDF using xhtml2pdf
        try:
            from xhtml2pdf import pisa
            from io import BytesIO
        except ImportError:
            raise ImportError(
                "xhtml2pdf package required for PDF generation. "
                "Install with: pip install xhtml2pdf"
            )

        # Create PDF from HTML
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            styled_html.encode('utf-8'),
            dest=pdf_buffer
        )

        if pisa_status.err:
            logger.error(f"PDF generation failed with error code: {pisa_status.err}")
            raise RuntimeError(f"PDF generation failed")

        pdf_bytes = pdf_buffer.getvalue()
        logger.info(f"Generated {len(pdf_bytes)} byte PDF document")

        return pdf_bytes

    async def generate_json(self, charter: AIProjectCharter) -> str:
        """
        Generate structured JSON charter export.

        Implements FR-7.3 (JSON format).

        Args:
            charter: Complete AIProjectCharter object

        Returns:
            JSON-formatted charter as string

        Raises:
            ValueError: If charter is None or invalid
        """
        if charter is None:
            raise ValueError("Charter cannot be None")

        logger.info(f"Generating JSON charter for project: {charter.project_name}")

        # Custom JSON encoder for datetime, UUID, and Enum
        from dataclasses import asdict
        from uuid import UUID
        from enum import Enum
        from datetime import timedelta

        def convert_dict_keys(obj):
            """Recursively convert Enum keys in dictionaries to strings."""
            if isinstance(obj, dict):
                return {
                    (k.value if isinstance(k, Enum) else k): convert_dict_keys(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [convert_dict_keys(item) for item in obj]
            else:
                return obj

        def json_encoder(obj):
            """Convert non-serializable objects to JSON-compatible format."""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, timedelta):
                return str(obj)
            else:
                # For any other object, convert to string
                return str(obj)

        # Convert charter dataclass to dict recursively
        charter_dict = asdict(charter)

        # Convert Enum keys to strings
        charter_dict = convert_dict_keys(charter_dict)

        # Format as JSON with custom encoder
        json_str = json.dumps(charter_dict, indent=2, default=json_encoder)
        logger.info(f"Generated {len(json_str)} character JSON document")

        return json_str

    # =========================================================================
    # PRIVATE HELPER METHODS - Charter Section Generators
    # =========================================================================

    def _generate_executive_summary(self, charter: AIProjectCharter) -> str:
        """Generate auto-summarized executive summary."""
        summary = []

        summary.append(f"**Project:** {charter.project_name}")
        summary.append("")
        summary.append(f"**Business Objective:** {charter.problem_statement.business_objective}")
        summary.append("")
        summary.append(f"**ML Approach:** {charter.problem_statement.ml_archetype.value}")
        summary.append("")
        summary.append(f"**Overall Feasibility:** {charter.overall_feasibility.value}")
        summary.append("")
        summary.append(f"**Governance Decision:** {charter.governance_decision.value}")

        if charter.governance_decision.value != "proceed":
            summary.append("")
            summary.append(f"**Decision Reasoning:** {charter.ethical_risk_report.decision_reasoning}")

        summary.append("")
        summary.append("### Critical Success Factors")
        for factor in charter.critical_success_factors:
            summary.append(f"- {factor}")

        summary.append("")
        summary.append("### Major Risks")
        for risk in charter.major_risks:
            summary.append(f"- {risk}")

        return "\n".join(summary)

    def _generate_strategic_alignment(self, charter: AIProjectCharter) -> str:
        """Generate Strategic Alignment section (Stage 2 data)."""
        content = []

        content.append("### Business Goals")
        content.append("")

        for kpi in charter.metric_alignment_matrix.business_kpis:
            content.append(f"**{kpi.name}**")
            content.append(f"- Description: {kpi.description}")
            content.append(f"- Current Baseline: {kpi.current_baseline}")
            content.append(f"- Target Value: {kpi.target_value}")
            content.append(f"- Timeframe: {kpi.target_timeframe}")
            content.append(f"- Business Impact: {kpi.business_impact}")
            content.append("")

        content.append("### Financial Impact")
        content.append("")
        content.append(f"Total business impact across all KPIs demonstrates significant value potential.")

        return "\n".join(content)

    def _generate_problem_definition(self, charter: AIProjectCharter) -> str:
        """Generate Problem Definition section (Stage 1 data)."""
        content = []

        content.append(charter.problem_statement.business_objective)
        content.append("")

        content.append("### ML Archetype Mapping")
        content.append(f"**Archetype:** {charter.problem_statement.ml_archetype.value}")
        content.append("")
        content.append(f"**Justification:** {charter.problem_statement.ml_archetype_justification}")
        content.append("")

        content.append("### Input Features")
        content.append("")
        content.append("| Feature Name | Data Type | Source System | Production Available |")
        content.append("|--------------|-----------|---------------|---------------------|")
        for feature in charter.problem_statement.input_features:
            available = "✓" if feature.availability_in_production else "✗"
            content.append(f"| {feature.name} | {feature.data_type} | {feature.source_system} | {available} |")
        content.append("")

        content.append("### Target Output")
        content.append(f"**Name:** {charter.problem_statement.target_output.name}")
        content.append("")
        content.append(f"**Type:** {charter.problem_statement.target_output.type}")
        content.append("")
        content.append(f"**Description:** {charter.problem_statement.target_output.description}")

        return "\n".join(content)

    def _generate_technical_feasibility(self, charter: AIProjectCharter) -> str:
        """Generate Technical Feasibility Assessment section (Stage 3 data)."""
        content = []

        content.append("### Data Quality Scores")
        content.append("")
        content.append("| Quality Dimension | Score (0-10) |")
        content.append("|------------------|--------------|")

        for dimension, score in charter.data_quality_scorecard.quality_scores.items():
            content.append(f"| {dimension.value} | {score} |")

        content.append("")
        content.append(f"**Overall Data Feasibility:** {charter.data_quality_scorecard.overall_feasibility.value}")
        content.append("")

        content.append("### Labeling Strategy")
        content.append(f"**Method:** {charter.data_quality_scorecard.labeling_strategy.labeling_method}")
        content.append("")
        content.append(f"**Estimated Cost:** ${charter.data_quality_scorecard.labeling_strategy.estimated_cost:,.2f}")
        content.append("")
        content.append(f"**Timeline:** {charter.data_quality_scorecard.labeling_strategy.estimated_time}")

        return "\n".join(content)

    def _generate_user_context(self, charter: AIProjectCharter) -> str:
        """Generate User Context and Interaction section (Stage 4 data)."""
        content = []

        content.append("### User Personas")
        content.append("")

        for persona in charter.user_context.user_personas:
            content.append(f"**{persona.name}**")
            content.append(f"- Role: {persona.role}")
            content.append(f"- Technical Proficiency: {persona.technical_proficiency}")
            content.append(f"- AI Interaction Frequency: {persona.ai_interaction_frequency}")
            content.append(f"- Decision Authority: {persona.decision_authority}")
            content.append("")

        content.append("### Interpretability Requirements")
        content.append(f"**Required Level:** {charter.user_context.interpretability_needs.required_level}")
        content.append("")
        content.append(f"**Explanation Method:** {charter.user_context.interpretability_needs.explanation_method}")

        return "\n".join(content)

    def _generate_metric_alignment(self, charter: AIProjectCharter) -> str:
        """Generate Metric Alignment Matrix section (Stage 2 causal pathways)."""
        content = []

        content.append("### Causal Connection Analysis")
        content.append("")

        for pathway in charter.metric_alignment_matrix.causal_pathways:
            content.append(f"**{pathway.model_metric} → {pathway.business_kpi}**")
            content.append("")
            content.append(f"Causal Mechanism: {pathway.causal_mechanism}")
            content.append("")

        content.append(f"**Actionability Window:** {charter.metric_alignment_matrix.actionability_window}")

        return "\n".join(content)

    def _generate_ethical_risk_assessment(self, charter: AIProjectCharter) -> str:
        """Generate Ethical Risk Assessment section (Stage 5 data)."""
        content = []

        content.append("### Residual Risk Summary")
        content.append("")
        content.append("| Ethical Principle | Residual Risk Level |")
        content.append("|-------------------|---------------------|")

        for principle, risk_level in charter.ethical_risk_report.residual_risks.items():
            content.append(f"| {principle.value} | {risk_level.name} |")

        content.append("")
        content.append("### Governance Checkpoint Decision")
        content.append(f"**Decision:** {charter.ethical_risk_report.governance_decision.value}")
        content.append("")
        content.append(f"**Reasoning:** {charter.ethical_risk_report.decision_reasoning}")

        return "\n".join(content)

    def _generate_operational_strategy(self, charter: AIProjectCharter) -> str:
        """Generate Operational Strategy section (Stage 5 monitoring plan)."""
        content = []

        plan = charter.ethical_risk_report.monitoring_plan

        content.append("### Continuous Monitoring Plan")
        content.append("")
        content.append(f"**Monitoring Frequency:** {plan.monitoring_frequency}")
        content.append("")

        content.append("**Metrics to Monitor:**")
        for metric in plan.metrics_to_monitor:
            content.append(f"- {metric}")

        content.append("")
        content.append(f"**Review Process:** {plan.review_process}")
        content.append("")
        content.append(f"**Escalation Procedure:** {plan.escalation_procedure}")

        return "\n".join(content)
