"""
LLM Router Usage Example

Demonstrates how to use the LLM Router with automatic model switching
between Claude Sonnet and Haiku based on task complexity.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.base import ModelTier
from src.llm.config import (
    estimate_cost,
    get_model_tier_from_task_type,
    load_llm_config,
    validate_environment,
)
from src.llm.router import LLMRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Basic usage with automatic model selection."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Basic Usage with Automatic Model Selection")
    print("=" * 60)

    # Load configuration from environment
    config = load_llm_config()
    router = LLMRouter(config)

    # Example 1: Fast task (uses Haiku)
    print("\n1. Fast Task - Simple Question")
    response = await router.route(
        prompt="What is 2 + 2?",
        model_tier=ModelTier.FAST,
    )

    print(f"   Response: {response.content}")
    print(f"   Model: {response.model}")
    print(f"   Tokens: {response.total_tokens}")
    print(
        f"   Cost: ${estimate_cost(response.prompt_tokens, response.completion_tokens, response.model):.6f}"
    )

    # Example 2: Balanced task (uses Sonnet)
    print("\n2. Balanced Task - Code Generation")
    response = await router.route(
        prompt="Write a Python function to calculate fibonacci numbers",
        model_tier=ModelTier.BALANCED,
        max_tokens=500,
    )

    print(f"   Response: {response.content[:100]}...")
    print(f"   Model: {response.model}")
    print(f"   Tokens: {response.total_tokens}")
    print(
        f"   Cost: ${estimate_cost(response.prompt_tokens, response.completion_tokens, response.model):.6f}"
    )


async def example_task_type_routing():
    """Demonstrate automatic tier selection based on task type."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Automatic Tier Selection by Task Type")
    print("=" * 60)

    config = load_llm_config()
    router = LLMRouter(config)

    tasks = [
        ("summary", "Summarize this in one sentence: AI is transforming software"),
        ("code_generation", "Create a REST API endpoint in Python"),
        ("architecture_design", "Design a microservices architecture for e-commerce"),
    ]

    for task_type, prompt in tasks:
        # Get recommended tier
        tier = get_model_tier_from_task_type(task_type)

        print(f"\nTask Type: {task_type}")
        print(f"Recommended Tier: {tier.value}")

        response = await router.route(
            prompt=prompt,
            model_tier=tier,
            max_tokens=300,
        )

        print(f"Model Used: {response.model}")
        print(f"Tokens: {response.total_tokens}")
        print(
            f"Cost: ${estimate_cost(response.prompt_tokens, response.completion_tokens, response.model):.6f}"
        )


async def example_cost_comparison():
    """Compare costs between Haiku and Sonnet for different tasks."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Cost Comparison - Haiku vs Sonnet")
    print("=" * 60)

    config = load_llm_config()
    router = LLMRouter(config)

    prompt = "List 5 benefits of using Python for data science"

    # Test with Haiku
    print("\nUsing Haiku (Fast):")
    haiku_response = await router.route(
        prompt=prompt,
        model_tier=ModelTier.FAST,
    )

    haiku_cost = estimate_cost(
        haiku_response.prompt_tokens,
        haiku_response.completion_tokens,
        haiku_response.model,
    )

    print(f"   Model: {haiku_response.model}")
    print(f"   Tokens: {haiku_response.total_tokens}")
    print(f"   Latency: {haiku_response.latency_ms}ms")
    print(f"   Cost: ${haiku_cost:.6f}")

    # Test with Sonnet
    print("\nUsing Sonnet (Balanced):")
    sonnet_response = await router.route(
        prompt=prompt,
        model_tier=ModelTier.BALANCED,
    )

    sonnet_cost = estimate_cost(
        sonnet_response.prompt_tokens,
        sonnet_response.completion_tokens,
        sonnet_response.model,
    )

    print(f"   Model: {sonnet_response.model}")
    print(f"   Tokens: {sonnet_response.total_tokens}")
    print(f"   Latency: {sonnet_response.latency_ms}ms")
    print(f"   Cost: ${sonnet_cost:.6f}")

    # Comparison
    print(f"\nCost Savings with Haiku: ${sonnet_cost - haiku_cost:.6f}")
    print(
        f"Percentage Saved: {((sonnet_cost - haiku_cost) / sonnet_cost * 100):.1f}%"
    )


async def example_streaming():
    """Demonstrate streaming responses."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Streaming Response")
    print("=" * 60)

    config = load_llm_config()
    router = LLMRouter(config)

    # Note: Streaming implementation depends on your specific needs
    # This is a placeholder for streaming functionality
    print("\nStreaming a creative story (with Sonnet):")
    print("Stream: ", end="", flush=True)

    # For now, use regular completion
    response = await router.route(
        prompt="Write a one-paragraph story about a robot learning to code",
        model_tier=ModelTier.BALANCED,
        max_tokens=200,
    )

    # Simulate streaming output
    for char in response.content:
        print(char, end="", flush=True)
        await asyncio.sleep(0.01)

    print(f"\n\nModel: {response.model}")
    print(f"Tokens: {response.total_tokens}")


