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
    from .services import DashboardAnalytics
    
    kpis = DashboardAnalytics.get_financial_kpis()
    demographics = DashboardAnalytics.get_user_demographics()
    
    if not kpis:
        all_movies = MovieService.get_all_movies(limit=10000)
        total_films = len(all_movies)
        
        genres_count = {}
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
    else:
        total_users = demographics.get('total_users', User.objects.count())
        admin_users = User.objects.filter(role='admin').count()
        regular_users = total_users - admin_users
        
        context = {
            'total_films': kpis.get('total_movies', 0),
            'total_users': total_users,
            'admin_users': admin_users,
            'regular_users': regular_users,
            'total_revenue_b': kpis.get('total_revenue_b', 0),
            'avg_roi': kpis.get('avg_roi', 0),
            'avg_rating': kpis.get('avg_rating', 0),
            'demographics': demographics,
        }
    
    return render(request, 'admin_dashboard.html', context)

@admin_required
def admin_movies_list(request):
    page = int(request.GET.get('page', 1))
    search = request.GET.get('search', '').strip()
    genre = request.GET.get('genre', '').strip()
    
    limit = 20
    skip = (page - 1) * limit
    
    if search:
        movies = MovieService.search_movies(search, limit=1000)
    elif genre:
        movies = MovieService.get_movies_by_genre(genre, limit=1000)
    else:
        movies = MovieService.get_all_movies(limit=1000, skip=skip)
    
    total_count = len(movies)
    movies_page = movies[skip:skip + limit] if skip > 0 else movies[:limit]
    
    for movie in movies_page:
        movie['genre_list'] = movie.get('genres', '').split('|')
    
    return JsonResponse({
        'movies': movies_page,
        'page': page,
        'total': total_count,
        'has_more': len(movies) > skip + limit
    })

