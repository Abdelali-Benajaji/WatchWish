from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .services import MovieService

def index(request):
    movie_title = request.GET.get('movie', '').strip()
    recommendations = []
    searched_movie = None
    error = None
    
    if movie_title:
        searched_movie = MovieService.get_movie_by_title(movie_title)
        if searched_movie:
            searched_movie['genre_list'] = searched_movie['genres'].split('|')
            recommendations = MovieService.get_recommendations(movie_title, limit=5)
            for rec in recommendations:
                rec['genre_list'] = rec['genres'].split('|')
        else:
            error = f"Movie '{movie_title}' not found in our database."
    
    return render(request, 'index.html', {
        'movie_title': movie_title,
        'searched_movie': searched_movie,
        'recommendations': recommendations,
        'error': error
    })

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

def user_recommendations(request):
    user_id = request.GET.get('user_id', '').strip()
    recommendations = []
    error = None
    
    if user_id:
        try:
            user_id_int = int(user_id)
            recommendations = MovieService.get_user_recommendations(user_id_int, limit=10)
            if not recommendations:
                error = f"No recommendations found for user ID {user_id_int}."
            else:
                for rec in recommendations:
                    rec['genre_list'] = rec['genres'].split('|')
        except ValueError:
            error = "Please enter a valid user ID (numeric value)."
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    
    return render(request, 'user_recommendations.html', {
        'user_id': user_id,
        'recommendations': recommendations,
        'error': error
    })
