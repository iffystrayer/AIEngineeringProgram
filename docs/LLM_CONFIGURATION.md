# LLM Configuration Guide

## Overview

This project uses an intelligent LLM routing system that automatically selects between Claude Sonnet and Claude Haiku based on task complexity, optimizing for both performance and cost.

## Model Tiers

The system supports three model tiers:

1. **FAST** - Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
   - Use for: Quick queries, summaries, simple translations
   - Cost: ~5x cheaper than Sonnet
   - Speed: ~2.5x faster than Sonnet

2. **BALANCED** - Claude Sonnet 4 (`claude-sonnet-4-20250514`)
   - Use for: General-purpose tasks, code generation, analysis
   - Cost: Standard pricing
   - Speed: Balanced performance

3. **POWERFUL** - Claude Sonnet 4 (configurable to Opus if needed)
   - Use for: Complex reasoning, multi-step planning, critical decisions
   - Cost: Higher (Opus: ~5x more than Sonnet)
   - Speed: Slower but most capable

## Configuration

### 1. Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Update the following variables in `.env`:

```bash
# Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Default model when tier not specified
ANTHROPIC_DEFAULT_MODEL=claude-sonnet-4-20250514

# Model assignments per tier
ANTHROPIC_MODEL_FAST=claude-haiku-4-5-20251001
ANTHROPIC_MODEL_BALANCED=claude-sonnet-4-20250514
ANTHROPIC_MODEL_POWERFUL=claude-sonnet-4-20250514

# Enable automatic cost optimization
LLM_COST_OPTIMIZATION=true
```

### 2. Router Configuration

The LLM Router is configured in your application code:

```python
from src.llm.router import LLMRouter
from src.llm.base import ModelTier
import os

# Configuration dictionary
llm_config = {
    "default_provider": "anthropic",
    "default_model": os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-sonnet-4-20250514"),
    "providers": {
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "models": {
                "fast": os.getenv("ANTHROPIC_MODEL_FAST", "claude-haiku-4-5-20251001"),
                "balanced": os.getenv("ANTHROPIC_MODEL_BALANCED", "claude-sonnet-4-20250514"),
                "powerful": os.getenv("ANTHROPIC_MODEL_POWERFUL", "claude-sonnet-4-20250514"),
            }
        }
    },
    "fallback_chain": ["anthropic"],
    "cost_optimization": os.getenv("LLM_COST_OPTIMIZATION", "true").lower() == "true",
}

# Initialize router
llm_router = LLMRouter(llm_config)
```

## Usage Examples

### Basic Usage (Automatic Tier Selection)

```python
# Fast tier - Uses Haiku for quick tasks
response = await llm_router.route(
    prompt="Summarize this text in one sentence: [text]",
    model_tier=ModelTier.FAST
)

# Balanced tier - Uses Sonnet for general tasks
response = await llm_router.route(
    prompt="Write a Python function to parse JSON files",
    model_tier=ModelTier.BALANCED
)

# Powerful tier - Uses Sonnet (or Opus) for complex tasks
response = await llm_router.route(
    prompt="Design a distributed system architecture for...",
    model_tier=ModelTier.POWERFUL
)
```

### Explicit Model Selection

```python
# Explicitly use Haiku 4.5
response = await llm_router.route(
    prompt="What is 2+2?",
    model_tier=ModelTier.FAST,
    model="claude-haiku-4-5-20251001"
)

# Explicitly use Sonnet 4
response = await llm_router.route(
    prompt="Implement a complex algorithm",
    model_tier=ModelTier.BALANCED,
    model="claude-sonnet-4-20250514"
)
```

### With Additional Parameters

```python
response = await llm_router.route(
    prompt="Generate creative story ideas",
    model_tier=ModelTier.BALANCED,
    temperature=0.9,  # Higher creativity
    max_tokens=1000,
    stop_sequences=["###", "END"]
)
```

### Agent Integration

```python
class Stage1Agent(BaseAgent):
    def __init__(self, llm_router: LLMRouter):
        self.llm_router = llm_router

    async def analyze_requirements(self, user_input: str) -> dict:
        # Use Sonnet for complex analysis
        response = await self.llm_router.route(
            prompt=f"Analyze these requirements: {user_input}",
            model_tier=ModelTier.BALANCED
        )

        return self._parse_response(response.content)

    async def generate_summary(self, analysis: dict) -> str:
        # Use Haiku for simple summarization
        response = await self.llm_router.route(
            prompt=f"Summarize in 2 sentences: {analysis}",
            model_tier=ModelTier.FAST
        )

        return response.content
```

