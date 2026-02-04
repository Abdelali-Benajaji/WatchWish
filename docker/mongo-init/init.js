// MongoDB initialization script for WatchWish database

db = db.getSiblingDB('watchwish');

// Create collections
db.createCollection('movies');
db.createCollection('directors');
db.createCollection('actors');

// Create indexes for better query performance
db.movies.createIndex({ "title": 1 });
db.movies.createIndex({ "release_year": 1 });
db.movies.createIndex({ "popularity": -1 });
db.movies.createIndex({ "vote_average": -1 });
db.movies.createIndex({ "imdb_id": 1 }, { unique: true, sparse: true });
db.movies.createIndex({ "tmdb_id": 1 }, { unique: true, sparse: true });

db.directors.createIndex({ "name": 1 });
db.directors.createIndex({ "tmdb_id": 1 }, { unique: true, sparse: true });

db.actors.createIndex({ "name": 1 });
db.actors.createIndex({ "tmdb_id": 1 }, { unique: true, sparse: true });

print('WatchWish database initialized successfully!');