async def example_agent_integration():
    """Example of using LLM Router in an agent."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Agent Integration")
    print("=" * 60)

    class SimpleAgent:
        """Example agent that uses LLM Router intelligently."""

        def __init__(self, llm_router: LLMRouter):
            self.llm_router = llm_router

        async def analyze_code(self, code: str) -> dict:
            """Analyze code (complex task - uses Sonnet)."""
            prompt = f"Analyze this code and identify issues:\n\n{code}"

            response = await self.llm_router.route(
                prompt=prompt,
                model_tier=ModelTier.BALANCED,
                max_tokens=500,
            )

            return {
                "analysis": response.content,
                "model": response.model,
                "tokens": response.total_tokens,
            }

        async def summarize_analysis(self, analysis: str) -> str:
            """Summarize analysis (simple task - uses Haiku)."""
            prompt = f"Summarize in one sentence:\n\n{analysis}"

            response = await self.llm_router.route(
                prompt=prompt,
                model_tier=ModelTier.FAST,
                max_tokens=100,
            )

            return response.content

    # Initialize agent
    config = load_llm_config()
    router = LLMRouter(config)
    agent = SimpleAgent(router)

    # Test code
    test_code = """
def calculate(x, y):
    result = x / y
    return result
"""

    # Analyze code (uses Sonnet)
    print("\nAnalyzing code (uses Sonnet)...")
    analysis_result = await agent.analyze_code(test_code)
    print(f"   Model: {analysis_result['model']}")
    print(f"   Analysis: {analysis_result['analysis'][:150]}...")

    # Summarize (uses Haiku)
    print("\nSummarizing analysis (uses Haiku)...")
    summary = await agent.summarize_analysis(analysis_result["analysis"])
    print(f"   Summary: {summary}")


async def validate_config():
    """Validate configuration before running examples."""
    print("\n" + "=" * 60)
    print("CONFIGURATION VALIDATION")
    print("=" * 60)

    results = validate_environment()

    for key, value in results.items():
        status = "✓" if value else "✗"
        print(f"{status} {key.replace('_', ' ').title()}: {value}")

    if not all(results.values()):
        print("\n⚠️  WARNING: Some configuration is missing!")
        print("Please check your .env file and ensure all required variables are set.")
        print("See .env.example for reference.\n")
        return False

    print("\n✓ Configuration is valid!\n")
    return True


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("LLM ROUTER - USAGE EXAMPLES")
    print("Claude Sonnet 4 & Haiku 4.5 Intelligent Routing")
    print("=" * 60)

    # Validate configuration first
    if not await validate_config():
        print("Please fix configuration issues before running examples.")
        return

    # Run examples
    try:
        await example_basic_usage()
        await example_task_type_routing()
        await example_cost_comparison()
        await example_streaming()
        await example_agent_integration()

        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and API key.")


if __name__ == "__main__":
    asyncio.run(main())