## Cost Optimization

When `LLM_COST_OPTIMIZATION=true`, the router intelligently selects models based on:

1. **Task Complexity**: Analyzes prompt complexity and selects appropriate tier
2. **Token Count**: Uses Haiku for short prompts, Sonnet for longer contexts
3. **Response Requirements**: Considers max_tokens and response quality needs

### Manual Cost Optimization Strategy

```python
# Simple queries -> Haiku
if len(prompt) < 200 and not requires_reasoning:
    model_tier = ModelTier.FAST

# General tasks -> Sonnet
elif requires_code_generation or moderate_complexity:
    model_tier = ModelTier.BALANCED

# Complex reasoning -> Sonnet/Opus
else:
    model_tier = ModelTier.POWERFUL
```

## Model Capabilities Comparison

| Feature | Haiku 4.5 | Sonnet 4 |
|---------|-----------|----------|
| Speed | ⚡⚡⚡ Fast | ⚡⚡ Moderate |
| Cost | 💰 $0.0004/1K in | 💰💰💰 $0.003/1K in |
| Context | 200K tokens | 200K tokens |
| Vision | ✅ Yes | ✅ Yes |
| Function Calling | ✅ Yes | ✅ Yes |
| JSON Mode | ✅ Yes | ✅ Yes |
| Best For | Summaries, Q&A | Code, Analysis |

## Testing Configuration

Test your configuration:

```python
import asyncio
from src.llm.router import LLMRouter
from src.llm.base import ModelTier

async def test_llm_config():
    # Initialize router
    llm_router = LLMRouter(llm_config)

    # Validate credentials
    validation = await llm_router.validate_all_providers()
    print(f"Provider validation: {validation}")

    # Test Haiku
    haiku_response = await llm_router.route(
        prompt="Say hello in one word",
        model_tier=ModelTier.FAST
    )
    print(f"Haiku response: {haiku_response.content}")
    print(f"Model used: {haiku_response.model}")
    print(f"Tokens: {haiku_response.total_tokens}")

    # Test Sonnet
    sonnet_response = await llm_router.route(
        prompt="Explain quantum computing in detail",
        model_tier=ModelTier.BALANCED
    )
    print(f"Sonnet response: {sonnet_response.content[:100]}...")
    print(f"Model used: {sonnet_response.model}")
    print(f"Tokens: {sonnet_response.total_tokens}")

if __name__ == "__main__":
    asyncio.run(test_llm_config())
```

## Troubleshooting

### Model Not Found Error

If you see "model not found", ensure:
1. Model name in `.env` matches exactly: `claude-haiku-4-5-20251001`
2. API key has access to Claude 4 models
3. Model mappings in `anthropic_provider.py` are correct

### Cost Optimization Not Working

Check:
1. `LLM_COST_OPTIMIZATION=true` in `.env`
2. Model tier is specified in `route()` calls
3. Router config includes all model tier mappings

### High Costs

Monitor and optimize:
```python
# Log token usage
response = await llm_router.route(prompt, model_tier=ModelTier.FAST)
print(f"Cost: ~${(response.total_tokens / 1000) * 0.0006:.4f}")

# Use appropriate tiers
# ❌ BAD: Using Sonnet for simple tasks
await llm_router.route("What's 2+2?", model_tier=ModelTier.BALANCED)

# ✅ GOOD: Using Haiku for simple tasks
await llm_router.route("What's 2+2?", model_tier=ModelTier.FAST)
```

## Best Practices

1. **Default to FAST tier** for simple operations
2. **Use BALANCED tier** for code generation and analysis
3. **Reserve POWERFUL tier** for critical decisions only
4. **Monitor token usage** and costs regularly
5. **Test with different tiers** to find optimal balance
6. **Enable cost optimization** in production
7. **Set appropriate max_tokens** to prevent waste

## Additional Resources

- [Anthropic Model Documentation](https://docs.anthropic.com/claude/docs/models)
- [Claude Pricing](https://www.anthropic.com/pricing)
- [API Reference](https://docs.anthropic.com/claude/reference)
