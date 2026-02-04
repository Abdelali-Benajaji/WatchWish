# WatchWish - Movie Dataset Management System

A Django-based movie dataset management system with MongoDB integration, containerized with Docker.

## Project Structure

```
WatchWish/
├── backend/              # Django project
│   ├── config/          # Django settings and configuration
│   ├── movies/          # Movies app
│   └── manage.py        # Django management script
├── data/                # Movie datasets storage
├── docker/              # Docker-related configurations
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Docker image definition
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose
- Git

## Tech Stack

- **Backend Framework**: Django 5.0
- **Database**: MongoDB
- **Containerization**: Docker & Docker Compose
- **Python**: 3.11

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd WatchWish
```

### 2. Build and run with Docker Compose

```bash
docker-compose up --build
```

The application will be available at:
- Django: http://localhost:8000
- MongoDB: localhost:27017

### 3. Run migrations (if needed)

```bash
docker-compose exec web python manage.py migrate
```

### 4. Create a superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

## Development

### Running Django commands

```bash
docker-compose exec web python manage.py <command>
```

### Accessing the MongoDB shell

```bash
docker-compose exec mongodb mongosh
```

### Viewing logs

```bash
docker-compose logs -f web
```

## Environment Configuration

Create a `.env` file in the root directory for environment variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
MONGO_DB_NAME=watchwish
MONGO_HOST=mongodb
MONGO_PORT=27017
```

## Project Components

### Backend (Django)

- **config/**: Main Django project settings
- **movies/**: Django app for movie management
  - Models for movie data
  - Views and templates
  - API endpoints

### Data

- Store your movie datasets (CSV, JSON, etc.) in the `data/` directory
- These files will be accessible from the Django container

## MongoDB Integration

This project uses `djongo` for Django-MongoDB integration, providing:
- Django ORM compatibility with MongoDB
- Native MongoDB document support
- Seamless model definitions

## Docker Services

- **web**: Django application
- **mongodb**: MongoDB database

## Git Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches

### Commit Convention
Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

## Tasks Progress (WISH-84)

- [x] Git & GitHub setup
- [x] Architecture du Dépôt
- [x] Configuration Docker
- [x] Gestion des dépendances
- [x] Setup Git & .gitignore

## License

[Your License Here]

## Contributors

- ABDELALI BEN-AJAJI
