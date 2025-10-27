# U-AIP Scoping Assistant - Administrator Guide

**System Administration and Operations Guide**

This guide covers system administration, deployment, monitoring, and troubleshooting for the U-AIP Scoping Assistant.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Operations](#operations)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Security](#security)
7. [Disaster Recovery](#disaster-recovery)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

### System Requirements
```
Hardware:
  - CPU: 2+ cores
  - RAM: 4 GB minimum (8 GB recommended)
  - Storage: 20 GB minimum (SSD recommended)

Software:
  - Docker: 20.10+
  - Docker Compose: 1.29+
  - Python: 3.9+ (for local development)
  - PostgreSQL: 16 (runs in container)

Network:
  - Port 38937 (API)
  - Port 15432 (Database - internal only)
  - Internet access for package installation
```

### Architecture Components
```
┌─────────────┐
│  FastAPI    │ Port 38937
│  Server     │
└──────┬──────┘
       │
┌──────▼──────────────┐
│  PostgreSQL 16      │ Port 15432 (internal)
│  Database           │
└─────────────────────┘
```

---

## Installation & Setup

### Step 1: Clone Repository
```bash
git clone <repository_url>
cd AIEngineeringProgram
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### Step 3: Initialize Docker Containers
```bash
# Build and start containers
docker-compose up -d

# Verify containers are running
docker-compose ps

# Output should show:
# uaip-api    | Running
# uaip-db     | Running
# uaip-app    | Running
```

### Step 4: Initialize Database
```bash
# Run migrations
docker exec uaip-api alembic upgrade head

# Verify tables created
docker exec uaip-db psql -U uaip_user -d uaip_scoping -c "\dt"

# Should show tables: users, sessions, stage_data, etc.
```

### Step 5: Verify Installation
```bash
# Check API health
curl http://localhost:38937/api/v1/health

# Output should be:
# {"status":"healthy","components":{"api":"healthy","database":"healthy"}}
```

---

## Configuration

### Environment Variables

#### Required Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=15432
DB_NAME=uaip_scoping
DB_USER=uaip_user
DB_PASSWORD=secure_password_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=38937

# JWT Secret (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_secret_key_here
```

#### Optional Variables
```bash
# Encryption (NFR-5.1)
ENCRYPTION_ENABLED=false
SESSION_ENCRYPTION_KEY=  # Generate if enabling

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json or text

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Feature Flags

#### Encryption
To enable data encryption at rest:
```bash
# 1. Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Set environment variables
export ENCRYPTION_ENABLED=true
export SESSION_ENCRYPTION_KEY="<generated_key>"

# 3. Restart API
docker-compose restart uaip-api
```

#### Audit Logging
Coming in Phase 2D - will log all user actions for compliance.

### Database Configuration

#### Connection Pooling
```
Current: asyncpg with built-in connection pooling
Pool Size: 10 connections
Timeout: 30 seconds
Retry: 3 attempts
```

#### Backup Configuration
See Disaster Recovery section below.

---

## Operations

### Starting & Stopping

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop without removing volumes (data preserved)
docker-compose down --volumes

# Restart specific service
docker-compose restart uaip-api
docker-compose restart uaip-db

# View logs
docker-compose logs -f uaip-api
docker-compose logs -f uaip-db

# View logs for specific time
docker-compose logs --since 10m uaip-api
```

### Database Operations

#### Create Database Backup
```bash
# Full database backup
docker exec uaip-db pg_dump -U uaip_user uaip_scoping > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup (smaller file)
docker exec uaip-db pg_dump -U uaip_user uaip_scoping | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Restore Database
```bash
# From uncompressed backup
docker exec -i uaip-db psql -U uaip_user uaip_scoping < backup_20251026_000000.sql

# From compressed backup
gunzip < backup_20251026_000000.sql.gz | docker exec -i uaip-db psql -U uaip_user uaip_scoping
```

#### View Database Status
```bash
# Connect to database
docker exec -it uaip-db psql -U uaip_user -d uaip_scoping

# List all tables
\dt

# Get table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Count users
SELECT COUNT(*) FROM users;

# Count sessions
SELECT COUNT(*) FROM sessions;
```

#### Run Database Migrations
```bash
# Apply pending migrations
docker exec uaip-api alembic upgrade head

# Check migration status
docker exec uaip-api alembic current

# Create new migration (requires Alembic setup)
docker exec uaip-api alembic revision --autogenerate -m "migration_name"
```

### User Management

#### Create Admin User (Manual)
```bash
# Access database
docker exec -it uaip-db psql -U uaip_user -d uaip_scoping

# Insert admin user
INSERT INTO users (user_id, email, password_hash, name, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'admin@example.com',
  'bcrypt_hash_here',
  'Admin User',
  NOW(),
  NOW()
);
```

#### Reset User Password
```bash
# Generate new password hash (requires bcrypt)
python3 << 'EOF'
import bcrypt
password = "NewPassword123!"
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(password.encode(), salt).decode()
print(f"UPDATE users SET password_hash = '{hashed}' WHERE email = 'user@example.com';")
EOF

# Execute update
docker exec uaip-db psql -U uaip_user -d uaip_scoping -c "UPDATE users SET password_hash = '...' WHERE email = 'user@example.com';"
```

#### Lock/Unlock User Account
```bash
# Add status column if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

# Lock user
UPDATE users SET status = 'locked' WHERE email = 'user@example.com';

# Unlock user
UPDATE users SET status = 'active' WHERE email = 'user@example.com';
```

---

## Monitoring & Maintenance

### Health Checks

#### API Health Endpoint
```bash
curl http://localhost:38937/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "ollama": "healthy"
  }
}
```

#### Container Health
```bash
# Check container status
docker-compose ps

