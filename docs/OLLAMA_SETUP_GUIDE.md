# Ollama Setup Guide for U-AIP

**Local LLM Development with Zero Cost** 🚀

This guide shows you how to use local Ollama models for cost-free development and testing of the U-AIP system.

---

## Why Ollama?

### Benefits

✅ **Zero Cost** - No API fees, unlimited usage
✅ **Complete Privacy** - Data never leaves your machine
✅ **Offline Capability** - Work without internet
✅ **Fast Iteration** - No rate limits, instant testing
✅ **Production Fallback** - Use as backup when commercial APIs unavailable

### Use Cases

| Environment | Primary Provider | Fallback | Purpose |
|------------|-----------------|----------|---------|
| **Development** | Ollama | - | Cost-free local testing |
| **Staging** | Ollama | Anthropic | Test with both local and commercial |
| **Production** | Anthropic | Ollama | Commercial primary, local fallback |

---

## Installation

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from:
# https://ollama.com/download
```

### 2. Verify Installation

```bash
ollama --version
# Should output: ollama version 0.x.x
```

### 3. Start Ollama Server

```bash
ollama serve
```

Ollama runs on **http://localhost:11434** by default.

---

## Available Models

### Your Current Models

Based on `ollama list`, you have:

| Model | Size | Best For | Context |
|-------|------|----------|---------|
| **llama3.2** | 2.0 GB | Fast general tasks, conversation | 8K |
| **gemma3** | 3.3 GB | Balanced capability, reasoning | 8K |
| **deepseek-r1** | 5.2 GB | Complex reasoning, analysis | 32K |
| **qwen3-coder** | Cloud | Code generation, technical tasks | 32K |
| **gpt-oss:20b** | 13 GB | Advanced reasoning (slower) | 8K |

### Recommended Models for U-AIP

```bash
# Already installed:
ollama pull llama3.2        # ✓ Fast tier
ollama pull gemma3          # ✓ Balanced tier
ollama pull deepseek-r1     # ✓ Powerful tier

# Optional high-performance models:
ollama pull qwen2:7b        # Alternative balanced model
ollama pull phi3:medium     # Very fast, efficient
ollama pull mistral:latest  # Good for structured output
```

---

## Configuration

### Development Configuration (Local Ollama Only)

Create `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
```

Use config file: `config/llm_config_ollama.yaml`

```yaml
llm:
  default_provider: ollama

  providers:
    ollama:
      base_url: http://localhost:11434
      default_model: llama3.2

      models:
        fast: llama3.2         # 2GB, fastest
        balanced: gemma3       # 3.3GB, good balance
        powerful: deepseek-r1  # 5.2GB, most capable
```

### Staging Configuration (Ollama + Commercial Fallback)

```yaml
llm:
  default_provider: ollama

  providers:
    ollama:
      base_url: http://localhost:11434
      default_model: llama3.2

    anthropic:
      api_key: ${ANTHROPIC_API_KEY}
      default_model: claude-3-haiku

  fallback_chain:
    - ollama      # Try local first
    - anthropic   # Fallback to commercial
```

### Production Configuration (Commercial + Ollama Fallback)

```yaml
llm:
  default_provider: anthropic

  providers:
    anthropic:
      api_key: ${ANTHROPIC_API_KEY}
      default_model: claude-3-sonnet

    ollama:
      base_url: http://localhost:11434
      default_model: deepseek-r1

  fallback_chain:
    - anthropic   # Primary
    - ollama      # Fallback when API unavailable
```

---

## Usage Examples

### Basic Usage

```python
from src.llm.providers.ollama_provider import OllamaProvider
from src.llm.base import LLMRequest, LLMMessage

# Create provider
provider = OllamaProvider(
    base_url="http://localhost:11434",
    default_model="llama3.2"
)

# Create request
request = LLMRequest(
    messages=[
        LLMMessage(role="user", content="What is the capital of France?")
    ],
    temperature=0.7,
    max_tokens=100
)

