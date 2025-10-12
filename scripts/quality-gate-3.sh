#!/usr/bin/env bash
#
# Quality Gate 3 - Pre-Production Deployment Validation
# Run this before deploying to production
#
# U-AIP Scoping Assistant - Production Readiness Check
# Comprehensive validation for production deployment

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=============================================="
echo "  Quality Gate 3 - Production Readiness"
echo "=============================================="
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "❌ Error: Virtual environment not found"
    exit 1
fi

FAILED=0
WARNINGS=0

# Step 1: Full Test Suite (All Tiers)
echo "Step 1/10: Running complete test suite (all tiers)..."
if pytest tests/ -v -m "" --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80 --timeout=300; then
    echo "✅ Complete test suite passed"
else
    echo "❌ Complete test suite failed"
    FAILED=1
fi
echo ""

# Step 2: Regression Tests
echo "Step 2/10: Running regression tests..."
if pytest tests/ -v -m regression --timeout=300; then
    echo "✅ Regression tests passed"
else
    echo "❌ Regression tests failed"
    FAILED=1
fi
echo ""

# Step 3: Integration Tests
echo "Step 3/10: Running integration tests..."
if pytest tests/integration/ -v --timeout=300; then
    echo "✅ Integration tests passed"
else
    echo "❌ Integration tests failed"
    FAILED=1
fi
echo ""

# Step 4: Security Scan (Strict)
echo "Step 4/10: Running comprehensive security scan..."
if bandit -r src/ -c pyproject.toml -ll; then
    echo "✅ Security scan passed (high severity only)"
else
    echo "❌ Security vulnerabilities found"
    FAILED=1
fi
echo ""

# Step 5: Dependency Vulnerabilities
echo "Step 5/10: Scanning dependencies for vulnerabilities..."
if pip-audit; then
    echo "✅ No vulnerabilities in dependencies"
else
    echo "❌ Vulnerable dependencies found"
    FAILED=1
fi
echo ""

# Step 6: Docker Build Test
echo "Step 6/10: Testing Docker build..."
if [ -f "Dockerfile" ]; then
    if docker build -t uaip-scoping-assistant:test .; then
        echo "✅ Docker build successful"
    else
        echo "❌ Docker build failed"
        FAILED=1
    fi
else
    echo "⚠️  Dockerfile not found - skipping"
    WARNINGS=1
fi
echo ""

# Step 7: Docker Security Scan
echo "Step 7/10: Scanning Docker image for vulnerabilities..."
if command -v trivy &> /dev/null; then
    if docker images uaip-scoping-assistant:test &> /dev/null; then
        if trivy image --severity HIGH,CRITICAL --exit-code 1 uaip-scoping-assistant:test; then
            echo "✅ Docker image security scan passed"
        else
            echo "❌ Critical vulnerabilities in Docker image"
            FAILED=1
        fi
    else
        echo "⚠️  Docker image not built - skipping scan"
        WARNINGS=1
    fi
else
    echo "⚠️  Trivy not installed - skipping Docker scan"
    echo "   Install with: brew install aquasecurity/trivy/trivy"
    WARNINGS=1
fi
echo ""

# Step 8: Environment Configuration Check
echo "Step 8/10: Validating environment configuration..."
if [ -f ".env.example" ]; then
    echo "✅ .env.example exists"
    if grep -q "ANTHROPIC_API_KEY" .env.example && \
       grep -q "DB_HOST" .env.example && \
       grep -q "DB_PASSWORD" .env.example; then
        echo "✅ Required environment variables documented"
    else
        echo "❌ Missing required environment variables in .env.example"
        FAILED=1
    fi
else
    echo "❌ .env.example not found"
    FAILED=1
fi
echo ""

# Step 9: Database Migration Check
echo "Step 9/10: Checking database schema..."
if [ -f "database/init.sql" ]; then
    echo "✅ Database schema file exists"
else
    echo "⚠️  database/init.sql not found"
    WARNINGS=1
fi
echo ""

# Step 10: Documentation Check
echo "Step 10/10: Verifying documentation..."
REQUIRED_DOCS=("README.md" "SWE_SPECIFICATION.md" "PROJECT_WORKFLOW.md")
for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc exists"
    else
        echo "❌ $doc missing"
        FAILED=1
    fi
done
echo ""

# Summary
echo "=============================================="
echo "  Quality Gate 3 Summary"
echo "=============================================="
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "✅ Quality Gate 3 PASSED (No Issues)"
    else
        echo "⚠️  Quality Gate 3 PASSED (With Warnings)"
        echo ""
        echo "Review warnings above before deploying."
    fi
    echo ""
    echo "🚀 Code is PRODUCTION READY!"
    echo ""
    echo "Pre-deployment checklist:"
    echo "  ☐ Review CHANGELOG.md"
    echo "  ☐ Update version in pyproject.toml"
    echo "  ☐ Tag release: git tag -a v1.0.0 -m 'Release v1.0.0'"
    echo "  ☐ Push tag: git push origin v1.0.0"
    echo "  ☐ Build production image: docker build -t uaip:v1.0.0 ."
    echo "  ☐ Deploy to production environment"
    echo "  ☐ Run smoke tests"
    echo "  ☐ Monitor application logs"
    exit 0
else
    echo "❌ Quality Gate 3 FAILED"
    echo ""
    echo "Critical issues found. DO NOT DEPLOY TO PRODUCTION."
    echo "Fix all failures above and re-run this script."
    exit 1
fi
