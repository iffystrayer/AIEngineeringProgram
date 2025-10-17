# U-AIP Administrator Guide

**Universal AI Project Charter Generator - System Administration**
Version 1.0 | Last Updated: October 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Installation and Deployment](#installation-and-deployment)
3. [Configuration Management](#configuration-management)
4. [Security and Access Control](#security-and-access-control)
5. [Monitoring and Observability](#monitoring-and-observability)
6. [Database Management](#database-management)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance and Updates](#maintenance-and-updates)
10. [Performance Tuning](#performance-tuning)

---

## System Overview

### Architecture Components

U-AIP is a containerized Python application with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                         U-AIP System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   CLI/API    │────▶│ Orchestrator │────▶│  Stage      │ │
│  │   Interface  │     │    Agent     │     │  Agents     │ │
│  └──────────────┘     └──────────────┘     │  (1-5)      │ │
│         │                     │             └─────────────┘ │
│         │                     ▼                     │        │
│         │            ┌──────────────┐              │        │
│         │            │ Conversation │              │        │
│         │            │   Engine     │◀─────────────┘        │
│         │            └──────────────┘                       │
│         │                     │                              │
│         ▼                     ▼                              │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │  PostgreSQL  │     │  LLM Router  │────▶│  External   │ │
│  │   Database   │     │              │     │  LLM APIs   │ │
│  └──────────────┘     └──────────────┘     └─────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘

External Monitoring:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Prometheus  │  │   Grafana    │  │     Loki     │
│  (Metrics)   │  │ (Dashboards) │  │    (Logs)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Application** | Python | 3.11+ | Core logic |
| **Web Framework** | FastAPI | 0.104+ | API endpoints |
| **Database** | PostgreSQL | 15+ | Session storage |
| **Containerization** | Docker | 24.0+ | Deployment |
| **Orchestration** | Docker Compose | 2.20+ | Multi-container |
| **Metrics** | Prometheus | 2.45+ | Monitoring |
| **Logging** | Loki | 2.9+ | Log aggregation |
| **Dashboards** | Grafana | 10.0+ | Visualization |
| **LLM Integration** | OpenAI/Anthropic/etc | Various | AI capabilities |

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 20 GB SSD
- **Network**: 100 Mbps
- **OS**: Linux (Ubuntu 22.04+), macOS 12+, Windows 11 with WSL2

#### Recommended Requirements (Production)
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB SSD (faster I/O)
- **Network**: 1 Gbps
- **OS**: Ubuntu 22.04 LTS or RHEL 9

#### Ports Used

| Port | Service | Purpose | External? |
|------|---------|---------|-----------|
| 10000 | U-AIP API | Main application | Yes |
| 60543 | PostgreSQL | Database | No (internal) |
| 60090 | Prometheus | Metrics collection | Admin only |
| 60001 | Grafana | Monitoring dashboards | Admin only |
| 60100 | Loki | Log aggregation | Admin only |

**IMPORTANT**: Ports 8000, 3000, and all 4-digit ports are RESERVED and must NOT be used.

---

## Installation and Deployment

### Prerequisites

1. **Install Docker and Docker Compose**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# RHEL/CentOS
sudo yum install -y docker docker-compose-plugin

# macOS (via Homebrew)
brew install docker docker-compose

# Verify installation
docker --version
docker compose version
```

2. **Install Python 3.11+ (for local development)**

```bash
# Ubuntu/Debian
sudo apt-get install -y python3.11 python3.11-venv

# macOS
brew install python@3.11

# Verify
python3.11 --version
```

3. **Install uv (Python package manager)**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

### Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/uaip.git
cd uaip
```

#### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**

```bash
# Application Settings
APP_NAME=U-AIP
APP_VERSION=1.0.0
ENVIRONMENT=production  # development, staging, production
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=60543
POSTGRES_DB=uaip
POSTGRES_USER=uaip_user
POSTGRES_PASSWORD=<CHANGE_THIS_SECURE_PASSWORD>

# LLM Configuration
LLM_PROVIDER=openai  # openai, anthropic, azure, gemini
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>  # if using Claude
LLM_MODEL=gpt-4  # or claude-3-opus, etc.
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_TIMEOUT_SECONDS=30

# Security Settings
SECRET_KEY=<GENERATE_SECURE_RANDOM_KEY>
JWT_SECRET=<GENERATE_SECURE_RANDOM_KEY>
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ORIGINS=https://your-domain.com

# Monitoring Configuration (Optional)
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=<SECURE_ADMIN_PASSWORD>
LOKI_RETENTION_DAYS=30

# Feature Flags
CONVERSATION_ENGINE_ENABLED=true
SECURITY_HARDENING_ENABLED=true
RATE_LIMITING_ENABLED=true
```

**Generate Secure Keys:**

```bash
# Generate random secret keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# uaip-app            Up                  0.0.0.0:10000->10000/tcp
# postgres            Up                  5432/tcp
# prometheus          Up                  0.0.0.0:60090->9090/tcp
# grafana             Up                  0.0.0.0:60001->3000/tcp
# loki                Up                  0.0.0.0:60100->3100/tcp

# Check logs
docker-compose logs -f uaip-app
```

#### 4. Initialize Database

```bash
# Run database migrations
docker exec -it uaip-app python -m alembic upgrade head

# Verify database schema
docker exec -it postgres psql -U uaip_user -d uaip -c "\dt"
```

#### 5. Verify Installation

```bash
# Health check
curl http://localhost:10000/health

# Expected response:
# {"status": "healthy", "database": "connected", "llm": "available"}

# API documentation
open http://localhost:10000/docs
```

### Production Deployment

#### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml uaip

# Check services
docker service ls

# Scale application
docker service scale uaip_app=3
```

#### Using Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/app.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment
kubectl get pods -n uaip
kubectl get svc -n uaip

# View logs
kubectl logs -f deployment/uaip-app -n uaip
```

#### Using Cloud Platforms

**AWS ECS:**
```bash
# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t uaip:latest .
docker tag uaip:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/uaip:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/uaip:latest

# Deploy ECS task
aws ecs update-service --cluster uaip-cluster --service uaip-service --force-new-deployment
```

**Google Cloud Run:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/uaip
gcloud run deploy uaip --image gcr.io/<project-id>/uaip --platform managed --region us-central1
```

**Azure Container Instances:**
```bash
# Create container group
az container create \
  --resource-group uaip-rg \
  --name uaip-app \
  --image <registry>/uaip:latest \
  --ports 10000 \
  --environment-variables POSTGRES_HOST=<db-host> POSTGRES_PASSWORD=<password>
```

---

## Configuration Management

### Application Configuration

Configuration managed via:
1. **Environment variables** (.env file)
2. **Configuration files** (config/*.yaml)
3. **Database settings** (runtime configuration)

#### LLM Provider Configuration

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...  # Optional
LLM_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1  # Default
```

**Anthropic Claude:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-opus-20240229
```

**Azure OpenAI:**
```bash
LLM_PROVIDER=azure
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
```

**Google Gemini:**
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=...
LLM_MODEL=gemini-pro
```

**Custom LLM Endpoint:**
```bash
LLM_PROVIDER=custom
CUSTOM_LLM_ENDPOINT=https://your-llm-api.com/v1/chat/completions
CUSTOM_LLM_API_KEY=...
LLM_MODEL=your-model-name
```

#### Quality and Security Configuration

```yaml
# config/conversation.yaml
conversation_engine:
  quality_threshold: 7.0  # 0-10 scale
  max_quality_attempts: 3  # Max follow-up loops
  timeout_seconds: 30  # LLM API timeout

security:
  max_question_length: 500  # characters
  max_response_length: 10000  # characters
  max_follow_up_length: 2000  # characters

  # Prompt injection detection patterns
  injection_patterns:
    - "ignore.*previous.*instructions"
    - "forget.*everything"
    - "system.*prompt"
    - "you.*are.*now"
    - "override"

rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst_size: 10
```

#### Stage Agent Configuration

```yaml
# config/stages.yaml
stage_agents:
  stage1:
    name: "Business Translation"
    question_groups: 4
    quality_threshold: 7.0
    max_attempts: 3

  stage2:
    name: "Success Criteria"
    quality_threshold: 7.5  # Higher for metrics
    max_attempts: 3

  stage3:
    name: "Data Assessment"
    quality_threshold: 7.0
    data_quality_threshold: 0.7  # Minimum acceptable

  stage4:
    name: "User Impact"
    quality_threshold: 7.0

  stage5:
    name: "Ethical Risk"
    quality_threshold: 8.0  # Highest for ethics
    governance_thresholds:
      halt: 5  # Critical risk level
      committee: 4  # High risk level
      revise: 3  # Medium risk level
```

### Database Configuration

#### Connection Pool Settings

```python
# config/database.py
DATABASE_CONFIG = {
    "min_pool_size": 5,
    "max_pool_size": 20,
    "pool_recycle": 3600,  # Recycle connections after 1 hour
    "pool_pre_ping": True,  # Test connections before use
    "echo": False,  # Set True for SQL debugging
    "connect_timeout": 10,
}
```

#### Schema Migrations

```bash
# Create new migration
docker exec -it uaip-app alembic revision --autogenerate -m "Description"

# Apply migrations
docker exec -it uaip-app alembic upgrade head

# Rollback one version
docker exec -it uaip-app alembic downgrade -1

# View migration history
docker exec -it uaip-app alembic history
```

---

## Security and Access Control

### Authentication and Authorization

#### User Management

```bash
# Create admin user
docker exec -it uaip-app python -m src.cli.admin create-user \
  --email admin@example.com \
  --role admin \
  --password <secure-password>

# List users
docker exec -it uaip-app python -m src.cli.admin list-users

# Deactivate user
docker exec -it uaip-app python -m src.cli.admin deactivate-user \
  --email user@example.com

# Reset password
docker exec -it uaip-app python -m src.cli.admin reset-password \
  --email user@example.com
```

#### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **User** | Create sessions, view own charters, export own data |
| **Reviewer** | View all charters, comment on charters |
| **Admin** | All user permissions + user management, system configuration |
| **SuperAdmin** | All admin permissions + database access, security settings |

#### API Authentication

**JWT Token-Based:**

```bash
# Get access token
curl -X POST http://localhost:10000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response:
# {"access_token": "eyJ...", "token_type": "bearer", "expires_in": 3600}

# Use token in requests
curl -H "Authorization: Bearer eyJ..." http://localhost:10000/api/sessions
```

**API Key-Based:**

```bash
# Generate API key for service accounts
docker exec -it uaip-app python -m src.cli.admin create-api-key \
  --name "CI/CD Pipeline" \
  --role service

# Use API key
curl -H "X-API-Key: <api-key>" http://localhost:10000/api/sessions
```

### Security Hardening

#### SSL/TLS Configuration

**Using Nginx Reverse Proxy:**

```nginx
# /etc/nginx/sites-available/uaip
server {
    listen 443 ssl http2;
    server_name uaip.example.com;

    ssl_certificate /etc/letsencrypt/live/uaip.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/uaip.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:10000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Firewall Rules

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH (admin only)
sudo ufw deny 10000/tcp  # Block direct app access
sudo ufw deny 60543/tcp  # Block database access
sudo ufw enable

# RHEL/CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload
```

#### Security Headers

```python
# Already configured in FastAPI app
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}
```

#### Secrets Management

**Using Docker Secrets (Swarm):**

```bash
# Create secret
echo "my-secret-password" | docker secret create postgres_password -

# Use in docker-compose.yml
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

**Using Kubernetes Secrets:**

```bash
# Create secret
kubectl create secret generic uaip-secrets \
  --from-literal=postgres-password=<password> \
  --from-literal=openai-api-key=<key> \
  -n uaip

# Reference in deployment
env:
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: uaip-secrets
        key: postgres-password
```

**Using HashiCorp Vault:**

```bash
# Store secrets
vault kv put secret/uaip/production \
  postgres_password=<password> \
  openai_api_key=<key>

# Retrieve in app
export POSTGRES_PASSWORD=$(vault kv get -field=postgres_password secret/uaip/production)
```

### Security Best Practices

1. **Regular Updates**
   ```bash
   # Update base images monthly
   docker pull python:3.11-slim
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Vulnerability Scanning**
   ```bash
   # Scan images for vulnerabilities
   docker scan uaip:latest

   # Scan dependencies
   pip install safety
   safety check --file requirements.txt
   ```

3. **Audit Logging**
   - All admin actions logged
   - Failed login attempts tracked
   - API access logged
   - Logs retained for 90 days (configurable)

4. **Data Encryption**
   - Database encryption at rest (PostgreSQL pgcrypto)
   - TLS 1.3 for data in transit
   - API keys hashed with bcrypt
   - Session tokens JWT with RS256

---

## Monitoring and Observability

### Prometheus Metrics

#### Available Metrics

**Application Metrics:**

```prometheus
# Session metrics
uaip_sessions_created_total{user_id, project_name}
uaip_sessions_completed_total{user_id}
uaip_sessions_failed_total{user_id, reason}
uaip_session_duration_seconds{user_id, project_name}

# Stage metrics
uaip_stage_completion_time_seconds{stage_number}
uaip_stage_attempts_total{stage_number, user_id}
uaip_stage_failures_total{stage_number, reason}

# Quality loop metrics
uaip_quality_loops_total{stage, question_number}
uaip_quality_scores{stage, question_number}
uaip_quality_escalations_total{stage, reason}

# Governance decisions
uaip_governance_decisions_total{decision}  # PROCEED, REVISE, HALT, etc.

# LLM API metrics
uaip_llm_requests_total{provider, model}
uaip_llm_latency_seconds{provider, model}
uaip_llm_errors_total{provider, error_type}
uaip_llm_tokens_used_total{provider, model, type}  # type=input/output

# Security metrics
uaip_prompt_injections_blocked_total{stage}
uaip_input_validation_failures_total{reason}
uaip_rate_limit_exceeded_total{user_id}

# Database metrics
uaip_database_connections_active
uaip_database_connections_total
uaip_database_query_duration_seconds{operation}
```

**System Metrics:**

```prometheus
# CPU and Memory
process_cpu_seconds_total
process_resident_memory_bytes

# HTTP requests
http_requests_total{method, path, status}
http_request_duration_seconds{method, path}

# Python runtime
python_gc_objects_collected_total{generation}
python_info{version}
```

#### Accessing Prometheus

```bash
# Open Prometheus UI
open http://localhost:60090

# Query examples
uaip_sessions_completed_total
rate(uaip_llm_requests_total[5m])
histogram_quantile(0.95, uaip_session_duration_seconds_bucket)
```

### Grafana Dashboards

#### Accessing Grafana

```bash
# Open Grafana
open http://localhost:60001

# Default credentials
Username: admin
Password: <GRAFANA_ADMIN_PASSWORD from .env>
```

#### Pre-configured Dashboards

1. **U-AIP Overview Dashboard**
   - Active sessions
   - Completion rate
   - Average session duration
   - Governance decision distribution

2. **Performance Dashboard**
   - Request latency (p50, p95, p99)
   - LLM API latency
   - Database query performance
   - Error rates

3. **Quality Metrics Dashboard**
   - Quality score distribution
   - Escalation rate by stage
   - Follow-up question frequency
   - User response quality trends

4. **Security Dashboard**
   - Prompt injection attempts
   - Input validation failures
   - Rate limiting events
   - Failed authentication attempts

5. **Infrastructure Dashboard**
   - CPU and memory usage
   - Container health
   - Database connections
   - Disk I/O

#### Creating Custom Dashboards

```json
// Example panel JSON
{
  "targets": [
    {
      "expr": "rate(uaip_sessions_completed_total[5m])",
      "legendFormat": "Completions/sec"
    }
  ],
  "title": "Session Completion Rate"
}
```

### Loki Log Aggregation

#### Accessing Logs

```bash
# Open Loki/Grafana Explore
open http://localhost:60001/explore

# LogQL query examples
{container="uaip-app"} |= "ERROR"
{container="uaip-app"} | json | level="error"
{container="uaip-app"} | json | user_id="123"
```

#### Log Levels

```python
# Application uses Python logging
DEBUG    # Development details
INFO     # Normal operations (session created, stage completed)
WARNING  # Quality escalations, retries
ERROR    # Failed operations, exceptions
CRITICAL # System failures, security incidents
```

#### Structured Logging

```python
# Logs are JSON-formatted for easy parsing
{
  "timestamp": "2025-10-17T10:30:00Z",
  "level": "INFO",
  "logger": "src.agents.orchestrator",
  "message": "Session created",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user@example.com",
  "project_name": "Customer Churn Prediction"
}
```

### Alerting

#### Prometheus Alertmanager

**Alert Rules:**

```yaml
# /etc/prometheus/alerts.yml
groups:
  - name: uaip_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(uaip_sessions_failed_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High session failure rate"
          description: "{{ $value }} sessions failing per second"

      # LLM API failures
      - alert: LLMAPIFailures
        expr: rate(uaip_llm_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "LLM API experiencing failures"
          description: "Provider {{ $labels.provider }} failing"

      # Database connection exhaustion
      - alert: DatabaseConnectionsHigh
        expr: uaip_database_connections_active / uaip_database_connections_total > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly exhausted"

      # Security incidents
      - alert: PromptInjectionAttempts
        expr: rate(uaip_prompt_injections_blocked_total[5m]) > 0.01
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Prompt injection attacks detected"
          description: "{{ $value }} attempts per second"
```

**Notification Channels:**

```yaml
# /etc/alertmanager/alertmanager.yml
global:
  slack_api_url: 'https://hooks.slack.com/services/xxx'

receivers:
  - name: 'slack-critical'
    slack_configs:
      - channel: '#uaip-alerts'
        title: 'U-AIP Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'email-admin'
    email_configs:
      - to: 'admin@example.com'
        from: 'alerts@uaip.io'
        smarthost: 'smtp.gmail.com:587'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<pagerduty-integration-key>'

route:
  group_by: ['alertname']
  receiver: 'slack-critical'

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true

    - match:
        severity: warning
      receiver: 'email-admin'
```

---

## Database Management

### Schema Overview

```sql
-- Core tables
sessions          -- User interview sessions
checkpoints       -- Stage completion snapshots
conversation_history  -- Q&A transcript
users             -- User accounts
api_keys          -- Service account tokens
audit_logs        -- Admin action audit trail

-- Deliverables tables
problem_statements       -- Stage 1 output
metric_alignment_matrix  -- Stage 2 output
data_quality_scorecards  -- Stage 3 output
user_contexts            -- Stage 4 output
ethical_risk_reports     -- Stage 5 output
ai_project_charters      -- Final output
```

### Backup Strategy

#### Automated Backups

```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-uaip-db.sh

# /usr/local/bin/backup-uaip-db.sh
#!/bin/bash
BACKUP_DIR="/var/backups/uaip"
DATE=$(date +%Y%m%d_%H%M%S)

docker exec postgres pg_dump -U uaip_user -Fc uaip > "$BACKUP_DIR/uaip_$DATE.dump"

# Retain last 30 days
find $BACKUP_DIR -name "uaip_*.dump" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/uaip_$DATE.dump" s3://uaip-backups/
```

#### Manual Backup

```bash
# Full database backup
docker exec postgres pg_dump -U uaip_user -Fc uaip > uaip_backup.dump

# Backup specific table
docker exec postgres pg_dump -U uaip_user -t sessions uaip > sessions_backup.sql

# Backup schema only
docker exec postgres pg_dump -U uaip_user -s uaip > schema_backup.sql
```

#### Restore from Backup

```bash
# Stop application
docker-compose stop uaip-app

# Restore database
docker exec -i postgres pg_restore -U uaip_user -d uaip -c < uaip_backup.dump

# Restart application
docker-compose start uaip-app

# Verify
docker exec -it uaip-app python -m src.cli.admin verify-db
```

### Database Maintenance

#### Vacuum and Analyze

```bash
# Auto-vacuum is enabled by default
# Manual vacuum (run monthly)
docker exec postgres psql -U uaip_user -d uaip -c "VACUUM ANALYZE;"

# Check bloat
docker exec postgres psql -U uaip_user -d uaip -c "
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

#### Index Maintenance

```bash
# Rebuild indexes (if needed)
docker exec postgres psql -U uaip_user -d uaip -c "REINDEX DATABASE uaip;"

# Check index usage
docker exec postgres psql -U uaip_user -d uaip -c "
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
"
```

#### Data Retention

```bash
# Archive old sessions (> 1 year)
docker exec -it uaip-app python -m src.cli.admin archive-sessions --older-than 365

# Delete archived sessions (> 3 years)
docker exec -it uaip-app python -m src.cli.admin delete-archived --older-than 1095

# Cleanup orphaned checkpoints
docker exec -it uaip-app python -m src.cli.admin cleanup-orphaned-data
```

---

## Backup and Recovery

### Disaster Recovery Plan

#### RPO and RTO Targets

- **RPO (Recovery Point Objective)**: 24 hours (daily backups)
- **RTO (Recovery Time Objective)**: 4 hours (restore + verify)

#### Recovery Procedures

**Scenario 1: Application Container Failure**

```bash
# Check container status
docker-compose ps

# Restart failed container
docker-compose restart uaip-app

# If restart fails, recreate
docker-compose up -d --force-recreate uaip-app

# Verify health
curl http://localhost:10000/health
```

**Scenario 2: Database Corruption**

```bash
# Stop application
docker-compose stop uaip-app

# Restore from latest backup
LATEST_BACKUP=$(ls -t /var/backups/uaip/*.dump | head -1)
docker exec -i postgres pg_restore -U uaip_user -d uaip -c < $LATEST_BACKUP

# Run migrations to ensure schema is current
docker exec -it uaip-app alembic upgrade head

# Restart application
docker-compose start uaip-app

# Verify data integrity
docker exec -it uaip-app python -m src.cli.admin verify-db
```

**Scenario 3: Complete System Failure**

```bash
# 1. Provision new server
# 2. Install Docker and Docker Compose
# 3. Clone repository
git clone https://github.com/your-org/uaip.git && cd uaip

# 4. Restore .env file from backup
scp backup-server:/secure-backups/.env .

# 5. Deploy containers
docker-compose up -d

# 6. Restore database
scp backup-server:/var/backups/uaip/latest.dump .
docker exec -i postgres pg_restore -U uaip_user -d uaip -c < latest.dump

# 7. Verify system
curl http://localhost:10000/health
docker-compose logs -f uaip-app
```

### High Availability Setup

**Multi-Node Deployment (Docker Swarm):**

```yaml
# docker-compose.ha.yml
version: '3.8'

services:
  app:
    image: uaip:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      placement:
        constraints:
          - node.role == worker
    networks:
      - uaip-network

  postgres:
    image: postgres:15-alpine
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.database == true
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: uaip
      POSTGRES_USER: uaip_user
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    secrets:
      - postgres_password
    networks:
      - uaip-network

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    deploy:
      replicas: 2
      placement:
        constraints:
          - node.role == worker
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    networks:
      - uaip-network

networks:
  uaip-network:
    driver: overlay

volumes:
  postgres-data:

secrets:
  postgres_password:
    external: true
```

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptom**: Container exits immediately

**Diagnosis**:
```bash
# Check logs
docker-compose logs uaip-app

# Common errors:
# - Database connection failed
# - LLM API key invalid
# - Port already in use
```

**Solutions**:
```bash
# Database not ready
docker-compose up -d postgres
sleep 10
docker-compose up -d uaip-app

# Port conflict
lsof -i :10000  # Find process using port
# Change APP_PORT in .env

# Invalid API key
# Update .env with valid key
docker-compose restart uaip-app
```

#### High Memory Usage

**Diagnosis**:
```bash
# Check container stats
docker stats uaip-app

# Check Python memory
docker exec uaip-app python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

**Solutions**:
```bash
# Increase container memory limit
# docker-compose.yml
services:
  app:
    mem_limit: 2g
    mem_reservation: 1g

# Restart with new limits
docker-compose up -d
```

#### Database Connection Pool Exhausted

**Symptom**: `FATAL: remaining connection slots are reserved`

**Solution**:
```bash
# Check active connections
docker exec postgres psql -U uaip_user -c "SELECT count(*) FROM pg_stat_activity;"

# Increase max connections
# docker-compose.yml
postgres:
  command: -c max_connections=200

# Or adjust pool size in app config
# config/database.py
max_pool_size: 50  # Reduce if needed
```

#### LLM API Timeouts

**Symptom**: Sessions stuck on specific questions

**Diagnosis**:
```bash
# Check LLM metrics
curl http://localhost:60090/api/v1/query?query=uaip_llm_latency_seconds

# Check logs for timeout errors
docker-compose logs uaip-app | grep "TimeoutError"
```

**Solutions**:
```bash
# Increase timeout
# .env
LLM_TIMEOUT_SECONDS=60

# Switch to faster model
LLM_MODEL=gpt-3.5-turbo  # Instead of gpt-4

# Use fallback provider
LLM_FALLBACK_PROVIDER=anthropic
ANTHROPIC_API_KEY=...

docker-compose restart uaip-app
```

### Debug Mode

```bash
# Enable debug logging
docker-compose down
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose up -d

# Follow logs
docker-compose logs -f uaip-app

# Disable when done
sed -i 's/LOG_LEVEL=DEBUG/LOG_LEVEL=INFO/' .env
docker-compose restart uaip-app
```

### Performance Profiling

```bash
# Enable profiling
docker exec -it uaip-app python -m cProfile -o profile.stats -m src.cli.main start --project-name "Test"

# Analyze profile
docker exec -it uaip-app python -m pstats profile.stats
# >>> sort cumulative
# >>> stats 20
```

---

## Maintenance and Updates

### Regular Maintenance Tasks

#### Daily
- Monitor Grafana dashboards for anomalies
- Review error logs (Loki)
- Check disk space usage

#### Weekly
- Review security alerts
- Check backup success
- Analyze slow queries

#### Monthly
- Update dependencies
- Review and rotate logs
- Database vacuum and analyze
- Review user access

#### Quarterly
- Security audit
- Update base images
- Review and update documentation
- Capacity planning

### Update Procedures

#### Application Updates

```bash
# 1. Backup current state
./scripts/backup-before-update.sh

# 2. Pull latest code
git fetch origin
git checkout v1.1.0  # Or specific version

# 3. Review changelog
cat CHANGELOG.md

# 4. Update dependencies
docker-compose build --no-cache

# 5. Run migrations
docker-compose up -d postgres
docker exec -it uaip-app alembic upgrade head

# 6. Deploy new version
docker-compose up -d uaip-app

# 7. Verify
curl http://localhost:10000/health
docker-compose logs -f uaip-app

# 8. Monitor for 24 hours

# 9. If issues, rollback
git checkout v1.0.0
docker-compose build
docker-compose up -d
```

#### Database Migrations

```bash
# Test migration in staging first
docker exec -it uaip-app alembic upgrade head --sql > migration.sql
# Review migration.sql

# Apply in production
docker exec -it uaip-app alembic upgrade head

# Verify
docker exec postgres psql -U uaip_user -d uaip -c "\dt"
```

---

## Performance Tuning

### Database Optimization

```sql
-- postgresql.conf tuning for production
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
```

### Application Tuning

```python
# Async worker pool
WORKER_COUNT = (CPU_CORES * 2) + 1

# Database connection pool
DB_POOL_SIZE = min(WORKER_COUNT * 2, 50)

# LLM request batching
LLM_BATCH_SIZE = 5
LLM_BATCH_TIMEOUT = 1.0  # seconds
```

### Caching Strategy

```python
# Redis cache (optional)
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour

# Cache LLM responses
CACHE_LLM_RESPONSES = True
LLM_CACHE_TTL = 86400  # 24 hours

# Cache stage validations
CACHE_VALIDATIONS = True
VALIDATION_CACHE_TTL = 3600
```

---

**Document Version**: 1.0
**Last Updated**: October 2025
**For Support**: support@uaip.io
**Documentation**: [https://docs.uaip.io](https://docs.uaip.io)
