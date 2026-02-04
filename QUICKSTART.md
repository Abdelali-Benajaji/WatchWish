# 🚀 WatchWish Quick Start

Get started with WatchWish in 5 minutes!

## Prerequisites

- Docker Desktop installed
- Git installed

## Setup in 5 Steps

### 1️⃣ Navigate to Project

```bash
cd WatchWish
```

### 2️⃣ Build & Start

```bash
docker-compose up --build -d
```

Wait for services to start (~30 seconds)

### 3️⃣ Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 4️⃣ Create Admin User

```bash
docker-compose exec web python manage.py createsuperuser
```

Follow prompts to create your admin account.

### 5️⃣ Access the Application

Open your browser:

- **Home**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api

## 🎬 Import Movie Data

Place your CSV file in the `data/` folder, then:

```bash
docker-compose exec web python manage.py import_movies /app/data/your_movies.csv
```

## 📊 Try the API

```bash
# Get all movies
curl http://localhost:8000/api/movies/

# Get top rated
curl http://localhost:8000/api/movies/top_rated/

# Get statistics
curl http://localhost:8000/api/movies/statistics/
```

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Access Django shell
docker-compose exec web python manage.py shell

# Access MongoDB shell
docker-compose exec mongodb mongosh watchwish
```

## 📚 More Information

- Full documentation: `README.md`
- Setup guide: `SETUP.md`
- API docs: `API_DOCUMENTATION.md`
- Git workflow: `GIT_GUIDE.md`

## 🐛 Troubleshooting

**Port already in use?**
```bash
# Change ports in docker-compose.yml
# Or kill the process:
lsof -ti:8000 | xargs kill -9
```

**MongoDB not connecting?**
```bash
# Wait a bit longer, then:
docker-compose restart web
```

**Need to reset everything?**
```bash
docker-compose down -v
docker-compose up --build -d
```

## ✅ You're Ready!

Start building with WatchWish! 🎉
