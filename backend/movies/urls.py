from django.urls import path
from . import views

urlpatterns = [
    path('movies/', views.list_movies, name='list_movies'),
    path('movies/create/', views.create_movie, name='create_movie'),
    path('movies/<str:movie_id>/', views.get_movie, name='get_movie'),
    path('movies/<str:movie_id>/update/', views.update_movie, name='update_movie'),
    path('movies/<str:movie_id>/delete/', views.delete_movie, name='delete_movie'),
]
