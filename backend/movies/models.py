from django.db import models
from djongo import models as djongo_models


class Movie(models.Model):
    """
    Movie model for storing movie information
    """
    # MongoDB ObjectId will be automatically created as _id
    title = models.CharField(max_length=255, db_index=True)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    
    # Release information
    release_date = models.DateField(null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True, db_index=True)
    
    # Descriptions
    overview = models.TextField(blank=True, null=True)
    tagline = models.CharField(max_length=500, blank=True, null=True)
    
    # Ratings and popularity
    vote_average = models.FloatField(default=0.0)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0.0)
    
    # Runtime and status
    runtime = models.IntegerField(null=True, blank=True, help_text="Runtime in minutes")
    status = models.CharField(max_length=50, blank=True, null=True)
    
    # Financial data
    budget = models.BigIntegerField(default=0)
    revenue = models.BigIntegerField(default=0)
    
    # Language and country
    original_language = models.CharField(max_length=10, blank=True, null=True)
    spoken_languages = models.JSONField(default=list, blank=True)
    production_countries = models.JSONField(default=list, blank=True)
    
    # Companies and crew
    production_companies = models.JSONField(default=list, blank=True)
    
    # Genres
    genres = models.JSONField(default=list, blank=True)
    
    # External IDs
    imdb_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    
    # Media
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional data
    homepage = models.URLField(max_length=500, blank=True, null=True)
    keywords = models.JSONField(default=list, blank=True)
    
    # Adult content flag
    adult = models.BooleanField(default=False)
    
    # Video availability
    video = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity', '-release_date']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['release_year']),
            models.Index(fields=['-popularity']),
            models.Index(fields=['-vote_average']),
        ]
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'
    
    def __str__(self):
        return f"{self.title} ({self.release_year or 'N/A'})"
    
    @property
    def genre_names(self):
        """Extract genre names from genres JSON"""
        if isinstance(self.genres, list):
            return [g.get('name', '') for g in self.genres if isinstance(g, dict)]
        return []
    
    @property
    def profit(self):
        """Calculate profit"""
        if self.revenue and self.budget:
            return self.revenue - self.budget
        return 0


class Director(models.Model):
    """
    Director model for storing director information
    """
    name = models.CharField(max_length=255, db_index=True)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    profile_path = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Director'
        verbose_name_plural = 'Directors'
    
    def __str__(self):
        return self.name


class Actor(models.Model):
    """
    Actor model for storing cast information
    """
    name = models.CharField(max_length=255, db_index=True)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    profile_path = models.CharField(max_length=255, blank=True, null=True)
    gender = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Actor'
        verbose_name_plural = 'Actors'
    
    def __str__(self):
        return self.name


class MovieCast(models.Model):
    """
    Relationship between movies and actors with character information
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast')
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name='movies')
    character = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['movie', 'actor', 'character']
        verbose_name = 'Movie Cast'
        verbose_name_plural = 'Movie Casts'
    
    def __str__(self):
        return f"{self.actor.name} as {self.character} in {self.movie.title}"


class MovieDirector(models.Model):
    """
    Relationship between movies and directors
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='directors')
    director = models.ForeignKey(Director, on_delete=models.CASCADE, related_name='movies')
    
    class Meta:
        unique_together = ['movie', 'director']
        verbose_name = 'Movie Director'
        verbose_name_plural = 'Movie Directors'
    
    def __str__(self):
        return f"{self.director.name} directed {self.movie.title}"
