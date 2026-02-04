# WatchWish API Documentation

Base URL: `http://localhost:8000/api/`

## Authentication

Currently, the API does not require authentication. For production, consider adding:
- Token authentication
- OAuth2
- API keys

## Endpoints

### Movies

#### List All Movies

```
GET /api/movies/
```

**Query Parameters:**
- `page` (int): Page number
- `search` (string): Search in title, original_title, overview, tagline
- `year` (int): Filter by release year
- `year_min` (int): Minimum release year
- `year_max` (int): Maximum release year
- `rating_min` (float): Minimum rating
- `rating_max` (float): Maximum rating
- `genre` (string): Filter by genre name
- `ordering` (string): Sort by field (e.g., `-popularity`, `vote_average`)

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/movies/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Movie",
      "release_year": 2024,
      "vote_average": 8.5,
      "popularity": 150.0,
      "poster_path": "/path/to/poster.jpg",
      "genre_names": ["Action", "Drama"],
      "overview": "Movie description..."
    }
  ]
}
```

#### Get Single Movie

```
GET /api/movies/{id}/
```

**Response:**
```json
{
  "id": 1,
  "title": "The Movie",
  "original_title": "Original Title",
  "tagline": "The best movie ever",
  "overview": "Full description...",
  "release_date": "2024-01-01",
  "release_year": 2024,
  "status": "Released",
  "runtime": 120,
  "vote_average": 8.5,
  "vote_count": 1000,
  "popularity": 150.0,
  "budget": 10000000,
  "revenue": 50000000,
  "profit": 40000000,
  "genres": [
    {"id": 28, "name": "Action"}
  ],
  "genre_names": ["Action"],
  "original_language": "en",
  "spoken_languages": [
    {"iso_639_1": "en", "name": "English"}
  ],
  "production_companies": [
    {"id": 1, "name": "Studio"}
  ],
  "production_countries": [
    {"iso_3166_1": "US", "name": "United States"}
  ],
  "imdb_id": "tt1234567",
  "tmdb_id": 12345,
  "poster_path": "/path/to/poster.jpg",
  "backdrop_path": "/path/to/backdrop.jpg",
  "homepage": "https://movie.com",
  "keywords": ["action", "thriller"],
  "adult": false,
  "video": false,
  "cast": [
    {
      "actor": {
        "id": 1,
        "name": "Actor Name",
        "tmdb_id": 123,
        "profile_path": "/path/to/profile.jpg",
        "gender": 2
      },
      "character": "Character Name",
      "order": 0
    }
  ],
  "directors": [
    {
      "director": {
        "id": 1,
        "name": "Director Name",
        "tmdb_id": 456,
        "profile_path": "/path/to/profile.jpg"
      }
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Movie

```
POST /api/movies/
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "New Movie",
  "original_title": "Original Title",
  "release_date": "2024-06-01",
  "release_year": 2024,
  "overview": "Description",
  "vote_average": 7.5,
  "popularity": 50.0,
  "budget": 5000000,
  "revenue": 15000000,
  "runtime": 105,
  "genres": [{"id": 28, "name": "Action"}],
  "imdb_id": "tt9999999",
  "tmdb_id": 99999
}
```

#### Update Movie

```
PUT /api/movies/{id}/
Content-Type: application/json
```

```
PATCH /api/movies/{id}/
Content-Type: application/json
```

#### Delete Movie

```
DELETE /api/movies/{id}/
```

#### Custom Actions

##### Get Statistics

```
GET /api/movies/statistics/
```

**Response:**
```json
{
  "total_movies": 1000,
  "average_rating": 6.8,
  "total_budget": 1000000000,
  "total_revenue": 5000000000,
  "movies_by_year": [
    {"release_year": 2024, "count": 50},
    {"release_year": 2023, "count": 120}
  ]
}
```

##### Get Top Rated Movies

```
GET /api/movies/top_rated/?limit=10
```

##### Get Most Popular Movies

```
GET /api/movies/most_popular/?limit=10
```

##### Get Highest Grossing Movies

```
GET /api/movies/highest_grossing/?limit=10
```

### Directors

#### List All Directors

```
GET /api/directors/
```

**Query Parameters:**
- `page` (int): Page number
- `search` (string): Search by name
- `ordering` (string): Sort by field

**Response:**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Director Name",
      "tmdb_id": 123,
      "profile_path": "/path/to/profile.jpg"
    }
  ]
}
```

#### Get Single Director

```
GET /api/directors/{id}/
```

#### Create Director

```
POST /api/directors/
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Director",
  "tmdb_id": 789,
  "profile_path": "/path/to/profile.jpg"
}
```

#### Update Director

```
PUT /api/directors/{id}/
PATCH /api/directors/{id}/
```

#### Delete Director

```
DELETE /api/directors/{id}/
```

### Actors

#### List All Actors

```
GET /api/actors/
```

**Query Parameters:**
- `page` (int): Page number
- `search` (string): Search by name
- `ordering` (string): Sort by field

**Response:**
```json
{
  "count": 200,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Actor Name",
      "tmdb_id": 456,
      "profile_path": "/path/to/profile.jpg",
      "gender": 2
    }
  ]
}
```

#### Get Single Actor

```
GET /api/actors/{id}/
```

#### Create Actor

```
POST /api/actors/
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Actor",
  "tmdb_id": 999,
  "profile_path": "/path/to/profile.jpg",
  "gender": 1
}
```

#### Update Actor

```
PUT /api/actors/{id}/
PATCH /api/actors/{id}/
```

#### Delete Actor

```
DELETE /api/actors/{id}/
```

## Response Codes

- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Pagination

All list endpoints are paginated with 20 items per page by default.

**Pagination Fields:**
- `count`: Total number of items
- `next`: URL to next page
- `previous`: URL to previous page
- `results`: Array of items

## Filtering Examples

```bash
# Get movies from 2024
curl "http://localhost:8000/api/movies/?year=2024"

