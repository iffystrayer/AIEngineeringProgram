# Quick Reference Guide
## U-AIP Scoping Assistant - Development Standards

**Quick access to essential commands and checklists**

---

## 🚀 Daily Developer Workflow

```bash
# 1. Start your day
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/phase1-task-name

# 3. Write tests FIRST (TDD)
# Create test file: tests/test_component.py
# Write failing tests

# 4. Run tests (they should fail - RED)
uv run pytest tests/test_component.py -v

# 5. Implement code (make tests pass - GREEN)
# Write minimal implementation

# 6. Run tests (they should pass)
uv run pytest tests/test_component.py -v

# 7. Refactor and repeat

# 8. Checkpoint frequently (every 30-60 min)
./scripts/create-checkpoint.sh
# OR manually:
git add .
git commit -m "[TASK_ID] Brief description"

# 9. Before requesting review - run Quality Gate 1
./scripts/quality-gate-1.sh

# 10. Create pull request
git push origin feature/phase1-task-name
# Then create PR on GitHub

# 11. After approval - merge and cleanup
git checkout develop
git pull origin develop
git branch -d feature/phase1-task-name
```

---

## ✅ Essential Commands

### Testing
```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run only unit tests (fast)
uv run pytest tests/unit/ -v

# Run only regression tests
uv run pytest -m regression -v

# Run tests for specific file
uv run pytest tests/test_orchestrator.py -v

# Run tests with keyword match
uv run pytest -k "test_session" -v

# Stop on first failure
uv run pytest -x

# Show test durations
uv run pytest --durations=10
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Check formatting (without modifying)
uv run black --check src/

# Lint code
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check --fix src/

# Type checking
uv run mypy src/
```

### Security Scanning
```bash
# Scan dependencies
uv run pip-audit

# Scan code for security issues
uv run bandit -r src/

# Scan Docker image
trivy image uaip-assistant:latest
```

### Quality Gates
```bash
# Gate 1: Testing (before code review)
./scripts/quality-gate-1.sh

# Gate 3: Regression (before production)
./scripts/quality-gate-3.sh
```

### Docker
```bash
# Build and start services
docker compose up -d --build

# View logs
docker compose logs -f uaip-app

# Stop services
docker compose down

# Rebuild specific service
docker compose build uaip-app

# Execute command in container
docker compose exec uaip-app python -m pytest

# Clean everything (including volumes)
docker compose down -v
```

---

## 📋 Essential Checklists

### Before Starting Task
```
□ Task list updated (task moved to IN_PROGRESS)
□ Feature branch created from develop
□ Tests written FIRST (TDD)
□ Ready to code
```

### Before Committing
```
□ All tests passing (uv run pytest -v)
□ Code formatted (black)
□ Linting passed (ruff)
□ Task list updated
□ Commit message follows format
```

### Before Requesting Review
```
□ Quality Gate 1 passed (./scripts/quality-gate-1.sh)
□ All tests passing
□ Coverage ≥80%
□ Type checking passed (mypy)
□ Security scans passed
□ Task marked COMPLETED in task list
□ Checkpoint log updated
□ Pull request created with proper template
```

### Before Merging to Develop
```
□ At least 1 reviewer approval
□ All review comments addressed
□ All CI checks passing
□ No merge conflicts
```

### Before Merging to Main (Production)
```
□ Quality Gate 3 passed (./scripts/quality-gate-3.sh)
□ All regression tests passing
□ Docker builds successfully
□ Security scans passed
□ Performance benchmarks met
□ Phase completion checklist complete
```

---

## 🔍 Quick Troubleshooting

### Tests Failing
```bash
# Run single test with full output
uv run pytest tests/test_file.py::test_name -vvs

# Run with debugger
uv run pytest tests/test_file.py::test_name --pdb

# Clear pytest cache
rm -rf .pytest_cache
uv run pytest --cache-clear
```

### Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall dependencies
uv pip install -r pyproject.toml

# Check virtual environment
which python
```

### Docker Issues
```bash
# View container logs
docker compose logs uaip-app

# Restart services
docker compose restart

# Rebuild from scratch
docker compose down -v
docker compose up -d --build

# Check container health
docker compose ps
```

### Git Issues
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- <file>

# Update branch with latest develop
git checkout feature/my-branch
git rebase develop

# Resolve merge conflicts
# 1. Fix conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue
```

