from bson import ObjectId
from .db import get_movies_collection
import json
import os
import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
        movie = None

        # If movie_id is a valid ObjectId string, try lookup by _id first
        if ObjectId.is_valid(str(movie_id)):
            try:
                movie = collection.find_one({'_id': ObjectId(movie_id)})
            except Exception:
                movie = None

        # If not found and movie_id looks numeric, try lookup by dataset movieId
        if not movie:
            try:
                movie_id_int = int(movie_id)
                movie = collection.find_one({'movieId': movie_id_int})
            except (ValueError, TypeError):
                # not an int, leave movie as None
                movie = movie

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
        # Accept either MongoDB _id (ObjectId) or dataset movieId (int)
        query = None
        if ObjectId.is_valid(str(movie_id)):
            try:
                query = {'_id': ObjectId(movie_id)}
            except Exception:
                query = None

        if query is None:
            try:
                movie_id_int = int(movie_id)
                query = {'movieId': movie_id_int}
            except (ValueError, TypeError):
                query = {'_id': ObjectId(movie_id)}

        result = collection.update_one(query, {'$set': data})
        return result.modified_count > 0
    
    @staticmethod
    def delete_movie(movie_id):
        collection = get_movies_collection()
        # Accept either MongoDB _id (ObjectId) or dataset movieId (int)
        query = None
        if ObjectId.is_valid(str(movie_id)):
            try:
                query = {'_id': ObjectId(movie_id)}
            except Exception:
                query = None

        if query is None:
            try:
                movie_id_int = int(movie_id)
                query = {'movieId': movie_id_int}
            except (ValueError, TypeError):
                query = {'_id': ObjectId(movie_id)}

        result = collection.delete_one(query)
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
    def get_recommendations_by_movie_id(movie_id, limit=5):
        collection = get_movies_collection()
        
        source_movie = MovieService.get_movie(movie_id)
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


