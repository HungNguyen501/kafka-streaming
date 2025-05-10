ProjectName := kafka-streaming

docker-compose-up:
	@docker compose -f docker-compose.yaml up -d

docker-compose-down:
	@docker compose -f docker-compose.yaml down --volumes --remove-orphans

.DEFAULT_GOAL := help
.PHONY: help
all: help
help: Makefile
	@echo $(ProjectName)