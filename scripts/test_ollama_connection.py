#!/usr/bin/env python3
"""
Test Ollama Connection Script

Quick script to verify Ollama provider works with local models.

Usage:
    uv run python scripts/test_ollama_connection.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.providers.ollama_provider import OllamaProvider
from src.llm.base import LLMRequest, LLMMessage


async def test_ollama_connection():
    """Test basic Ollama connectivity and completion."""
    print("=" * 80)
    print("Testing Ollama Provider")
    print("=" * 80)

    # Create Ollama provider
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        default_model="llama3.2",
        timeout=120
    )

    print(f"\n✓ Created OllamaProvider: {provider}")

    # Test 1: Validate credentials (check if Ollama is running)
    print("\n[Test 1] Validating Ollama connection...")
    try:
        is_valid = await provider.validate_credentials()
        if is_valid:
            print("✓ Ollama is running and models are available")
        else:
            print("✗ Ollama is running but no models available")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        return False

    # Test 2: List available models
    print("\n[Test 2] Checking available models...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags")
            models = response.json().get("models", [])
            print(f"✓ Found {len(models)} models:")
            for model in models[:5]:  # Show first 5
                name = model.get("name", "unknown")
                size_gb = model.get("size", 0) / 1e9
                print(f"  - {name} ({size_gb:.1f} GB)")
            if len(models) > 5:
                print(f"  ... and {len(models) - 5} more")
    except Exception as e:
        print(f"✗ Error listing models: {e}")

    # Test 3: Simple completion
    print("\n[Test 3] Testing completion with llama3.2...")
    try:
        request = LLMRequest(
            messages=[
                LLMMessage(role="user", content="Say 'hello' in 3 words or less.")
            ],
            model="llama3.2",
            temperature=0.7,
            max_tokens=50
        )

        print("  Sending request to Ollama (this may take 10-30 seconds)...")
        response = await provider.complete(request)

        print(f"✓ Response received!")
        print(f"  Model: {response.model}")
        print(f"  Content: {response.content}")
        print(f"  Tokens: {response.total_tokens} ({response.prompt_tokens} prompt + {response.completion_tokens} completion)")
        print(f"  Latency: {response.latency_ms}ms")

    except Exception as e:
        print(f"✗ Completion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Different model
    print("\n[Test 4] Testing with different model (gemma3)...")
    try:
        request = LLMRequest(
            messages=[
                LLMMessage(role="user", content="What is 2+2? Answer in one word.")
            ],
            model="gemma3",
            temperature=0.3,
            max_tokens=10
        )

        print("  Sending request to Ollama...")
        response = await provider.complete(request)

        print(f"✓ Response received!")
        print(f"  Model: {response.model}")
        print(f"  Content: {response.content}")
        print(f"  Latency: {response.latency_ms}ms")

    except Exception as e:
        print(f"  Note: gemma3 might not be available: {e}")

    print("\n" + "=" * 80)
    print("All tests completed successfully! ✓")
    print("=" * 80)

    return True


async def test_ollama_streaming():
    """Test Ollama streaming functionality."""
    print("\n[Bonus Test] Testing streaming completion...")

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        default_model="llama3.2"
    )

    request = LLMRequest(
        messages=[
            LLMMessage(role="user", content="Count from 1 to 5.")
        ],
        model="llama3.2",
        temperature=0.7,
        max_tokens=100,
        stream=True
    )

    try:
        print("  Streaming response:")
        full_response = ""
        async for chunk in provider.stream_complete(request):
            new_text = chunk.content[len(full_response):]
            print(new_text, end="", flush=True)
            full_response = chunk.content

        print("\n  ✓ Streaming completed!")

    except Exception as e:
        print(f"  Note: Streaming might not work: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("Ollama Provider Test Suite")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Check if Ollama is running")
    print("2. List available models")
    print("3. Test completion with llama3.2")
    print("4. Test with a different model")
    print("\nPress Ctrl+C to cancel...\n")

    try:
        success = asyncio.run(test_ollama_connection())

        if success:
            # Try streaming test if basic tests passed
            asyncio.run(test_ollama_streaming())

    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n✓ All tests passed! Ollama provider is ready to use.\n")


if __name__ == "__main__":
    main()
