# WatchWish Setup Guide

This guide will help you set up the WatchWish project locally.

## Prerequisites

Make sure you have the following installed:

- **Docker Desktop** (v20.10 or higher)
- **Docker Compose** (v2.0 or higher)
- **Git** (v2.30 or higher)

### Verify Installation

```bash
docker --version
docker-compose --version
git --version
```

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd WatchWish
```

### 2. Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` if needed (default values should work for local development).

### 3. Build Docker Images

```bash
docker-compose build
```

Or use the Makefile:

```bash
make build
```

### 4. Start Services

```bash
docker-compose up -d
```

Or:

```bash
make up
```

This will start:
- Django application on http://localhost:8000
- MongoDB on localhost:27017

### 5. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

Or:

```bash
make migrate
```

### 6. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

Or:

```bash
make createsuperuser
```

Follow the prompts to create an admin account.

### 7. Access the Application

- **Home Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Browser**: http://localhost:8000/api
- **Movies API**: http://localhost:8000/api/movies/

## Importing Movie Data

### Prepare Your Dataset

1. Place your CSV file in the `data/` directory
2. Ensure it has the required columns (see `data/README.md`)

### Import Command

```bash
docker-compose exec web python manage.py import_movies /app/data/your_file.csv
```

Or use the Makefile:

```bash
make import-movies FILE=data/your_file.csv
```

## Development Workflow

### Starting Services

```bash
make up
```

### Viewing Logs

```bash
make logs
```

### Stopping Services

```bash
make down
```

### Restarting Services

```bash
make restart
```

### Accessing Django Shell

```bash
make shell
```

### Accessing MongoDB Shell

```bash
make db-shell
```

### Running Tests

```bash
make test
```

## Common Issues and Solutions

### Issue: Port Already in Use

If port 8000 or 27017 is already in use:

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
lsof -ti:27017 | xargs kill -9
```

Or change the port in `docker-compose.yml`.

### Issue: Permission Denied

On Linux, you might need to run Docker commands with `sudo` or add your user to the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: MongoDB Connection Failed

Wait a few seconds for MongoDB to fully initialize, then restart the web service:

```bash
docker-compose restart web
```

### Issue: Import Fails

Check:
1. CSV file exists in `data/` directory
2. CSV has required columns
3. File encoding is UTF-8

## Project Structure

```
WatchWish/
├── backend/
│   ├── config/              # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── movies/              # Movies app
│   │   ├── management/      # Custom commands
│   │   ├── templates/       # HTML templates
│   │   ├── models.py        # Database models
│   │   ├── views.py         # API views
│   │   ├── serializers.py   # REST serializers
│   │   └── urls.py          # URL routing
│   └── manage.py
├── data/                    # Movie datasets
├── docker/                  # Docker configs
│   └── mongo-init/
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Docker image
├── Makefile                # Common commands
└── README.md
```

## Next Steps

1. Import your movie dataset
2. Explore the API at http://localhost:8000/api
3. Access the admin panel at http://localhost:8000/admin
4. Start building features!

## Need Help?

- Check the main README.md
- Review `data/README.md` for dataset requirements
- Check Docker logs: `make logs`
- Review Django logs in the container

## Cleaning Up

To remove all containers, volumes, and start fresh:

```bash
make clean
```

**Warning**: This will delete all data in the database!
