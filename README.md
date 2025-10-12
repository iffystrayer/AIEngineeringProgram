# AI Engineering Program

**A comprehensive AI engineering learning and development program**

This repository contains projects, specifications, and resources for advanced AI engineering practices.

## 🎯 Current Project: U-AIP Scoping Assistant

**An intelligent, conversational AI agent system for rigorous AI project evaluation**

Built with Claude Agent SDK | Following U-AIP Protocol | TDD-Driven Development

---

## 📋 Project Overview

The U-AIP Scoping Assistant automates the Universal AI Project Scoping and Framing Protocol, transforming a multi-week manual evaluation process into a 30-45 minute guided conversation that produces comprehensive AI Project Charter documents.

**Key Features:**
- 🤖 **5 Specialized Stage Agents** - Business, Value, Data, User, Ethics
- 🔍 **3 Reflection Agents** - Quality assurance through self-evaluation
- 📊 **Automated Governance Decisions** - Proceed/Revise/Halt based on ethical risk
- 📄 **APA 7 Compliant Charters** - Professional 24-page documentation
- 🐳 **Fully Containerized** - Docker-based deployment
- ✅ **100% TDD Coverage** - Test-driven development throughout

---

## 📚 Documentation

### Essential Reading (Start Here)

1. **[SWE_SPECIFICATION.md](SWE_SPECIFICATION.md)** (1,430 lines)
   - Complete technical specification
   - System architecture and component details
   - Sections 1-8.1

2. **[SWE_SPEC_COMPLETION.md](SWE_SPEC_COMPLETION.md)** (Comprehensive)
   - Remaining specification sections 8.2-19
   - Testing strategy, deployment, security
   - Performance requirements and monitoring

3. **[PROJECT_WORKFLOW.md](PROJECT_WORKFLOW.md)** ⚠️ **MANDATORY**
   - Development standards and rules
   - TDD methodology
   - Checkpoint and code review processes
   - Quality gates and enforcement

4. **[CONVERSATION_FLOW_EXAMPLES.md](CONVERSATION_FLOW_EXAMPLES.md)**
   - Detailed user interaction examples
   - Shows exactly how CLI interface works
   - Quality reflection loop demonstrations

5. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
   - Essential commands and checklists
   - Daily developer workflow
   - Troubleshooting guide

6. **[TASK_LIST.md](TASK_LIST.md)** 🔄 **LIVING DOCUMENT**
   - Atomic task breakdown
   - Current progress tracking
   - Task assignments and dependencies

---

## 🏗️ Project Structure

