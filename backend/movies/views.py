from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .services import MovieService
from .decorators import admin_required

def index(request):
    movie_title = request.GET.get('movie', '').strip()
    recommendations = []
    searched_movie = None
    error = None
    
    if movie_title:
        searched_movie = MovieService.get_movie_by_title(movie_title)
        if searched_movie:
            searched_movie['genre_list'] = searched_movie['genres'].split('|')
            recommendations = MovieService.get_recommendations(movie_title, limit=12)
            for rec in recommendations:
                rec['genre_list'] = rec['genres'].split('|')
        else:
            error = f"Movie '{movie_title}' not found in our database."
    else:
        import random
        all_movies = MovieService.get_all_movies(limit=200)
        if all_movies:
            recommendations = random.sample(all_movies, min(len(all_movies), 20))
            for rec in recommendations:
                 rec['genre_list'] = rec['genres'].split('|')

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

from django.contrib.auth.decorators import login_required

@login_required
def user_recommendations(request):
    user_id = request.GET.get('user_id', '').strip()
    recommendations = []
    error = None
    
    # automated user id selection
    if not user_id:
        # User ID Offset to avoid conflict with dataset user IDs
        # Dataset max ID is around 610 (for small MovieLens) or higher. 
        # Detailed check showed 999999 (from our test script, likely our test user).
        # Let's use 1,000,000 as base. 
        # So Django User ID 1 becomes 1,000,001
        user_id = str(request.user.id + 1000000)
    
    if user_id:
        try:
            user_id_int = int(user_id)
            recommendations = MovieService.get_user_recommendations(user_id_int, limit=10)
            if not recommendations:
                error = f"No recommendations found yet. Rate some movies to get started!"
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

@csrf_exempt
@require_http_methods(["POST"])
def rate_movie(request):
    if not request.user.is_authenticated:
         return JsonResponse({'error': 'Authentication required'}, status=401)
         
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        score = data.get('score')
        
        if not movie_id or score is None:
            return JsonResponse({'error': 'Missing movie_id or score'}, status=400)
            
        # simple 1-5 scale.
        if float(score) < 1 or float(score) > 5:
             return JsonResponse({'error': 'Score must be between 1 and 5'}, status=400)
             
        # User ID Offset logic for consistency with user_recommendations
        # Django User ID 1 -> Rating User ID 1000001
        user_id = request.user.id + 1000000
        
        MovieService.add_user_rating(user_id, movie_id, float(score))
        
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect
from django import forms

User = get_user_model()

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'user'
        if commit:
            user.save()
        return user

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def movie_detail(request, movie_id):
    movie = MovieService.get_movie(movie_id)
    
    if not movie:
        return render(request, 'index.html', {
            'error': f"Movie not found.",
            'movie_title': '',
            'searched_movie': None,
            'recommendations': []
        })
    
    movie['genre_list'] = movie['genres'].split('|')
    
    recommendations = MovieService.get_recommendations_by_movie_id(movie_id, limit=12)
    for rec in recommendations:
        rec['genre_list'] = rec['genres'].split('|')
    
    imdb_url = None
    tmdb_url = None
    
    if movie.get('imdbId'):
        imdb_id = str(movie.get('imdbId')).zfill(7)
        imdb_url = f"http://www.imdb.com/title/tt{imdb_id}/"
    
    if movie.get('tmdbId'):
        try:
            tmdb_id = str(int(float(movie.get('tmdbId'))))
            tmdb_url = f"https://www.themoviedb.org/movie/{tmdb_id}"
        except (ValueError, TypeError):
            tmdb_url = None
    
    return render(request, 'movie_detail.html', {
        'movie': movie,
        'recommendations': recommendations,
        'imdb_url': imdb_url,
        'tmdb_url': tmdb_url
    })

@admin_required
def admin_dashboard(request):
    from .models import User
    
    all_movies = MovieService.get_all_movies(limit=10000)
    total_films = len(all_movies)
    
    genres_count = {}
    total_budget = 0
    total_revenue = 0
    movies_with_budget = 0
    
    for movie in all_movies:
        if movie.get('genres'):
            for genre in movie['genres'].split('|'):
                genre = genre.strip()
                if genre:
                    genres_count[genre] = genres_count.get(genre, 0) + 1
    
    total_users = User.objects.count()
    admin_users = User.objects.filter(role='admin').count()
    regular_users = total_users - admin_users
    
    context = {
        'total_films': total_films,
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'genres_count_json': json.dumps(genres_count),
        'movies': all_movies[:10],
    }
    
    return render(request, 'admin_dashboard.html', context)

@admin_required
def admin_dashboard_api(request):
    from .models import User
    
    endpoint = request.GET.get('endpoint', '')
    
    if endpoint == 'stats':
        all_movies = MovieService.get_all_movies(limit=10000)
        
        genres_count = {}
        for movie in all_movies:
            if movie.get('genres'):
                for genre in movie['genres'].split('|'):
                    genre = genre.strip()
                    if genre:
                        genres_count[genre] = genres_count.get(genre, 0) + 1
        
        total_users = User.objects.count()
        
        return JsonResponse({
            'total_films': len(all_movies),
            'total_users': total_users,
            'genres': genres_count,
            'movies': all_movies[:100]
        })
    
    return JsonResponse({'error': 'Invalid endpoint'}, status=400)
