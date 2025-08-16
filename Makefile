include .env

DOCKER_IMAGE_NAME="${COMPOSE_PROJECT_NAME}-miner"


.PHONY: ps img up down down-fast restart hard-restart reset reset-fast logs exec stats env clean

ps:
	docker ps -a

img:
	docker images

up:
	docker compose up -d

down:
	docker compose down

down-fast:
	docker compose down --timeout 2

restart:
	docker compose down --timeout 2 && docker compose up -d

hard-restart:
	docker compose down && docker compose up -d

reset:
	docker compose down && docker rmi ${DOCKER_IMAGE_NAME} && docker compose up -d

reset-fast:
	docker compose down --timeout 2 && docker rmi ${DOCKER_IMAGE_NAME} && docker compose up -d

logs:
	docker logs lnmarkets-bot

logs-watch:
	docker logs -f lnmarkets-bot

exec:
	docker exec -it lnmarkets-bot bash

stats:
	docker stats lnmarkets-bot

env:
	docker exec lnmarkets-bot env

clean:
	docker rmi ${DOCKER_IMAGE_NAME}
