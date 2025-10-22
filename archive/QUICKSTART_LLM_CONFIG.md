# Quick Start: LLM Configuration

This guide will help you configure Claude Code to intelligently switch between Claude Sonnet 4 and Claude Haiku 4.5 based on task complexity.

## Step 1: Create Your .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

## Step 2: Configure API Key and Models

Add/update these lines in your `.env` file:

```bash
# Your Anthropic API key (required)
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here

# Default model
ANTHROPIC_DEFAULT_MODEL=claude-sonnet-4-20250514

# Model tier configuration
ANTHROPIC_MODEL_FAST=claude-haiku-4-5-20251001      # Fast & cheap
ANTHROPIC_MODEL_BALANCED=claude-sonnet-4-20250514    # Default
ANTHROPIC_MODEL_POWERFUL=claude-sonnet-4-20250514    # Complex tasks

# Enable automatic cost optimization
LLM_COST_OPTIMIZATION=true
```

## Step 3: Test Your Configuration

Run the example script to verify everything works:

```bash
# Make sure you're in the project root
cd /Users/ifiokmoses/code/AIEngineeringProgram

# Install required dependencies if not already installed
uv pip install anthropic python-dotenv

# Run the test script
python examples/llm_usage_example.py
```

Expected output:
```
==============================================================
CONFIGURATION VALIDATION
==============================================================
✓ Anthropic Api Key: True
✓ Anthropic Model Configured: True
✓ Cost Optimization Enabled: True
✓ Has Env File: True

✓ Configuration is valid!
```

## Step 4: Use in Your Code

### Basic Usage

```python
from src.llm.config import load_llm_config
from src.llm.router import LLMRouter
from src.llm.base import ModelTier

# Initialize router (do this once at startup)
config = load_llm_config()
llm_router = LLMRouter(config)

# Use Haiku for fast tasks
response = await llm_router.route(
    prompt="Summarize this text: ...",
    model_tier=ModelTier.FAST
)

# Use Sonnet for complex tasks
response = await llm_router.route(
    prompt="Design a system architecture for ...",
    model_tier=ModelTier.BALANCED
)
```

### In Your Agents

Update your agent initialization to use the router:

```python
# In src/agents/orchestrator.py or similar
from src.llm.config import load_llm_config
from src.llm.router import LLMRouter

class Orchestrator:
    def __init__(self):
        # Initialize LLM router
        llm_config = load_llm_config()
        self.llm_router = LLMRouter(llm_config)

        # Pass to agents
        self.stage1_agent = Stage1Agent(llm_router=self.llm_router)
        self.stage2_agent = Stage2Agent(llm_router=self.llm_router)
        # ... etc
```

## Step 5: Optimize Your Costs

### When to Use Each Tier

**Use FAST (Haiku) for:**
- Simple Q&A
- Text summaries
- Data validation
- Classification tasks
- Keyword extraction
- Simple translations

**Use BALANCED (Sonnet) for:**
- Code generation
- Code analysis
- Business logic
- Requirement analysis
- Most agent tasks

**Use POWERFUL (Sonnet/Opus) for:**
- System architecture
- Strategic planning
- Complex reasoning
- Critical decisions

### Example Cost Savings

For a typical workflow:

```
❌ Before (all Sonnet):
- 10 summaries: 10,000 tokens × $0.003 = $0.030
- 5 analyses: 50,000 tokens × $0.003 = $0.150
Total: $0.180

✅ After (smart routing):
- 10 summaries (Haiku): 10,000 tokens × $0.0004 = $0.004
- 5 analyses (Sonnet): 50,000 tokens × $0.003 = $0.150
Total: $0.154

Savings: $0.026 (14% reduction)
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"

**Solution:** Make sure your `.env` file exists and contains your API key:
```bash
# Check if .env exists
ls -la .env

# Verify it contains the key
grep ANTHROPIC_API_KEY .env
```

### Error: "Model not found"

**Solution:** Ensure model names are exactly correct:
- ✅ `claude-haiku-4-5-20251001`
- ✅ `claude-sonnet-4-20250514`
- ❌ `claude-haiku-4` (short name, not full API name in env)

### Error: "anthropic package not installed"

**Solution:** Install the Anthropic SDK:
```bash
uv pip install anthropic
```

### Models Not Switching

**Solution:** Verify you're specifying `model_tier` parameter:
```python
# ❌ Wrong - no tier specified
response = await llm_router.route(prompt="...")

# ✅ Correct - tier specified
response = await llm_router.route(
    prompt="...",
    model_tier=ModelTier.FAST
)
```

## Additional Configuration Options

### Custom Timeout

```bash
# In .env
ANTHROPIC_TIMEOUT=60  # seconds
ANTHROPIC_MAX_RETRIES=3
```

### Disable Cost Optimization

```bash
# In .env
LLM_COST_OPTIMIZATION=false
```

This will still respect your `model_tier` choices but won't automatically optimize.

### Multiple Providers (Advanced)

```bash
# In .env - add OpenAI as fallback
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL_BALANCED=gpt-4
```

Then update your config:
```python
config = load_llm_config(enable_fallback=True)
# Will try Anthropic first, then OpenAI if it fails
```

## Next Steps

1. **Read the full documentation:** `docs/LLM_CONFIGURATION.md`
2. **Run the examples:** `python examples/llm_usage_example.py`
3. **Update your agents** to use the LLM Router
4. **Monitor costs** and adjust tier usage as needed

## Quick Reference

| Task Type | Tier | Model | Cost/1K in |
|-----------|------|-------|------------|
| Summary | FAST | Haiku 4.5 | $0.0004 |
| Analysis | BALANCED | Sonnet 4 | $0.003 |
| Planning | POWERFUL | Sonnet 4 | $0.003 |

## Support

If you encounter issues:
1. Check `.env` file is configured correctly
2. Verify API key has access to Claude 4 models
3. Review logs for detailed error messages
4. Check `docs/LLM_CONFIGURATION.md` for detailed troubleshooting

---

**Remember:** Start with FAST tier and move up only when needed. This keeps costs low while maintaining quality! 💰⚡
