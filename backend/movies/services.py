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
        base_path = os.path.join(settings.BASE_DIR.parent, 'data')
        model1_path = os.path.join(base_path, 'model_movies_rec.json')
        model2_path = os.path.join(base_path, 'model_movies_rec2.json')
        
        recommendations_map = {}
        
        try:
            with open(model1_path, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data['userId'] == user_id:
                        for rec in data['recommendations']:
                            movie_id = rec['movieId']
                            if movie_id not in recommendations_map:
                                recommendations_map[movie_id] = {'movieId': movie_id, 'score': 0, 'count': 0}
                            recommendations_map[movie_id]['score'] += rec['score']
                            recommendations_map[movie_id]['count'] += 1
                        break
        except FileNotFoundError:
            pass
        
        try:
            with open(model2_path, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data['userId'] == user_id:
                        for rec in data['recommendations']:
                            movie_id = rec['movieId']
                            if movie_id not in recommendations_map:
                                recommendations_map[movie_id] = {'movieId': movie_id, 'score': 0, 'count': 0}
                            recommendations_map[movie_id]['score'] += rec['score']
                            recommendations_map[movie_id]['count'] += 1
                        break
        except FileNotFoundError:
            pass
        
        if not recommendations_map:
            return []
        
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
