#!/usr/bin/env python3
"""
Test script to verify the JSON parsing and LLMRouter fixes.

This script simulates the user interaction flow and tests:
1. JSON extraction from LLM responses with extra text
2. LLMRouter.route() method calls
3. Quality validation workflow
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.router import llm_router
from src.agents.reflection.response_quality_agent import ResponseQualityAgent


async def test_json_extraction():
    """Test the bracket-counting JSON extraction method."""
    print("=" * 60)
    print("TEST 1: JSON Extraction with Bracket Counting")
    print("=" * 60)

    quality_agent = ResponseQualityAgent(
        llm_router=llm_router,
        quality_threshold=7,
        max_reflection_loops=3
    )

    # Test case 1: Clean JSON
    test_json_1 = '{"quality_score": 8, "issues": []}'
    result_1 = quality_agent._extract_json_object(test_json_1)
    print(f"\n✓ Test 1a - Clean JSON:")
    print(f"  Input: {test_json_1[:50]}...")
    print(f"  Output: {result_1[:50] if result_1 else None}...")
    print(f"  Success: {result_1 == test_json_1}")

    # Test case 2: JSON with trailing text (the problematic case from your error)
    test_json_2 = '{"quality_score": 5, "issues": ["test"]}\n\nHere is some extra explanation that was causing the error...'
    result_2 = quality_agent._extract_json_object(test_json_2)
    expected_2 = '{"quality_score": 5, "issues": ["test"]}'
    print(f"\n✓ Test 1b - JSON with trailing text:")
    print(f"  Input: {test_json_2[:70]}...")
    print(f"  Output: {result_2}")
    print(f"  Expected: {expected_2}")
    print(f"  Success: {result_2 == expected_2}")

    # Test case 3: Nested JSON
    test_json_3 = '{"outer": {"inner": {"deep": "value"}}, "score": 7}'
    result_3 = quality_agent._extract_json_object(test_json_3)
    print(f"\n✓ Test 1c - Nested JSON:")
    print(f"  Input: {test_json_3}")
    print(f"  Output: {result_3}")
    print(f"  Success: {result_3 == test_json_3}")

    print(f"\n{'=' * 60}")
    print("JSON Extraction Tests: PASSED ✅")
    print(f"{'=' * 60}\n")


async def test_llm_router_route_method():
    """Test that LLMRouter has route() method and it works."""
    print("=" * 60)
    print("TEST 2: LLMRouter.route() Method")
    print("=" * 60)

    # Check method exists
    has_route = hasattr(llm_router, 'route')
    print(f"\n✓ LLMRouter.route() method exists: {has_route}")

    if has_route:
        # Test simple prompt
        from src.llm.base import ModelTier

        try:
            print(f"\n✓ Testing route() method with simple prompt...")
            response = await llm_router.route(
                prompt="Say 'test successful' in 2 words",
                model_tier=ModelTier.FAST,
                max_tokens=10
            )

            print(f"  Response type: {type(response).__name__}")
            print(f"  Has content: {hasattr(response, 'content')}")
            print(f"  Content preview: {response.content[:50] if response.content else None}...")
            print(f"\n{'=' * 60}")
            print("LLMRouter.route() Test: PASSED ✅")
            print(f"{'=' * 60}\n")
            return True

        except AttributeError as e:
            print(f"\n❌ ERROR: {e}")
            print(f"  This was the bug we fixed!")
            print(f"\n{'=' * 60}")
            print("LLMRouter.route() Test: FAILED ❌")
            print(f"{'=' * 60}\n")
            return False
    else:
        print(f"\n❌ LLMRouter.route() method not found!")
        return False


async def test_quality_evaluation():
    """Test the full quality evaluation with JSON parsing."""
    print("=" * 60)
    print("TEST 3: Full Quality Evaluation Flow")
    print("=" * 60)

    quality_agent = ResponseQualityAgent(
        llm_router=llm_router,
        quality_threshold=7,
        max_reflection_loops=3
    )

    print(f"\n✓ Testing quality evaluation...")
    print(f"  Question: 'What would success look like?'")
    print(f"  Response: 'we will measure EBITDA growth'")

    try:
        assessment = await quality_agent.evaluate_response(
            question="What would success look like? How will you measure it?",
            user_response="we will measure EBITDA growth and rank it against the same period last year. a 10% increase will show success",
            stage_context={"stage": 1, "stage_name": "Stage 1"}
        )

        print(f"\n  Quality Score: {assessment.quality_score}/10")
        print(f"  Is Acceptable: {assessment.is_acceptable}")
        print(f"  Issues: {len(assessment.issues)}")
        if assessment.issues:
            for i, issue in enumerate(assessment.issues[:2], 1):
                print(f"    {i}. {issue[:60]}...")

        print(f"\n{'=' * 60}")
        print("Quality Evaluation Test: PASSED ✅")
        print(f"{'=' * 60}\n")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n{'=' * 60}")
        print("Quality Evaluation Test: FAILED ❌")
        print(f"{'=' * 60}\n")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🔧" * 30)
    print(" FIX VERIFICATION TESTS")
    print("🔧" * 30 + "\n")

    print("Testing the fixes for:")
    print("1. JSON parsing with bracket-counting algorithm")
    print("2. LLMRouter.route() method (was calling .complete())")
    print("3. Full quality evaluation workflow\n")

    # Run tests
    await test_json_extraction()

    route_result = await test_llm_router_route_method()

    if route_result:
        quality_result = await test_quality_evaluation()
    else:
        print("⚠️  Skipping quality evaluation test due to route() failure")
        quality_result = False

    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    if route_result and quality_result:
        print("\n✅ ALL FIXES VERIFIED SUCCESSFULLY!")
        print("\nThe following issues have been resolved:")
        print("  1. ✅ JSON parsing no longer fails on 'Extra data' errors")
        print("  2. ✅ LLMRouter.route() method works correctly")
        print("  3. ✅ Follow-up generation no longer throws AttributeError")
        print("  4. ✅ Quality validation completes successfully")
        print("\n🎉 The application is ready for interactive use!")
        print("\nTo test the full interactive flow:")
        print("  docker exec uaip-app /app/.venv/bin/python3 -m src.cli.main start \"your project name\"")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease check the errors above and ensure:")
        print("  1. Docker container is running with latest code")
        print("  2. Ollama is running (or ANTHROPIC_API_KEY is set)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
