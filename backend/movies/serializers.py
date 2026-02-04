from rest_framework import serializers
from .models import Movie, Director, Actor, MovieCast, MovieDirector


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ['id', 'name', 'tmdb_id', 'profile_path']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', 'tmdb_id', 'profile_path', 'gender']


class MovieCastSerializer(serializers.ModelSerializer):
    actor = ActorSerializer(read_only=True)
    
    class Meta:
        model = MovieCast
        fields = ['actor', 'character', 'order']


class MovieDirectorSerializer(serializers.ModelSerializer):
    director = DirectorSerializer(read_only=True)
    
    class Meta:
        model = MovieDirector
        fields = ['director']


class MovieListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    genre_names = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'release_year', 'vote_average', 
            'popularity', 'poster_path', 'genre_names', 'overview'
        ]


class MovieDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single movie view"""
    genre_names = serializers.ReadOnlyField()
    profit = serializers.ReadOnlyField()
    cast = MovieCastSerializer(many=True, read_only=True)
    directors = MovieDirectorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'original_title', 'tagline', 'overview',
            'release_date', 'release_year', 'status', 'runtime',
            'vote_average', 'vote_count', 'popularity',
            'budget', 'revenue', 'profit',
            'genres', 'genre_names',
            'original_language', 'spoken_languages',
            'production_companies', 'production_countries',
            'imdb_id', 'tmdb_id',
            'poster_path', 'backdrop_path', 'homepage',
            'keywords', 'adult', 'video',
            'cast', 'directors',
            'created_at', 'updated_at'
        ]


class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating movies"""
    
    class Meta:
        model = Movie
        fields = [
            'title', 'original_title', 'tagline', 'overview',
            'release_date', 'release_year', 'status', 'runtime',
            'vote_average', 'vote_count', 'popularity',
            'budget', 'revenue',
            'genres', 'original_language', 'spoken_languages',
            'production_companies', 'production_countries',
            'imdb_id', 'tmdb_id',
            'poster_path', 'backdrop_path', 'homepage',
            'keywords', 'adult', 'video'
        ]