# Get completion
response = await provider.complete(request)
print(response.content)  # "The capital of France is Paris."
```

### With LLMRouter

```python
from src.llm.router import LLMRouter
import yaml

# Load configuration
with open("config/llm_config_ollama.yaml") as f:
    config = yaml.safe_load(f)

# Create router
router = LLMRouter(config["llm"])

# Route request (automatically uses Ollama)
response = await router.route(
    prompt="Explain test-driven development in 2 sentences.",
    model_tier=ModelTier.BALANCED
)

print(f"Provider: {response.provider}")  # "ollama"
print(f"Model: {response.model}")        # "gemma3"
print(f"Response: {response.content}")
```

### Streaming Responses

```python
# Enable streaming for real-time output
request = LLMRequest(
    messages=[LLMMessage(role="user", content="Count from 1 to 10.")],
    stream=True
)

async for chunk in provider.stream_complete(request):
    print(chunk.content, end="", flush=True)
```

---

## Testing

### Quick Connection Test

```bash
# Test Ollama provider
uv run python scripts/test_ollama_connection.py
```

Expected output:
```
✓ Ollama is running and models are available
✓ Found 10 models
✓ Response received!
  Model: llama3.2
  Content: Hello!
  Tokens: 41 (38 prompt + 3 completion)
  Latency: 12578ms
```

### Run Provider Tests

```bash
# Run Ollama provider unit tests
uv run pytest tests/llm/test_ollama_provider.py -v
```

### Integration Test with U-AIP

```bash
# Test full U-AIP workflow with Ollama
uv run pytest tests/integration/test_ollama_integration.py -v
```

---

## Docker Integration

### Access Ollama from Docker Containers

**Problem:** Docker containers can't access `localhost:11434` directly.

**Solution:** Use `host.docker.internal`

```yaml
# In docker-compose.yml or config
llm:
  providers:
    ollama:
      base_url: http://host.docker.internal:11434  # Not localhost!
```

**Alternative:** Run Ollama in Docker

```bash
# Run Ollama in Docker (if needed)
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama
```

Then pull models:
```bash
docker exec -it ollama ollama pull llama3.2
```

---

## Performance Tuning

### Model Selection by Use Case

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| **Quick testing** | llama3.2 (2GB) | Fast, efficient |
| **Development iteration** | gemma3 (3.3GB) | Good balance |
| **Complex reasoning** | deepseek-r1 (5.2GB) | Most capable |
| **Code generation** | qwen3-coder | Specialized |
| **Long context** | deepseek-r1 or qwen3-coder | 32K context |

### Latency Expectations

| Model | First Request | Subsequent | Tokens/sec |
|-------|--------------|------------|------------|
| llama3.2 | 10-15s | 5-8s | ~15 |
| gemma3 | 10-15s | 5-10s | ~12 |
| deepseek-r1 | 15-20s | 8-12s | ~10 |

**Note:** First request loads model into memory (slower), subsequent requests are faster.

### Optimization Tips

1. **Keep models in memory** - Don't restart Ollama frequently
2. **Use smaller models for testing** - llama3.2 for fast iteration
3. **Increase timeout** - Set `timeout=120` for large models
4. **Reduce max_tokens** - Lower `max_tokens` for faster responses

---

## Troubleshooting

### Ollama Not Running

**Error:** `Cannot connect to Ollama at http://localhost:11434`

**Fix:**
```bash
# Start Ollama server
ollama serve

# Or check if running
curl http://localhost:11434/api/tags
```

### Model Not Available

**Error:** `model 'llama3.2' not found`

**Fix:**
```bash
# Pull the model
ollama pull llama3.2

# List available models
ollama list
```

### Slow Responses

**Issue:** Completions taking >30 seconds