# View resource usage
docker stats

# View container logs for errors
docker-compose logs --grep ERROR
```

### Performance Monitoring

#### Database Query Performance
```bash
# Enable query logging (warning: verbose)
docker exec uaip-db psql -U uaip_user -d uaip_scoping -c \
  "ALTER SYSTEM SET log_min_duration_statement = 1000;"

# Reload configuration
docker exec uaip-db psql -U uaip_user -d uaip_scoping -c "SELECT pg_reload_conf();"

# View slow queries
docker logs uaip-db | grep duration
```

#### API Response Times
```bash
# Using curl with timing
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:38937/api/v1/health
```

#### Rate Limit Status
```bash
# Check current rate limit usage (depends on slowapi stats)
# Currently stored in-memory, not exposed via API
```

### Scheduled Maintenance

#### Daily Tasks
- [ ] Monitor error logs
- [ ] Check disk space: `docker exec uaip-db df -h`
- [ ] Verify API is responding: `curl http://localhost:38937/api/v1/health`

#### Weekly Tasks
- [ ] Create backup: `docker exec uaip-db pg_dump -U uaip_user uaip_scoping > weekly_backup.sql`
- [ ] Review user registrations
- [ ] Check rate limit usage patterns
- [ ] Review slow query logs

#### Monthly Tasks
- [ ] Update dependencies: `docker-compose down && docker pull && docker-compose up -d`
- [ ] Review security logs
- [ ] Audit user accounts
- [ ] Capacity planning review
- [ ] Full disaster recovery test

---

## Security

### Authentication & Authorization

#### Secret Key Management
```bash
# Generate new secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update SECRET_KEY in .env
# Restart API: docker-compose restart uaip-api

# Note: Changing secret key invalidates all existing tokens
```

#### JWT Token Management
```bash
# Tokens are valid for 24 hours
# Implemented in: src/auth/security.py

# To reduce token lifetime, modify:
TOKEN_EXPIRATION_SECONDS = 86400  # seconds (currently 24 hours)
```

### Data Security

