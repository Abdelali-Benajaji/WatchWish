from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .services import MovieService

@csrf_exempt
@require_http_methods(["POST"])
def create_movie(request):
    try:
        data = json.loads(request.body)
        movie_id = MovieService.create_movie(data)
        return JsonResponse({'id': movie_id, 'message': 'Movie created successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_movie(request, movie_id):
    try:
        movie = MovieService.get_movie(movie_id)
        if movie:
            return JsonResponse(movie)
        return JsonResponse({'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def list_movies(request):
    try:
        limit = int(request.GET.get('limit', 100))
        skip = int(request.GET.get('skip', 0))
        genre = request.GET.get('genre')
        search = request.GET.get('search')
        
        if search:
            movies = MovieService.search_movies(search, limit)
        elif genre:
            movies = MovieService.get_movies_by_genre(genre, limit)
        else:
            movies = MovieService.get_all_movies(limit=limit, skip=skip)
        
        return JsonResponse({'movies': movies, 'count': len(movies)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def update_movie(request, movie_id):
    try:
        data = json.loads(request.body)
        success = MovieService.update_movie(movie_id, data)
        if success:
            return JsonResponse({'message': 'Movie updated successfully'})
        return JsonResponse({'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_movie(request, movie_id):
    try:
        success = MovieService.delete_movie(movie_id)
        if success:
            return JsonResponse({'message': 'Movie deleted successfully'})
        return JsonResponse({'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
