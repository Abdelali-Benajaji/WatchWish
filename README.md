# Movies App - MongoDB Integration

This app uses PyMongo to interact with MongoDB for storing and managing movie data, while Django auth/admin uses SQLite.

## Architecture

- **Django Auth/Admin**: Uses SQLite (db.sqlite3)
- **Movies Data**: Uses MongoDB via PyMongo
- **Database Connection**: Direct PyMongo connection (no ORM)

## Files

- `db.py`: MongoDB connection utilities
- `services.py`: MovieService class with CRUD operations
- `views.py`: API endpoints for movie operations
- `urls.py`: URL routing for movie endpoints

## Configuration

MongoDB settings are configured in `backend/config/settings.py`:

```python
MONGODB_SETTINGS = {
    'host': 'localhost',
    'port': 27017,
    'db_name': 'watchwish_db',
    'username': '',  # optional
    'password': '',  # optional
}
```

These can be overridden using environment variables:
- `MONGODB_HOST`
- `MONGODB_PORT`
- `MONGODB_DB_NAME`
- `MONGODB_USERNAME`
- `MONGODB_PASSWORD`

## Movie Recommendation Feature

### Setup Instructions

1. Load the movie data into MongoDB:
```bash
python backend/manage.py load_movie_data
```

2. Start the Django development server:
```bash
python backend/manage.py runserver
```

3. Open your browser and navigate to `http://localhost:8000/`

### Features

- **Movie Search**: Enter a movie title in the search box at the index page
- **Recommendations**: Get 5 similar movie recommendations based on genre matching
- **Genre Display**: View genres for each movie as color-coded tags

### How It Works

The recommendation system:
1. Searches for the entered movie title in the MongoDB database
2. Extracts the genres of the searched movie
3. Finds other movies with overlapping genres
4. Ranks movies by the number of matching genres
5. Returns the top 5 most similar movies

## API Endpoints

- `GET /` - Movie recommendation interface (Django template)
- `GET /api/movies/` - List movies (supports ?limit, ?skip, ?genre, ?search)
- `POST /api/movies/create/` - Create a movie
- `GET /api/movies/<movie_id>/` - Get a specific movie
- `PUT /api/movies/<movie_id>/update/` - Update a movie
- `DELETE /api/movies/<movie_id>/delete/` - Delete a movie

## Movie Document Structure

```json
{
    "_id": "ObjectId",
    "title": "Movie Title",
    "description": "Movie description",
    "genre": "Action",
    "release_year": 2024,
    "rating": 8.5,
    ...
}
```