#### Encryption at Rest
```bash
# Enable encryption for sensitive data
export ENCRYPTION_ENABLED=true
export SESSION_ENCRYPTION_KEY="fernet_key_here"

# Data encrypted: stage_data, conversation_history
# Algorithm: Fernet (AES-128 CBC)
```

#### Password Security
```bash
# Passwords hashed with bcrypt (12 rounds)
# Implementation: src/auth/security.py

# Never:
# - Store plaintext passwords
# - Return password in API responses
# - Log passwords
# - Transmit without HTTPS (in production)
```

#### Database Access Control
```bash
# Current database user has limited permissions
DB_USER=uaip_user  # Has SELECT, INSERT, UPDATE, DELETE only

# For additional security:
# - Change uaip_user password periodically
# - Use separate read-only user for backups
# - Enable SSL connections in production
```

### Network Security

#### HTTPS/TLS (Production)
```bash
# Install SSL certificate (Let's Encrypt example)
certbot certonly --standalone -d yourdomain.com

# Update nginx/reverse proxy configuration
# See production deployment guide

# Redirect HTTP to HTTPS
# Enable HSTS headers
```

#### CORS Configuration
```bash
# Edit src/api/main.py
ALLOWED_ORIGINS = [
  "http://localhost:3000",
  "https://yourdomain.com",
]

# Restart API
docker-compose restart uaip-api
```

#### Rate Limiting
```bash
# Current limits (per user):
# 100 requests/hour general
# 10,000 requests/hour global

# Configure in: src/api/main.py
# limiter = Limiter(key_func=get_remote_address)
# @limiter.limit("100/hour")
```

### Audit & Compliance

#### Activity Logging
Currently logs to `docker logs uaip-api`

Future (Phase 2D):
- Comprehensive audit trail
- User action logging
- Data access tracking
- Compliance reporting

#### Data Retention
```bash
# Current: All data retained indefinitely
# Future: Configurable retention policy

# To manually delete old sessions:
DELETE FROM sessions WHERE last_updated_at < NOW() - INTERVAL '1 year';
```

---

## Disaster Recovery

### Backup Strategy

#### Automated Backups (Recommended)
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/uaip_backup_$TIMESTAMP.sql.gz"

docker exec uaip-db pg_dump -U uaip_user uaip_scoping | gzip > $BACKUP_FILE
echo "Backup created: $BACKUP_FILE"

# Keep only last 30 days
find $BACKUP_DIR -name "uaip_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
# 0 2 * * * /path/to/backup.sh
```

#### Cloud Backups
For production:
```bash
# Upload backups to S3
aws s3 cp uaip_backup_20251026_000000.sql.gz s3://backup-bucket/uaip/

# or Azure Blob Storage
az storage blob upload -c backups -f uaip_backup_20251026_000000.sql.gz
```

### Recovery Procedures

#### Full System Recovery
```bash
# 1. Stop running containers
docker-compose down

# 2. Remove containers and volumes (WARNING: data loss)
docker-compose down -v

# 3. Start fresh containers
docker-compose up -d

# 4. Restore database backup
docker exec -i uaip-db psql -U uaip_user uaip_scoping < backup.sql

# 5. Run migrations (if needed)
docker exec uaip-api alembic upgrade head

# 6. Verify
curl http://localhost:38937/api/v1/health
```

#### Partial Recovery (Database Only)
```bash
# 1. Keep containers running
# 2. Connect to database
docker exec -it uaip-db psql -U uaip_user uaip_scoping

# 3. Drop and recreate database
DROP DATABASE uaip_scoping;
CREATE DATABASE uaip_scoping OWNER uaip_user;

# 4. Exit and restore backup
exit
docker exec -i uaip-db psql -U uaip_user uaip_scoping < backup.sql
```

#### Point-in-Time Recovery
```bash
# PostgreSQL supports point-in-time recovery
# Set up in production with WAL archiving

