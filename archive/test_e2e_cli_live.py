#!/usr/bin/env python3
"""
End-to-End CLI Test with Live Connections (No Mocks)

This script runs a complete questionnaire flow using:
- Real database connections
- Real LLM (Anthropic or Ollama)
- Mock user input (automated responses)

Usage:
    python test_e2e_cli_live.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


async def run_e2e_test():
    """Run complete e2e test with live connections."""
    
    console.print(
        Panel.fit(
            "[bold cyan]🧪 E2E CLI Test - Live Connections[/bold cyan]\n"
            "[dim]Testing complete flow: Initialization → Charter Creation[/dim]\n"
            "[yellow]⚠️  Using LIVE database and LLM connections[/yellow]",
            border_style="cyan",
        )
    )
    
    # Import required modules
    from src.database.connection import DatabaseConfig, DatabaseManager
    from src.database.repositories.session_repository import SessionRepository
    from src.llm.router import llm_router
    from src.agents.orchestrator import Orchestrator
    from src.models.schemas import SessionStatus
    from src.agents.mocks.mock_input_handler import MockInputHandler
    
    # Test configuration
    project_name = f"E2E CLI Test - {datetime.now().strftime('%Y%m%d-%H%M%S')}"
    user_id = f"cli-test-{datetime.now().timestamp()}"
    
    console.print(f"\n[cyan]Test Configuration:[/cyan]")
    console.print(f"  • Project: {project_name}")
    console.print(f"  • User ID: {user_id}")
    console.print(f"  • Database: Live PostgreSQL (port 15432)")
    console.print(f"  • LLM: Live (Anthropic/Ollama)")
    console.print(f"  • Input: Automated (MockInputHandler)")
    
    # Step 1: Initialize Database
    console.print("\n[bold cyan]Step 1: Initialize Database Connection[/bold cyan]")
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
        console.print("  1. Run: docker compose up -d uaip-db")
        console.print("  2. Verify .env configuration")
        raise
    
    try:
        # Step 2: Create Session
        console.print("\n[bold cyan]Step 2: Create New Session[/bold cyan]")
        session_repo = SessionRepository(db_manager)
        session = await session_repo.create_new(
            user_id=user_id,
            project_name=project_name
        )
        console.print(f"[green]✓ Session created: {session.session_id}[/green]")
        
        # Step 3: Initialize Orchestrator with Real LLM
        console.print("\n[bold cyan]Step 3: Initialize Orchestrator (Live LLM)[/bold cyan]")
        orchestrator = Orchestrator(
            db_pool=db_manager.pool,
            llm_router=llm_router,
            config={}
        )
        console.print("[green]✓ Orchestrator initialized with live LLM router[/green]")
        
        # Step 4: Run Through All 5 Stages
        console.print("\n[bold cyan]Step 4: Execute 5-Stage Questionnaire[/bold cyan]")
        
        stage_names = {
            1: "Business Translation",
            2: "Value Quantification", 
            3: "Data Feasibility",
            4: "User Centricity",
            5: "Ethical Governance"
        }
        
        # Set up mock input handler for automated responses
        mock_handler = MockInputHandler()
        
        for stage_num in range(1, 6):
            stage_name = stage_names[stage_num]
            console.print(f"\n[yellow]{'='*60}[/yellow]")
            console.print(f"[bold cyan]Stage {stage_num}: {stage_name}[/bold cyan]")
            console.print(f"[yellow]{'='*60}[/yellow]")
            
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]Running Stage {stage_num} with live LLM...",
                        total=None
                    )
                    
                    # Get stage agent
                    stage_agent = orchestrator.stage_agents[stage_num](session)
                    
                    # Run stage (uses conduct_interview method)
                    stage_output = await stage_agent.conduct_interview()
                    
                    # Store output
                    session.stage_data[stage_num] = stage_output
                    await session_repo.update_stage(
                        session.session_id,
                        stage_num,
                        stage_output
                    )
                    
                    progress.update(task, completed=True)
                
                console.print(f"[green]✓ Stage {stage_num} completed[/green]")
                
                # Advance to next stage
                if stage_num < 5:
                    session.current_stage = stage_num + 1
                    await session_repo.update_current_stage(
                        session.session_id,
                        stage_num + 1
                    )
                else:
                    session.status = SessionStatus.COMPLETED
                    await session_repo.update_status(
                        session.session_id,
                        SessionStatus.COMPLETED
                    )
                
            except Exception as e:
                console.print(f"[red]✗ Stage {stage_num} failed: {e}[/red]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
                raise
        
        # Step 5: Generate Charter
        console.print("\n[bold cyan]Step 5: Generate AI Project Charter[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Generating charter...", total=None)
            charter = await orchestrator.generate_charter(session)
        
        console.print("[green]✓ Charter generated[/green]")
        
        # Display Results
        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]🎉 E2E Test Complete - SUCCESS![/bold green]\n\n"
                f"[bold]Test Summary:[/bold]\n"
                f"  • Project: {project_name}\n"
                f"  • Session ID: {session.session_id}\n"
                f"  • All 5 stages completed with live LLM\n"
                f"  • Charter generated successfully\n\n"
                f"[bold]Charter Details:[/bold]\n"
                f"  • Governance Decision: {charter.governance_decision.value}\n"
                f"  • Overall Feasibility: {charter.overall_feasibility.value}\n"
                f"  • Critical Success Factors: {len(charter.critical_success_factors)}\n"
                f"  • Major Risks: {len(charter.major_risks)}\n\n"
                f"[bold cyan]Verification Commands:[/bold cyan]\n"
                f"  • View session: uv run python -m src.cli.main status {session.session_id}\n"
                f"  • Export charter: uv run python -m src.cli.main export {session.session_id}",
                title="[bold green]✅ Test Report[/bold green]",
                border_style="green",
            )
        )
        
        return {
            "success": True,
            "session_id": str(session.session_id),
            "project_name": project_name,
            "governance_decision": charter.governance_decision.value,
            "feasibility": charter.overall_feasibility.value
        }
        
    finally:
        await db_manager.close()


def main():
    """Main entry point."""
    console.print("\n[dim]Starting E2E test with live connections...[/dim]\n")
    
    try:
        result = asyncio.run(run_e2e_test())
        console.print(f"\n[green]✅ Test passed! Session: {result['session_id']}[/green]\n")
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red]❌ Test failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
