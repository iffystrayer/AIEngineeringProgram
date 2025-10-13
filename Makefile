# ==============================================================================
# U-AIP Scoping Assistant - Makefile
# ==============================================================================

.PHONY: help build up down restart logs ps exec-app exec-db test clean

# Default target
.DEFAULT_GOAL := help

# ==============================================================================
# Docker Operations
# ==============================================================================

help: ## Show this help message
	@echo "U-AIP Scoping Assistant - Docker Commands"
	@echo "=========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker compose build --no-cache

up: ## Start all services
	docker compose up -d
	@echo "✅ Services started!"
	@echo "Database: localhost:15432"
	@echo "Run 'make logs' to view logs"

down: ## Stop all services
	docker compose down
	@echo "✅ Services stopped"

restart: down up ## Restart all services

logs: ## View logs (all services)
	docker compose logs -f

logs-app: ## View application logs only
	docker compose logs -f uaip-app

logs-db: ## View database logs only
	docker compose logs -f uaip-db

ps: ## Show running containers
	docker compose ps

# ==============================================================================
# Container Access
# ==============================================================================

exec-app: ## Open shell in application container
	docker compose exec uaip-app bash

exec-db: ## Open psql in database container
	docker compose exec uaip-db psql -U uaip_user -d uaip_scoping

# ==============================================================================
# Application Commands
# ==============================================================================

cli: ## Run CLI command (usage: make cli CMD="start 'Project Name'")
	docker compose exec uaip-app python -m src.cli.main $(CMD)

start: ## Start a new session (usage: make start PROJECT="Project Name")
	docker compose exec uaip-app python -m src.cli.main start "$(PROJECT)"

list: ## List sessions
	docker compose exec uaip-app python -m src.cli.main list

resume: ## Resume session (usage: make resume SESSION_ID=xxx)
	docker compose exec uaip-app python -m src.cli.main resume $(SESSION_ID)

# ==============================================================================
# Database Operations
# ==============================================================================

db-init: ## Initialize database schema
	docker compose exec uaip-db psql -U uaip_user -d uaip_scoping -f /docker-entrypoint-initdb.d/01-init.sql

db-reset: ## Reset database (WARNING: destroys all data)
	docker compose down -v
	docker compose up -d uaip-db
	@echo "⚠️  Database reset complete"

db-backup: ## Backup database
	docker compose exec uaip-db pg_dump -U uaip_user uaip_scoping > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up"

db-restore: ## Restore database (usage: make db-restore FILE=backup.sql)
	docker compose exec -T uaip-db psql -U uaip_user -d uaip_scoping < $(FILE)
	@echo "✅ Database restored"

# ==============================================================================
# Development
# ==============================================================================

test: ## Run tests in container
	docker compose exec uaip-app python -m pytest tests/ -v

test-integration: ## Run integration tests
	docker compose exec uaip-app python -m pytest tests/integration/ -v

shell: exec-app ## Alias for exec-app

# ==============================================================================
# Cleanup
# ==============================================================================

clean: ## Remove all containers, volumes, and images
	docker compose down -v --rmi all
	@echo "✅ Cleanup complete"

prune: ## Remove unused Docker resources
	docker system prune -f
	@echo "✅ Prune complete"

# ==============================================================================
# Health Checks
# ==============================================================================

health: ## Check service health
	@echo "Checking service health..."
	@docker compose ps
	@echo ""
	@echo "Database health:"
	@docker compose exec uaip-db pg_isready -U uaip_user -d uaip_scoping || echo "❌ Database not ready"
	@echo ""
	@echo "Application health:"
	@docker compose exec uaip-app python -c "print('✅ Application container running')" || echo "❌ Application not ready"

# ==============================================================================
# Monitoring
# ==============================================================================

stats: ## Show container stats
	docker stats --no-stream uaip-db uaip-app

inspect-db: ## Inspect database container
	docker inspect uaip-db

inspect-app: ## Inspect application container
	docker inspect uaip-app
