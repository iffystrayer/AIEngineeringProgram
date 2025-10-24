# U-AIP Scoping Assistant

**An intelligent, conversational AI agent system for rigorous AI project evaluation**

[![Status](https://img.shields.io/badge/Status-Alpha_Prototype-orange)](./COMPREHENSIVE_AUDIT_REPORT_2025.md)
[![Tests](https://img.shields.io/badge/Tests-See_P1_Tasks-blue)](./P1_ATOMIC_TASK_LIST.md)
[![Security](https://img.shields.io/badge/Security-Alpha_No_Auth-orange)](./COMPREHENSIVE_AUDIT_REPORT_2025.md)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![Audit](https://img.shields.io/badge/Audit-Complete-green)](./COMPREHENSIVE_AUDIT_REPORT_2025.md)

🔧 **Alpha Prototype - Work in Progress** | Built with Claude | Following U-AIP Protocol | Foundation Fixes Underway

---

## ⚠️ CURRENT STATUS: Alpha Prototype

This project is in active development. The backend engine and frontend UI are functional, but integration testing and production features are in progress.

**What Works:**
- ✅ Backend REST API (13 endpoints implemented, 13,582 lines Python)
- ✅ CLI interface for session management
- ✅ Frontend UI components (React/TypeScript, 8,000 lines)
- ✅ Database schema and persistence (PostgreSQL, 7 tables)
- ✅ Multi-agent orchestration architecture

**What's In Progress (P1 High Priority Tasks):**
- 🔄 Test infrastructure verification → [P1.1](./P1_ATOMIC_TASK_LIST.md#p11-fix-test-infrastructure-2-3-hours)
- 🔄 Frontend-backend integration testing → [P1.5](./P1_ATOMIC_TASK_LIST.md#p15-verify-frontend-backend-integration-4-6-hours)
- 🔄 Documentation accuracy updates → [P1.2](./P1_ATOMIC_TASK_LIST.md#p12-reconcile-documentation-with-reality-2-3-hours)
- 🔄 Database migrations (Alembic) → [P1.3](./P1_ATOMIC_TASK_LIST.md#p13-add-database-migrations-3-4-hours)

**Not Yet Implemented:**
- ❌ Authentication/authorization system (P2.1)
- ❌ HTTPS/TLS configuration
- ❌ CI/CD pipeline (P2.2)
- ❌ Rate limiting (P3.3)
- ❌ Monitoring/observability (P3.1)

**For Detailed Assessment:**
- 📊 [Comprehensive Audit Report](./COMPREHENSIVE_AUDIT_REPORT_2025.md) - Brutal truth about current state
- 📋 [P1 Atomic Task List](./P1_ATOMIC_TASK_LIST.md) - Foundation fixes (Week 1)
- 📄 [Test Results](./TEST_RESULTS.md) - 795 tests verified (75.3% pass rate)
- 🔗 [Integration Results](./INTEGRATION_TEST_RESULTS.md) - Live backend-database testing
- 📈 [P1 Progress](./P1_PROGRESS_SUMMARY.md) - Foundation phase progress

---

## ⚠️ Known Issues

### Critical (Blocks Production)

**1. No Authentication System**
- Impact: API completely open, anyone can access/modify data
- Status: P2.1 (planned)
- Workaround: Use only in trusted networks

**2. Session Retrieval Bug**
- Impact: Sessions created via API cannot be retrieved (returns 404)
- Status: Under investigation
- Tracked in: [INTEGRATION_TEST_RESULTS.md](./INTEGRATION_TEST_RESULTS.md#issue-2-session-retrieval-returns-404--open)

**3. Session List Returns Empty**
- Impact: Cannot list sessions via API despite DB records
- Status: Under investigation
- Tracked in: [INTEGRATION_TEST_RESULTS.md](./INTEGRATION_TEST_RESULTS.md#issue-3-list-sessions-returns-empty--open)

### High Priority

**4. No Database Migrations**
- Impact: Schema changes require manual SQL and downtime
- Status: P1.3 (in queue)
- Risk: Data loss on schema evolution

**5. Integration Test Failures**
- Impact: 58 integration tests fail (stdin interaction)
- Status: Documented in [TEST_RESULTS.md](./TEST_RESULTS.md)
- Fix: Mock stdin or refactor tests

### Medium Priority

**6. No HTTPS/TLS**
- Impact: Credentials transmitted in plaintext
- Status: P2+ (planned)

**7. No Rate Limiting**
- Impact: API vulnerable to abuse, LLM cost risk
- Status: P3.3 (planned)

**8. Schema Mismatches in Tests**
- Impact: 8 test failures due to outdated fixtures
- Status: Documented, fixable

### See Also
- [Full Issue List](./INTEGRATION_TEST_RESULTS.md#issues-found)
- [Test Failures](./TEST_RESULTS.md#failing-test-categories)

---

## 📋 Project Overview

The U-AIP Scoping Assistant **aims to** automate the Universal AI Project Scoping and Framing Protocol, transforming a multi-week manual evaluation process into a guided conversation that produces comprehensive AI Project Charter documents.

### 🎯 What It Does (When Complete)

**Input:** Business idea ("Reduce customer churn for our SaaS product")

**Output:** Complete AI Project Charter with:
- Precise problem definition & ML archetype
- Measurable business KPIs aligned to technical metrics
- Data quality assessment (6 dimensions)
- User-centric design & interaction patterns
- Ethical risk analysis & governance decision

**Key Innovation:** Intelligent quality validation catches vague responses and generates contextual follow-ups automatically.

---

## 🚀 Quick Start (Alpha Prototype)

### Prerequisites

- Python 3.11+
- Docker + Docker Compose
- Node.js 18+ (for frontend)
- Anthropic API key OR Ollama (for local LLM)

### Backend Setup

```bash
# 1. Clone and navigate to project
cd /path/to/AIEngineeringProgram

# 2. Install dependencies
uv pip install -e ".[dev]"

# 3. Create .env from template
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# 4. Start database
docker-compose up -d uaip-db

# 5. Run migrations (once P1.3 complete)
# alembic upgrade head

# 6. Start API server
uv run uvicorn src.api.main:app --reload --port 38937
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Create frontend .env
echo "VITE_API_URL=http://localhost:38937/api/v1" > .env

# 4. Start dev server
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:38937/api/v1/docs (Swagger UI)
- Database: localhost:15432

### CLI Usage

```bash
# Start interactive session
uv run python -m src.cli.main start "your project name"

# List sessions
uv run python -m src.cli.main list

# Resume session
uv run python -m src.cli.main resume <session-id>
```

**⚠️ Note:** Integration between frontend and backend is being verified as part of P1 tasks.

---

## ✨ Key Features

### 🤖 Multi-Stage Workflow
- **Stage 1:** Business Translation - Problem definition
- **Stage 2:** Value Quantification - KPI alignment
- **Stage 3:** Data Feasibility - Quality assessment
- **Stage 4:** User Centricity - UX design
- **Stage 5:** Ethical Governance - Risk analysis

### 🔍 ConversationEngine (Implemented)
- **Quality Validation:** Automatic vague response detection (0-10 scoring)
- **Follow-up Generation:** Context-aware clarification questions
- **Max 3 Attempts:** Prevents infinite loops
- **History Tracking:** Complete audit trail

### 📊 Automated Governance
- **Risk Assessment:** Evidence-based scoring
- **Mitigation Planning:** Cost-benefit analysis
- **Residual Risk Calculation:** Quantitative assessment
- **Decision Logic:** Proceed/Revise/Submit/Halt

### 🛡️ Security Status

**What's Secure:**
- ✅ Secrets in environment variables
- ✅ Parameterized queries (SQL injection prevention)
- ✅ PII sanitization in logs
- ✅ Pre-commit security hooks (Bandit, detect-secrets)

**Critical Gaps (Alpha):**
- ❌ **NO AUTHENTICATION** - API is completely open
- ❌ **NO HTTPS** - HTTP only
- ❌ **NO RATE LIMITING** - Abuse vulnerable
- ❌ **NO AUTHORIZATION** - No access control

**Security Grade:** D+ (Not production ready)

See [Security Audit](./COMPREHENSIVE_AUDIT_REPORT_2025.md#-security-audit) for details.

---

## 🧪 Testing

### Test Infrastructure: Verified ✅

**Backend Tests:** [Full Results →](./TEST_RESULTS.md)
- **Total:** 795 tests
- **Passed:** 599 (75.3%)
- **Failed:** 72 (9.1%)
- **Skipped:** 124 (15.6%)
- **Grade:** C+ (Core logic solid, fixable issues)

**What Works:**
- ✅ All stage agent unit tests pass
- ✅ All reflection agent tests pass
- ✅ Database repository tests pass
- ✅ API endpoint tests pass
- ✅ Core business logic verified

**Known Issues:**
- Integration tests requiring stdin (58 failures)
- Schema mismatches in fixtures (8 failures)
- Missing markdown2 dependency (1 failure)
- See [TEST_RESULTS.md](./TEST_RESULTS.md) for details

**Frontend Tests:** Pending npm install
- Test files exist (component, E2E, Playwright)
- Run after: `cd frontend && npm install`

**Run Tests:**
```bash
# Backend (all)
uv run pytest tests/ -v

# Backend (skip integration)
uv run pytest tests/ --ignore=tests/integration/ -v

# Frontend
cd frontend && npm test
```

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- Python 3.11+ with asyncio
- FastAPI (REST API)
- PostgreSQL 16 (asyncpg)
- Pydantic 2.5+ (validation)
- Anthropic Claude / Ollama

**Frontend:**
- React 19.1.1
- TypeScript 5.9.3
- Vite 7.1.7
- TanStack Query (state management)
- Tailwind CSS 4.1.14

**Infrastructure:**
- Docker + Docker Compose
- Pre-commit hooks (Black, Ruff, MyPy, Bandit)

### System Components

```
┌──────────────────────────────────────┐
│    Frontend (React/TypeScript)       │
│    localhost:5173                    │
└────────────┬─────────────────────────┘
             │ HTTP (API calls)
             ▼
┌──────────────────────────────────────┐
│    REST API (FastAPI)                │
│    localhost:38937/api/v1            │
│    - 13 endpoints                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│    Orchestrator                      │
│    - Session management              │
│    - Stage routing                   │
└────┬─────────────────────────────────┘
     │
     ├─► Stage Agents (5)
     │   - Business Translation
     │   - Value Quantification
     │   - Data Feasibility
     │   - User Centricity
     │   - Ethical Governance
     │
     ├─► Reflection Agents (3)
     │   - Quality Assessment
     │   - Stage-Gate Validation
     │   - Consistency Checker
     │
     └─► LLM Router
         - Anthropic Claude
         - Ollama (local)
```

---

## 📊 Development Progress

### Current Status: 🔧 Foundation Fixes (Week 1)

**Completed:**
- ✅ Backend architecture (13,582 lines Python)
- ✅ Frontend components (8,000 lines TypeScript)
- ✅ Database schema (7 tables, proper indexing)
- ✅ REST API (13 endpoints)
- ✅ Comprehensive audit ([Full Report](./COMPREHENSIVE_AUDIT_REPORT_2025.md))

**P1 Completed (High Priority):**
- ✅ Fix test infrastructure ([P1.1](./P1_ATOMIC_TASK_LIST.md#p11-fix-test-infrastructure-2-3-hours)) - 795 tests verified
- ✅ Backend-DB integration ([P1.5](./P1_ATOMIC_TASK_LIST.md#p15-verify-frontend-backend-integration-4-6-hours)) - Live testing complete

**P1 In Progress:**
- 🔄 Reconcile documentation ([P1.2](./P1_ATOMIC_TASK_LIST.md#p12-reconcile-documentation-with-reality-2-3-hours)) - In progress
- ⏭️ Add database migrations ([P1.3](./P1_ATOMIC_TASK_LIST.md#p13-add-database-migrations-3-4-hours))
- ⏭️ Review Docker builds ([P1.4](./P1_ATOMIC_TASK_LIST.md#p14-fix-dockerfile-to-use-lockfile-30-minutes))

**Next (P2 - Medium Priority):**
- ❌ Authentication system (2-3 days)
- ❌ CI/CD pipeline (1-2 days)
- ❌ Harden LLM integration (1-2 days)
- ❌ Refactor Orchestrator (2-3 days)

**Timeline:**
- Week 1: P1 (foundation fixes)
- Weeks 2-3: P2 (security, automation)
- Week 4+: P3 (polish, observability)
- **Production-ready:** 4-6 weeks

---

## 🐳 Docker Deployment

### Start Services

```bash
# Build and start database
docker-compose up -d uaip-db

# Build application container
docker build -t uaip-app .

# Start full stack
docker-compose up -d
```

**Services:**
- `uaip-db`: PostgreSQL 16 (port 15432)
- `uaip-app`: Application container

**⚠️ Note:** Frontend not yet containerized. See P2 tasks.

---

## 🤝 Contributing

### Before Contributing

1. Read [Comprehensive Audit Report](./COMPREHENSIVE_AUDIT_REPORT_2025.md)
2. Review [P1 Atomic Task List](./P1_ATOMIC_TASK_LIST.md)
3. Check GitHub issues for "good first issue" label

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/task-description

# 2. Install pre-commit hooks
pre-commit install

# 3. Make changes (tests first if TDD)

# 4. Run tests
uv run pytest tests/ -v

# 5. Commit (hooks will run automatically)
git commit -m "feat: description"

# 6. Push and create PR
git push origin feature/task-description
```

### Priority Tasks (Help Wanted)

See [P1 Atomic Task List](./P1_ATOMIC_TASK_LIST.md) for specific tasks needing help.

**High Priority:**
- P1.1: Fix test infrastructure
- P1.3: Add database migrations (Alembic)
- P1.5: Verify frontend-backend integration

---

## 📈 Quality Metrics

|| Metric | Status | Details |
||--------|--------|--------|
|| Test Coverage | ✅ Verified | 795 tests, 75.3% pass rate ([Results](./TEST_RESULTS.md)) |
|| Code Quality | ✅ Excellent | Black, Ruff, MyPy configured |
|| Architecture | ✅ Well-designed | Multi-agent, modular |
|| Security | ❌ Alpha | No auth, no HTTPS, no rate limiting |
|| Documentation | 🔄 In Progress | Being updated (P1.2) |
|| Database | ✅ Verified | Live connections tested ([Integration](./INTEGRATION_TEST_RESULTS.md)) |
|| Deployment | ❌ Manual | No CI/CD |

**Current Grade:** C+ (Solid foundation, production gaps documented)

**Honest Assessment:**
- Tests work and are documented
- Backend-database integration verified with live connections
- Core agent logic is solid
- Critical bugs found and documented
- Security is alpha-stage only

See [Comprehensive Audit](./COMPREHENSIVE_AUDIT_REPORT_2025.md) and [P1 Progress](./P1_PROGRESS_SUMMARY.md)

---

## 🗓️ Roadmap

### Week 1 (P1 - High Priority)
- Fix test infrastructure
- Honest documentation
- Database migrations
- Verify integration

### Weeks 2-3 (P2 - Medium Priority)
- Authentication system
- CI/CD pipeline
- Harden LLM integration
- Refactor architecture

### Week 4+ (P3 - Low Priority)
- Monitoring/observability
- Rate limiting
- Documentation polish
- Accessibility

### Future (Beyond MVP)
- Real-time collaboration
- Portfolio intelligence
- Integration ecosystem (Jira, Slack, etc.)
- Compliance modules (GDPR, HIPAA)

---

## 📞 Getting Help

### Documentation
- **Current Status:** [This README](#️-current-status-alpha-prototype)
- **Detailed Audit:** [COMPREHENSIVE_AUDIT_REPORT_2025.md](./COMPREHENSIVE_AUDIT_REPORT_2025.md)
- **Task List:** [P1_ATOMIC_TASK_LIST.md](./P1_ATOMIC_TASK_LIST.md)
- **Architecture:** [System Components](#system-components)

### Issues
- **Bug Reports:** Create GitHub issue with reproduction steps
- **Feature Requests:** Create issue with use case description
- **Security Issues:** Report privately (see SECURITY.md)

---

## 🏆 What Makes This Project Special

### The ConversationEngine
- Intelligent quality validation (0-10 scoring)
- Contextual follow-up question generation
- Prevents vague responses automatically
- Complete conversation audit trail

### Multi-Agent Architecture
- 5 specialized stage agents
- 3 reflection agents for quality control
- Stage-gate validation prevents skipping
- Cross-stage consistency checking

### Structured Data Model
- Pydantic schemas for type safety
- JSONB for flexible storage
- Runtime validation throughout

---

## 📝 License

*To be determined*

---

## 🙏 Acknowledgments

**Built with:**
- Claude Agent SDK by Anthropic
- Universal AI Project Scoping and Framing Protocol (U-AIP)
- Python async/await architecture
- PostgreSQL for persistence

**Special Thanks:**
- Anthropic team for Claude Sonnet 4 & Haiku 4.5
- Ollama project for local LLM support
- Open-source Python community

---

## 📧 Contact

**Project Status:** 🔧 Alpha Prototype - Foundation Fixes Underway
**Last Updated:** October 24, 2025
**Version:** 0.1.0-alpha
**Next Milestone:** P1 Completion (Foundation Fixes)

**Ready to contribute?** See [P1 Atomic Task List](./P1_ATOMIC_TASK_LIST.md) for specific tasks!

---

**This is a work in progress. Contributions welcome!** 🚀
