# Movie Datasets

Place your movie dataset files here.

## Supported Formats

- CSV (`.csv`)
- JSON (`.json`)
- Excel (`.xlsx`)

## Expected CSV Columns

For the import script to work properly, your CSV should include the following columns:

### Required Columns
- `title` - Movie title
- `release_date` - Release date (YYYY-MM-DD format)
- `vote_average` - Average rating
- `popularity` - Popularity score

### Optional Columns
- `id` or `tmdb_id` - The Movie Database ID
- `imdb_id` - IMDb ID
- `original_title` - Original title
- `tagline` - Movie tagline
- `overview` - Movie description
- `release_year` - Release year
- `status` - Release status
- `runtime` - Runtime in minutes
- `vote_count` - Number of votes
- `budget` - Production budget
- `revenue` - Box office revenue
- `original_language` - Original language code
- `poster_path` - Poster image path
- `backdrop_path` - Backdrop image path
- `homepage` - Official homepage URL
- `adult` - Adult content flag (true/false)
- `video` - Video availability (true/false)
- `genres` - JSON array of genre objects
- `production_companies` - JSON array of company objects
- `production_countries` - JSON array of country objects
- `spoken_languages` - JSON array of language objects
- `keywords` - JSON array of keyword objects

## Import Instructions

After placing your CSV file in this directory, run:

```bash
docker-compose exec web python manage.py import_movies /app/data/your_file.csv
```

## Sample Data Sources

You can get movie datasets from:
- [The Movie Database (TMDb)](https://www.themoviedb.org/)
- [IMDb Datasets](https://www.imdb.com/interfaces/)
- [Kaggle Movie Datasets](https://www.kaggle.com/datasets?search=movies)
- [MovieLens](https://grouplens.org/datasets/movielens/)

## Notes

- Large datasets may take some time to import
- Duplicate movies (based on tmdb_id) will be skipped
- Invalid data rows will be reported in the console
