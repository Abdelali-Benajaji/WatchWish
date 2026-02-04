.PHONY: help build up down restart logs shell db-shell migrate makemigrations createsuperuser test clean

help:
	@echo "WatchWish - Available Commands"
	@echo "==============================="
	@echo "make build          - Build Docker images"
	@echo "make up             - Start all services"
	@echo "make down           - Stop all services"
	@echo "make restart        - Restart all services"
	@echo "make logs           - View logs"
	@echo "make shell          - Access Django shell"
	@echo "make db-shell       - Access MongoDB shell"
	@echo "make migrate        - Run migrations"
	@echo "make makemigrations - Create migrations"
	@echo "make createsuperuser- Create Django superuser"
	@echo "make test           - Run tests"
	@echo "make clean          - Remove containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services are running!"
	@echo "Django: http://localhost:8000"
	@echo "MongoDB: localhost:27017"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

db-shell:
	docker-compose exec mongodb mongosh watchwish

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	@echo "Removed all containers and volumes"

import-movies:
	@echo "Usage: make import-movies FILE=data/your_file.csv"
	@if [ -z "$(FILE)" ]; then \
		echo "Error: Please specify FILE=path/to/file.csv"; \
	else \
		docker-compose exec web python manage.py import_movies /app/$(FILE); \
	fi
