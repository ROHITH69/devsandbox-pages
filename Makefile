.DEFAULT_GOAL := help
.PHONY: help validate build up down logs test screenshots clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n",$$1,$$2}'

validate: ## Static checks on site/ (HTML, links, required files)
	python scripts/validate.py

build: ## Build the container image
	docker compose build

up: ## Run the site at http://localhost:8080
	docker compose up -d --build

down: ## Stop and remove the container
	docker compose down

logs: ## Follow container logs
	docker compose logs -f web

test: validate up ## Validate, start the container, run HTTP smoke tests
	python scripts/smoke_test.py http://localhost:8080/

screenshots: up ## Capture screenshots into ./screenshots
	docker compose --profile tools run --rm screenshots

clean: ## Remove containers and the local image
	docker compose --profile tools down --rmi local --remove-orphans
