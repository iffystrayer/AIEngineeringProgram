#!/usr/bin/env python3
"""
Setup test database for integration tests.

Creates test database and initializes schema from database/init.sql
"""

import asyncio
import sys
from pathlib import Path

import asyncpg


async def setup_test_database():
    """Create test database and initialize schema."""

    # Connection parameters
    host = "localhost"
    port = 15432
    user = "uaip_user"
    password = "changeme"
    test_db = "uaip_scoping_test"
    
    try:
        # Connect to default postgres database to create test database
        print(f"Connecting to PostgreSQL at {host}:{port}...")
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        
        # Check if test database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            test_db
        )
        
        if exists:
            print(f"Test database '{test_db}' already exists. Dropping and recreating...")
            # Terminate existing connections
            await conn.execute(
                f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                f"FROM pg_stat_activity "
                f"WHERE pg_stat_activity.datname = '{test_db}' "
                f"AND pid <> pg_backend_pid()"
            )
            # Drop database
            await conn.execute(f"DROP DATABASE IF EXISTS {test_db}")
        
        # Create test database
        print(f"Creating test database '{test_db}'...")
        await conn.execute(f"CREATE DATABASE {test_db}")
        await conn.close()
        
        # Connect to test database and initialize schema
        print(f"Initializing schema...")
        test_conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=test_db
        )
        
        # Read and execute init.sql
        init_sql_path = Path(__file__).parent.parent / "database" / "init.sql"
        if not init_sql_path.exists():
            print(f"ERROR: {init_sql_path} not found")
            sys.exit(1)
        
        with open(init_sql_path, "r") as f:
            schema_sql = f.read()
        
        # Execute schema
        await test_conn.execute(schema_sql)
        await test_conn.close()
        
        print(f"✅ Test database '{test_db}' created and initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(setup_test_database())
    sys.exit(0 if success else 1)

