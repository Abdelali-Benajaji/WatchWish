from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from .models import User
from .services import MovieService, DashboardAnalytics
from .db import get_movies_collection, get_user_ratings_collection, get_user_recommendations_collection
import json

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Permissions', {'fields': ('role',)}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

class MovieAdminProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies Database'
        app_label = 'movies'

@admin.register(MovieAdminProxy)
class MovieAdmin(admin.ModelAdmin):
    change_list_template = 'admin/movies_changelist.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_module_permission(self, request):
        return request.user.is_staff
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        collection = get_movies_collection()
        
        total_movies = collection.count_documents({})
        
        movies_with_budget = collection.count_documents({'budget': {'$gt': 0}})
        movies_with_revenue = collection.count_documents({'revenue': {'$gt': 0}})
        
        try:
            movies = list(collection.find().limit(100).sort('movieId', -1))
            for movie in movies:
                movie['_id'] = str(movie['_id'])
                if movie.get('budget', 0) > 0 and movie.get('revenue', 0) > 0:
                    movie['roi'] = round(movie['revenue'] / movie['budget'], 2)
                else:
                    movie['roi'] = 0
            
            extra_context['movies'] = movies
        except Exception as e:
            print(f"Error fetching movies: {e}")
            extra_context['movies'] = []
        
        extra_context['total_movies'] = total_movies
        extra_context['movies_with_budget'] = movies_with_budget
        extra_context['movies_with_revenue'] = movies_with_revenue
        
        return super().changelist_view(request, extra_context)

class RatingsAdminProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = 'Rating'
        verbose_name_plural = 'User Ratings'
        app_label = 'movies'

@admin.register(RatingsAdminProxy)
class RatingsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/ratings_changelist.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_module_permission(self, request):
        return request.user.is_staff
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        collection = get_user_ratings_collection()
        
        total_ratings = collection.count_documents({})
        
        avg_rating_pipeline = [
            {'$group': {'_id': None, 'avg_rating': {'$avg': '$score'}}}
        ]
        
        try:
            avg_result = list(collection.aggregate(avg_rating_pipeline))
            avg_rating = round(avg_result[0]['avg_rating'], 2) if avg_result else 0
        except Exception as e:
            print(f"Error calculating average rating: {e}")
            avg_rating = 0
        
        unique_users = collection.distinct('userId')
        unique_movies = collection.distinct('movieId')
        
        try:
            ratings = list(collection.find().limit(100).sort('userId', -1))
            for rating in ratings:
                rating['_id'] = str(rating['_id'])
                
                movie = MovieService.get_movie(rating['movieId'])
                if movie:
                    rating['movie_title'] = movie.get('title', 'Unknown')
                else:
                    rating['movie_title'] = 'Unknown'
            
            extra_context['ratings'] = ratings
        except Exception as e:
            print(f"Error fetching ratings: {e}")
            extra_context['ratings'] = []
        
        extra_context['total_ratings'] = total_ratings
        extra_context['avg_rating'] = avg_rating
        extra_context['unique_users'] = len(unique_users)
        extra_context['unique_movies'] = len(unique_movies)
        
        return super().changelist_view(request, extra_context)

class RecommendationsAdminProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = 'Recommendation'
        verbose_name_plural = 'ML Recommendations'
        app_label = 'movies'

@admin.register(RecommendationsAdminProxy)
class RecommendationsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/recommendations_changelist.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_module_permission(self, request):
        return request.user.is_staff
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        collection = get_user_recommendations_collection()
        
        total_docs = collection.count_documents({})
        
        unique_users = collection.distinct('userId')
        
        model_counts = {}
        try:
            docs = collection.find()
            for doc in docs:
                model = doc.get('model', 'unknown')
                model_counts[model] = model_counts.get(model, 0) + 1
        except Exception as e:
            print(f"Error counting models: {e}")
        
        try:
            recs = list(collection.find().limit(50).sort('userId', -1))
            for rec in recs:
                rec['_id'] = str(rec['_id'])
                rec['rec_count'] = len(rec.get('recommendations', []))
                
                if rec.get('recommendations'):
                    top_rec = rec['recommendations'][0]
                    movie = MovieService.get_movie(top_rec['movieId'])
                    if movie:
                        rec['top_movie'] = movie.get('title', 'Unknown')
                        rec['top_score'] = round(top_rec.get('score', 0), 3)
                    else:
                        rec['top_movie'] = 'Unknown'
                        rec['top_score'] = 0
            
            extra_context['recommendations'] = recs
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
            extra_context['recommendations'] = []
        
        extra_context['total_docs'] = total_docs
        extra_context['unique_users'] = len(unique_users)
        extra_context['model_counts'] = model_counts
        
        return super().changelist_view(request, extra_context)

class AnalyticsAdminProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = 'Analytics'
        verbose_name_plural = 'Analytics Dashboard'
        app_label = 'movies'

@admin.register(AnalyticsAdminProxy)
class AnalyticsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/analytics_dashboard.html'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_module_permission(self, request):
        return request.user.is_staff
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        DashboardAnalytics.load_data()
        
        kpis = DashboardAnalytics.get_financial_kpis()
        genre_stats = DashboardAnalytics.get_genre_statistics()
        demographics = DashboardAnalytics.get_user_demographics()
        
        if not kpis:
            all_movies = MovieService.get_all_movies(limit=10000)
            total_movies = len(all_movies)
            total_revenue = sum(m.get('revenue', 0) for m in all_movies if m.get('revenue', 0) > 0)
            total_budget = sum(m.get('budget', 0) for m in all_movies if m.get('budget', 0) > 0)
            
            kpis = {
                'total_movies': total_movies,
                'total_revenue_b': round(total_revenue / 1_000_000_000, 1),
                'total_budget_b': round(total_budget / 1_000_000_000, 1),
                'avg_roi': round(total_revenue / total_budget, 1) if total_budget > 0 else 0,
                'avg_rating': 0
            }
        
        if not genre_stats:
            genre_stats = []
        
        extra_context['kpis'] = kpis
        extra_context['genre_stats'] = genre_stats[:10]
        extra_context['demographics'] = demographics
        
        genre_labels = [g['genre'] for g in genre_stats[:10]]
        genre_counts = [g['count'] for g in genre_stats[:10]]
        genre_revenues = [g['avg_revenue'] for g in genre_stats[:10]]
        
        extra_context['genre_labels_json'] = json.dumps(genre_labels)
        extra_context['genre_counts_json'] = json.dumps(genre_counts)
        extra_context['genre_revenues_json'] = json.dumps(genre_revenues)
        
        total_users = User.objects.count()
        admin_users = User.objects.filter(role='admin').count()
        regular_users = total_users - admin_users
        
        extra_context['total_users'] = total_users
        extra_context['admin_users'] = admin_users
        extra_context['regular_users'] = regular_users
        
        return super().changelist_view(request, extra_context)
