from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Count
from .models import Movie, Director, Actor
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    MovieCreateUpdateSerializer,
    DirectorSerializer,
    ActorSerializer
)


class MovieViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Movie CRUD operations
    """
    queryset = Movie.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'original_title', 'overview', 'tagline']
    ordering_fields = ['release_year', 'vote_average', 'popularity', 'budget', 'revenue', 'created_at']
    ordering = ['-popularity']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MovieCreateUpdateSerializer
        return MovieDetailSerializer
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        
        # Filter by year
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(release_year=year)
        
        # Filter by year range
        year_min = self.request.query_params.get('year_min', None)
        year_max = self.request.query_params.get('year_max', None)
        if year_min:
            queryset = queryset.filter(release_year__gte=year_min)
        if year_max:
            queryset = queryset.filter(release_year__lte=year_max)
        
        # Filter by rating range
        rating_min = self.request.query_params.get('rating_min', None)
        rating_max = self.request.query_params.get('rating_max', None)
        if rating_min:
            queryset = queryset.filter(vote_average__gte=rating_min)
        if rating_max:
            queryset = queryset.filter(vote_average__lte=rating_max)
        
        # Filter by genre (assuming genres is stored as JSON)
        genre = self.request.query_params.get('genre', None)
        if genre:
            queryset = queryset.filter(genres__contains=genre)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about movies in the database
        """
        stats = {
            'total_movies': Movie.objects.count(),
            'average_rating': Movie.objects.aggregate(Avg('vote_average'))['vote_average__avg'],
            'total_budget': Movie.objects.aggregate(models.Sum('budget'))['budget__sum'],
            'total_revenue': Movie.objects.aggregate(models.Sum('revenue'))['revenue__sum'],
            'movies_by_year': list(
                Movie.objects.values('release_year')
                .annotate(count=Count('id'))
                .order_by('-release_year')[:10]
            ),
        }
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """
        Get top rated movies
        """
        limit = int(request.query_params.get('limit', 10))
        movies = Movie.objects.filter(vote_count__gte=100).order_by('-vote_average')[:limit]
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def most_popular(self, request):
        """
        Get most popular movies
        """
        limit = int(request.query_params.get('limit', 10))
        movies = Movie.objects.order_by('-popularity')[:limit]
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def highest_grossing(self, request):
        """
        Get highest grossing movies
        """
        limit = int(request.query_params.get('limit', 10))
        movies = Movie.objects.filter(revenue__gt=0).order_by('-revenue')[:limit]
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)


class DirectorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Director CRUD operations
    """
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ActorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Actor CRUD operations
    """
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


def home(request):
    """
    Home page view
    """
    return render(request, 'movies/home.html', {
        'title': 'WatchWish - Movie Dataset'
    })