@admin_required
@csrf_exempt
def admin_dashboard_api(request):
    from .models import User
    from .services import DashboardAnalytics, MLMovieAnalyzer
    
    endpoint = request.GET.get('endpoint', '')
    
    if request.method == 'POST':
        endpoint = 'simulate'
    
    if endpoint == 'kpis':
        kpis = DashboardAnalytics.get_financial_kpis()
        
        if not kpis:
            all_movies = MovieService.get_all_movies(limit=10000)
            
            total_movies = len(all_movies)
            total_revenue = 0
            total_budget = 0
            total_rating = 0
            valid_revenue_count = 0
            valid_rating_count = 0
            valid_budget_count = 0
            
            for movie in all_movies:
                if movie.get('revenue') and movie['revenue'] > 0:
                    total_revenue += movie['revenue']
                    valid_revenue_count += 1
                if movie.get('budget') and movie['budget'] > 0:
                    total_budget += movie['budget']
                    valid_budget_count += 1
                if movie.get('vote_average'):
                    total_rating += movie['vote_average']
                    valid_rating_count += 1
            
            avg_roi = (total_revenue / total_budget) if total_budget > 0 else 0
            avg_rating = (total_rating / valid_rating_count) if valid_rating_count > 0 else 0
            total_revenue_b = total_revenue / 1_000_000_000
            
            kpis = {
                'total_movies': total_movies,
                'total_revenue_b': round(total_revenue_b, 1),
                'avg_roi': round(avg_roi, 1),
                'avg_rating': round(avg_rating, 1)
            }
        
        return JsonResponse({
            'status': 'ok',
            'data': kpis
        })
    
    elif endpoint == 'genre_stats':
        stats = DashboardAnalytics.get_genre_statistics()
        
        if not stats:
            all_movies = MovieService.get_all_movies(limit=10000)
            
            genre_data = {}
            for movie in all_movies:
                if movie.get('genres'):
                    for genre in movie['genres'].split('|'):
                        genre = genre.strip()
                        if not genre:
                            continue
                        
                        if genre not in genre_data:
                            genre_data[genre] = {
                                'genre': genre,
                                'count': 0,
                                'total_budget': 0,
                                'total_revenue': 0,
                                'budget_count': 0,
                                'revenue_count': 0
                            }
                        
                        genre_data[genre]['count'] += 1
                        
                        if movie.get('budget') and movie['budget'] > 0:
                            genre_data[genre]['total_budget'] += movie['budget']
                            genre_data[genre]['budget_count'] += 1
                        
                        if movie.get('revenue') and movie['revenue'] > 0:
                            genre_data[genre]['total_revenue'] += movie['revenue']
                            genre_data[genre]['revenue_count'] += 1
            
            stats = []
            for genre, data in genre_data.items():
                avg_budget = (data['total_budget'] / data['budget_count'] / 1_000_000) if data['budget_count'] > 0 else 0
                avg_revenue = (data['total_revenue'] / data['revenue_count'] / 1_000_000) if data['revenue_count'] > 0 else 0
                avg_roi = (data['total_revenue'] / data['total_budget']) if data['total_budget'] > 0 else 0
                
                stats.append({
                    'genre': genre,
                    'count': data['count'],
                    'avg_budget': round(avg_budget, 0),
                    'avg_revenue': round(avg_revenue, 0),
                    'avg_roi': round(avg_roi, 1)
                })
            
            stats.sort(key=lambda x: x['avg_roi'], reverse=True)
        
        return JsonResponse({
            'status': 'ok',
            'data': stats
        })
    
    elif endpoint == 'top_movies':
        limit = int(request.GET.get('limit', 10))
        genre = request.GET.get('genre', '').strip()
        
        top_movies = DashboardAnalytics.get_top_movies(limit=limit, genre=genre if genre else None)
        
        if not top_movies:
            all_movies = MovieService.get_all_movies(limit=10000)
            
            valid_movies = []
            for movie in all_movies:
                if movie.get('budget') and movie['budget'] > 0 and movie.get('revenue') and movie['revenue'] > 0:
                    if genre:
                        if movie.get('genres') and genre in movie['genres']:
                            valid_movies.append(movie)
                    else:
                        valid_movies.append(movie)
            
            for movie in valid_movies:
                movie['roi'] = round(movie['revenue'] / movie['budget'], 1)
                movie['budget_m'] = round(movie['budget'] / 1_000_000, 0)
                movie['revenue_m'] = round(movie['revenue'] / 1_000_000, 0)
                movie['vote_average'] = round(movie.get('vote_average', 0), 1)
                if not movie.get('poster'):
                    movie['poster'] = ''
                if not movie.get('overview'):
                    movie['overview'] = ''
            
            valid_movies.sort(key=lambda x: x['roi'], reverse=True)
            top_movies = valid_movies[:limit]
        
        return JsonResponse({
            'status': 'ok',
            'data': top_movies
        })
    
    elif endpoint == 'simulate':
        try:
            data = json.loads(request.body)
            pitch = data.get('pitch', '')
            genre = data.get('genre', 'sci-fi')
            budget_tier = data.get('budget_tier', 'mid')
            
            similar_films_ml = MLMovieAnalyzer.analyze_movie_concept(pitch, top_n=5)
            
            if similar_films_ml:
                similar_films = []
                for film in similar_films_ml:
                    budget = film.get('budget', 0)
                    revenue = film.get('revenue', 0)
                    year = film.get('release_date', '')[:4] if film.get('release_date') else ''
                    
                    similar_films.append({
                        'title': film['title'],
                        'year': year,
                        'genres': film['genres'],
                        'poster': film.get('poster', ''),
                        'budget_m': round(budget / 1_000_000, 0) if budget > 0 else 0,
                        'revenue_m': round(revenue / 1_000_000, 0) if revenue > 0 else 0,
                        'vote_average': film.get('vote_average', 0),
                        'roi': round(revenue / budget, 1) if budget > 0 else 0,
                        'similarity': film['similarity'],
                        'overview': film.get('description', '')
                    })
                
                avg_revenue = sum(f['revenue_m'] for f in similar_films if f['revenue_m'] > 0) / max(1, len([f for f in similar_films if f['revenue_m'] > 0]))
                avg_roi = sum(f['roi'] for f in similar_films if f['roi'] > 0) / max(1, len([f for f in similar_films if f['roi'] > 0]))
                avg_similarity = sum(f['similarity'] for f in similar_films) / max(1, len(similar_films))
                
                viability = min(95, int(avg_similarity * 0.7 + (avg_roi * 5)))
                est_revenue_m = int(avg_revenue * 1.2)
                est_roi = round(avg_roi * 0.9, 1)
                risk = "Low" if viability > 75 else "Medium" if viability > 60 else "High"
                audience_match = min(95, int(avg_similarity))
                
                genre_counts = {}
                for film in similar_films_ml:
                    for g in film['genres'].split('|'):
                        g = g.strip()
                        if g:
                            genre_counts[g] = genre_counts.get(g, 0) + 1
                
                predicted_genre = max(genre_counts, key=genre_counts.get) if genre_counts else genre.title()
            else:
                viability = 75 + (len(pitch) % 20)
                est_revenue_m = 200 + (len(pitch) * 2)
                est_roi = 2.0 + (len(pitch) % 20) / 10
                risk = "Low" if viability > 85 else "Medium" if viability > 70 else "High"
                audience_match = 70 + (len(pitch) % 25)
                predicted_genre = genre.title()
                
                similar_films = []
                all_movies = MovieService.get_all_movies(limit=100)
                for movie in all_movies[:5]:
                    if movie.get('genres') and movie.get('budget', 0) > 0 and movie.get('revenue', 0) > 0:
                        budget = movie.get('budget', 0)
                        revenue = movie.get('revenue', 0)
                        roi = round(revenue / budget, 1) if budget > 0 else 0
                        similar_films.append({
                            'title': movie['title'],
                            'year': movie.get('year', ''),
                            'genres': movie['genres'],
                            'poster': movie.get('poster', ''),
                            'budget_m': round(budget / 1_000_000, 0),
                            'revenue_m': round(revenue / 1_000_000, 0),
                            'vote_average': round(movie.get('vote_average', 0), 1),
                            'roi': roi,
                            'similarity': 85 - (len(similar_films) * 5),
                            'overview': movie.get('overview', '')
                        })
            
            return JsonResponse({
                'status': 'ok',
                'data': {
                    'viability': viability,
                    'risk': risk,
                    'predicted_genre': predicted_genre,
                    'est_revenue_m': est_revenue_m,
                    'est_roi': est_roi,
                    'audience_match': audience_match,
                    'similar_films': similar_films
                }
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
    
    elif endpoint == 'stats':
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
    
    elif endpoint == 'demographics':
        demographics = DashboardAnalytics.get_user_demographics()
        
        if not demographics:
            total_users = User.objects.count()
            demographics = {
                'total_users': total_users,
                'by_gender': {},
                'by_age_group': {},
                'by_occupation': {}
            }
        
        return JsonResponse({
            'status': 'ok',
            'data': demographics
        })
    
    return JsonResponse({'error': 'Invalid endpoint'}, status=400)
