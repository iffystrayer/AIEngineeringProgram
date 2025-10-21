"""
Test Suite: Database Connection Module

Tests the database connection pool manager and configuration.

Following TDD methodology:
- Tests for configuration, initialization, health checks
- Connection acquisition and transaction management
- Error handling and resource cleanup
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.database.connection import (
    DatabaseConfig,
    DatabaseConnectionError,
    DatabaseManager,
    close_database,
    get_database_manager,
    initialize_database,
)

# ============================================================================
# TEST CONFIGURATION
# ============================================================================


class TestDatabaseConfig:
    """Tests for DatabaseConfig class."""

    def test_config_initialization_with_defaults(self) -> None:
        """Config should initialize with default values."""
        config = DatabaseConfig()

        assert config.host == "localhost"
        assert config.port == 15432
        assert config.database == "uaip_scoping"
        assert config.user == "uaip_user"
        assert config.password == "changeme"
        assert config.min_pool_size == 2
        assert config.max_pool_size == 10
        assert config.command_timeout == 30.0

    def test_config_initialization_with_custom_values(self) -> None:
        """Config should accept custom values."""
        config = DatabaseConfig(
            host="db.example.com",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_password",
            min_pool_size=5,
            max_pool_size=20,
            command_timeout=60.0,
        )

        assert config.host == "db.example.com"
        assert config.port == 5432
        assert config.database == "test_db"
        assert config.user == "test_user"
        assert config.password == "test_password"
        assert config.min_pool_size == 5
        assert config.max_pool_size == 20
        assert config.command_timeout == 60.0

    def test_config_from_env(self) -> None:
        """Config should load from environment variables."""
        env_vars = {
            "DB_HOST": "prod.db.com",
            "DB_PORT": "5432",
            "DB_NAME": "production_db",
            "DB_USER": "prod_user",
            "DB_PASSWORD": "prod_password",
            "DB_POOL_MIN_SIZE": "3",
            "DB_POOL_MAX_SIZE": "15",
            "DB_POOL_TIMEOUT": "45.0",
        }

        with patch.dict(os.environ, env_vars):
            config = DatabaseConfig.from_env()

            assert config.host == "prod.db.com"
            assert config.port == 5432
            assert config.database == "production_db"
            assert config.user == "prod_user"
            assert config.password == "prod_password"
            assert config.min_pool_size == 3
            assert config.max_pool_size == 15
            assert config.command_timeout == 45.0

    def test_config_from_env_with_missing_vars_uses_defaults(self) -> None:
        """Config should use defaults for missing env vars."""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig.from_env()

            assert config.host == "localhost"
            assert config.port == 15432
            assert config.database == "uaip_scoping"

    def test_get_connection_string_excludes_password(self) -> None:
        """Connection string should not include password for logging."""
        config = DatabaseConfig(
            host="db.example.com",
            port=5432,
            database="test_db",
            user="test_user",
            password="secret_password",
        )

        conn_string = config.get_connection_string()

        assert conn_string == "postgresql://test_user@db.example.com:5432/test_db"
        assert "secret_password" not in conn_string


# ============================================================================
# TEST DATABASE MANAGER
# ============================================================================


@pytest.fixture
def mock_config() -> DatabaseConfig:
    """Create mock database configuration."""
    return DatabaseConfig(
        host="localhost",
        port=15432,
        database="test_db",
        user="test_user",
        password="test_password",
    )


@pytest.fixture
def database_manager(mock_config: DatabaseConfig) -> DatabaseManager:
    """Create DatabaseManager instance."""
    return DatabaseManager(mock_config)


class TestDatabaseManager:
    """Tests for DatabaseManager class."""

    def test_manager_initialization(self, mock_config: DatabaseConfig) -> None:
        """Manager should initialize with config."""
        manager = DatabaseManager(mock_config)

        assert manager.config == mock_config
        assert manager._pool is None
        assert not manager.is_initialized

    @pytest.mark.asyncio
    async def test_initialize_creates_pool(self, database_manager: DatabaseManager) -> None:
        """Initialize should create connection pool."""
        from unittest.mock import AsyncMock, MagicMock
        from contextlib import asynccontextmanager

        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(return_value=None)

        # Create a proper async context manager for acquire()
        @asynccontextmanager
        async def mock_acquire():
            yield mock_conn

        mock_pool.acquire = mock_acquire

        # Mock create_pool to return the pool directly (not a coroutine)
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()

            assert database_manager.is_initialized
            mock_create_pool.assert_called_once()
            mock_conn.execute.assert_called_once_with("SELECT 1")

    @pytest.mark.asyncio
    async def test_initialize_raises_on_connection_failure(
        self, database_manager: DatabaseManager
    ) -> None:
        """Initialize should raise DatabaseConnectionError on failure."""
        with patch("asyncpg.create_pool", side_effect=Exception("Connection failed")):
            with pytest.raises(DatabaseConnectionError, match="Database connection failed"):
                await database_manager.initialize()

    @pytest.mark.asyncio
    async def test_initialize_is_idempotent(self, database_manager: DatabaseManager) -> None:
        """Initialize should not reinitialize if already initialized."""
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()
            await database_manager.initialize()  # Call again

            # Should only create pool once
            assert mock_create_pool.call_count == 1

    @pytest.mark.asyncio
    async def test_close_closes_pool(self, database_manager: DatabaseManager) -> None:
        """Close should properly close the connection pool."""
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_pool.close = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()
            await database_manager.close()

            assert not database_manager.is_initialized
            mock_pool.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_is_safe_when_not_initialized(
        self, database_manager: DatabaseManager
    ) -> None:
        """Close should not error when pool is not initialized."""
        await database_manager.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_acquire_raises_when_not_initialized(
        self, database_manager: DatabaseManager
    ) -> None:
        """Acquire should raise if pool not initialized."""
        with pytest.raises(DatabaseConnectionError, match="not initialized"):
            async with database_manager.acquire():
                pass

    @pytest.mark.asyncio
    async def test_acquire_yields_connection(self, database_manager: DatabaseManager) -> None:
        """Acquire should yield database connection."""
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()

            async with database_manager.acquire() as conn:
                assert conn == mock_conn

    @pytest.mark.asyncio
    async def test_transaction_commits_on_success(self, database_manager: DatabaseManager) -> None:
        """Transaction should commit on successful completion."""
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_transaction = MagicMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_conn.transaction.return_value = mock_transaction
            mock_conn.execute = AsyncMock()
            mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.acquire.return_value.__aexit__ = AsyncMock()
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()

            async with database_manager.transaction() as conn:
                await conn.execute("INSERT INTO test VALUES (1)")

            # Transaction context manager should have been used
            mock_conn.transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_returns_true_when_healthy(
        self, database_manager: DatabaseManager
    ) -> None:
        """Health check should return True when database is healthy."""
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.fetchval = AsyncMock(return_value=1)
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()
            result = await database_manager.health_check()

            assert result is True
            mock_conn.fetchval.assert_called_once_with("SELECT 1")

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_not_initialized(
        self, database_manager: DatabaseManager
    ) -> None:
        """Health check should return False when pool not initialized."""
        result = await database_manager.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_returns_false_on_error(
        self, database_manager: DatabaseManager
    ) -> None:
        """Health check should return False on connection error."""
        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            mock_conn.fetchval = AsyncMock(side_effect=Exception("Connection lost"))
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()
            result = await database_manager.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_execute_script_runs_sql_file(
        self, database_manager: DatabaseManager, tmp_path: Path
    ) -> None:
        """Execute script should run SQL file contents."""
        # Create temporary SQL script
        script_path = tmp_path / "test_script.sql"
        script_path.write_text("CREATE TABLE test (id INTEGER);")

        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await database_manager.initialize()
            await database_manager.execute_script(str(script_path))

            # Should have executed the script content
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args[0][0]
            assert "CREATE TABLE test" in call_args


# ============================================================================
# TEST GLOBAL FUNCTIONS
# ============================================================================


class TestGlobalFunctions:
    """Tests for module-level database functions."""

    def test_get_database_manager_creates_singleton(self, mock_config: DatabaseConfig) -> None:
        """get_database_manager should create singleton instance."""
        from src.database import connection

        connection._db_manager = None  # Reset global state

        manager = get_database_manager(mock_config)
        manager2 = get_database_manager()

        assert manager is manager2

        # Cleanup
        connection._db_manager = None

    def test_get_database_manager_raises_without_config(self) -> None:
        """get_database_manager should raise if config not provided initially."""
        from src.database import connection

        connection._db_manager = None  # Reset global state

        with pytest.raises(ValueError, match="DatabaseConfig required"):
            get_database_manager()

        # Cleanup
        connection._db_manager = None

    @pytest.mark.asyncio
    async def test_initialize_database_creates_and_initializes_manager(
        self, mock_config: DatabaseConfig
    ) -> None:
        """initialize_database should create and initialize manager."""
        from src.database import connection

        connection._db_manager = None  # Reset global state

        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            manager = await initialize_database(mock_config)

            assert manager.is_initialized

        # Cleanup
        await close_database()
        connection._db_manager = None

    @pytest.mark.asyncio
    async def test_close_database_closes_manager(self, mock_config: DatabaseConfig) -> None:
        """close_database should close global manager."""
        from src.database import connection

        connection._db_manager = None  # Reset global state

        with patch("asyncpg.create_pool") as mock_create_pool:
            mock_pool = MagicMock()
            mock_pool.acquire = AsyncMock()
            mock_pool.close = AsyncMock()
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def mock_acquire():
                yield mock_conn
            mock_pool.acquire = mock_acquire
            mock_create_pool.return_value = mock_pool

            await initialize_database(mock_config)
            await close_database()

            assert connection._db_manager is None
