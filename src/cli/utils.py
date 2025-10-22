"""
CLI Utility Functions

Provides helper functions for rich terminal display and formatting.
"""

from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.columns import Columns
from rich.rule import Rule
from rich.tree import Tree

console = Console()


def print_header(text: str, style: str = "cyan") -> None:
    """Print a formatted header."""
    console.print(f"\n[bold {style}]{text}[/bold {style}]")
    console.print(Align.center(Rule(style=style)))


def print_section(title: str, content: str, style: str = "cyan") -> None:
    """Print a section with title and content."""
    console.print(
        Panel(
            content,
            title=f"[bold {style}]{title}[/bold {style}]",
            border_style=style,
            box=ROUNDED,
            padding=(1, 2),
        )
    )


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] [bold green]{message}[/bold green]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] [bold red]{message}[/bold red]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] [bold yellow]{message}[/bold yellow]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[cyan]ℹ[/cyan] [bold cyan]{message}[/bold cyan]")


def print_step(step_num: int, total_steps: int, message: str) -> None:
    """Print a step in a process."""
    percentage = (step_num / total_steps) * 100
    console.print(f"[cyan][{step_num}/{total_steps}][/cyan] {message} [dim]({percentage:.0f}%)[/dim]")


def create_status_table(
    data: list[dict[str, Any]],
    title: str = "Status",
    columns: Optional[list[str]] = None,
) -> Table:
    """Create a formatted status table."""
    table = Table(title=title, box=ROUNDED, show_header=True, header_style="bold cyan")
    
    if not data:
        return table
    
    # Use provided columns or extract from first item
    cols = columns or list(data[0].keys())
    
    for col in cols:
        table.add_column(col, style="white")
    
    for item in data:
        row = [str(item.get(col, "")) for col in cols]
        table.add_row(*row)
    
    return table


def create_key_value_table(data: dict[str, Any], title: str = "Information") -> Table:
    """Create a key-value table."""
    table = Table(title=title, box=ROUNDED, show_header=False)
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    for key, value in data.items():
        table.add_row(key, str(value))
    
    return table


def create_progress_bar(current: int, total: int, label: str = "Progress") -> str:
    """Create a progress bar string."""
    percentage = (current / total) * 100
    filled = int(percentage / 5)
    bar = "█" * filled + "░" * (20 - filled)
    return f"[cyan]{label}:[/cyan] [{bar}] {percentage:.1f}% ({current}/{total})"


def display_tree(items: dict[str, list[str]], title: str = "Structure") -> None:
    """Display a tree structure."""
    tree = Tree(f"[bold cyan]{title}[/bold cyan]")
    
    for parent, children in items.items():
        branch = tree.add(f"[cyan]{parent}[/cyan]")
        for child in children:
            branch.add(f"[dim]{child}[/dim]")
    
    console.print(tree)


def display_columns(left: str, right: str, title: str = "Comparison") -> None:
    """Display two columns side by side."""
    left_panel = Panel(left, title="[bold cyan]Left[/bold cyan]", border_style="cyan", box=ROUNDED)
    right_panel = Panel(right, title="[bold cyan]Right[/bold cyan]", border_style="cyan", box=ROUNDED)
    
    console.print(Columns([left_panel, right_panel]))


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_size(bytes_size: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"


def create_status_indicator(status: str) -> str:
    """Create a colored status indicator."""
    status_map = {
        "completed": "[green]✓ Completed[/green]",
        "in_progress": "[cyan]► In Progress[/cyan]",
        "paused": "[yellow]⏸ Paused[/yellow]",
        "abandoned": "[red]✗ Abandoned[/red]",
        "pending": "[dim]○ Pending[/dim]",
    }
    return status_map.get(status.lower(), f"[white]{status}[/white]")


def create_stage_indicator(current: int, total: int = 5) -> str:
    """Create a stage progress indicator."""
    stages = []
    for i in range(1, total + 1):
        if i < current:
            stages.append(f"[green]✓[/green]")
        elif i == current:
            stages.append(f"[bold cyan]●[/bold cyan]")
        else:
            stages.append(f"[dim]○[/dim]")
    return " ".join(stages)


def print_loading_spinner(message: str, duration: float = 2.0) -> None:
    """Display a loading spinner."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(f"[cyan]{message}[/cyan]", total=None)
        import time
        time.sleep(duration)


def print_box(content: str, title: str = "", style: str = "cyan", padding: tuple = (1, 2)) -> None:
    """Print content in a box."""
    panel = Panel(
        content,
        title=f"[bold {style}]{title}[/bold {style}]" if title else None,
        border_style=style,
        box=ROUNDED,
        padding=padding,
    )
    console.print(panel)


def print_divider(char: str = "─", style: str = "dim") -> None:
    """Print a divider line."""
    console.print(f"[{style}]{char * 80}[/{style}]")


def print_centered(text: str, style: str = "white") -> None:
    """Print centered text."""
    console.print(Align.center(Text(text, style=style)))


def print_bullet_list(items: list[str], title: str = "", style: str = "cyan") -> None:
    """Print a bullet list."""
    if title:
        console.print(f"\n[bold {style}]{title}:[/bold {style}]")
    for item in items:
        console.print(f"  [green]•[/green] [{style}]{item}[/{style}]")
    console.print()

