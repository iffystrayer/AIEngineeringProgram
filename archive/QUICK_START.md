# U-AIP Scoping Assistant - Quick Start Guide

## Prerequisites

### 1. System Requirements
- Python 3.11 or higher
- Docker Desktop (for PostgreSQL database)
- macOS, Linux, or Windows with WSL2

### 2. LLM Provider (Choose One)
**Option A: Anthropic Claude (Recommended)**
- Create account at https://console.anthropic.com
- Generate API key
- Set environment variable:
  ```bash
  export ANTHROPIC_API_KEY="your-api-key-here"
  ```

**Option B: Ollama (Local, Cost-Free)**
- Install: https://ollama.ai/download
- Start server:
  ```bash
  ollama serve
  ```
- Pull model:
  ```bash
  ollama pull llama3
  ```

## Installation

### Step 1: Install the CLI Tool

```bash
# Navigate to project directory
cd /Users/ifiokmoses/code/AIEngineeringProgram

# Install the package in development mode with uv
uv pip install -e .

# OR install with standard pip
pip install -e .
```

This creates the `uaip` command globally available in your terminal.

### Step 2: Verify Installation

```bash
# Check if command is available
uaip --help

# Expected output:
# Usage: uaip [OPTIONS] COMMAND [ARGS]...
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   start   Start a new AI project scoping session
#   export  Export session charter to PDF/Markdown
#   list    List all scoping sessions
#   resume  Resume an existing session
```

### Step 3: Start Database

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Verify database is running
docker ps --filter "name=postgres"

# Expected: Container status "Up" and "healthy"
```

### Step 4: Set Environment Variables

Create or update `.env` file in project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:60432/uaip_dev

# LLM Provider (choose one)
ANTHROPIC_API_KEY=your-api-key-here
# OR
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Observability
LANGFUSE_PUBLIC_KEY=your-key
LANGFUSE_SECRET_KEY=your-secret
LANGFUSE_HOST=http://localhost:60300
```

## Usage

### Starting Your First Session

```bash
# Start an interactive scoping session
uaip start "customer churn prediction for SaaS company"
```

### What Happens Next

The system will guide you through **5 stages** with interactive questions:

#### Stage 1: Business Translation (4 question groups)
```
┌────────────────────────────────────────────────────────┐
│ What business problem are you trying to solve?        │
└────────────────────────────────────────────────────────┘

Your response> _
```

- Define business objective
- Assess AI suitability
- Determine ML archetype
- Set scope boundaries

#### Stage 2: Value Quantification (4 question groups)
- Define SMART KPIs
- Select technical metrics
- Map causal connections
- Validate actionability window

#### Stage 3: Data Feasibility (4 question groups)
- Inventory data sources
- Assess 6 quality dimensions
- Plan labeling strategy
- Evaluate FAIR compliance

#### Stage 4: User Centricity (4 question groups)
- Define user personas
- Map AI user journey
- Specify interpretability needs
- Design feedback mechanisms

#### Stage 5: Ethical Governance (5 question groups)
- Assess risks across 5 principles
- Plan mitigation strategies
- Calculate residual risk
- Determine governance decision

### Quality Validation

Every response is scored 0-10:

```
Your response> We want to improve things

⚠️ Quality validation feedback:
Score: 4/10
Issues identified:
  • Response is too vague - please be more specific

┌────────────────────────────────────────────────────────┐
│ Can you specify what metric you want to improve?      │
└────────────────────────────────────────────────────────┘

Improved response> Reduce customer churn from 15% to 10% over 6 months

✓ Response accepted (quality: 8/10)
```

### Completion

After all stages, you'll see:

```
🎉 Project Scoping Complete!

Governance Decision: PROCEED_WITH_MONITORING
Overall Feasibility: HIGH

Charter saved to database
View charter: uaip export <session_id>
```

## Common Issues & Solutions

### Issue: `command not found: uaip`

**Solution 1: Install the package**
```bash
uv pip install -e .
# OR
pip install -e .
```

**Solution 2: Use direct Python execution**
```bash
uv run python -m src.cli.main start "your project idea"
```

**Solution 3: Create alias (temporary fix)**
```bash
# Add to ~/.zshrc or ~/.bashrc
alias uaip='uv run python -m src.cli.main'

# Reload shell
source ~/.zshrc
```

### Issue: Database connection error

