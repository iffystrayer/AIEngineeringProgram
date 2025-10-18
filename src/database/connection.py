"""
Database Connection Module

Manages PostgreSQL connection pooling using asyncpg for the U-AIP system.
Provides async context managers for connection and transaction management.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Pool

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""

    pass


class DatabaseConfig:
    """Database connection configuration."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 15432,
        database: str = "uaip_scoping",
        user: str = "uaip_user",
        password: str = "changeme",
        min_pool_size: int = 2,
        max_pool_size: int = 10,
        command_timeout: float = 30.0,
    ) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self.command_timeout = command_timeout

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""
        import os

        from dotenv import load_dotenv

        load_dotenv()

        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "15432")),
            database=os.getenv("DB_NAME", "uaip_scoping"),
            user=os.getenv("DB_USER", "uaip_user"),
            password=os.getenv("DB_PASSWORD", "changeme"),
            min_pool_size=int(os.getenv("DB_POOL_MIN_SIZE", "2")),
            max_pool_size=int(os.getenv("DB_POOL_MAX_SIZE", "10")),
            command_timeout=float(os.getenv("DB_POOL_TIMEOUT", "30.0")),
        )

    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string (without password for logging)."""
        return f"postgresql://{self.user}@{self.host}:{self.port}/{self.database}"


class DatabaseManager:
    """
    Manages database connection pool lifecycle.

    Provides async context managers for acquiring connections and executing
    queries with proper error handling and connection management.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._pool: Pool | None = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """
        Initialize the connection pool.

        Raises:
            DatabaseConnectionError: If pool creation fails
        """
        if self._pool is not None:
            logger.warning("Database pool already initialized")
            return

        async with self._lock:
            if self._pool is not None:  # Double-check after acquiring lock
                return

            try:
                logger.info(f"Initializing database pool: {self.config.get_connection_string()}")

                self._pool = await asyncpg.create_pool(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.user,
                    password=self.config.password,
                    min_size=self.config.min_pool_size,
                    max_size=self.config.max_pool_size,
                    command_timeout=self.config.command_timeout,
                )

                # Test connection
                async with self._pool.acquire() as conn:
                    await conn.execute("SELECT 1")

                logger.info("Database pool initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize database pool: {e}")
                raise DatabaseConnectionError(f"Database connection failed: {e}") from e

    async def close(self) -> None:
        """Close the connection pool and cleanup resources."""
        if self._pool is None:
            return

        async with self._lock:
            if self._pool is None:
                return

            try:
                logger.info("Closing database pool")
                await self._pool.close()
                self._pool = None
                logger.info("Database pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing database pool: {e}")
                raise

    @property
    def is_initialized(self) -> bool:
        """Check if the pool is initialized."""
        return self._pool is not None

    @property
    def pool(self) -> Pool | None:
        """Get the underlying connection pool."""
        return self._pool

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Acquire a connection from the pool.

        Usage:
            async with db_manager.acquire() as conn:
                result = await conn.fetchval("SELECT 1")

        Yields:
            asyncpg.Connection: Database connection

        Raises:
            DatabaseConnectionError: If pool is not initialized or acquisition fails
        """
        if self._pool is None:
            raise DatabaseConnectionError("Database pool not initialized")

        try:
            async with self._pool.acquire() as connection:
                yield connection
        except Exception as e:
            logger.error(f"Error acquiring database connection: {e}")
            raise DatabaseConnectionError(f"Failed to acquire connection: {e}") from e

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """
        Acquire a connection and start a transaction.

        Automatically commits on success or rolls back on error.

        Usage:
            async with db_manager.transaction() as conn:
                await conn.execute("INSERT INTO...")
                await conn.execute("UPDATE...")
            # Transaction committed automatically

        Yields:
            asyncpg.Connection: Database connection with active transaction

        Raises:
            DatabaseConnectionError: If transaction fails
        """
        async with self.acquire() as connection, connection.transaction():
            yield connection

    async def health_check(self) -> bool:
        """
        Perform a health check on the database connection.

        Returns:
            bool: True if healthy, False otherwise
        """
        if self._pool is None:
            logger.warning("Health check failed: Pool not initialized")
            return False

        try:
            async with self._pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def execute_script(self, script_path: str) -> None:
        """
        Execute a SQL script file (e.g., schema initialization).

        Args:
            script_path: Path to the SQL script file

        Raises:
            DatabaseConnectionError: If script execution fails
        """
        try:
            with open(script_path) as f:
                script = f.read()

            async with self.acquire() as conn:
                await conn.execute(script)

            logger.info(f"Successfully executed script: {script_path}")

        except Exception as e:
            logger.error(f"Failed to execute script {script_path}: {e}")
            raise DatabaseConnectionError(f"Script execution failed: {e}") from e


# Singleton instance for application-wide use
_db_manager: DatabaseManager | None = None


def get_database_manager(config: DatabaseConfig | None = None) -> DatabaseManager:
    """
    Get or create the global DatabaseManager instance.

    Args:
        config: Database configuration (required on first call)

    Returns:
        DatabaseManager: Global database manager instance

    Raises:
        ValueError: If called without config when manager doesn't exist
    """
    global _db_manager

    if _db_manager is None:
        if config is None:
            raise ValueError("DatabaseConfig required for first initialization")
        _db_manager = DatabaseManager(config)

    return _db_manager


async def initialize_database(config: DatabaseConfig | None = None) -> DatabaseManager:
    """
    Initialize the global database manager.

    Args:
        config: Database configuration (uses env vars if not provided)

    Returns:
        DatabaseManager: Initialized database manager

    Raises:
        DatabaseConnectionError: If initialization fails
    """
    if config is None:
        config = DatabaseConfig.from_env()

    manager = get_database_manager(config)
    await manager.initialize()
    return manager


async def close_database() -> None:
    """Close the global database manager."""
    global _db_manager

    if _db_manager is not None:
        await _db_manager.close()
        _db_manager = None
