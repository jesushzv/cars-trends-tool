# Makefile for Cars Trends Tool
# Provides convenient commands for testing, Docker, and deployment

.PHONY: help test test-local test-ci test-ci-debug clean

help:
	@echo "Cars Trends Tool - Available Commands:"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run tests locally (quick)"
	@echo "  make test-ci       - Run tests in Docker (matches CI environment)"
	@echo "  make test-ci-debug - Open interactive shell in test container"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build all Docker images"
	@echo "  make docker-up     - Start all services with Docker Compose"
	@echo "  make docker-down   - Stop all services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove test artifacts and caches"

# Local testing (fast, but may have environment differences)
test test-local:
	@echo "🧪 Running tests locally..."
	cd backend && pytest --tb=short -v

# CI environment testing (slower, but matches GitHub Actions)
test-ci:
	@echo "🐳 Building test Docker image (matching CI environment)..."
	docker build -f Dockerfile.test -t cars-trends-test .
	@echo ""
	@echo "🧪 Running tests in Docker container..."
	docker run --rm cars-trends-test

# Interactive debugging in CI environment
test-ci-debug:
	@echo "🐳 Building test Docker image..."
	docker build -f Dockerfile.test -t cars-trends-test .
	@echo ""
	@echo "🔍 Opening interactive shell in test container..."
	@echo "   (Run 'pytest' inside to test, 'exit' to quit)"
	docker run --rm -it cars-trends-test /bin/bash

# Docker Compose commands
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost"
	@echo "   Backend:  http://localhost:8000"

docker-down:
	@echo "🛑 Stopping services..."
	docker-compose down

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"

