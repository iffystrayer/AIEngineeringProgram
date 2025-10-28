# Database Migrations

This project uses Alembic for database schema migrations.

## Status

✅ **Alembic Initialized** - Framework is in place
🔄 **Initial Migration** - Template created, needs schema from `database/init.sql`

## Quick Start

### Run Migrations
```bash
# Apply all migrations
uv run alembic upgrade head

# Check current version
uv run alembic current

# View migration history
uv run alembic history
```

### Create New Migration
```bash
# Auto-generate from model changes
uv run alembic revision --autogenerate -m "Description"

# Create empty migration
uv run alembic revision -m "Description"

# Edit migrations/versions/XXXX_description.py
# Then apply: uv run alembic upgrade head
```

### Rollback
```bash
# Rollback one version
uv run alembic downgrade -1

# Rollback to specific version
uv run alembic downgrade <revision_id>

# Rollback all
uv run alembic downgrade base
```

## TODO

- [ ] Populate initial migration (`91652a9f0ca1`) with schema from `database/init.sql`
- [ ] Configure `alembic.ini` to use environment variables for DB connection
- [ ] Update Docker to run migrations on startup
- [ ] Test migration upgrade/downgrade cycle

## Files

- `alembic.ini` - Configuration
- `migrations/env.py` - Runtime environment
- `migrations/versions/` - Migration files
- `database/init.sql` - Current schema (to be migrated)

## Production Deployment

1. Backup database
2. Run: `uv run alembic upgrade head`
3. Verify: `uv run alembic current`
4. If issues: `uv run alembic downgrade -1`

---

**Framework Ready:** Alembic is configured and ready. Schema migration needs completion.
