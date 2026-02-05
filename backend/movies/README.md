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

## API Endpoints

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
