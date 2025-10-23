"""
Pytest Configuration and Fixtures

Provides shared fixtures for all tests including:
- Mock database manager
- Test database setup
- Common test data
"""

import asyncio
import os
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


# ============================================================================
# ASYNCIO CONFIGURATION
# ============================================================================


def pytest_configure(config: Any) -> None:
    """Configure pytest with asyncio support."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (deselect with '-m \"not asyncio\"')"
    )


@pytest.fixture(scope="function")
def event_loop() -> Any:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest_asyncio.fixture
async def mock_db_manager() -> AsyncMock:
    """
    Create mock database manager for unit tests.
    
    Returns:
        AsyncMock: Mock DatabaseManager instance
    """
    manager = AsyncMock()
    
    # Mock transaction context manager
    async def mock_transaction():
        conn = AsyncMock()
        conn.execute = AsyncMock(return_value=None)
        conn.fetchrow = AsyncMock(return_value=None)
        conn.fetch = AsyncMock(return_value=[])
        return conn
    
    manager.transaction = AsyncMock(return_value=mock_transaction())
    manager.acquire = AsyncMock()
    manager.initialize = AsyncMock()
    manager.close = AsyncMock()
    
    return manager


@pytest_asyncio.fixture
async def test_db_manager() -> AsyncGenerator[Any, None]:
    """
    Create real database manager for integration tests.

    Sets up test database and cleans up after tests.

    Yields:
        DatabaseManager: Real database manager connected to test database
    """
    from src.database.connection import DatabaseManager, DatabaseConfig

    # Use test database with correct credentials
    config = DatabaseConfig(
        host="localhost",
        port=15432,
        database="uaip_scoping_test",
        user="uaip_user",
        password="changeme",
        min_pool_size=1,
        max_pool_size=2,  # Reduced pool size to avoid connection issues
    )

    manager = DatabaseManager(config)

    try:
        await manager.initialize()
        yield manager
    finally:
        try:
            await manager.close()
        except Exception:
            pass  # Ignore errors during cleanup


@pytest.fixture
def api_test_db_manager(event_loop):
    """
    Create real database manager for API tests (synchronous fixture).

    This fixture is for use with TestClient which is synchronous.
    It initializes the database manager using the pytest event loop.

    Yields:
        DatabaseManager: Real database manager connected to test database
    """
    from src.database.connection import DatabaseManager, DatabaseConfig

    # Use test database with correct credentials
    config = DatabaseConfig(
        host="localhost",
        port=15432,
        database="uaip_scoping_test",
        user="uaip_user",
        password="changeme",
        min_pool_size=2,
        max_pool_size=10,
    )

    manager = DatabaseManager(config)

    try:
        # Initialize using the pytest event loop
        event_loop.run_until_complete(manager.initialize())
        yield manager
    finally:
        # Close using the pytest event loop
        event_loop.run_until_complete(manager.close())


# ============================================================================
# COMMON TEST DATA FIXTURES
# ============================================================================


@pytest.fixture
def sample_session_data() -> dict[str, Any]:
    """Create sample session data for testing."""
    from uuid import uuid4
    from datetime import datetime
    
    return {
        "session_id": uuid4(),
        "user_id": "test_user_123",
        "project_name": "Customer Churn Prediction",
        "started_at": datetime.utcnow(),
        "last_updated_at": datetime.utcnow(),
        "current_stage": 1,
        "stage_data": {},
        "conversation_history": [],
        "status": "IN_PROGRESS",
        "checkpoints": [],
    }


@pytest.fixture
def sample_problem_statement() -> dict[str, Any]:
    """Create sample problem statement for testing."""
    return {
        "business_problem": "We need to predict customer churn",
        "business_context": "E-commerce platform with 100k customers",
        "success_criteria": "Reduce churn by 15%",
        "constraints": "Must work with existing data pipeline",
    }


@pytest.fixture
def sample_stage_data() -> dict[str, Any]:
    """Create sample stage data for testing."""
    return {
        "stage_1": {
            "business_problem": "Predict customer churn",
            "business_context": "E-commerce platform",
        },
        "stage_2": {
            "success_criteria": "Reduce churn by 15%",
            "metrics": ["Precision", "Recall"],
        },
        "stage_3": {
            "data_sources": ["Customer database", "Transaction logs"],
            "data_quality": "Good",
        },
        "stage_4": {
            "user_impact": "Positive",
            "stakeholders": ["Product team", "Customer success"],
        },
        "stage_5": {
            "ethical_risks": "Bias in predictions",
            "governance": "Proceed",
        },
    }


# ============================================================================
# ENVIRONMENT FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def setup_test_env() -> None:
    """Set up test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DB_HOST"] = "localhost"
    os.environ["DB_PORT"] = "15432"
    os.environ["DB_NAME"] = "uaip_scoping_test"
    os.environ["DB_USER"] = "uaip_user"
    os.environ["DB_PASSWORD"] = "changeme"


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_after_test() -> None:
    """Clean up after each test."""
    yield
    # Add cleanup code here if needed


# ============================================================================
# API TEST FIXTURES
# ============================================================================


@pytest.fixture
def api_client(event_loop, api_test_db_manager):
    """
    Create FastAPI test client with initialized database.

    This fixture provides a TestClient that has the database initialized
    and ready for testing API endpoints.
    """
    from fastapi.testclient import TestClient
    from src.api.main import app

    # Initialize the API modules with the database manager
    import src.api.main as api_main
    api_main.db_manager = api_test_db_manager

    # Initialize repositories
    from src.database.repositories.session_repository import SessionRepository
    from src.database.repositories.stage_data_repository import StageDataRepository
    from src.database.repositories.checkpoint_repository import CheckpointRepository
    from src.agents.orchestrator import Orchestrator

    api_main.session_repo = SessionRepository(api_test_db_manager)
    api_main.stage_data_repo = StageDataRepository(api_test_db_manager)
    api_main.checkpoint_repo = CheckpointRepository(api_test_db_manager)
    api_main.orchestrator = Orchestrator(api_test_db_manager)

    return TestClient(app)