```
uaip-scoping-assistant/
├── README.md                          # This file
├── SWE_SPECIFICATION.md               # Technical specification (main)
├── SWE_SPEC_COMPLETION.md             # Specification completion
├── PROJECT_WORKFLOW.md                # Development standards (MANDATORY)
├── CONVERSATION_FLOW_EXAMPLES.md      # User interaction examples
├── QUICK_REFERENCE.md                 # Command reference
├── TASK_LIST.md                       # Atomic task list (updated daily)
│
├── pyproject.toml                     # Python dependencies (to be created)
├── docker-compose.yml                 # Docker services (to be created)
├── Dockerfile                         # App container (to be created)
├── .env.example                       # Environment template (to be created)
├── .gitignore                         # Git ignore rules (to be created)
│
├── src/                               # Application source (to be created)
│   ├── __init__.py
│   ├── agents/                        # 8 agent implementations
│   │   ├── orchestrator.py
│   │   ├── stage1_agent.py
│   │   ├── stage2_agent.py
│   │   ├── stage3_agent.py
│   │   ├── stage4_agent.py
│   │   ├── stage5_agent.py
│   │   ├── response_quality_agent.py
│   │   ├── stage_gate_validator.py
│   │   └── consistency_checker.py
│   ├── database/                      # Database layer
│   │   ├── connection.py
│   │   └── repositories/
│   ├── tools/                         # Validation & calculation tools
│   │   ├── validators.py
│   │   ├── calculators.py
│   │   └── document_generator.py
│   ├── models/                        # Data models
│   │   └── schemas.py
│   ├── cli/                           # CLI interface
│   │   └── main.py
│   └── monitoring/                    # Prometheus metrics
│       └── metrics_server.py
│
├── tests/                             # Test suite (TDD) (to be created)
│   ├── conftest.py
│   ├── test_orchestrator.py
│   ├── agents/
│   │   ├── test_stage1_agent.py
│   │   ├── test_stage2_agent.py
│   │   ├── test_stage3_agent.py
│   │   ├── test_stage4_agent.py
│   │   ├── test_stage5_agent.py
│   │   ├── test_response_quality_agent.py
│   │   ├── test_stage_gate_validator.py
│   │   └── test_consistency_checker.py
│   ├── tools/
│   │   ├── test_validators.py
│   │   └── test_calculators.py
│   ├── integration/
│   │   ├── test_database_layer.py
│   │   └── test_complete_session_flow.py
│   └── fixtures/
│       ├── mock_responses.py
│       └── test_data.py
│
├── config/                            # Configuration files (to be created)
│   ├── questions/                     # YAML question templates
│   │   ├── stage1_questions.yaml
│   │   ├── stage2_questions.yaml
│   │   ├── stage3_questions.yaml
│   │   ├── stage4_questions.yaml
│   │   └── stage5_questions.yaml
│   └── validation/                    # Validation rules
│       ├── quality_thresholds.yaml
│       ├── stage_gate_requirements.yaml
│       └── consistency_rules.yaml
│
├── templates/                         # Document templates (to be created)
│   ├── charter_template.md
│   └── charter_styles.css
│
├── database/                          # Database schema (to be created)
│   └── init.sql
│
├── scripts/                           # Automation scripts (to be created)
│   ├── quality-gate-1.sh
│   ├── quality-gate-3.sh
│   ├── run-regression.sh
│   ├── security-scan.sh
│   └── create-checkpoint.sh
│
├── charters/                          # Generated charters (output dir)
│   └── .gitkeep
│
└── security/                          # Security reports (to be created)
    └── .gitkeep
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# macOS
brew install python@3.11
brew install --cask docker
pip install uv

# Install trivy (security scanning)
brew install aquasecurity/trivy/trivy
```

### Development Setup

```bash
# 1. Clone repository
cd /Users/ifiokmoses/code/AIEngineeringProgram/uaip-scoping-assistant

# 2. Initialize project (Task F1.1-F1.2)
uv init
uv venv
source .venv/bin/activate

# 3. Install dependencies (Task F1.2)
uv pip install -r pyproject.toml

# 4. Install development tools (Task F1.3-F1.4)
uv pip install pre-commit
pre-commit install

# 5. Set up environment (Task F1.7)
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# 6. Start PostgreSQL (Task DOC1.2)
docker compose up -d uaip-db

# 7. Run tests (should pass specification tests)
uv run pytest -v
```

---

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run only fast unit tests
uv run pytest tests/unit/ -v

# Run regression tests
uv run pytest -m regression -v

# Run quality gate 1 (before code review)
./scripts/quality-gate-1.sh
```

---

## 🐳 Docker Deployment

```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f uaip-app

# Access CLI inside container
docker compose exec uaip-app python -m src.cli.main start

