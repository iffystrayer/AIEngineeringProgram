# Docker Setup Guide

Complete guide for running U-AIP Scoping Assistant with Docker.

## Prerequisites

- Docker Engine 20.10+ and Docker Compose V2
- At least 2GB RAM available
- At least 5GB disk space

## Quick Start

### 1. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` and set your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

### 2. Start Services

```bash
# Start all services (database + application)
docker compose up -d

# Or use the Makefile
make up
```

### 3. Verify Services

```bash
# Check service status
docker compose ps

# Or use Makefile
make health
```

Expected output:
```
✅ Database: healthy
✅ Application: running
```

### 4. Use the CLI

```bash
# Interactive shell in app container
docker compose exec uaip-app bash

# Inside container, run CLI commands
python -m src.cli.main start "My Project"
python -m src.cli.main list
python -m src.cli.main --help

# Or directly from host (using Makefile)
make cli CMD="start 'Customer Churn Prediction'"
make list
```

## Architecture

### Services

1. **uaip-db** (PostgreSQL 16)
   - Port: 15432 (host) → 5432 (container)
   - Database: uaip_scoping
   - User: uaip_user
   - Auto-initializes schema from `database/init.sql`

2. **uaip-app** (Python 3.11)
   - Multi-stage build for optimized size
   - Non-root user for security
   - Persistent volumes for data/logs/charters

### Networks

- **uaip-network**: Bridge network (172.28.0.0/16)
- Services communicate using service names (e.g., `uaip-db`)

### Volumes

- **uaip-db-data**: PostgreSQL data persistence
- **uaip-app-data**: Application data
- **uaip-app-logs**: Application logs
- **uaip-app-charters**: Generated charter documents

## Common Operations

### Starting and Stopping

```bash
# Start services
make up

# Stop services (keeps data)
make down

# Restart services
make restart

# View logs
make logs
make logs-app  # Application only
make logs-db   # Database only
```

### Running CLI Commands

```bash
# Start new session
make start PROJECT="Customer Churn Model"

# List sessions
make list

# Resume session
make resume SESSION_ID=550e8400-e29b-41d4-a716-446655440000

# Custom command
make cli CMD="start --help"
```

### Database Operations

```bash
# Access PostgreSQL shell
make exec-db

# Backup database
make db-backup

# Restore database
make db-restore FILE=backup_20251012_103000.sql

# Reset database (WARNING: destroys data)
make db-reset
```

### Development

```bash
# Run tests in container
make test

# Run integration tests
make test-integration

# Open shell in app container
make shell
```

## Production Deployment

### 1. Security Hardening

Update `.env` with strong credentials:

```bash
DB_PASSWORD=$(openssl rand -base64 32)
```

### 2. Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  uaip-db:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M

  uaip-app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 3. Monitoring

Connect to global monitoring stack (Prometheus on port 60090):

```yaml
services:
  uaip-app:
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8000"
      - "prometheus.path=/metrics"
```

### 4. Backup Strategy

Automated daily backups:

```bash
# Add to crontab
0 2 * * * cd /path/to/project && make db-backup
```

## Troubleshooting

### Database Connection Issues

```bash
# Check database is healthy
docker compose exec uaip-db pg_isready -U uaip_user

# View database logs
make logs-db

# Verify connection from app
docker compose exec uaip-app python -c "
from src.database.connection import DatabaseConfig, DatabaseManager
import asyncio
async def test():
    config = DatabaseConfig(host='uaip-db', port=5432, database='uaip_scoping', user='uaip_user', password='changeme')
    db = DatabaseManager(config)
    await db.initialize()
    print('✅ Connected')
    await db.close()
asyncio.run(test())
"
```

### Application Errors

```bash
# Check application logs
make logs-app

# Enter container for debugging
make shell

# Check Python environment
docker compose exec uaip-app python --version
docker compose exec uaip-app pip list
```

### Port Conflicts

If port 15432 is already in use:

```bash
# Edit .env
DB_PORT=25432  # Use different 5-digit port

# Restart services
make restart
```

### Volume Issues

```bash
# List volumes
docker volume ls | grep uaip

# Inspect volume
docker volume inspect uaip-db-data

# Remove all volumes (WARNING: destroys data)
make clean
```

## Advanced Configuration

### Custom Network Subnet

Edit `docker-compose.yml`:

```yaml
networks:
  uaip-network:
    ipam:
      config:
        - subnet: 172.30.0.0/16
```

### Development Mode

Mount source code for hot reload:

```yaml
services:
  uaip-app:
    volumes:
      - ./src:/app/src:ro
```

### External Database

To use external PostgreSQL:

```yaml
# Remove uaip-db service
# Update uaip-app environment
environment:
  DB_HOST: external-db.example.com
  DB_PORT: 5432
```

## Maintenance

### Updating Images

```bash
# Pull latest base images
docker compose pull

# Rebuild application
make build

# Restart with new images
make restart
```

### Cleanup

```bash
# Remove stopped containers and unused images
make prune

# Complete cleanup (WARNING: destroys all data)
make clean
```

### Viewing Stats

```bash
# Container resource usage
make stats

# Detailed inspection
make inspect-app
make inspect-db
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker compose build

      - name: Start services
        run: docker compose up -d

      - name: Run tests
        run: make test

      - name: Cleanup
        run: make down
```

## Best Practices

1. **Always use `.env` file** - Never hardcode credentials
2. **Regular backups** - Automate with cron jobs
3. **Monitor logs** - Use `make logs` to watch for issues
4. **Health checks** - Run `make health` before operations
5. **Volume management** - Clean up old volumes periodically
6. **Security updates** - Rebuild images regularly
7. **Resource limits** - Set appropriate limits in production
8. **Network isolation** - Use custom networks for security

## Support

For issues or questions:
- Check logs: `make logs`
- Run health check: `make health`
- Review troubleshooting section above
- Open issue on GitHub

## Next Steps

After Docker setup:
- Configure monitoring integration (Prometheus port 60090)
- Set up automated backups
- Configure SSL/TLS if exposing externally
- Implement log aggregation (Loki port 60100)
- Deploy to production environment
