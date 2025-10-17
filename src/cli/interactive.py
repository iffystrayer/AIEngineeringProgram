"""
Interactive CLI utilities for collecting user input during stage interviews.

Provides rich, user-friendly prompts for collecting responses during multi-stage
interviews with quality validation loops.
"""

import logging
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

logger = logging.getLogger(__name__)
console = Console()


async def ask_user_question(
    question: str,
    stage_number: int,
    question_number: Optional[int] = None,
    context: Optional[str] = None,
) -> str:
    """
    Ask user a question interactively via CLI with rich formatting.

    Args:
        question: The question to ask
        stage_number: Current stage number (1-5)
        question_number: Optional question number within group
        context: Optional context to display before question

    Returns:
        User's response string
    """
    # Display context if provided
    if context:
        console.print(f"\n[dim]{context}[/dim]")

    # Format question header
    question_label = f"Stage {stage_number}"
    if question_number:
        question_label += f" - Question {question_number}"

    # Display question in a panel
    console.print(
        Panel.fit(
            f"[bold cyan]{question}[/bold cyan]",
            title=f"[bold yellow]{question_label}[/bold yellow]",
            border_style="cyan",
        )
    )

    # Get user input
    response = Prompt.ask("\n[bold green]Your response[/bold green]")

    return response


async def display_follow_up(
    follow_up_question: str,
    quality_score: int,
    issues: list[str],
) -> str:
    """
    Display quality validation feedback and ask follow-up question.

    Args:
        follow_up_question: The follow-up question to ask
        quality_score: Quality score from previous response (0-10)
        issues: List of quality issues identified

    Returns:
        User's improved response string
    """
    # Display quality feedback
    console.print("\n[yellow]⚠️  Quality validation feedback:[/yellow]")
    console.print(f"[dim]Score: {quality_score}/10[/dim]")

    if issues:
        console.print("[dim]Issues identified:[/dim]")
        for issue in issues:
            console.print(f"  • [dim]{issue}[/dim]")

    # Display follow-up question
    console.print(
        Panel.fit(
            f"[bold yellow]{follow_up_question}[/bold yellow]",
            title="[bold yellow]Follow-up[/bold yellow]",
            border_style="yellow",
        )
    )

    # Get improved response
    response = Prompt.ask("\n[bold green]Improved response[/bold green]")

    return response


def display_quality_success(quality_score: int) -> None:
    """
    Display success message when quality threshold is met.

    Args:
        quality_score: Quality score that passed threshold
    """
    console.print(f"[green]✓ Response accepted (quality: {quality_score}/10)[/green]\n")


def display_quality_escalation(attempts: int) -> None:
    """
    Display escalation message when max attempts reached.

    Args:
        attempts: Number of attempts made
    """
    console.print(
        f"[yellow]⚠️  Max attempts ({attempts}) reached. Proceeding with best response.[/yellow]\n"
    )


def display_stage_header(stage_number: int, stage_name: str) -> None:
    """
    Display stage header banner.

    Args:
        stage_number: Stage number (1-5)
        stage_name: Name of the stage
    """
    console.print(f"\n[bold yellow]{'=' * 60}[/bold yellow]")
    console.print(f"[bold cyan]Stage {stage_number}: {stage_name}[/bold cyan]")
    console.print(f"[bold yellow]{'=' * 60}[/bold yellow]\n")


def display_group_header(group_number: int, group_title: str) -> None:
    """
    Display question group header.

    Args:
        group_number: Question group number
        group_title: Title of the question group
    """
    console.print(f"\n[bold cyan]Question Group {group_number}: {group_title}[/bold cyan]")
    console.print("[dim]" + "─" * 60 + "[/dim]\n")
