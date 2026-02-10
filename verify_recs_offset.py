import os
import django
import sys
import time

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.services import MovieService
from movies.db import get_movies_collection, get_user_ratings_collection

def verify_live_recs_offset():
    print("Verifying Live Recommendations with Offset...")
    
    # 1. Create a dummy Django user ID (simulate request.user.id = 1)
    django_user_id = 1
    offset_user_id = django_user_id + 1000000
    
    # Clear existing ratings for this offset user
    ratings_col = get_user_ratings_collection()
    ratings_col.delete_many({'userId': offset_user_id})
    print(f"Cleared ratings for offset user {offset_user_id}")
    
    # 2. Check cold start (should be empty)
    recs = MovieService.get_user_recommendations(offset_user_id)
    print(f"Cold start recs count: {len(recs)}")
    
    # 3. Rate some movies (simulating rate_movie view logic)
    # Find some Horror movies to rate
    movies_col = get_movies_collection()
    horror_movies = list(movies_col.find({'genres': {'$regex': 'Horror'}}).limit(5))
    
    if not horror_movies:
        print("Error: No Horror movies found to rate!")
        return
        
    print(f"Rating {len(horror_movies)} Horror movies with 5 stars:")
    for movie in horror_movies:
        print(f" - {movie['title']}")
        MovieService.add_user_rating(offset_user_id, movie['movieId'], 5)
        
    # 4. Get recommendations again
    # The view calls get_user_recommendations. 
    # If using 'live' logic, it should call generate_live_recommendations if not found in pre-computed.
    # MovieService.get_user_recommendations calls generate_live_recommendations if fallback enabled.
    
    recs = MovieService.generate_live_recommendations(offset_user_id)
    print(f"\nGenerated {len(recs)} live recommendations:")
    for movie in recs:
        print(f" - {movie['title']} (Score: {movie.get('recommendation_score')})")
        
    # Verify genres of recommendations
    horror_count = 0
    for movie in recs:
        if 'Horror' in movie.get('genres', ''):
            horror_count += 1
            
    print(f"\nHorror movies in recommendations: {horror_count}/{len(recs)}")
    
    if len(recs) > 0 and horror_count > 0:
        print("SUCCESS: Live recommendations generated relevant movies for Offset User!")
    else:
        print("FAILURE: No relevant recommendations generated.")

if __name__ == "__main__":
    verify_live_recs_offset()
