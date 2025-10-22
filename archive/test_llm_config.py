#!/usr/bin/env python3
"""
Quick LLM Configuration Test

Run this script to verify your LLM configuration is working correctly.
"""

import asyncio
import os
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_environment():
    """Check if environment is configured."""
    print("Checking environment configuration...")
    print("-" * 60)

    required_vars = {
        "ANTHROPIC_API_KEY": "Anthropic API Key",
    }

    optional_vars = {
        "ANTHROPIC_DEFAULT_MODEL": "Default Model",
        "ANTHROPIC_MODEL_FAST": "Fast Model (Haiku)",
        "ANTHROPIC_MODEL_BALANCED": "Balanced Model (Sonnet)",
        "LLM_COST_OPTIMIZATION": "Cost Optimization",
    }

    all_ok = True

    # Check required
    print("\nRequired Configuration:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✓ {description}: {masked}")
        else:
            print(f"  ✗ {description}: NOT SET")
            all_ok = False

    # Check optional
    print("\nOptional Configuration:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {description}: {value}")
        else:
            print(f"  ○ {description}: Using default")

    print("-" * 60)
    return all_ok


async def test_llm_router():
    """Test LLM Router with both models."""
    print("\nTesting LLM Router...")
    print("-" * 60)

    try:
        from src.llm.config import load_llm_config
        from src.llm.router import LLMRouter
        from src.llm.base import ModelTier

        # Load config
        print("\n1. Loading configuration...")
        config = load_llm_config()
        print("   ✓ Configuration loaded")

        # Create router
        print("\n2. Initializing LLM Router...")
        router = LLMRouter(config)
        print("   ✓ Router initialized")

        # Get provider info
        print("\n3. Provider Information:")
        info = router.get_provider_info()
        for key, value in info.items():
            print(f"   - {key}: {value}")

        # Test Haiku (FAST)
        print("\n4. Testing Haiku 4.5 (FAST tier)...")
        print("   Sending: 'Say hello in one word'")

        haiku_response = await router.route(
            prompt="Say hello in one word",
            model_tier=ModelTier.FAST,
            max_tokens=10,
        )

        print(f"   ✓ Response: {haiku_response.content}")
        print(f"   ✓ Model: {haiku_response.model}")
        print(f"   ✓ Tokens: {haiku_response.total_tokens}")
        print(f"   ✓ Latency: {haiku_response.latency_ms}ms")

        # Test Sonnet (BALANCED)
        print("\n5. Testing Sonnet 4 (BALANCED tier)...")
        print("   Sending: 'What is 2+2? Answer in 5 words.'")

        sonnet_response = await router.route(
            prompt="What is 2+2? Answer in 5 words.",
            model_tier=ModelTier.BALANCED,
            max_tokens=20,
        )

        print(f"   ✓ Response: {sonnet_response.content}")
        print(f"   ✓ Model: {sonnet_response.model}")
        print(f"   ✓ Tokens: {sonnet_response.total_tokens}")
        print(f"   ✓ Latency: {sonnet_response.latency_ms}ms")

        # Cost comparison
        print("\n6. Cost Comparison:")
        haiku_cost = (
            haiku_response.prompt_tokens * 0.0004 / 1000
            + haiku_response.completion_tokens * 0.002 / 1000
        )
        sonnet_cost = (
            sonnet_response.prompt_tokens * 0.003 / 1000
            + sonnet_response.completion_tokens * 0.015 / 1000
        )

        print(f"   Haiku cost: ${haiku_cost:.6f}")
        print(f"   Sonnet cost: ${sonnet_cost:.6f}")
        print(f"   Haiku is ~{sonnet_cost/haiku_cost:.1f}x cheaper")

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour LLM configuration is working correctly!")
        print("You can now use the LLM Router in your agents.")
        print("\nNext steps:")
        print("  1. Read QUICKSTART_LLM_CONFIG.md for usage examples")
        print("  2. Run: python examples/llm_usage_example.py")
        print("  3. Update your agents to use the LLM Router")

        return True

    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  uv pip install anthropic python-dotenv")
        return False

    except Exception as e:
        print(f"\n✗ Test Failed: {e}")
        print("\nPlease check:")
        print("  1. ANTHROPIC_API_KEY is set correctly in .env")
        print("  2. API key has access to Claude 4 models")
        print("  3. Model names are correct in .env")
        return False


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("LLM CONFIGURATION TEST")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("\n✗ Environment check failed!")
        print("\nPlease create a .env file with your configuration:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your ANTHROPIC_API_KEY")
        print("  3. Run this test again")
        sys.exit(1)

    # Test router
    try:
        success = asyncio.run(test_llm_router())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
