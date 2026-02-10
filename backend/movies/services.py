from bson import ObjectId
from .db import get_movies_collection
import json
import os
from django.conf import settings

class MovieService:
    @staticmethod
    def create_movie(data):
        collection = get_movies_collection()
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_movie(movie_id):
        collection = get_movies_collection()
        movie = collection.find_one({'_id': ObjectId(movie_id)})
        if movie:
            movie['_id'] = str(movie['_id'])
        return movie
    
    @staticmethod
    def get_all_movies(filters=None, limit=100, skip=0):
        collection = get_movies_collection()
        query = filters or {}
        movies = list(collection.find(query).limit(limit).skip(skip))
        for movie in movies:
            movie['_id'] = str(movie['_id'])
        return movies
    
    @staticmethod
    def update_movie(movie_id, data):
        collection = get_movies_collection()
        result = collection.update_one(
            {'_id': ObjectId(movie_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete_movie(movie_id):
        collection = get_movies_collection()
        result = collection.delete_one({'_id': ObjectId(movie_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def search_movies(query_text, limit=50):
        collection = get_movies_collection()
        search_filter = {
            '$or': [
                {'title': {'$regex': query_text, '$options': 'i'}},
                {'description': {'$regex': query_text, '$options': 'i'}},
                {'genre': {'$regex': query_text, '$options': 'i'}},
            ]
        }
        movies = list(collection.find(search_filter).limit(limit))
        for movie in movies:
            movie['_id'] = str(movie['_id'])
        return movies
    
    @staticmethod
    def get_movies_by_genre(genre, limit=50):
        collection = get_movies_collection()
        movies = list(collection.find({'genre': genre}).limit(limit))
        for movie in movies:
            movie['_id'] = str(movie['_id'])
        return movies
    
    @staticmethod
    def count_movies(filters=None):
        collection = get_movies_collection()
        query = filters or {}
        return collection.count_documents(query)
    
    @staticmethod
    def get_movie_by_title(title):
        collection = get_movies_collection()
        movie = collection.find_one({'title': {'$regex': f'^{title}', '$options': 'i'}})
        if movie:
            movie['_id'] = str(movie['_id'])
        return movie
    
    @staticmethod
    def get_recommendations(movie_title, limit=5):
        collection = get_movies_collection()
        
        source_movie = collection.find_one({'title': {'$regex': f'^{movie_title}', '$options': 'i'}})
        if not source_movie:
            return []
        
        source_genres = set(source_movie['genres'].split('|'))
        
        all_movies = list(collection.find({'movieId': {'$ne': source_movie['movieId']}}))
        
        movie_scores = []
        for movie in all_movies:
            movie_genres = set(movie['genres'].split('|'))
            genre_overlap = len(source_genres & movie_genres)
            if genre_overlap > 0:
                movie_scores.append({
                    'movie': movie,
                    'score': genre_overlap
                })
        
        movie_scores.sort(key=lambda x: x['score'], reverse=True)
        
        recommendations = []
        for item in movie_scores[:limit]:
            movie = item['movie']
            movie['_id'] = str(movie['_id'])
            recommendations.append(movie)
        
        return recommendations
    
    @staticmethod
    def get_user_recommendations(user_id, limit=10):
        # Migrated to use MongoDB 'user_recommendations' collection
        # Assuming we prioritized model1, or merge them?
        # The original code loaded both and summed scores.
        # "model1_path" recommendations map update logic...
        # "model2_path" recommendations map update logic...
        
        # We need to replicate this logic using the DB.
        # The DB has documents: {userId, model, recommendations: [{movieId, score, ...}]}
        
        from .db import get_user_recommendations_collection
        rec_collection = get_user_recommendations_collection()
        
        # Find all recommendation docs for this user (from both models)
        cursor = rec_collection.find({'userId': user_id})
        
        recommendations_map = {}
        for doc in cursor:
            for rec in doc.get('recommendations', []):
                movie_id = rec['movieId']
                if movie_id not in recommendations_map:
                    recommendations_map[movie_id] = {'movieId': movie_id, 'score': 0, 'count': 0}
                recommendations_map[movie_id]['score'] += rec['score']
                recommendations_map[movie_id]['count'] += 1
        
        if not recommendations_map:
            # Fallback to live recommendations
            return MovieService.generate_live_recommendations(user_id, limit)

        sorted_recommendations = sorted(
            recommendations_map.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:limit]

        collection = get_movies_collection()
        result_movies = []

        for rec in sorted_recommendations:
            movie = collection.find_one({'movieId': rec['movieId']})
            if movie:
                movie['_id'] = str(movie['_id'])
                movie['recommendation_score'] = rec['score']
                result_movies.append(movie)

        return result_movies

    @staticmethod
    def add_user_rating(user_id, movie_id, score):
        from .db import get_user_ratings_collection
        collection = get_user_ratings_collection()
        
        # Upsert rating
        collection.update_one(
            {'userId': user_id, 'movieId': movie_id},
            {'$set': {'score': score}},
            upsert=True
        )
        return True

    @staticmethod
    def get_user_ratings(user_id):
        from .db import get_user_ratings_collection
        collection = get_user_ratings_collection()
        return list(collection.find({'userId': user_id}))

    @staticmethod
    def generate_live_recommendations(user_id, limit=10):
        # A simple content-based recommender for cold-start
        ratings = MovieService.get_user_ratings(user_id)
        
        if not ratings:
            return []
            
        # Get movies user liked (score >= 4)
        liked_movie_ids = [r['movieId'] for r in ratings if r['score'] >= 4]
        if not liked_movie_ids:
            # Fallback to any rated movie if no strong likes
            liked_movie_ids = [r['movieId'] for r in ratings]
            
        movies_collection = get_movies_collection()
        liked_movies = list(movies_collection.find({'movieId': {'$in': liked_movie_ids}}))
        
        if not liked_movies:
            return []
            
        # Collect genres from liked movies
        # We can also do actor/director matching if data available, but starting with genres
        target_genres = set()
        for movie in liked_movies:
            genres = movie.get('genres', '').split('|')
            target_genres.update(genres)
            
        # Find candidate movies that have these genres, excluding already rated ones
        rated_ids = [r['movieId'] for r in ratings]
        
        # optimization: verify if we have enough movies. 
        # If too many, maybe sample or limit?
        # For now, let's just find movies with at least one matching genre and score them.
        
        # Heuristic: Find movies that share genres.
        # This might be slow if we iterate all movies. 
        # MongoDB query to find movies with ANY of the target genres?
        # stored as "Action|Adventure", regex used elsewhere.
        
        # Better approach: 
        # For each liked movie, find similar movies (like get_recommendations) and aggregate.
        
        candidates = {}
        
        for source_movie in liked_movies:
            # Reusing logic from get_recommendations but for ID
            # Find movies not in rated_ids
            source_genres = set(source_movie.get('genres', '').split('|'))
            
            # This query might be heavy if done in loop. 
            # In a real app we'd use a search index or vector db.
            # Limiting the search space or cache?
            
            # Let's try to fetch a batch of candidates using genre string matching?
            # Or just fetch all movies? (There are 9000 movies in small dataset, might be OK, but 27M in full...)
            # We imported 'tmdb_allfilms.csv'. How many rows?
            # The verify script said 130k recs, but movies? "Updated 740 movies". 
            # Wait, 740 is very small. We can iterate 740 movies easily.
            # If the dataset is small, we can load all movies in memory or just query efficiently.
            
            # Let's fetch all movies once to avoid N+1 queries if N is small.
            # Checking count...
            # If count < 10000, we can do in-memory scoring.
            
            all_movies = list(movies_collection.find({'movieId': {'$nin': rated_ids}}))
            
            for candidate in all_movies:
                cand_id = candidate['movieId']
                cand_genres = set(candidate.get('genres', '').split('|'))
                
                overlap = len(source_genres & cand_genres)
                if overlap > 0:
                    if cand_id not in candidates:
                        candidates[cand_id] = {'movie': candidate, 'score': 0}
                    # Add to score (weighted by user rating of source?)
                    # source movie was liked (>=4), so we count it as +1 * overlap
                    candidates[cand_id]['score'] += overlap

        # Sort candidates
        sorted_candidates = sorted(
            candidates.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )[:limit]
        
        result = []
        for item in sorted_candidates:
            movie = item['movie']
            movie['_id'] = str(movie['_id'])
            movie['recommendation_score'] = item['score']
            result.append(movie)
            
        return result
