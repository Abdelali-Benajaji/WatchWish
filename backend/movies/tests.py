from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Movie, Director, Actor


class MovieModelTest(TestCase):
    """Test cases for Movie model"""
    
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2024,
            vote_average=8.5,
            popularity=100.0,
            budget=1000000,
            revenue=5000000
        )
    
    def test_movie_creation(self):
        """Test movie is created correctly"""
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(self.movie.release_year, 2024)
        self.assertEqual(self.movie.vote_average, 8.5)
    
    def test_movie_str(self):
        """Test movie string representation"""
        self.assertEqual(str(self.movie), "Test Movie (2024)")
    
    def test_movie_profit(self):
        """Test profit calculation"""
        self.assertEqual(self.movie.profit, 4000000)


class MovieAPITest(APITestCase):
    """Test cases for Movie API endpoints"""
    
    def setUp(self):
        self.movie1 = Movie.objects.create(
            title="Movie 1",
            release_year=2024,
            vote_average=8.0,
            popularity=90.0
        )
        self.movie2 = Movie.objects.create(
            title="Movie 2",
            release_year=2023,
            vote_average=7.5,
            popularity=80.0
        )
    
    def test_get_movies_list(self):
        """Test getting list of movies"""
        url = reverse('movie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_get_movie_detail(self):
        """Test getting single movie details"""
        url = reverse('movie-detail', args=[self.movie1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Movie 1")
    
    def test_filter_movies_by_year(self):
        """Test filtering movies by year"""
        url = reverse('movie-list')
        response = self.client.get(url, {'year': 2024})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_movies(self):
        """Test searching movies"""
        url = reverse('movie-list')
        response = self.client.get(url, {'search': 'Movie 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class DirectorModelTest(TestCase):
    """Test cases for Director model"""
    
    def setUp(self):
        self.director = Director.objects.create(
            name="Test Director",
            tmdb_id=12345
        )
    
    def test_director_creation(self):
        """Test director is created correctly"""
        self.assertEqual(self.director.name, "Test Director")
        self.assertEqual(self.director.tmdb_id, 12345)
    
    def test_director_str(self):
        """Test director string representation"""
        self.assertEqual(str(self.director), "Test Director")


class ActorModelTest(TestCase):
    """Test cases for Actor model"""
    
    def setUp(self):
        self.actor = Actor.objects.create(
            name="Test Actor",
            tmdb_id=67890,
            gender=1
        )
    
    def test_actor_creation(self):
        """Test actor is created correctly"""
        self.assertEqual(self.actor.name, "Test Actor")
        self.assertEqual(self.actor.tmdb_id, 67890)
        self.assertEqual(self.actor.gender, 1)
    
    def test_actor_str(self):
        """Test actor string representation"""
        self.assertEqual(str(self.actor), "Test Actor")