**Solutions:**
1. **Use smaller model**: Switch from deepseek-r1 → gemma3 → llama3.2
2. **Reduce max_tokens**: Lower from 4000 → 2000 → 1000
3. **Check system resources**: Ensure enough RAM available
4. **First request is slow**: Normal - model loads into memory

### Docker Container Can't Access Ollama

**Error:** `Connection refused` from Docker

**Fix:** Use `host.docker.internal` instead of `localhost`:
```yaml
base_url: http://host.docker.internal:11434
```

### Model Runs Out of Context

**Error:** `context length exceeded`

**Fix:** Use model with larger context:
```python
# Use deepseek-r1 (32K context) instead of llama3.2 (8K)
provider = OllamaProvider(default_model="deepseek-r1")
```

---

## Migration Path

### Phase 1: Development (Now)
- **Provider:** Ollama only
- **Cost:** $0/month
- **Purpose:** Fast local development

### Phase 2: Staging
- **Provider:** Ollama primary, Anthropic fallback
- **Cost:** ~$10-50/month (fallback only)
- **Purpose:** Test both local and commercial

### Phase 3: Production
- **Provider:** Anthropic primary, Ollama fallback
- **Cost:** $100-500/month
- **Purpose:** Production quality with local fallback

### Migration Script

```python
# Easy migration between providers
config = {
    "default_provider": "anthropic",  # Change to "ollama" for local
    "fallback_chain": ["anthropic", "ollama"]  # Automatic fallback
}

router = LLMRouter(config)
# Works the same regardless of provider!
```

---

## Cost Comparison

### Ollama (Local)
- **Setup:** Free
- **Per Request:** $0
- **Monthly:** $0
- **Annual:** $0
- **Hardware:** Uses your existing machine

### Anthropic Claude
- **Setup:** $0
- **Per 1M input tokens:** $3-15 (depending on model)
- **Monthly:** $100-500 (typical usage)
- **Annual:** $1,200-6,000

### ROI Calculation

```
Development Phase (3 months):
  Ollama: $0
  Anthropic: $300-1,500
  Savings: $300-1,500

Testing Phase (2 months):
  Ollama: $0
  Anthropic: $200-1,000
  Savings: $200-1,000

Total First-Year Savings: $500-2,500
```

---

## Best Practices

### 1. Use Ollama for Development ✅

```python
# Development: Fast iteration, zero cost
config["default_provider"] = "ollama"
```

### 2. Test with Commercial Before Production ✅

```python
# Staging: Ensure compatibility
config["fallback_chain"] = ["anthropic", "ollama"]
```

### 3. Keep Ollama as Production Fallback ✅

```python
# Production: Reliability + fallback
config["fallback_chain"] = ["anthropic", "ollama"]
```

### 4. Choose Right Model for Task ✅

```python
# Simple tasks → llama3.2 (fast)
# Complex reasoning → deepseek-r1 (capable)
# Code generation → qwen3-coder (specialized)
```

### 5. Monitor Performance ✅

```python
# Track latency and adjust
if response.latency_ms > 15000:
    # Switch to faster model
    model = "llama3.2"
```

---

## Summary

**✅ Ollama Integration Complete!**

- **Provider Implemented:** OllamaProvider with full BaseLLMProvider interface
- **Configuration:** `config/llm_config_ollama.yaml` ready to use
- **Testing:** All tests passing, live test successful
- **Documentation:** Complete setup and usage guide

**Your Models Ready:**
- llama3.2 (2GB) - Fast tier ⚡
- gemma3 (3.3GB) - Balanced tier ⚖️
- deepseek-r1 (5.2GB) - Powerful tier 🚀

**Next Steps:**
1. Use Ollama for all development
2. Add commercial API keys when ready for production
3. Keep Ollama as fallback for reliability

**Questions?** See [OLLAMA_FAQ.md](./OLLAMA_FAQ.md)

---

*Generated with local Ollama models - Zero cost! 🎉*