**Check database is running:**
```bash
docker ps --filter "name=postgres"
```

**Restart database:**
```bash
docker-compose restart postgres
```

**Check DATABASE_URL in .env:**
```bash
cat .env | grep DATABASE_URL
```

### Issue: API key not found

**Set environment variable:**
```bash
export ANTHROPIC_API_KEY="your-key"
```

**Or add to .env file:**
```bash
echo 'ANTHROPIC_API_KEY=your-key' >> .env
```

### Issue: Ollama connection error

**Start Ollama:**
```bash
ollama serve
```

**Check if running:**
```bash
curl http://localhost:11434/api/tags
```

**Pull model if needed:**
```bash
ollama pull llama3
```

## Advanced Usage

### Resume Session
```bash
uaip resume <session-id>
```

### List All Sessions
```bash
uaip list
```

### Export Charter
```bash
# PDF format
uaip export <session-id> --format pdf

# Markdown format
uaip export <session-id> --format markdown
```

### Specify Starting Stage
```bash
# Start from Stage 3 (if Stages 1-2 already complete)
uaip start "project name" --start-stage 3
```

### Use Specific LLM Provider
```bash
# Force Anthropic
uaip start "project" --provider anthropic

# Force Ollama
uaip start "project" --provider ollama
```

## Development Mode

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/integration/test_complete_multi_stage_conversation.py

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Verification
```bash
# Verify alpha is working
uv run python test_alpha_interactive.py

# Expected: All 3 tests pass
```

### Database Migrations
```bash
# Initialize database schema
uv run python -m src.database.init_db

# Reset database (WARNING: deletes all data)
docker-compose down -v postgres
docker-compose up -d postgres
uv run python -m src.database.init_db
```

## Tips for Best Experience

### 1. Be Specific
❌ "We want to improve customer retention"
✅ "Reduce customer churn from 15% to 10% over 6 months by predicting at-risk customers 30 days in advance"

### 2. Provide Metrics
❌ "We have good data quality"
✅ "Data accuracy >98%, completeness 95%, updated daily from CRM system"

### 3. Think Through Details
- The more specific you are, the better the final charter
- Quality validation helps guide you to better responses
- Use real numbers, timelines, and specific methods

### 4. Have Context Ready
Before starting, gather:
- Business KPIs and current baselines
- Data source information
- Stakeholder details
- Regulatory requirements
- Budget and timeline constraints

## Getting Help

### Documentation
- `ALPHA_INTERACTIVE_COMPLETE.md` - Implementation details
- `ALPHA_READINESS_VERIFICATION.md` - Verification report
- `E2E_DEMO_SCENARIO.md` - Full walkthrough example
- `README.md` - Project overview

### Support
- GitHub Issues: https://github.com/your-org/uaip-scoping/issues
- Documentation: https://docs.your-org.com/uaip

## Time Expectations

| Activity | Traditional | U-AIP Alpha | Savings |
|----------|------------|-------------|---------|
| Initial scoping | 2-3 weeks | 55 minutes | 96% |
| Requirements gathering | 1-2 weeks | Included | 100% |
| Stakeholder alignment | 3-5 days | Included | 100% |
| Ethics review | 1-2 weeks | Included | 100% |
| **Total** | **4-8 weeks** | **~1 hour** | **96%** |

## What You Get

At the end of a session:

1. **ProblemStatement** - ML archetype, features, scope
2. **MetricAlignmentMatrix** - KPIs, metrics, causal links
3. **DataQualityScorecard** - 6-dimension quality assessment
4. **UserContext** - Personas, journey map, HCI specs
5. **EthicalRiskReport** - 5-principle risk assessment
6. **AI Project Charter** - Complete requirements document

**Final Output:**
- Governance decision (Proceed/Revise/Halt/Committee)
- Overall feasibility (High/Medium/Low)
- ROI estimate
- Timeline and milestones
- Risk mitigation plan

---

## Quick Reference Card

```bash
# Installation
uv pip install -e .

# Start database
docker-compose up -d postgres

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Start session
uaip start "your AI project idea"

# Answer questions interactively
# Quality threshold: 7/10
# Max attempts per question: 3

# Get final charter
uaip export <session-id>
```

**Need Help?** Run `uaip --help` or check documentation.

🎉 **You're ready to scope your AI project in under an hour!**