# Get movies between 2020-2024
curl "http://localhost:8000/api/movies/?year_min=2020&year_max=2024"

# Get highly rated movies
curl "http://localhost:8000/api/movies/?rating_min=8.0"

# Search for movies
curl "http://localhost:8000/api/movies/?search=action"

# Sort by popularity (descending)
curl "http://localhost:8000/api/movies/?ordering=-popularity"

# Combine filters
curl "http://localhost:8000/api/movies/?year=2024&rating_min=7.0&ordering=-vote_average"
```

## Using with cURL

```bash
# Get all movies
curl http://localhost:8000/api/movies/

# Get single movie
curl http://localhost:8000/api/movies/1/

# Create movie
curl -X POST http://localhost:8000/api/movies/ \
  -H "Content-Type: application/json" \
  -d '{"title": "New Movie", "release_year": 2024}'

# Update movie
curl -X PATCH http://localhost:8000/api/movies/1/ \
  -H "Content-Type: application/json" \
  -d '{"vote_average": 9.0}'

# Delete movie
curl -X DELETE http://localhost:8000/api/movies/1/
```

## Using with Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get movies
response = requests.get(f"{BASE_URL}/movies/")
movies = response.json()

# Create movie
movie_data = {
    "title": "New Movie",
    "release_year": 2024,
    "vote_average": 8.0
}
response = requests.post(f"{BASE_URL}/movies/", json=movie_data)
new_movie = response.json()
```

## Using with JavaScript

```javascript
const BASE_URL = "http://localhost:8000/api";

// Get movies
fetch(`${BASE_URL}/movies/`)
  .then(response => response.json())
  .then(data => console.log(data));

// Create movie
fetch(`${BASE_URL}/movies/`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    title: "New Movie",
    release_year: 2024,
    vote_average: 8.0
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Implement rate limiting
- Add authentication
- Use caching

## CORS

CORS is enabled for:
- http://localhost:3000
- http://localhost:8000

Update `config/settings.py` to add more origins.