# For now, restore from most recent backup and reapply changes manually
```

### Failover Procedures

#### Single Server Failover
Currently not configured (single point of failure).

For production:
1. Set up secondary database server
2. Configure replication
3. Set up load balancer
4. Test failover procedures
5. Document runbooks

---

## Troubleshooting

### Common Issues

#### Database Connection Error
```
Error: could not translate host name "uaip-db" to address
```

**Solution:**
1. Check containers running: `docker-compose ps`
2. Check network: `docker network ls`
3. Restart services: `docker-compose down && docker-compose up -d`

#### Out of Memory
```
docker: Error response from daemon: OOM killer terminated this container.
```

**Solution:**
1. Check resource usage: `docker stats`
2. Increase Docker memory allocation
3. Review logs: `docker logs uaip-api`
4. Optimize queries (see Performance Monitoring)

#### High Disk Usage
```bash
# Check disk space
docker exec uaip-db df -h

# Find large files
docker exec uaip-db du -sh /var/lib/postgresql/data/*

# Clean up old backups
rm -f backups/uaip_backup_*.sql.gz older than 30 days
```

#### Slow Queries
```bash
# Enable slow query log
docker exec uaip-db psql -U uaip_user -d uaip_scoping << 'EOF'
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 second
SELECT pg_reload_conf();
EOF

# Review logs
docker logs uaip-db | grep duration

# Optimize with indexes (if needed)
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

#### Token Expiration Issues
```
Error: 401 Unauthorized - Invalid or expired token
```

**Solution:**
1. User needs to login again: `POST /api/v1/auth/login`
2. Get new token
3. Use new token in Authorization header

#### Rate Limit Errors
```
Error: 429 Too Many Requests
```

**Solution:**
1. Wait 1 hour for limit to reset
2. Review usage patterns
3. Consider increasing rate limit (if appropriate)

### Debug Mode

#### Enable Debug Logging
```bash
# Set in .env
LOG_LEVEL=DEBUG

# Restart API
docker-compose restart uaip-api

# View logs
docker logs uaip-api
```

#### Database Debug Queries
```bash
# Connect to database
docker exec -it uaip-db psql -U uaip_user -d uaip_scoping

# Show execution plan
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM sessions WHERE user_id = 'user123';

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables;
```

#### API Request Debugging
```bash
# Use curl with verbose output
curl -v -H "Authorization: bearer TOKEN" http://localhost:38937/api/v1/sessions

# Using Python requests library
python3 << 'EOF'
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
requests.get(
  "http://localhost:38937/api/v1/health",
  headers={"Authorization": "bearer TOKEN"}
)
EOF
```

### Getting Help

**Documentation:**
- Swagger UI: http://localhost:38937/docs
- ReDoc: http://localhost:38937/redoc
- Project Status: PROJECT_STATUS.md
- User Tutorial: USER_TUTORIAL.md

**Debug Information to Collect:**
1. Error message and stacktrace
2. Docker logs: `docker-compose logs`
3. Recent activity in database
4. System resource usage: `docker stats`
5. Network connectivity: `docker network inspect`

---

## Maintenance Checklist

### Weekly
- [ ] Verify API health endpoint responding
- [ ] Check error logs for issues
- [ ] Monitor disk space
- [ ] Verify backups are being created

### Monthly
- [ ] Review and archive logs
- [ ] Test disaster recovery procedure
- [ ] Update documentation
- [ ] Security review of access logs
- [ ] Capacity planning review

### Quarterly
- [ ] Security audit
- [ ] Dependency updates and patching
- [ ] Performance optimization
- [ ] User account review
- [ ] Compliance audit

### Annually
- [ ] Major version upgrades
- [ ] Full system security assessment
- [ ] Disaster recovery drill
- [ ] Capacity expansion planning
- [ ] Architecture review

---

**Last Updated:** October 26, 2025
**Version:** 1.0
**Maintained By:** DevOps/SRE Team
