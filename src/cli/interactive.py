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
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.align import Align
from rich.text import Text
from rich.box import Box, ROUNDED, HEAVY, DOUBLE
from rich.columns import Columns
from rich.rule import Rule

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


# ============================================================================
# ENHANCED RICH DISPLAY FUNCTIONS
# ============================================================================


def display_welcome_banner(app_name: str = "U-AIP Scoping Assistant") -> None:
    """
    Display an attractive welcome banner.

    Args:
        app_name: Name of the application
    """
    banner_text = Text(app_name, style="bold cyan", justify="center")
    subtitle = Text("Universal AI Project Scoping and Framing Protocol", style="dim cyan", justify="center")

    console.print("\n")
    console.print(Align.center(banner_text))
    console.print(Align.center(subtitle))
    console.print(Align.center(Rule(style="cyan")))
    console.print()


def display_progress_bar(current: int, total: int, label: str = "Progress") -> None:
    """
    Display a progress bar with percentage.

    Args:
        current: Current progress value
        total: Total value
        label: Label for the progress bar
    """
    percentage = (current / total) * 100
    filled = int(percentage / 5)
    bar = "█" * filled + "░" * (20 - filled)
    console.print(f"[cyan]{label}:[/cyan] [{bar}] {percentage:.1f}% ({current}/{total})")


def display_info_box(title: str, content: str, style: str = "cyan") -> None:
    """
    Display an information box with title and content.

    Args:
        title: Title of the box
        content: Content to display
        style: Style for the box border
    """
    console.print(
        Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            box=ROUNDED,
            padding=(1, 2),
        )
    )


def display_success_box(title: str, content: str) -> None:
    """
    Display a success message box.

    Args:
        title: Title of the box
        content: Content to display
    """
    display_info_box(title, content, style="green")


def display_error_box(title: str, content: str) -> None:
    """
    Display an error message box.

    Args:
        title: Title of the box
        content: Content to display
    """
    display_info_box(title, content, style="red")


def display_warning_box(title: str, content: str) -> None:
    """
    Display a warning message box.

    Args:
        title: Title of the box
        content: Content to display
    """
    display_info_box(title, content, style="yellow")


def display_key_value_pairs(data: dict[str, Any], title: str = "Information") -> None:
    """
    Display key-value pairs in a formatted table-like structure.

    Args:
        data: Dictionary of key-value pairs
        title: Title for the display
    """
    from rich.table import Table

    table = Table(title=title, box=ROUNDED, show_header=False)
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Value", style="white")

    for key, value in data.items():
        table.add_row(key, str(value))

    console.print(table)


def display_list_items(items: list[str], title: str = "Items", style: str = "cyan") -> None:
    """
    Display a list of items with bullet points.

    Args:
        items: List of items to display
        title: Title for the list
        style: Style for the items
    """
    console.print(f"\n[bold {style}]{title}:[/bold {style}]")
    for item in items:
        console.print(f"  [green]•[/green] [{style}]{item}[/{style}]")
    console.print()


def display_code_block(code: str, language: str = "python", title: str = "Code") -> None:
    """
    Display a code block with syntax highlighting.

    Args:
        code: Code to display
        language: Programming language for syntax highlighting
        title: Title for the code block
    """
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(
        Panel(
            syntax,
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            box=ROUNDED,
        )
    )


def display_markdown_content(markdown_text: str) -> None:
    """
    Display markdown-formatted content.

    Args:
        markdown_text: Markdown text to display
    """
    md = Markdown(markdown_text)
    console.print(md)


def display_spinner_task(task_name: str, duration: float = 2.0) -> None:
    """
    Display a spinner with a task name.

    Args:
        task_name: Name of the task
        duration: Duration to show spinner (in seconds)
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"[cyan]{task_name}[/cyan]", total=None)
        import time
        time.sleep(duration)


def display_stage_progress(current_stage: int, total_stages: int = 5) -> None:
    """
    Display stage progress with visual indicators.

    Args:
        current_stage: Current stage number
        total_stages: Total number of stages
    """
    stages = []
    for i in range(1, total_stages + 1):
        if i < current_stage:
            stages.append(f"[green]✓ Stage {i}[/green]")
        elif i == current_stage:
            stages.append(f"[bold cyan]► Stage {i}[/bold cyan]")
        else:
            stages.append(f"[dim]○ Stage {i}[/dim]")

    console.print("\n[bold cyan]Stage Progress:[/bold cyan]")
    for stage in stages:
        console.print(f"  {stage}")
    console.print()


def display_comparison_table(data: list[dict[str, Any]], title: str = "Comparison") -> None:
    """
    Display a comparison table.

    Args:
        data: List of dictionaries to display
        title: Title for the table
    """
    from rich.table import Table

    if not data:
        console.print("[yellow]No data to display[/yellow]")
        return

    table = Table(title=title, box=ROUNDED)

    # Add columns from first item
    for key in data[0].keys():
        table.add_column(key, style="cyan")

    # Add rows
    for item in data:
        table.add_row(*[str(v) for v in item.values()])

    console.print(table)


def display_tree_structure(items: dict[str, list[str]], title: str = "Structure") -> None:
    """
    Display a tree structure.

    Args:
        items: Dictionary with parent keys and child lists
        title: Title for the tree
    """
    from rich.tree import Tree

    tree = Tree(f"[bold cyan]{title}[/bold cyan]")

    for parent, children in items.items():
        branch = tree.add(f"[cyan]{parent}[/cyan]")
        for child in children:
            branch.add(f"[dim]{child}[/dim]")

    console.print(tree)
