from django.contrib import admin
from .models import Movie, Director, Actor, MovieCast, MovieDirector


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'vote_average', 'popularity', 'budget', 'revenue']
    list_filter = ['release_year', 'adult', 'status']
    search_fields = ['title', 'original_title', 'overview', 'imdb_id']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'original_title', 'tagline', 'overview')
        }),
        ('Release Information', {
            'fields': ('release_date', 'release_year', 'status')
        }),
        ('Ratings & Popularity', {
            'fields': ('vote_average', 'vote_count', 'popularity')
        }),
        ('Financial', {
            'fields': ('budget', 'revenue')
        }),
        ('Production', {
            'fields': ('runtime', 'genres', 'production_companies', 'production_countries')
        }),
        ('Language', {
            'fields': ('original_language', 'spoken_languages')
        }),
        ('External IDs', {
            'fields': ('imdb_id', 'tmdb_id')
        }),
        ('Media', {
            'fields': ('poster_path', 'backdrop_path', 'homepage')
        }),
        ('Additional', {
            'fields': ('keywords', 'adult', 'video')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id', 'gender', 'created_at']
    list_filter = ['gender']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ['movie', 'actor', 'character', 'order']
    list_filter = ['movie']
    search_fields = ['movie__title', 'actor__name', 'character']
    autocomplete_fields = ['movie', 'actor']


@admin.register(MovieDirector)
class MovieDirectorAdmin(admin.ModelAdmin):
    list_display = ['movie', 'director']
    search_fields = ['movie__title', 'director__name']
    autocomplete_fields = ['movie', 'director']
