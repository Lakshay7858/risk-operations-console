.PHONY: help install test lint format clean up down

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

test: ## Run backend tests
	cd backend && pytest tests/ -v --tb=short

lint: ## Run linters
	cd backend && flake8 app/ --max-line-length 120

format: ## Format code
	cd backend && black app/ --line-length 120

up: ## Start all services with Docker
	docker-compose up --build -d

down: ## Stop all services
	docker-compose down

clean: ## Clean artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf frontend/node_modules frontend/build
