.PHONY: start stop rebuild bash

PROJECT_NAME := chirps_analysis# Project name variable
USER := $(shell whoami)

CONTAINER_NAME := $(PROJECT_NAME)_$(USER)



start:
	@echo "Starting containers using docker-compose with container name: $(CONTAINER_NAME)"
	CONTAINER_NAME=$(CONTAINER_NAME) PROJECT_NAME=$(PROJECT_NAME) docker compose -f docker/docker-compose.yml up -d

stop:
	@echo "Stopping containers using docker-compose with container name: $(CONTAINER_NAME)"
	CONTAINER_NAME=$(CONTAINER_NAME) docker compose -f docker/docker-compose.yml down 

rebuild:
	@echo "Rebuilding containers..."
	CONTAINER_NAME=$(CONTAINER_NAME) PROJECT_NAME=$(PROJECT_NAME) docker compose -f docker/docker-compose.yml down
	CONTAINER_NAME=$(CONTAINER_NAME) PROJECT_NAME=$(PROJECT_NAME) docker compose -f docker/docker-compose.yml build
	CONTAINER_NAME=$(CONTAINER_NAME) PROJECT_NAME=$(PROJECT_NAME) docker compose -f docker/docker-compose.yml up -d

update-deps:
	PROJECT_NAME=$(PROJECT_NAME) docker exec $(CONTAINER_NAME) uv pip install --system -r pyproject.toml

bash: 
	PROJECT_NAME=$(PROJECT_NAME) docker exec -it $(CONTAINER_NAME) bash

