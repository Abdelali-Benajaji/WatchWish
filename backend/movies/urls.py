from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'movies', views.MovieViewSet, basename='movie')
router.register(r'directors', views.DirectorViewSet, basename='director')
router.register(r'actors', views.ActorViewSet, basename='actor')

app_name = 'movies'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
