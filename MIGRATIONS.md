# Database Migrations Guide

**Migration Tool:** Alembic  
**Database:** PostgreSQL 16  
**Schema Version:** 1.0.0 (Initial)

This project uses Alembic for database schema migrations, ensuring safe and repeatable schema evolution.

---

## Quick Reference

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history

# Create new migration
alembic revision -m "description"
```

---

## Setup

### 1. Install Alembic

Already installed as part of the project dependencies:
```bash
uv pip install -e ".[dev]"
```

### 2. Configuration

Alembic is configured to read database credentials from environment variables using `DatabaseConfig.from_env()`.

**Environment Variables Required:**
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 15432)
- `DB_NAME` (default: uaip_scoping)
- `DB_USER` (default: uaip_user)
- `DB_PASSWORD` (default: changeme)

Configuration files:
- `alembic.ini` - Alembic settings
- `migrations/env.py` - Migration environment setup
- `migrations/versions/` - Migration scripts

---

## Running Migrations

### Development

**Upgrade to latest version:**
```bash
alembic upgrade head
```

**Check current version:**
```bash
alembic current
```

**View pending migrations:**
```bash
alembic history
```

### Production

**IMPORTANT:** Always backup your database before running migrations in production!

```bash
# 1. Backup database
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations
alembic upgrade head

# 3. Verify
alembic current
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\dt"
```

### Docker Environment

If using Docker Compose:

```bash
# Database is already running via docker-compose
docker-compose up -d uaip-db

# Run migrations on host
alembic upgrade head

# OR run migrations inside container
docker-compose exec uaip-db alembic upgrade head
```

---

## Creating New Migrations

### Manual Migration (Recommended for this project)

Since we use asyncpg directly (not SQLAlchemy ORM), create migrations manually:

```bash
# 1. Create empty migration
alembic revision -m "add user authentication table"

# 2. Edit the generated file in migrations/versions/
# Fill in upgrade() and downgrade() functions

# 3. Test the migration
alembic upgrade head

# 4. Test rollback
alembic downgrade -1

# 5. Re-apply
alembic upgrade head
```

### Migration Template

```python
"""Description of changes

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-10-24 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'xxxxx'
down_revision = 'yyyyy'

def upgrade() -> None:
    # Add your schema changes here
    op.create_table(
        'new_table',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False)
    )

def downgrade() -> None:
    # Reverse the changes
    op.drop_table('new_table')
```

---

## Rollback

### Rollback One Version

```bash
alembic downgrade -1
```

### Rollback to Specific Version

```bash
alembic downgrade <revision_id>
```

### Rollback Everything

```bash
alembic downgrade base
```

**WARNING:** This will drop all tables! Only use for testing.

---

## Migration History

### Current Schema (v1.0.0)

**Revision:** 03033cebb647  
**Date:** October 24, 2025  
**Description:** Initial schema from init.sql

**Tables Created:**
1. `sessions` - User session tracking
2. `stage_data` - Stage responses (JSONB)
3. `conversation_history` - Complete conversation log
4. `checkpoints` - Stage completion snapshots
5. `project_charters` - Generated charters
6. `quality_metrics` - Quality scoring analytics
7. `consistency_reports` - Cross-stage validation

**Functions Created:**
- `update_sessions_timestamp()` - Auto-update last_updated_at
- `update_stage_data_timestamp()` - Auto-update updated_at
- `get_active_sessions_count()` - Count active sessions
- `get_session_progress(UUID)` - Calculate session progress %
- `mark_abandoned_sessions()` - Mark stale sessions

**Extensions:**
- `uuid-ossp` - UUID generation

---

## Troubleshooting

### "No module named 'src'"

Make sure you're running alembic from the project root directory:
```bash
cd /Users/ifiokmoses/code/AIEngineeringProgram
alembic upgrade head
```

### "Database connection failed"

Check your environment variables:
```bash
echo $DB_HOST
echo $DB_PORT
echo $DB_NAME

# Or check .env file
cat .env
```

### "Table already exists"

If tables were created manually (via init.sql), you need to mark the current state:

```bash
# Mark database as being at head revision without running migrations
alembic stamp head
```

### "Migration failed halfway"

Alembic uses transactions, so partial failures should rollback automatically. But to be safe:

```bash
# Check current state
alembic current

# If stuck, manually rollback
alembic downgrade -1

# Fix the migration
# Re-run
alembic upgrade head
```

---

## Best Practices

### DO

✅ **Always backup production databases before migrations**
✅ **Test migrations on a staging database first**
✅ **Write both upgrade() and downgrade() functions**
✅ **Use transactions for data migrations**
✅ **Document breaking changes in migration docstring**
✅ **Test rollback (downgrade) before deploying**

### DON'T

❌ **Don't modify existing migrations after they've been applied**
❌ **Don't delete migration files**
❌ **Don't skip versions**
❌ **Don't run migrations in multiple environments simultaneously**
❌ **Don't assume downgrade will preserve data**

---

## Schema Lifecycle

### Adding a Column

```python
def upgrade():
    op.add_column('sessions',
        sa.Column('email', sa.String(255), nullable=True)
    )

def downgrade():
    op.drop_column('sessions', 'email')
```

### Modifying a Column

```python
def upgrade():
    op.alter_column('sessions', 'user_id',
        existing_type=sa.String(255),
        type_=sa.String(500),
        existing_nullable=False
    )

def downgrade():
    op.alter_column('sessions', 'user_id',
        existing_type=sa.String(500),
        type_=sa.String(255),
        existing_nullable=False
    )
```

### Adding an Index

```python
def upgrade():
    op.create_index('idx_sessions_email',
        'sessions', ['email']
    )

def downgrade():
    op.drop_index('idx_sessions_email')
```

---

## Integration with Application

### Startup Check

The application should verify migration state on startup:

```python
from alembic.config import Config
from alembic import command

def check_migrations():
    """Verify database is at latest migration"""
    alembic_cfg = Config("alembic.ini")
    # Check current revision matches head
    # Raise error if out of date
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
- name: Run Migrations
  run: |
    # Backup
    pg_dump $DATABASE_URL > backup.sql
    
    # Migrate
    alembic upgrade head
    
    # Verify
    alembic current
```

---

## See Also

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Schema](./database/init.sql)
- [P1 Tasks](./P1_ATOMIC_TASK_LIST.md#p13-add-database-migrations-3-4-hours)

---

**Last Updated:** October 24, 2025  
**Schema Version:** 1.0.0  
**Migration Tool:** Alembic 1.17.0
