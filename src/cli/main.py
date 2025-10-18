"""
CLI Main Entry Point

Main command-line interface for U-AIP Scoping Assistant.
Provides commands for session management and interactive conversations.
"""

import asyncio
import os
import sys
from typing import Optional
from uuid import UUID

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Version information
__version__ = "1.0.0-dev"

# Initialize Rich console for beautiful output
console = Console()


# ============================================================================
# MAIN CLI GROUP
# ============================================================================


@click.group()
@click.version_option(version=__version__, prog_name="uaip")
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose debug logging",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """
    U-AIP Scoping Assistant - AI Project Evaluation Tool

    An intelligent, conversational AI agent system for rigorous AI project
    evaluation following the Universal AI Project Scoping and Framing Protocol.

    Commands:
      start   - Begin a new project scoping session
      resume  - Continue an existing session
      list    - List your scoping sessions
      delete  - Delete a session
      export  - Export project charter
      status  - Show session status

    Examples:
      uaip start "Customer Churn Prediction"
      uaip resume 550e8400-e29b-41d4-a716-446655440000
      uaip list --status in_progress
    """
    # Initialize context object for passing state between commands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    # Set up logging level
    if verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
    else:
        os.environ["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")


# ============================================================================
# START COMMAND
# ============================================================================


@cli.command(name="start")
@click.argument("project_name", required=False)
@click.option(
    "--user-id",
    default=os.getenv("USER", "default_user"),
    help="User identifier for session tracking",
)
@click.option(
    "--resume-from-stage",
    type=int,
    default=1,
    help="Resume from specific stage (1-5)",
)
@click.pass_context
def start_command(
    ctx: click.Context,
    project_name: Optional[str],
    user_id: str,
    resume_from_stage: int,
) -> None:
    """
    Start a new project scoping session.

    PROJECT_NAME: Name of the AI project to evaluate (optional, will prompt if not provided)

    This command creates a new scoping session and begins the interactive
    conversation with Stage 1 (Business Translation) agent.

    Example:
      uaip start "Customer Churn Prediction Model"
      uaip start --user-id john.doe
    """
    console.print(
        Panel.fit(
            "[bold cyan]U-AIP Scoping Assistant[/bold cyan]\n"
            "[dim]Starting new project evaluation session...[/dim]",
            border_style="cyan",
        )
    )

    # Prompt for project name if not provided
    if not project_name:
        project_name = click.prompt("Project Name", type=str)

    # Validate stage number
    if resume_from_stage < 1 or resume_from_stage > 5:
        console.print("[bold red]Error:[/bold red] Stage must be between 1 and 5", style="red")
        sys.exit(1)

    # Run async start logic
    try:
        asyncio.run(_start_session_async(project_name, user_id, resume_from_stage, ctx.obj))
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted by user.[/yellow]")
        console.print("[dim]Session saved. Use 'uaip resume <session-id>' to continue.[/dim]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


async def _start_session_async(
    project_name: str, user_id: str, start_stage: int, config: dict
) -> None:
    """
    Async implementation of session start logic.

    Args:
        project_name: Name of the project to evaluate
        user_id: User identifier
        start_stage: Stage number to start from (1-5)
        config: Configuration dictionary from context
    """
    from rich.spinner import Spinner
    from rich.live import Live

    from src.database.connection import DatabaseConfig, DatabaseManager
    from src.database.repositories.session_repository import SessionRepository

    # Show initializing spinner
    with console.status("[cyan]Initializing database connection...", spinner="dots"):
        # Load database configuration from environment
        db_config = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "15432")),
            database=os.getenv("DB_NAME", "uaip_scoping"),
            user=os.getenv("DB_USER", "uaip_user"),
            password=os.getenv("DB_PASSWORD", "changeme"),
        )

        # Initialize database manager
        db_manager = DatabaseManager(db_config)

        try:
            await db_manager.initialize()
        except Exception as e:
            console.print(
                "\n[bold red]Error:[/bold red] Failed to connect to database",
                style="red",
            )
            console.print(f"[dim]Details: {e}[/dim]")
            console.print(
                "\n[yellow]Troubleshooting:[/yellow]\n"
                "  1. Ensure PostgreSQL is running: docker compose up -d uaip-db\n"
                "  2. Verify database configuration in .env file\n"
                "  3. Check connection settings: DB_HOST, DB_PORT, DB_NAME"
            )
            raise

    try:
        # Create session in database
        with console.status("[cyan]Creating new session...", spinner="dots"):
            session_repo = SessionRepository(db_manager)
            session = await session_repo.create_new(
                user_id=user_id, project_name=project_name
            )

        # Display success message with session information
        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]✓ Session Created Successfully![/bold green]\n\n"
                f"[bold]Project Name:[/bold] {project_name}\n"
                f"[bold]Session ID:[/bold] {session.session_id}\n"
                f"[bold]User:[/bold] {user_id}\n"
                f"[bold]Current Stage:[/bold] {session.current_stage}/5\n"
                f"[bold]Status:[/bold] {session.status.value}\n\n"
                f"[dim]💾 Session saved to database[/dim]\n"
                f"[dim]⏸️  Press Ctrl+C anytime to pause[/dim]\n"
                f"[dim]▶️  Resume with: uaip resume {session.session_id}[/dim]",
                title="[bold cyan]Session Information[/bold cyan]",
                border_style="green",
            )
        )

        # Initialize orchestrator and LLM router
        console.print("\n[cyan]Initializing AI agents...[/cyan]")

        from src.llm.router import llm_router
        from src.agents.orchestrator import Orchestrator

        # Create orchestrator with database pool and LLM router
        orchestrator = Orchestrator(
            db_pool=db_manager.pool,
            llm_router=llm_router,
            config={}
        )

        # Load the session into orchestrator
        orchestrator.active_sessions[session.session_id] = session

        # Run through stages based on start_stage
        console.print(f"\n[bold cyan]Starting Multi-Stage Interview (Stages {start_stage}-5)[/bold cyan]")

        for stage_num in range(start_stage, 6):
            stage_names = {
                1: "Business Translation",
                2: "Value Quantification",
                3: "Data Feasibility",
                4: "User Centricity",
                5: "Ethical Governance"
            }
            stage_name = stage_names[stage_num]

            console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
            console.print(f"[bold cyan]Stage {stage_num}: {stage_name}[/bold cyan]")
            console.print(f"[bold yellow]{'='*60}[/bold yellow]\n")

            try:
                # Run the stage (no spinner - stage handles its own interactive prompts)
                stage_output = await orchestrator.run_stage(session, stage_num)

                console.print(f"\n[bold green]✓ Stage {stage_num} completed successfully![/bold green]")
                console.print(f"[dim]Output type: {type(stage_output).__name__}[/dim]")

                # Update session context with stage data
                if stage_num == 1:
                    session.stage1_data = stage_output
                elif stage_num == 2:
                    session.stage2_data = stage_output
                elif stage_num == 3:
                    session.stage3_data = stage_output
                elif stage_num == 4:
                    session.stage4_data = stage_output
                elif stage_num == 5:
                    session.stage5_data = stage_output

                # Advance to next stage (unless we're at stage 5)
                if stage_num < 5:
                    await orchestrator.advance_to_next_stage(session)
                else:
                    # Mark as completed
                    from src.models.schemas import SessionStatus
                    session.status = SessionStatus.COMPLETED
                    session.last_updated_at = session.started_at  # Update timestamp

            except KeyboardInterrupt:
                console.print(f"\n[yellow]Paused at Stage {stage_num}[/yellow]")
                console.print(f"[dim]Resume with: uaip resume {session.session_id}[/dim]")
                raise
            except Exception as e:
                console.print(f"[bold red]Error in Stage {stage_num}:[/bold red] {e}")
                if config.get("verbose"):
                    console.print_exception()
                raise

        # All stages completed - generate charter
        console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
        console.print("[bold green]All Stages Completed![/bold green]")
        console.print(f"[bold yellow]{'='*60}[/bold yellow]\n")

        with console.status("[cyan]Generating AI Project Charter...[/cyan]", spinner="dots"):
            charter = await orchestrator.generate_charter(session)

        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]🎉 Project Scoping Complete![/bold green]\n\n"
                f"[bold]Project:[/bold] {project_name}\n"
                f"[bold]Session ID:[/bold] {session.session_id}\n"
                f"[bold]Governance Decision:[/bold] {charter.governance_decision.value}\n"
                f"[bold]Overall Feasibility:[/bold] {charter.overall_feasibility.value}\n\n"
                f"[bold cyan]Export your charter:[/bold cyan]\n"
                f"  uaip export {session.session_id}\n\n"
                f"[dim]Session completed successfully and saved to database.[/dim]",
                title="[bold green]Success[/bold green]",
                border_style="green",
            )
        )

    finally:
        # Clean up database connection
        await db_manager.close()


# ============================================================================
# RESUME COMMAND
# ============================================================================


@cli.command(name="resume")
@click.argument("session_id", type=str)
@click.pass_context
def resume_command(ctx: click.Context, session_id: str) -> None:
    """
    Resume an existing scoping session.

    SESSION_ID: UUID of the session to resume

    This command loads an existing session and continues the conversation
    from where it was left off.

    Example:
      uaip resume 550e8400-e29b-41d4-a716-446655440000
    """
    console.print(
        Panel.fit(
            "[bold cyan]U-AIP Scoping Assistant[/bold cyan]\n"
            "[dim]Resuming session...[/dim]",
            border_style="cyan",
        )
    )

    # Validate UUID format
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        console.print("[bold red]Error:[/bold red] Invalid session ID format", style="red")
        console.print("[dim]Expected UUID format: 550e8400-e29b-41d4-a716-446655440000[/dim]")
        sys.exit(1)

    # Run async resume logic
    try:
        asyncio.run(_resume_session_async(session_uuid, ctx.obj))
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


async def _resume_session_async(session_id: UUID, config: dict) -> None:
    """
    Async implementation of session resume logic.

    Args:
        session_id: UUID of session to resume
        config: Configuration dictionary from context
    """
    from src.database.connection import DatabaseConfig, DatabaseManager
    from src.database.repositories.session_repository import SessionRepository
    from src.models.schemas import SessionStatus

    # Initialize database connection
    with console.status("[cyan]Connecting to database...", spinner="dots"):
        db_config = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "15432")),
            database=os.getenv("DB_NAME", "uaip_scoping"),
            user=os.getenv("DB_USER", "uaip_user"),
            password=os.getenv("DB_PASSWORD", "changeme"),
        )

        db_manager = DatabaseManager(db_config)

        try:
            await db_manager.initialize()
        except Exception as e:
            console.print(
                "\n[bold red]Error:[/bold red] Failed to connect to database",
                style="red",
            )
            console.print(f"[dim]Details: {e}[/dim]")
            console.print(
                "\n[yellow]Troubleshooting:[/yellow]\n"
                "  1. Ensure PostgreSQL is running: docker compose up -d uaip-db\n"
                "  2. Verify database configuration in .env file"
            )
            raise

    try:
        # Load session from database
        with console.status("[cyan]Loading session...", spinner="dots"):
            session_repo = SessionRepository(db_manager)
            session = await session_repo.get_by_id(session_id)

        # Handle session not found
        if session is None:
            console.print(
                f"\n[bold red]Error:[/bold red] Session {session_id} not found",
                style="red",
            )
            console.print(
                "\n[yellow]Suggestions:[/yellow]\n"
                f"  • Check the session ID is correct\n"
                f"  • Use [cyan]uaip list[/cyan] to see your sessions\n"
                f"  • Start a new session with [cyan]uaip start[/cyan]"
            )
            sys.exit(1)

        # Check session status and provide appropriate feedback
        if session.status == SessionStatus.COMPLETED:
            console.print("\n")
            console.print(
                Panel.fit(
                    f"[bold yellow]ℹ️  Session Already Completed[/bold yellow]\n\n"
                    f"[bold]Project:[/bold] {session.project_name}\n"
                    f"[bold]Session ID:[/bold] {session_id}\n"
                    f"[bold]Completed Stages:[/bold] 5/5\n\n"
                    f"[green]This session has been completed successfully.[/green]\n\n"
                    f"[dim]Export the charter with:[/dim]\n"
                    f"  [cyan]uaip export {session_id}[/cyan]",
                    title="[bold cyan]Session Information[/bold cyan]",
                    border_style="yellow",
                )
            )
            return

        if session.status == SessionStatus.ABANDONED:
            console.print("\n")
            console.print(
                Panel.fit(
                    f"[bold yellow]ℹ️  Session Abandoned[/bold yellow]\n\n"
                    f"[bold]Project:[/bold] {session.project_name}\n"
                    f"[bold]Session ID:[/bold] {session_id}\n\n"
                    f"[dim]This session was marked as abandoned.[/dim]\n\n"
                    f"[yellow]Options:[/yellow]\n"
                    f"  • Start a new session: [cyan]uaip start \"{session.project_name}\"[/cyan]\n"
                    f"  • Delete this session: [cyan]uaip delete {session_id}[/cyan]",
                    title="[bold cyan]Session Information[/bold cyan]",
                    border_style="yellow",
                )
            )
            return

        # Display session information
        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]✓ Session Loaded Successfully![/bold green]\n\n"
                f"[bold]Project Name:[/bold] {session.project_name}\n"
                f"[bold]Session ID:[/bold] {session_id}\n"
                f"[bold]User:[/bold] {session.user_id}\n"
                f"[bold]Current Stage:[/bold] {session.current_stage}/5\n"
                f"[bold]Status:[/bold] {session.status.value}\n"
                f"[bold]Started:[/bold] {session.started_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"[bold]Last Updated:[/bold] {session.last_updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                f"[dim]Completed {session.current_stage - 1}/5 stages[/dim]\n"
                f"[dim]💾 State restored from database[/dim]\n"
                f"[dim]⏸️  Press Ctrl+C anytime to pause[/dim]",
                title="[bold cyan]Session Information[/bold cyan]",
                border_style="green",
            )
        )

        # Show stage progress
        if session.current_stage > 1:
            console.print("\n[cyan]Completed Stages:[/cyan]")
            stage_names = {
                1: "Business Translation",
                2: "Value Quantification",
                3: "Data Feasibility",
                4: "User Centricity",
                5: "Ethical Evaluation",
            }
            for stage in range(1, session.current_stage):
                console.print(f"  ✓ [dim]Stage {stage}: {stage_names.get(stage, 'Unknown')}[/dim]")

        # Show next steps (placeholder for agent integration)
        console.print("\n[cyan]Next Steps:[/cyan]")
        current_stage_name = {
            1: "Business Translation",
            2: "Value Quantification",
            3: "Data Feasibility",
            4: "User Centricity",
            5: "Ethical Evaluation",
        }.get(session.current_stage, "Unknown")

        console.print(
            f"  1. [dim]Initialize Stage {session.current_stage} ({current_stage_name}) Agent[/dim] "
            f"[yellow]→ Coming in Phase 2[/yellow]"
        )
        console.print(
            "  2. [dim]Resume interactive conversation[/dim] [yellow]→ Coming in Phase 2[/yellow]"
        )
        console.print(
            f"  3. [dim]Complete Stage {session.current_stage}[/dim] [yellow]→ Coming in Phase 2[/yellow]"
        )

        console.print(
            "\n[yellow]Note:[/yellow] Full agent conversation workflow will be implemented in Phase 2."
        )
        console.print(
            "[dim]For now, session state has been loaded from database successfully.[/dim]"
        )

    finally:
        # Clean up database connection
        await db_manager.close()


# ============================================================================
# LIST COMMAND
# ============================================================================


@cli.command(name="list")
@click.option(
    "--user-id",
    default=os.getenv("USER", "default_user"),
    help="User identifier to filter sessions",
)
@click.option(
    "--status",
    type=click.Choice(["in_progress", "completed", "paused", "abandoned", "all"], case_sensitive=False),
    default="all",
    help="Filter by session status",
)
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Maximum number of sessions to display",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format",
)
@click.pass_context
def list_command(
    ctx: click.Context,
    user_id: str,
    status: str,
    limit: int,
    output_format: str,
) -> None:
    """
    List scoping sessions.

    Display a list of your project scoping sessions with status and progress.

    Example:
      uaip list
      uaip list --status in_progress
      uaip list --format json --limit 5
    """
    console.print(
        Panel.fit(
            "[bold cyan]U-AIP Scoping Assistant[/bold cyan]\n"
            "[dim]Listing sessions...[/dim]",
            border_style="cyan",
        )
    )

    # Run async list logic
    try:
        asyncio.run(_list_sessions_async(user_id, status, limit, output_format, ctx.obj))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


async def _list_sessions_async(
    user_id: str, status: str, limit: int, output_format: str, config: dict
) -> None:
    """
    Async implementation of session listing logic.

    Args:
        user_id: User identifier to filter by
        status: Session status filter
        limit: Maximum number of sessions to display
        output_format: Output format (table or json)
        config: Configuration dictionary from context
    """
    import json
    from src.database.connection import DatabaseConfig, DatabaseManager
    from src.database.repositories.session_repository import SessionRepository
    from src.models.schemas import SessionStatus

    # Initialize database connection
    with console.status("[cyan]Loading sessions...", spinner="dots"):
        db_config = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "15432")),
            database=os.getenv("DB_NAME", "uaip_scoping"),
            user=os.getenv("DB_USER", "uaip_user"),
            password=os.getenv("DB_PASSWORD", "changeme"),
        )

        db_manager = DatabaseManager(db_config)

        try:
            await db_manager.initialize()
        except Exception as e:
            console.print(
                "\n[bold red]Error:[/bold red] Failed to connect to database",
                style="red",
            )
            console.print(f"[dim]Details: {e}[/dim]")
            console.print(
                "\n[yellow]Troubleshooting:[/yellow]\n"
                "  1. Ensure PostgreSQL is running: docker compose up -d uaip-db\n"
                "  2. Verify database configuration in .env file"
            )
            raise

    try:
        # Query sessions from database
        session_repo = SessionRepository(db_manager)
        all_sessions = await session_repo.get_by_user_id(user_id)

        # Filter by status if not "all"
        if status != "all":
            status_enum = SessionStatus(status)
            filtered_sessions = [s for s in all_sessions if s.status == status_enum]
        else:
            filtered_sessions = all_sessions

        # Sort by last_updated_at (most recent first)
        sorted_sessions = sorted(
            filtered_sessions,
            key=lambda s: s.last_updated_at,
            reverse=True
        )

        # Apply limit
        limited_sessions = sorted_sessions[:limit]

        # Handle empty results
        if not limited_sessions:
            console.print("\n")
            console.print(
                Panel.fit(
                    "[bold yellow]No Sessions Found[/bold yellow]\n\n"
                    f"[dim]No sessions found for user:[/dim] [cyan]{user_id}[/cyan]\n"
                    f"[dim]Status filter:[/dim] [cyan]{status}[/cyan]\n\n"
                    "[bold]Get Started:[/bold]\n"
                    "  • Start a new session: [cyan]uaip start \"Project Name\"[/cyan]",
                    title="[bold cyan]Session List[/bold cyan]",
                    border_style="yellow",
                )
            )
            return

        # Output based on format
        if output_format == "table":
            # Create Rich table
            table = Table(title=f"Your Sessions ({len(limited_sessions)})")
            table.add_column("Session ID", style="cyan", no_wrap=True)
            table.add_column("Project Name", style="white", max_width=40)
            table.add_column("Stage", justify="center", style="yellow")
            table.add_column("Status", justify="center")
            table.add_column("Started", style="dim")
            table.add_column("Last Updated", style="dim")

            # Status color mapping
            status_colors = {
                SessionStatus.IN_PROGRESS: "cyan",
                SessionStatus.COMPLETED: "green",
                SessionStatus.PAUSED: "yellow",
                SessionStatus.ABANDONED: "red",
            }

            # Add rows
            for session in limited_sessions:
                # Truncate session ID to first 8 chars
                short_id = str(session.session_id)[:8] + "..."

                # Truncate project name if too long
                project_name = session.project_name
                if len(project_name) > 40:
                    project_name = project_name[:37] + "..."

                # Format stage
                stage_str = f"{session.current_stage}/5"

                # Color-code status
                status_color = status_colors.get(session.status, "white")
                status_str = f"[{status_color}]{session.status.value}[/{status_color}]"

                # Format dates
                started_str = session.started_at.strftime("%Y-%m-%d")
                updated_str = session.last_updated_at.strftime("%Y-%m-%d %H:%M")

                table.add_row(
                    short_id,
                    project_name,
                    stage_str,
                    status_str,
                    started_str,
                    updated_str
                )

            console.print("\n")
            console.print(table)

            # Show filter info and pagination hint
            console.print(f"\n[dim]Showing {len(limited_sessions)} of {len(filtered_sessions)} sessions[/dim]")
            if len(filtered_sessions) > limit:
                console.print(
                    f"[dim]Use [cyan]--limit {len(filtered_sessions)}[/cyan] to see all sessions[/dim]"
                )

            # Show helpful commands
            console.print("\n[bold]Quick Actions:[/bold]")
            console.print("  • Resume session: [cyan]uaip resume <session-id>[/cyan]")
            console.print("  • Filter by status: [cyan]uaip list --status in_progress[/cyan]")
            console.print("  • JSON output: [cyan]uaip list --format json[/cyan]")

        else:
            # JSON format
            json_data = []
            for session in limited_sessions:
                json_data.append({
                    "session_id": str(session.session_id),
                    "user_id": session.user_id,
                    "project_name": session.project_name,
                    "current_stage": session.current_stage,
                    "status": session.status.value,
                    "started_at": session.started_at.isoformat(),
                    "last_updated_at": session.last_updated_at.isoformat(),
                })

            console.print(json.dumps(json_data, indent=2))

    finally:
        # Clean up database connection
        await db_manager.close()


# ============================================================================
# DELETE COMMAND
# ============================================================================


@cli.command(name="delete")
@click.argument("session_id", type=str)
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_command(ctx: click.Context, session_id: str, force: bool) -> None:
    """
    Delete a scoping session.

    SESSION_ID: UUID of the session to delete

    This command permanently deletes a session and all related data
    (conversation history, checkpoints, charters). This action cannot be undone.

    Example:
      uaip delete 550e8400-e29b-41d4-a716-446655440000
      uaip delete 550e8400-e29b-41d4-a716-446655440000 --force
    """
    # Validate UUID format
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        console.print("[bold red]Error:[/bold red] Invalid session ID format", style="red")
        sys.exit(1)

    # Confirmation prompt unless --force
    if not force:
        confirmed = click.confirm(
            f"Are you sure you want to delete session {session_id}? "
            "This action cannot be undone."
        )
        if not confirmed:
            console.print("[yellow]Deletion cancelled.[/yellow]")
            sys.exit(0)

    console.print(f"[yellow]Deleting session {session_id}...[/yellow]")
    console.print(
        "\n[yellow]Note:[/yellow] This is a placeholder. "
        "Actual deletion will be implemented with database integration."
    )


# ============================================================================
# EXPORT COMMAND
# ============================================================================


@cli.command(name="export")
@click.argument("session_id", type=str)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["pdf", "markdown", "json"], case_sensitive=False),
    default="pdf",
    help="Export format",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path (defaults to charters/ directory)",
)
@click.pass_context
def export_command(
    ctx: click.Context,
    session_id: str,
    output_format: str,
    output: Optional[str],
) -> None:
    """
    Export project charter document.

    SESSION_ID: UUID of the session to export

    Generates and exports the AI Project Charter document in the specified format.

    Example:
      uaip export 550e8400-e29b-41d4-a716-446655440000
      uaip export 550e8400-e29b-41d4-a716-446655440000 --format markdown --output my_charter.md
    """
    # Validate UUID format
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        console.print("[bold red]Error:[/bold red] Invalid session ID format", style="red")
        sys.exit(1)

    # Run async export logic
    try:
        asyncio.run(_export_charter_async(session_uuid, output_format, output, ctx.obj))
    except KeyboardInterrupt:
        console.print("\n[yellow]Export interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


async def _export_charter_async(
    session_id: UUID, output_format: str, output_path: Optional[str], config: dict
) -> None:
    """
    Async implementation of charter export logic.

    Args:
        session_id: UUID of session to export
        output_format: Export format (pdf, markdown, json)
        output_path: Optional output file path
        config: Configuration dictionary from context
    """
    import os
    from pathlib import Path
    from src.database.connection import DatabaseConfig, DatabaseManager
    from src.database.repositories.charter_repository import CharterRepository
    from src.export import CharterDocumentGenerator

    console.print(
        Panel.fit(
            "[bold cyan]U-AIP Charter Export[/bold cyan]\n"
            f"[dim]Exporting session {session_id}...[/dim]",
            border_style="cyan",
        )
    )

    # Initialize database connection
    with console.status("[cyan]Connecting to database...", spinner="dots"):
        db_config = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "15432")),
            database=os.getenv("DB_NAME", "uaip_scoping"),
            user=os.getenv("DB_USER", "uaip_user"),
            password=os.getenv("DB_PASSWORD", "changeme"),
        )

        db_manager = DatabaseManager(db_config)

        try:
            await db_manager.initialize()
        except Exception as e:
            console.print(
                "\n[bold red]Error:[/bold red] Failed to connect to database",
                style="red",
            )
            console.print(f"[dim]Details: {e}[/dim]")
            console.print(
                "\n[yellow]Troubleshooting:[/yellow]\n"
                "  1. Ensure PostgreSQL is running: docker compose up -d uaip-db\n"
                "  2. Verify database configuration in .env file"
            )
            raise

    try:
        # Load charter from database
        with console.status("[cyan]Loading charter...", spinner="dots"):
            charter_repo = CharterRepository(db_manager)
            charter = await charter_repo.get_charter_by_session(session_id)

        if charter is None:
            console.print(
                f"\n[bold red]Error:[/bold red] No charter found for session {session_id}",
                style="red",
            )
            console.print(
                "\n[yellow]Note:[/yellow] Charters are created when sessions complete all 5 stages.\n"
                "[dim]This session may not be complete yet.[/dim]\n\n"
                "[bold]Next steps:[/bold]\n"
                "  • Check session status: [cyan]uaip status {session_id}[/cyan]\n"
                "  • Resume session: [cyan]uaip resume {session_id}[/cyan]"
            )
            sys.exit(1)

        # Generate export
        console.print(f"\n[cyan]Generating {output_format.upper()} export...[/cyan]")

        with console.status(f"[cyan]Generating {output_format} document...", spinner="dots"):
            generator = CharterDocumentGenerator()

            if output_format == "markdown":
                content = await generator.generate_markdown(charter)
                file_extension = ".md"
                content_bytes = content.encode('utf-8')
            elif output_format == "pdf":
                content_bytes = await generator.generate_pdf(charter)
                file_extension = ".pdf"
            else:  # json
                content = await generator.generate_json(charter)
                file_extension = ".json"
                content_bytes = content.encode('utf-8')

        # Determine output path
        if output_path:
            final_path = Path(output_path)
        else:
            # Default to charters/ directory
            charters_dir = Path("charters")
            charters_dir.mkdir(exist_ok=True)

            # Sanitize project name for filename
            safe_project_name = "".join(
                c if c.isalnum() or c in (' ', '_', '-') else '_'
                for c in charter.project_name
            ).strip().replace(' ', '_')

            filename = f"{safe_project_name}_{session_id}_charter{file_extension}"
            final_path = charters_dir / filename

        # Write file
        with console.status(f"[cyan]Writing to {final_path}...", spinner="dots"):
            if output_format in ["pdf"]:
                final_path.write_bytes(content_bytes)
            else:
                final_path.write_bytes(content_bytes)

        # Success message
        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]✓ Charter Exported Successfully![/bold green]\n\n"
                f"[bold]Project:[/bold] {charter.project_name}\n"
                f"[bold]Format:[/bold] {output_format.upper()}\n"
                f"[bold]Output:[/bold] {final_path.absolute()}\n"
                f"[bold]Size:[/bold] {len(content_bytes):,} bytes\n\n"
                f"[dim]Open with:[/dim]\n"
                f"  {final_path.absolute()}",
                title="[bold cyan]Export Complete[/bold cyan]",
                border_style="green",
            )
        )

    finally:
        # Clean up database connection
        await db_manager.close()


# ============================================================================
# STATUS COMMAND
# ============================================================================


@cli.command(name="status")
@click.argument("session_id", type=str)
@click.pass_context
def status_command(ctx: click.Context, session_id: str) -> None:
    """
    Show detailed session status.

    SESSION_ID: UUID of the session to inspect

    Displays detailed information about a session including current stage,
    progress, quality scores, and conversation history.

    Example:
      uaip status 550e8400-e29b-41d4-a716-446655440000
    """
    # Validate UUID format
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        console.print("[bold red]Error:[/bold red] Invalid session ID format", style="red")
        sys.exit(1)

    console.print(f"[cyan]Session Status: {session_id}[/cyan]")

    console.print(
        "\n[yellow]Note:[/yellow] This is a placeholder. "
        "Actual status display will be implemented with database integration."
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main() -> None:
    """Main entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
