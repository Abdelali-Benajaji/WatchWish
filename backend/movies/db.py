from pymongo import MongoClient
from django.conf import settings

_client = None
_db = None

def get_mongodb_client():
    global _client
    if _client is None:
        mongodb_settings = settings.MONGODB_SETTINGS
        username = mongodb_settings.get('username')
        password = mongodb_settings.get('password')
        host = mongodb_settings.get('host', 'localhost')
        port = mongodb_settings.get('port', 27017)
        
        if username and password:
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/"
        else:
            connection_string = f"mongodb://{host}:{port}/"
        
        _client = MongoClient(connection_string)
    return _client

def get_mongodb():
    global _db
    if _db is None:
        client = get_mongodb_client()
        db_name = settings.MONGODB_SETTINGS.get('db_name', 'watchwish_db')
        _db = client[db_name]
    return _db

def get_movies_collection():
    db = get_mongodb()
    return db['movies']

def get_user_recommendations_collection():
    db = get_mongodb()
    return db['user_recommendations']

def get_user_ratings_collection():
    db = get_mongodb()
    return db['user_ratings']