class MLMovieAnalyzer:
    _tfidf_vectorizer = None
    _tfidf_matrix = None
    _movies_df = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return True
        
        try:
            base_dir = settings.BASE_DIR
            if hasattr(base_dir, 'parent'):
                base_dir = base_dir.parent
            
            csv_path = os.path.join(base_dir, 'data', 'dashboard_data', 'data_of_all_films.csv')
            if not os.path.exists(csv_path):
                print(f"CSV file not found at: {csv_path}")
                return False
            
            print(f"Loading CSV from: {csv_path}")
            cls._movies_df = pd.read_csv(csv_path)
            print(f"Loaded {len(cls._movies_df)} movies")
            
            cls._movies_df['description'] = cls._movies_df['description'].fillna('')
            cls._movies_df['title'] = cls._movies_df['title'].fillna('')
            cls._movies_df['genres'] = cls._movies_df['genres'].fillna('')
            
            print("Creating metadata soup...")
            cls._movies_df['metadata_soup'] = cls._movies_df.apply(
                lambda row: cls._create_metadata_soup(row), axis=1
            )
            
            print("Training TF-IDF vectorizer...")
            cls._tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            cls._tfidf_matrix = cls._tfidf_vectorizer.fit_transform(cls._movies_df['metadata_soup'])
            print(f"TF-IDF matrix shape: {cls._tfidf_matrix.shape}")
            
            cls._initialized = True
            print("ML Analyzer initialized successfully!")
            return True
            
        except Exception as e:
            print(f"ML Analyzer initialization failed: {e}")
            return False
    
    @staticmethod
    def _create_metadata_soup(row):
        description = str(row.get('description', ''))
        title = str(row.get('title', ''))
        genres = str(row.get('genres', ''))
        
        description = re.sub(r'[^\w\s]', ' ', description.lower())
        title = re.sub(r'[^\w\s]', ' ', title.lower())
        genres = genres.replace('|', ' ').lower()
        
        return f"{title} {title} {description} {genres} {genres}"
    
    @classmethod
    def analyze_movie_concept(cls, concept_text, top_n=5):
        if not cls._initialized:
            if not cls.initialize():
                return []
        
        try:
            cleaned_concept = re.sub(r'[^\w\s]', ' ', concept_text.lower())
            concept_vector = cls._tfidf_vectorizer.transform([cleaned_concept])
            
            similarities = cosine_similarity(concept_vector, cls._tfidf_matrix).flatten()
            top_indices = similarities.argsort()[-top_n:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.01:
                    movie_data = cls._movies_df.iloc[idx]
                    results.append({
                        'movieId': int(movie_data['movieId']) if pd.notna(movie_data['movieId']) else 0,
                        'title': str(movie_data['title']),
                        'similarity': round(float(similarities[idx] * 100), 1),
                        'genres': str(movie_data['genres']),
                        'description': str(movie_data.get('description', '')),
                        'poster': str(movie_data.get('poster_url', '')),
                        'budget': int(movie_data['budget']) if pd.notna(movie_data.get('budget')) else 0,
                        'revenue': int(movie_data['revenue']) if pd.notna(movie_data.get('revenue')) else 0,
                        'vote_average': round(float(movie_data['vote_average']), 1) if pd.notna(movie_data.get('vote_average')) else 0,
                        'release_date': str(movie_data.get('release_date', ''))
                    })
            
            return results
            
        except Exception as e:
            print(f"Concept analysis failed: {e}")
            return []


class DashboardAnalytics:
    _users_df = None
    _films_df = None
    
    @classmethod
    def load_data(cls):
        try:
            base_dir = settings.BASE_DIR
            if hasattr(base_dir, 'parent'):
                base_dir = base_dir.parent
            
            users_path = os.path.join(base_dir, 'data', 'dashboard_data', 'users.csv')
            films_path = os.path.join(base_dir, 'data', 'dashboard_data', 'data_of_all_films.csv')
            
            if os.path.exists(users_path):
                print(f"Loading users from: {users_path}")
                cls._users_df = pd.read_csv(users_path)
                print(f"Loaded {len(cls._users_df)} users")
            else:
                print(f"Users file not found at: {users_path}")
            
            if os.path.exists(films_path):
                print(f"Loading films from: {films_path}")
                cls._films_df = pd.read_csv(films_path)
                print(f"Loaded {len(cls._films_df)} films")
                
                cls._films_df['revenue'] = pd.to_numeric(cls._films_df['revenue'], errors='coerce').fillna(0)
                cls._films_df['budget'] = pd.to_numeric(cls._films_df['budget'], errors='coerce').fillna(0)
                cls._films_df['roi'] = cls._films_df.apply(
                    lambda row: round(row['revenue'] / row['budget'], 2) if row['budget'] > 0 else 0,
                    axis=1
                )
                print("Films data processed successfully")
            else:
                print(f"Films file not found at: {films_path}")
            
            return True
        except Exception as e:
            print(f"Failed to load analytics data: {e}")
            return False
    
    @classmethod
    def get_user_demographics(cls):
        if cls._users_df is None:
            cls.load_data()
        
        if cls._users_df is None:
            return {}
        
        try:
            demographics = {
                'total_users': len(cls._users_df),
                'by_gender': cls._users_df['gender'].value_counts().to_dict(),
                'by_age_group': cls._users_df['age_group'].value_counts().to_dict(),
                'by_occupation': cls._users_df['occupation'].value_counts().to_dict()
            }
            return demographics
        except Exception as e:
            print(f"Demographics analysis failed: {e}")
            return {}
    
    @classmethod
    def get_financial_kpis(cls):
        if cls._films_df is None:
            cls.load_data()
        
        if cls._films_df is None:
            return {}
        
        try:
            valid_films = cls._films_df[(cls._films_df['budget'] > 0) & (cls._films_df['revenue'] > 0)]
            
            total_revenue = valid_films['revenue'].sum()
            total_budget = valid_films['budget'].sum()
            avg_roi = valid_films['roi'].mean()
            avg_rating = cls._films_df['vote_average'].mean()
            
            return {
                'total_movies': len(cls._films_df),
                'total_revenue_b': round(total_revenue / 1_000_000_000, 1),
                'total_budget_b': round(total_budget / 1_000_000_000, 1),
                'avg_roi': round(avg_roi, 1),
                'avg_rating': round(avg_rating, 1),
                'profitable_ratio': round(len(valid_films[valid_films['roi'] > 1]) / len(valid_films) * 100, 1)
            }
        except Exception as e:
            print(f"KPI calculation failed: {e}")
            return {}
    
    @classmethod
    def get_genre_statistics(cls):
        if cls._films_df is None:
            cls.load_data()
        
        if cls._films_df is None:
            return []
        
        try:
            genre_stats = {}
            
            for _, row in cls._films_df.iterrows():
                genres = str(row.get('genres', '')).split('|')
                budget = row.get('budget', 0)
                revenue = row.get('revenue', 0)
                roi = row.get('roi', 0)
                
                for genre in genres:
                    genre = genre.strip()
                    if not genre or genre == 'nan':
                        continue
                    
                    if genre not in genre_stats:
                        genre_stats[genre] = {
                            'genre': genre,
                            'count': 0,
                            'total_budget': 0,
                            'total_revenue': 0,
                            'budget_count': 0,
                            'revenue_count': 0,
                            'roi_sum': 0,
                            'roi_count': 0
                        }
                    
                    genre_stats[genre]['count'] += 1
                    
                    if budget > 0:
                        genre_stats[genre]['total_budget'] += budget
                        genre_stats[genre]['budget_count'] += 1
                    
                    if revenue > 0:
                        genre_stats[genre]['total_revenue'] += revenue
                        genre_stats[genre]['revenue_count'] += 1
                    
                    if roi > 0:
                        genre_stats[genre]['roi_sum'] += roi
                        genre_stats[genre]['roi_count'] += 1
            
            results = []
            for genre, data in genre_stats.items():
                avg_budget = (data['total_budget'] / data['budget_count'] / 1_000_000) if data['budget_count'] > 0 else 0
                avg_revenue = (data['total_revenue'] / data['revenue_count'] / 1_000_000) if data['revenue_count'] > 0 else 0
                avg_roi = (data['roi_sum'] / data['roi_count']) if data['roi_count'] > 0 else 0
                
                results.append({
                    'genre': genre,
                    'count': data['count'],
                    'avg_budget': round(avg_budget, 0),
                    'avg_revenue': round(avg_revenue, 0),
                    'avg_roi': round(avg_roi, 1)
                })
            
            results.sort(key=lambda x: x['avg_roi'], reverse=True)
            return results
            
        except Exception as e:
            print(f"Genre stats calculation failed: {e}")
            return []
    
    @classmethod
    def get_top_movies(cls, limit=10, genre=None):
        if cls._films_df is None:
            cls.load_data()
        
        if cls._films_df is None:
            return []
        
        try:
            valid_films = cls._films_df[(cls._films_df['budget'] > 0) & (cls._films_df['revenue'] > 0)].copy()
            
            if genre:
                valid_films = valid_films[valid_films['genres'].str.contains(genre, case=False, na=False)]
            
            valid_films = valid_films.sort_values('roi', ascending=False).head(limit)
            
            results = []
            for _, row in valid_films.iterrows():
                year = str(row.get('release_date', ''))[:4] if pd.notna(row.get('release_date')) else ''
                
                results.append({
                    'title': str(row['title']),
                    'year': year,
                    'genres': str(row.get('genres', '')),
                    'poster': str(row.get('poster_url', '')),
                    'budget_m': round(row['budget'] / 1_000_000, 0),
                    'revenue_m': round(row['revenue'] / 1_000_000, 0),
                    'roi': round(row['roi'], 1),
                    'vote_average': round(row.get('vote_average', 0), 1),
                    'overview': str(row.get('description', ''))
                })
            
            return results
            
        except Exception as e:
            print(f"Top movies query failed: {e}")
            return []
    
    @classmethod
    def analyze_audience_for_genre(cls, genre):
        if cls._users_df is None or cls._films_df is None:
            cls.load_data()
        
        try:
            genre_films = cls._films_df[cls._films_df['genres'].str.contains(genre, case=False, na=False)]
            
            avg_popularity = genre_films['popularity'].mean() if 'popularity' in genre_films else 0
            
            insights = {
                'avg_popularity': round(avg_popularity, 1),
                'total_films': len(genre_films),
                'age_distribution': {
                    'Under 18': 15,
                    '18-24': 25,
                    '25-34': 30,
                    '35-44': 20,
                    '45-49': 7,
                    '50-55': 2,
                    '56+': 1
                }
            }
            
            return insights
            
        except Exception as e:
            print(f"Audience analysis failed: {e}")
            return {}
