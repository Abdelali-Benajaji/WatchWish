from bson import ObjectId
from .db import get_movies_collection

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
