# GearGo Docker Makefile

.PHONY: help build up down restart logs shell migrate collectstatic superuser setup test clean

# Default target
help:
	@echo "GearGo Docker Management Commands:"
	@echo ""
	@echo "  build        - Build Docker images"
	@echo "  up           - Start all services"
	@echo "  down         - Stop all services"
	@echo "  restart      - Restart all services"
	@echo "  logs         - Show logs from all services"
	@echo "  shell        - Open shell in web container"
	@echo "  migrate      - Run database migrations"
	@echo "  collectstatic - Collect static files"
	@echo "  superuser    - Create Django superuser"
	@echo "  setup        - Initial setup (migrate + collectstatic + setup data)"
	@echo "  test         - Run tests"
	@echo "  clean        - Remove containers, images, and volumes"
	@echo "  reset        - Clean everything and start fresh"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# Show logs from all services
logs:
	docker-compose logs -f

# Show logs from specific service
logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

logs-celery:
	docker-compose logs -f celery

# Open shell in web container
shell:
	docker-compose exec web python manage.py shell

# Run database migrations
migrate:
	docker-compose exec web python manage.py migrate

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Create Django superuser
superuser:
	docker-compose exec web python manage.py createsuperuser

# Setup initial data
setup-data:
	docker-compose exec web python manage.py setup_initial_data

# Setup email templates
setup-email:
	docker-compose exec web python manage.py setup_email_templates

# Initial setup (migrate + collectstatic + setup data)
setup: migrate collectstatic setup-data setup-email
	@echo "Initial setup completed!"

# Run tests
test:
	docker-compose exec web python manage.py test

# Remove containers, images, and volumes
clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Reset everything and start fresh
reset: clean build up setup
	@echo "Fresh start completed!"

# Quick development commands
dev-up:
	docker-compose up -d db redis
	@echo "Database and Redis started. Run 'make dev-web' to start Django server."

dev-web:
	docker-compose up web

# Production-like commands
prod-build:
	docker-compose -f docker-compose.yml build --no-cache

prod-up:
	docker-compose -f docker-compose.yml up -d

# Database commands
db-backup:
	docker-compose exec db pg_dump -U geargo_user geargo_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore:
	@echo "Usage: make db-restore FILE=backup_file.sql"
	docker-compose exec -T db psql -U geargo_user geargo_db < $(FILE)

# Health check
health:
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "Database connection test:"
	@docker-compose exec web python -c "import psycopg2; conn = psycopg2.connect('postgresql://geargo_user:geargo_password@db:5432/geargo_db'); print('✅ Database connection successful')"
