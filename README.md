# WatchWish

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.11-green.svg)
![MongoDB](https://img.shields.io/badge/mongodb-latest-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A modern movie recommendation platform built with Django and MongoDB, featuring intelligent movie suggestions powered by machine learning algorithms.

## 📋 Project Overview

WatchWish is a comprehensive movie recommendation system that helps users discover films tailored to their preferences. The platform leverages a dual-database architecture combining Django's robust authentication system with MongoDB's flexible document storage for movie data. Built with scalability and performance in mind, WatchWish provides a seamless experience for movie enthusiasts looking for their next favorite film.

### Key Features

- **Intelligent Recommendations**: ML-powered movie suggestions based on user preferences
- **Flexible Movie Database**: Store and retrieve movie data with MongoDB's schema-less design
- **Secure Authentication**: Django's built-in auth system for user management
- **RESTful API**: Clean API endpoints for movie operations (CRUD)
- **Docker Support**: Containerized deployment for consistent environments
- **Advanced Search**: Filter movies by genre, year, rating, and more

## 🏗️ Architecture

WatchWish employs a unique dual-database architecture that separates concerns and optimizes each database for its specific use case:

### Dual-Database Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      Django Application                      │
├──────────────────────────┬──────────────────────────────────┤
│   Django Auth/Admin      │      Movies Application          │
│   (SQLite Database)      │      (MongoDB Database)          │
├──────────────────────────┼──────────────────────────────────┤
│ - User accounts          │ - Movie documents                │
│ - Permissions            │ - Ratings & reviews              │
│ - Sessions               │ - Recommendations                │
│ - Admin interface        │ - Genre classifications          │
└──────────────────────────┴──────────────────────────────────┘
```

### Component Breakdown

1. **SQLite (Default Database)**
   - Handles Django's authentication and authorization
   - Manages admin interface data
   - Stores user sessions and permissions
   - Configured via Django ORM

2. **MongoDB (Movies Database)**
   - Stores movie documents with flexible schemas
   - Connected via PyMongo (direct driver, not ORM)
   - Handles high-volume movie data efficiently
   - Supports complex queries and aggregations

3. **Connection Layer**
   - `backend/movies/db.py`: MongoDB connection utilities
   - `backend/movies/services.py`: Business logic and CRUD operations
   - Environment-based configuration for production flexibility

## 🚀 Technology Stack

### Backend Framework
- **Django 5.2.11** - High-level Python web framework
- **Python 3.11** - Core programming language

### Databases
- **SQLite** - Default Django database for auth/admin
- **MongoDB** - NoSQL database for movies data
- **PyMongo 4.16.0** - Official MongoDB driver for Python

### Machine Learning & Data Processing
- **scikit-learn 1.8.0** - ML algorithms for recommendations
- **pandas 3.0.0** - Data manipulation and analysis
- **numpy 2.4.2** - Numerical computing
- **scipy 1.17.0** - Scientific computing

### DevOps & Deployment
- **Docker** - Containerization platform
- **Docker Compose** - Multi-container orchestration

### Additional Dependencies
- **python-dotenv 1.2.1** - Environment variable management
- **requests 2.32.5** - HTTP library
- **dnspython 2.8.0** - DNS toolkit for MongoDB connections

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized setup)
- MongoDB (for local development without Docker)

### Docker Setup (Recommended)

The fastest way to get started with WatchWish:

```bash
# Clone the repository
git clone <repository-url>
cd watchwish

# Start the application with Docker Compose
docker-compose up

# The application will be available at http://localhost:8000
```

This will automatically:
- Build the Django application container
- Start a MongoDB container
- Run database migrations
- Launch the development server

### Local Development Setup

For development without Docker:

```bash
# Clone the repository
git clone <repository-url>
cd watchwish

# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create and activate virtual environment (Unix/macOS)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# Create a .env file in the root directory
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB_NAME=watchwish_db

# Run MongoDB (ensure MongoDB is running on localhost:27017)
# Windows: mongod
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod

# Navigate to backend directory
cd backend

# Run migrations for Django auth/admin database
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The application will be available at `http://localhost:8000`.

## 🎯 Usage

### API Endpoints

WatchWish provides a RESTful API for movie operations:

#### List Movies
```bash
GET /api/movies/
```
Query parameters:
- `limit` - Number of results to return
- `skip` - Number of results to skip (pagination)
- `genre` - Filter by genre
- `search` - Search in title and description

Example:
```bash
curl "http://localhost:8000/api/movies/?genre=Action&limit=10"
```

#### Create a Movie
```bash
POST /api/movies/create/
Content-Type: application/json

{
    "title": "Inception",
    "description": "A thief who steals corporate secrets...",
    "genre": "Sci-Fi",
    "release_year": 2010,
    "rating": 8.8
}
```

#### Get a Specific Movie
```bash
GET /api/movies/<movie_id>/
```

#### Update a Movie
```bash
PUT /api/movies/<movie_id>/update/
Content-Type: application/json

{
    "title": "Inception (Updated)",
    "rating": 9.0
}
```

#### Delete a Movie
```bash
DELETE /api/movies/<movie_id>/delete/
```

### Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` to manage users and permissions.

## ⚙️ Configuration

### Environment Variables

Configure the application using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_HOST` | MongoDB server host | `localhost` |
| `MONGODB_PORT` | MongoDB server port | `27017` |
| `MONGODB_DB_NAME` | Database name | `watchwish_db` |
| `MONGODB_USERNAME` | MongoDB username (optional) | `""` |
| `MONGODB_PASSWORD` | MongoDB password (optional) | `""` |

### MongoDB Settings

MongoDB configuration is defined in `backend/config/settings.py`:

```python
MONGODB_SETTINGS = {
    'host': os.getenv('MONGODB_HOST', 'localhost'),
    'port': int(os.getenv('MONGODB_PORT', 27017)),
    'db_name': os.getenv('MONGODB_DB_NAME', 'watchwish_db'),
    'username': os.getenv('MONGODB_USERNAME', ''),
    'password': os.getenv('MONGODB_PASSWORD', ''),
}
```

## 🧪 Testing

Run the test suite:

```bash
# Navigate to backend directory
cd backend

# Run all tests
python manage.py test

# Run tests for movies app only
python manage.py test movies

# Run tests with verbose output
python manage.py test --verbosity=2
```

## 📁 Project Structure

```
watchwish/
├── backend/
│   ├── config/              # Django project settings
│   │   ├── settings.py      # Main settings file
│   │   ├── urls.py          # Root URL configuration
│   │   └── wsgi.py          # WSGI application
│   ├── movies/              # Movies application
│   │   ├── db.py            # MongoDB connection utilities
│   │   ├── services.py      # Business logic & CRUD operations
│   │   ├── views.py         # API endpoints
│   │   ├── urls.py          # Movie URL routing
│   │   ├── models.py        # Django models (if any)
│   │   └── tests.py         # Test cases
│   └── manage.py            # Django management script
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── entrypoint.sh            # Container startup script
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## 🔧 Development

### Code Style

- Follow standard Django conventions
- PEP 8 compliance for Python code
- Keep code DRY (Don't Repeat Yourself)
- Write descriptive variable and function names

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes following existing patterns
3. Add tests for new functionality
4. Update documentation as needed
5. Submit pull request for review

## 🐳 Docker Details

### Services

The `docker-compose.yml` defines two services:

1. **web**: Django application
   - Builds from Dockerfile
   - Exposes port 8000
   - Depends on MongoDB service

2. **mongo**: MongoDB database
   - Uses official MongoDB image
   - Exposes port 27017
   - Data persists in Docker volume

### Container Commands

```bash
# Start services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up --build

# Execute commands in web container
docker-compose exec web python backend/manage.py migrate
docker-compose exec web python backend/manage.py createsuperuser
```

## 📊 Database Schema

### MongoDB Collections

#### movies
```json
{
    "_id": "ObjectId",
    "title": "string",
    "description": "string",
    "genre": "string",
    "release_year": "integer",
    "rating": "float",
    "director": "string (optional)",
    "cast": ["string"] "(optional)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django Software Foundation for the excellent web framework
- MongoDB team for the flexible NoSQL database
- scikit-learn community for ML tools

## 📞 Support

For issues, questions, or contributions, please open an issue on the project repository.

---

**Note**: This is a development setup. For production deployment, ensure you:
- Change `SECRET_KEY` in settings.py
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Set up proper MongoDB authentication
- Use a production-grade web server (Gunicorn, uWSGI)
- Configure HTTPS and security headers
