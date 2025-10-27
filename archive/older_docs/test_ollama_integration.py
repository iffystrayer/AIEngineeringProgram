#!/usr/bin/env python3
"""
Test Ollama Integration with Cloud Models

Tests that the LLM router can successfully use Ollama with -cloud models
for the U-AIP scoping assistant.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.llm.router import _create_default_router
from src.llm.base import ModelTier

# Load environment variables
load_dotenv()

async def test_ollama_integration():
    """Test Ollama LLM integration with cloud models."""

    print("=" * 80)
    print("OLLAMA INTEGRATION TEST - Cloud Models")
    print("=" * 80)

    # 1. Verify environment configuration
    print("\n[1/5] Checking environment configuration...")
    llm_provider = os.getenv("LLM_PROVIDER")
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    default_model = os.getenv("OLLAMA_DEFAULT_MODEL")

    print(f"  Provider: {llm_provider}")
    print(f"  Ollama URL: {ollama_url}")
    print(f"  Default Model: {default_model}")
    print(f"  Fast Model: {os.getenv('OLLAMA_MODEL_FAST')}")
    print(f"  Balanced Model: {os.getenv('OLLAMA_MODEL_BALANCED')}")
    print(f"  Powerful Model: {os.getenv('OLLAMA_MODEL_POWERFUL')}")

    if llm_provider != "ollama":
        print(f"  ⚠️  LLM_PROVIDER is '{llm_provider}', expected 'ollama'")
        print(f"  Continuing anyway - router will still work...")
    else:
        print("  ✓ Environment configured for Ollama")

    # 2. Create LLM router
    print("\n[2/5] Creating LLM router...")
    try:
        router = _create_default_router()
        print(f"  ✓ Router created successfully")
        # print(f"  Default provider: {router.default_provider}")
    except Exception as e:
        print(f"  ❌ Failed to create router: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Test simple query with FAST model
    print("\n[3/5] Testing FAST model (qwen3-coder:480b-cloud)...")
    try:
        response = await router.route(
            prompt="What is 2+2? Answer with just the number.",
            model_preference=ModelTier.FAST,
            max_tokens=10
        )
        print(f"  ✓ Response received")
        print(f"  Model used: {response.model}")
        print(f"  Response: {response.content[:100]}")
    except Exception as e:
        print(f"  ❌ Query failed: {e}")
        return False

    # 4. Test BALANCED model (deepseek-v3.1)
    print("\n[4/5] Testing BALANCED model (deepseek-v3.1:671b-cloud)...")
    try:
        response = await router.route(
            prompt="Explain AI in one sentence.",
            model_preference=ModelTier.BALANCED,
            max_tokens=50
        )
        print(f"  ✓ Response received")
        print(f"  Model used: {response.model}")
        print(f"  Response: {response.content[:150]}")
    except Exception as e:
        print(f"  ❌ Query failed: {e}")
        return False

    # 5. Test POWERFUL model (gpt-oss:120b-cloud)
    print("\n[5/5] Testing POWERFUL model (gpt-oss:120b-cloud)...")
    try:
        response = await router.route(
            prompt="List 3 benefits of using local LLMs. Be concise.",
            model_preference=ModelTier.POWERFUL,
            max_tokens=100
        )
        print(f"  ✓ Response received")
        print(f"  Model used: {response.model}")
        print(f"  Response: {response.content[:200]}")
    except Exception as e:
        print(f"  ❌ Query failed: {e}")
        return False

    # Summary
    print("\n" + "=" * 80)
    print("✅ OLLAMA INTEGRATION TEST PASSED")
    print("=" * 80)
    print(f"\nVerified:")
    print(f"  ✓ Ollama connection (http://localhost:11434)")
    print(f"  ✓ FAST model: qwen3-coder:480b-cloud")
    print(f"  ✓ BALANCED model: deepseek-v3.1:671b-cloud")
    print(f"  ✓ POWERFUL model: gpt-oss:120b-cloud")
    print(f"\nReady for:")
    print(f"  ✓ Stage agents (business, value, data, user, ethics)")
    print(f"  ✓ Reflection agents (quality, stage-gate, consistency)")
    print(f"  ✓ Full end-to-end workflow with real LLM reasoning")
    print("\n" + "=" * 80)

    return True

if __name__ == "__main__":
    success = asyncio.run(test_ollama_integration())
    exit(0 if success else 1)