---

## 📊 Task Status Reference

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **PENDING** | Ready to start | Assign owner, start work |
| **IN_PROGRESS** | Being worked on | Complete task, run tests |
| **TESTING** | Tests running | Fix failures or move to REVIEW |
| **REVIEW** | Awaiting code review | Wait for reviewer feedback |
| **BLOCKED** | Cannot proceed | Identify blocker, escalate |
| **REVISIONS** | Changes requested | Address feedback, retest |
| **COMPLETED** | Merged to develop | Archive, start next task |

---

## 🎯 Quality Gate Pass Criteria

### Gate 1: Testing
- ✅ All tests pass (0 failures)
- ✅ Coverage ≥80%
- ✅ Type checking passes (mypy)
- ✅ Linting passes (ruff)
- ✅ Format check passes (black)
- ✅ No security vulnerabilities (pip-audit, bandit)

### Gate 2: Code Review
- ✅ 1+ reviewer approval
- ✅ All comments addressed
- ✅ TDD compliance verified
- ✅ Task list updated

### Gate 3: Regression
- ✅ All regression tests pass
- ✅ Integration tests pass
- ✅ E2E tests pass
- ✅ Docker builds successfully
- ✅ No critical Docker vulnerabilities

---

## 🔐 Security Severity Response Times

| Severity | Action | Timeline |
|----------|--------|----------|
| **CRITICAL** | Block merge, fix immediately | 4 hours |
| **HIGH** | Fix before merge | 24 hours |
| **MEDIUM** | Create ticket, fix next sprint | 1 week |
| **LOW** | Document, address opportunistically | Backlog |

---

## 📝 Commit Message Format

```
[TYPE][TASK_ID] Brief description (max 50 chars)

- Detailed changes
- One per line
- Be specific

Task: TASK_ID
Status: COMPLETED/IN_PROGRESS
Tests: X/Y passing
Coverage: Z%
```

**Types:** `[FEAT]` `[TEST]` `[FIX]` `[REFACTOR]` `[DOCS]` `[CHORE]` `[WIP]` `[CHECKPOINT]`

---

## 🔧 Pre-commit Hook Setup

```bash
# Install pre-commit
uv pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks (emergency only)
git commit --no-verify -m "message"
```

---

## 📈 Coverage Commands

```bash
# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# Open report in browser
open htmlcov/index.html

# Show missing lines
uv run pytest --cov=src --cov-report=term-missing

# Fail if coverage below threshold
uv run pytest --cov=src --cov-fail-under=80
```

---

## 🏷️ pytest Markers

```bash
# Run only regression tests
uv run pytest -m regression

# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run Tier 1 tests (fast)
uv run pytest -m tier1

# Run Tier 2 tests (full)
uv run pytest -m tier2

# Run Tier 3 tests (E2E, slow)
uv run pytest -m tier3
```

---

## 🆘 Help & Support

**Documentation:**
- Main Spec: [SWE_SPECIFICATION.md](cci:1:///Users/ifiokmoses/code/AIEngineeringProgram/uaip-scoping-assistant/SWE_SPECIFICATION.md:1:1-1430:68)
- Completion: [SWE_SPEC_COMPLETION.md](cci:1:///Users/ifiokmoses/code/AIEngineeringProgram/uaip-scoping-assistant/SWE_SPEC_COMPLETION.md:1:1-3:56)
- Workflow: [PROJECT_WORKFLOW.md](cci:1:///Users/ifiokmoses/code/AIEngineeringProgram/uaip-scoping-assistant/PROJECT_WORKFLOW.md:1:1-3:58)
- Conversations: [CONVERSATION_FLOW_EXAMPLES.md](cci:1:///Users/ifiokmoses/code/AIEngineeringProgram/uaip-scoping-assistant/CONVERSATION_FLOW_EXAMPLES.md:1:1-54:66)

**Common Issues:**
- See PROJECT_WORKFLOW.md Section 9.4 for troubleshooting
- Check task list for blockers
- Review checkpoint log for patterns

**Escalation:**
- If blocked >4 hours: Update task list, notify lead
- If regression fails: Follow incident protocol (PROJECT_WORKFLOW.md Section 6.7)
- If security critical found: Immediate escalation

---

**Last Updated:** 2025-10-12
**Version:** 1.0.0
