#!/usr/bin/env python3
"""
Quick test script to verify alpha interactive workflow.

This script tests the basic flow without requiring full user interaction.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.router import llm_router
from src.agents.orchestrator import Orchestrator
from src.models.schemas import Session, SessionStatus
from uuid import uuid4
from datetime import datetime


async def test_orchestrator_initialization():
    """Test that orchestrator can be initialized with llm_router."""
    print("Testing orchestrator initialization...")

    try:
        orchestrator = Orchestrator(
            db_pool=None,  # No DB for this test
            llm_router=llm_router,
            config={}
        )

        print(f"✅ Orchestrator initialized successfully")
        print(f"   - LLM router available: {orchestrator.llm_router is not None}")
        print(f"   - Stage agents registered: {list(orchestrator.stage_agents.keys())}")
        print(f"   - Quality agent available: {orchestrator.reflection_agents.get('quality') is not None}")

        return True
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return False


async def test_stage1_agent_creation():
    """Test that Stage 1 agent can be created with quality agent."""
    print("\nTesting Stage 1 agent creation...")

    try:
        orchestrator = Orchestrator(
            db_pool=None,
            llm_router=llm_router,
            config={}
        )

        # Create a mock session (simple object with required attributes)
        from types import SimpleNamespace
        session = SimpleNamespace(
            session_id=uuid4(),
            project_name="Test Project",
            status=SessionStatus.IN_PROGRESS,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            stage1_data=None,
            stage2_data=None,
            stage3_data=None,
            stage4_data=None,
            stage5_data=None
        )

        # Create stage 1 agent
        stage1_factory = orchestrator.stage_agents[1]
        stage1_agent = stage1_factory(session)

        print(f"✅ Stage 1 agent created successfully")
        print(f"   - Quality agent attached: {stage1_agent.quality_agent is not None}")
        print(f"   - Quality threshold: {stage1_agent.quality_threshold}")
        print(f"   - Max attempts: {stage1_agent.max_quality_attempts}")
        print(f"   - Question groups loaded: {len(stage1_agent.question_groups)}")

        return True
    except Exception as e:
        print(f"❌ Stage 1 agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_interactive_cli_imports():
    """Test that interactive CLI utilities can be imported."""
    print("\nTesting interactive CLI imports...")

    try:
        from src.cli.interactive import (
            ask_user_question,
            display_follow_up,
            display_quality_success,
            display_stage_header,
            display_group_header
        )

        print(f"✅ Interactive CLI utilities imported successfully")
        print(f"   - ask_user_question: {ask_user_question}")
        print(f"   - display_follow_up: {display_follow_up}")
        print(f"   - display_quality_success: {display_quality_success}")

        return True
    except Exception as e:
        print(f"❌ Interactive CLI imports failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("ALPHA INTERACTIVE WORKFLOW VERIFICATION")
    print("=" * 60)

    results = []

    # Test 1: Orchestrator initialization
    results.append(await test_orchestrator_initialization())

    # Test 2: Stage 1 agent creation
    results.append(await test_stage1_agent_creation())

    # Test 3: Interactive CLI imports
    results.append(await test_interactive_cli_imports())

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    total = len(results)
    passed = sum(results)

    print(f"Tests passed: {passed}/{total}")

    if all(results):
        print("\n✅ ALL TESTS PASSED - Alpha is ready for interactive use!")
        print("\nNext steps:")
        print("  1. Ensure ANTHROPIC_API_KEY or Ollama is available")
        print("  2. Run: uaip start \"<your project idea>\"")
        print("  3. Answer questions interactively as they appear")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Fix issues before using alpha")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
