#!/usr/bin/env bash
#
# Quality Gate 1 - Pre-Code Review Validation
# Run this before requesting code review
#
# U-AIP Scoping Assistant - Development Workflow Enforcement
# Ensures code meets minimum quality standards before review

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=============================================="
echo "  Quality Gate 1 - Pre-Code Review"
echo "=============================================="
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Error: Virtual environment not found"
    echo "   Run: uv venv && uv pip install -e '.[dev]'"
    exit 1
fi

FAILED=0

# Step 1: Code Formatting
echo "Step 1/7: Running Black formatter..."
if black src/ tests/ --check; then
    echo "✅ Black formatting passed"
else
    echo "❌ Black formatting failed"
    echo "   Fix with: black src/ tests/"
    FAILED=1
fi
echo ""

# Step 2: Import Sorting
echo "Step 2/7: Checking import sorting..."
if python -m isort src/ tests/ --check-only; then
    echo "✅ Import sorting passed"
else
    echo "❌ Import sorting failed"
    echo "   Fix with: isort src/ tests/"
    FAILED=1
fi
echo ""

# Step 3: Linting
echo "Step 3/7: Running Ruff linter..."
if ruff check src/ tests/; then
    echo "✅ Ruff linting passed"
else
    echo "❌ Ruff linting failed"
    echo "   Fix with: ruff check src/ tests/ --fix"
    FAILED=1
fi
echo ""

# Step 4: Type Checking
echo "Step 4/7: Running MyPy type checker..."
if mypy src/ --config-file pyproject.toml; then
    echo "✅ MyPy type checking passed"
else
    echo "❌ MyPy type checking failed"
    echo "   Review type errors and fix"
    FAILED=1
fi
echo ""

# Step 5: Security Scanning
echo "Step 5/7: Running Bandit security scanner..."
if bandit -r src/ -c pyproject.toml --quiet; then
    echo "✅ Bandit security scan passed"
else
    echo "❌ Bandit security scan failed"
    echo "   Review security warnings"
    FAILED=1
fi
echo ""

# Step 6: Test Suite
echo "Step 6/7: Running test suite..."
if pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=80; then
    echo "✅ All tests passed with ≥80% coverage"
else
    echo "❌ Tests failed or coverage below 80%"
    echo "   Fix failing tests and increase coverage"
    FAILED=1
fi
echo ""

# Step 7: Dependency Security
echo "Step 7/7: Checking dependency vulnerabilities..."
if pip-audit --require-hashes --disable-pip 2>/dev/null || pip-audit; then
    echo "✅ No known vulnerabilities in dependencies"
else
    echo "⚠️  Vulnerabilities found in dependencies"
    echo "   Review and update affected packages"
    # Don't fail gate for dependency vulnerabilities (warning only)
fi
echo ""

# Summary
echo "=============================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ Quality Gate 1 PASSED"
    echo ""
    echo "Your code is ready for review!"
    echo "Next steps:"
    echo "  1. git add ."
    echo "  2. git commit -m '[TASK] Description'"
    echo "  3. git push origin <branch>"
    echo "  4. Create pull request"
    exit 0
else
    echo "❌ Quality Gate 1 FAILED"
    echo ""
    echo "Please fix the issues above before requesting review."
    echo "Run this script again after fixing."
    exit 1
fi