# Stop services
docker compose down
```

---

## 📈 Development Progress

**Current Phase:** Phase 1 - Foundation (Weeks 1-2)

**Progress:** 0% (0/25 tasks completed)

See [TASK_LIST.md](TASK_LIST.md) for detailed task breakdown and assignments.

---

## 🔒 Security

- ✅ All secrets in environment variables (never committed)
- ✅ Dependency scanning with `pip-audit`
- ✅ Code security scanning with `bandit`
- ✅ Docker image scanning with `trivy`
- ✅ Pre-commit hooks prevent secret commits

---

## ⚙️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Framework | Claude Agent SDK | Latest |
| Database | PostgreSQL | 15+ |
| Container | Docker + Compose | 24+ |
| CLI | Rich + Click/Typer | Latest |
| Testing | pytest + pytest-cov | Latest |
| Linting | Ruff | Latest |
| Formatting | Black | Latest |
| Type Checking | MyPy | Latest |
| PDF Generation | WeasyPrint | Latest |

---

## 📊 Development Workflow

### The Five Pillars

```
1. ATOMIC TASKS    - Break work into smallest units
2. TEST FIRST      - Write tests before implementation (TDD)
3. CHECKPOINT OFTEN - Commit every 30-60 minutes
4. PEER REVIEW     - No code merges without review
5. CONTINUOUS TEST - Regression & vulnerability checks
```

### Daily Developer Loop

```
[SELECT TASK] → [WRITE TESTS] → [IMPLEMENT] → [CHECKPOINT] → [REVIEW] → [MERGE]
     ↑                                                                      │
     └──────────────────────────────────────────────────────────────────────┘
```

**See [PROJECT_WORKFLOW.md](PROJECT_WORKFLOW.md) for complete details.**

---

## 🎯 Quality Standards

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Test Coverage | ≥80% | Quality Gate 1 |
| TDD Compliance | 100% | Code Review |
| Checkpoint Frequency | Every 60 min | Daily review |
| Code Review Approval | ≥1 reviewer | Git branch protection |
| Security Vulnerabilities | 0 high/critical | Quality Gates |

---

## 📞 Getting Help

**Documentation Issues:**
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common commands
- Review [PROJECT_WORKFLOW.md](PROJECT_WORKFLOW.md) for process questions

**Technical Issues:**
- Check [TASK_LIST.md](TASK_LIST.md) for known blockers
- Review checkpoint log for patterns
- Escalate if blocked >4 hours

**Security Issues:**
- Critical vulnerabilities: Immediate escalation
- Report in security/ directory

---

## 🗓️ Development Timeline

```
Week 1-2:  Phase 1 - Foundation & Infrastructure
Week 3-4:  Phase 2 - Stage Interview Agents
Week 5:    Phase 3 - Reflection Agent System
Week 6:    Phase 4 - Document Generation
Week 7:    Phase 5 - Integration & Testing
Week 8:    Phase 6 - Deployment Preparation
───────────────────────────────────────────────
Total:     8 weeks to v1.0 production
```

**Current Week:** Week 1
**Next Milestone:** Phase 1 completion (Foundation + Database + CLI + Docker)

---

## 🤝 Contributing

**Before contributing:**
1. ✅ Read [PROJECT_WORKFLOW.md](PROJECT_WORKFLOW.md) (MANDATORY)
2. ✅ Review [SWE_SPECIFICATION.md](SWE_SPECIFICATION.md)
3. ✅ Check [TASK_LIST.md](TASK_LIST.md) for available tasks
4. ✅ Follow TDD methodology strictly
5. ✅ Checkpoint code every 30-60 minutes

**Contribution Workflow:**
```bash
# 1. Select atomic task from TASK_LIST.md
# 2. Create feature branch
git checkout -b feature/phase1-task-id

# 3. Write tests FIRST (TDD)
# 4. Implement minimal code to pass
# 5. Checkpoint frequently
git add .
git commit -m "[TASK_ID] Description..."

# 6. Run quality gate 1
./scripts/quality-gate-1.sh

# 7. Create pull request
# 8. Address review comments
# 9. Merge after approval
```

---

## 📝 License

*To be determined*

---

## 🙏 Acknowledgments

**Built using:**
- Claude Agent SDK by Anthropic
- Universal AI Project Scoping and Framing Protocol (U-AIP)
- Test-Driven Development methodology

---

## 📧 Contact

*Project lead contact information to be added*

---

**Project Status:** 🟡 In Development - Phase 1
**Last Updated:** 2025-10-12
**Version:** 1.0.0-dev
