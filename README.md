# WatchWish - Movie Recommendation Platform

A Django-based movie discovery and recommendation platform using MongoDB for data persistence and content-based recommendation algorithms.

## Overview

**WatchWish** helps users discover movies by providing personalized recommendations based on movie ratings. The platform combines collaborative and content-based filtering with a user-friendly web interface for searching, rating, and discovering similar movies.

### Tech Stack

- **Backend**: Django 5.2
- **Database**: MongoDB (via PyMongo) for movies, ratings, and recommendations
- **Authentication**: Django auth with SQLite
- **ML/Algorithms**: scikit-learn, pandas, numpy
- **Frontend**: Django templates with HTML/CSS/JavaScript

## Project Structure

```
WatchWish/
├── backend/
│   ├── config/              # Django project settings
│   │   ├── settings.py      # Database & middleware config
│   │   ├── urls.py          # Root URL routing
│   │   └── wsgi.py/asgi.py  # Application entry points
│   ├── movies/              # Main Django app
│   │   ├── models.py        # Data models
│   │   ├── views.py         # View handlers
│   │   ├── services.py      # Business logic (MovieService)
│   │   ├── db.py            # MongoDB connection utilities
│   │   ├── urls.py          # App URL routing
│   │   ├── templates/       # HTML templates
│   │   ├── static/          # CSS, JavaScript
│   │   └── management/commands/  # Custom Django commands
│   ├── manage.py            # Django CLI
│   └── db.sqlite3           # SQLite for Django auth/admin
├── data/                    # Data files (movies CSV, recommendations JSON)
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker MongoDB setup
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- MongoDB (local or Docker)
- pip (Python package manager)

### Step 1: Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure MongoDB

**Option A: Docker (Recommended)**
```bash
docker-compose up -d
```
MongoDB will run on `localhost:27017`

**Option B: Local MongoDB**
Ensure MongoDB is running on `localhost:27017`

### Step 4: Load Movie Data

```bash
python backend/manage.py load_movie_data
```

### Step 5: Create Django Admin User (Optional)

```bash
python backend/manage.py createsuperuser
```

### Step 6: Start Development Server

```bash
python backend/manage.py runserver
```

Access the app at `http://localhost:8000/`

## Database Configuration

MongoDB settings in `backend/config/settings.py`:

```python
MONGODB_SETTINGS = {
    'host': 'localhost',
    'port': 27017,
    'db_name': 'watchwish_db',
    'username': '',  # optional
    'password': '',  # optional
}
```

Override via environment variables:
- `MONGODB_HOST`
- `MONGODB_PORT`
- `MONGODB_DB_NAME`
- `MONGODB_USERNAME`
- `MONGODB_PASSWORD`

## Features

### 1. Movie Search
- Browse and search movies by title
- Full-text search across title, description, and genres
- Instant results with pagination

### 2. Movie Discovery
- View detailed movie information
- See genres, descriptions, and poster images
- Related movie recommendations

### 3. Personalized Recommendations
- Rate movies on a 5-star scale
- Get personalized recommendations based on ratings
- Uses collaborative and content-based filtering
- Two ML models (scikit-learn based) for enhanced accuracy

### 4. User Authentication
- Sign up and login
- Persistent user ratings and preferences
- Personalized recommendation feed

### 5. Movie Detail Page
- Full movie information with high-quality posters
- Rating interface (1-5 stars)
- "Similar Movies" recommendations
- Genre tags

## API Endpoints

### Frontend Routes
- `GET /` - Home/search page
- `GET /movie/<movie_id>/` - Movie detail page
- `GET /user-recommendations/` - Personalized recommendations
- `GET /accounts/signup/` - User registration
- `GET /accounts/login/` - User login

### API Endpoints
- `GET /api/movies/` - List movies (supports `?limit`, `?skip`, `?genre`, `?search`)
- `POST /api/movies/create/` - Create a movie
- `GET /api/movies/<movie_id>/` - Get movie details (by ObjectId or movieId)
- `PUT /api/movies/<movie_id>/update/` - Update a movie
- `DELETE /api/movies/<movie_id>/delete/` - Delete a movie
- `POST /api/movies/rate/` - Rate a movie (authenticated)

## Movie Data Model

### Movies Collection
```json
{
  "_id": "ObjectId",
  "movieId": 88466,
  "title": "Inception",
  "description": "A thief who steals corporate secrets...",
  "genres": "Action|Adventure|Sci-Fi",
  "poster_url": "https://...",
  "release_year": 2010,
  "rating": 8.8,
  "actors": "Leonardo DiCaprio|Ellen Page",
  "director": "Christopher Nolan"
}
```

### User Ratings Collection
```json
{
  "userId": 1000001,
  "movieId": 88466,
  "score": 5.0
}
```

### User Recommendations Collection
```json
{
  "userId": 1000001,
  "model": "collaborative_filtering",
  "recommendations": [
    {"movieId": 299534, "score": 0.95},
    {"movieId": 568124, "score": 0.92}
  ]
}
```

## Testing

Run tests with:
```bash
python backend/manage.py test
```

## Development

### File Descriptions

- **services.py** - Core business logic (MovieService class)
  - `get_movie()` - Fetch movie by ID (supports both ObjectId and numeric movieId)
  - `get_movie_by_title()` - Search by title
  - `get_recommendations()` - Get similar movies
  - `get_user_recommendations()` - Personalized recs
  - `add_user_rating()` - Save user ratings
  - `generate_live_recommendations()` - Content-based filtering

- **views.py** - Request handlers
  - `index()` - Home/search view
  - `movie_detail()` - Movie detail view
  - `user_recommendations()` - Recommendation feed
  - `rate_movie()` - Rate submission
  - `signup()` - Registration

- **db.py** - MongoDB utilities
  - Connection pooling
  - Collection getters

## Troubleshooting

### "InvalidId: '88466' is not a valid ObjectId"
The service now automatically handles both MongoDB ObjectIds and numeric dataset movieIds. Ensure you're using the latest `services.py`.

### MongoDB Connection Error
- Check MongoDB is running: `mongo --version`
- For Docker: `docker ps` to verify container is up
- Check MONGODB_SETTINGS in settings.py

### No Recommendations
- Ensure user has rated at least one movie
- Check user_ratings collection has entries
- Verify recommendation algorithm has data

## Contributing

- Follow Django conventions
- Add tests for new features
- Update this README for significant changes

## License

WatchWish © 2026