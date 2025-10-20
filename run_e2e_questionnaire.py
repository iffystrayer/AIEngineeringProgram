#!/usr/bin/env python3
"""
End-to-End Questionnaire Runner

Runs a complete questionnaire flow from beginning to charter generation.
This script demonstrates the full U-AIP workflow with real LLM interactions.

Usage:
    python run_e2e_questionnaire.py [--project-name "Project Name"] [--user-id user123]
"""

import asyncio
import os
import sys
from pathlib import Path
from uuid import UUID

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


async def run_e2e_questionnaire(project_name: str = "AI Chatbot Assistant", user_id: str = "demo_user"):
    """
    Run a complete end-to-end questionnaire flow.
    
    Args:
        project_name: Name of the project to evaluate
        user_id: User identifier for session tracking
    """
    
    console.print(
        Panel.fit(
            "[bold cyan]🚀 U-AIP End-to-End Questionnaire Runner[/bold cyan]\n"
            "[dim]Running complete workflow from Stage 1 to Charter Generation[/dim]",
            border_style="cyan",
        )
    )
    
    # Import required modules
    from src.database.connection import DatabaseConfig, DatabaseManager
    from src.database.repositories.session_repository import SessionRepository
    from src.llm.router import llm_router
    from src.agents.orchestrator import Orchestrator
    from src.models.schemas import SessionStatus
    
    # Initialize database
    console.print("\n[cyan]Step 1: Initializing Database Connection[/cyan]")
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
        console.print("[green]✓ Database connected[/green]")
    except Exception as e:
        console.print(f"[red]✗ Database connection failed: {e}[/red]")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("  1. Ensure PostgreSQL is running: docker compose up -d uaip-db")
        console.print("  2. Verify database configuration in .env file")
        raise
    
    try:
        # Create session
        console.print("\n[cyan]Step 2: Creating Session[/cyan]")
        session_repo = SessionRepository(db_manager)
        session = await session_repo.create_new(user_id=user_id, project_name=project_name)
        console.print(f"[green]✓ Session created: {session.session_id}[/green]")
        
        # Initialize orchestrator
        console.print("\n[cyan]Step 3: Initializing Orchestrator[/cyan]")
        orchestrator = Orchestrator(
            db_pool=db_manager.pool,
            llm_router=llm_router,
            config={}
        )
        orchestrator.active_sessions[session.session_id] = session
        console.print("[green]✓ Orchestrator initialized[/green]")
        
        # Run through all 5 stages
        console.print("\n[cyan]Step 4: Running Multi-Stage Interview[/cyan]")
        
        stage_names = {
            1: "Business Translation",
            2: "Value Quantification",
            3: "Data Feasibility",
            4: "User Centricity",
            5: "Ethical Governance"
        }
        
        for stage_num in range(1, 6):
            stage_name = stage_names[stage_num]
            console.print(f"\n[bold yellow]{'='*60}[/bold yellow]")
            console.print(f"[bold cyan]Stage {stage_num}: {stage_name}[/bold cyan]")
            console.print(f"[bold yellow]{'='*60}[/bold yellow]")
            
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task(f"Running Stage {stage_num}...", total=None)
                    
                    # Run the stage
                    stage_output = await orchestrator.run_stage(session, stage_num)
                    
                console.print(f"[green]✓ Stage {stage_num} completed[/green]")
                
                # Advance to next stage
                if stage_num < 5:
                    await orchestrator.advance_to_next_stage(session)
                else:
                    session.status = SessionStatus.COMPLETED
                    
            except Exception as e:
                console.print(f"[red]✗ Stage {stage_num} failed: {e}[/red]")
                raise
        
        # Generate charter
        console.print("\n[cyan]Step 5: Generating AI Project Charter[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Generating charter...", total=None)
            charter = await orchestrator.generate_charter(session)
        
        console.print("[green]✓ Charter generated[/green]")
        
        # Display results
        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]🎉 Questionnaire Complete![/bold green]\n\n"
                f"[bold]Project:[/bold] {project_name}\n"
                f"[bold]Session ID:[/bold] {session.session_id}\n"
                f"[bold]Governance Decision:[/bold] {charter.governance_decision.value}\n"
                f"[bold]Overall Feasibility:[/bold] {charter.overall_feasibility.value}\n\n"
                f"[bold cyan]Next Steps:[/bold cyan]\n"
                f"  • Export charter: python -m src.cli.main export {session.session_id}\n"
                f"  • View session: python -m src.cli.main status {session.session_id}",
                title="[bold green]Success[/bold green]",
                border_style="green",
            )
        )
        
        return session, charter
        
    finally:
        await db_manager.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run end-to-end questionnaire")
    parser.add_argument("--project-name", default="AI Chatbot Assistant", help="Project name")
    parser.add_argument("--user-id", default="demo_user", help="User ID")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_e2e_questionnaire(args.project_name, args.user_id))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

