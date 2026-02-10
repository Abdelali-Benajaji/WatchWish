import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.services import MovieService
from movies.db import get_movies_collection, get_user_ratings_collection

def verify_live_recs():
    print("Verifying Live Recommendations...")
    
    # 1. Create a dummy user ID
    user_id = 999999
    
    # Clear existing ratings for this user
    ratings_col = get_user_ratings_collection()
    ratings_col.delete_many({'userId': user_id})
    print(f"Cleared ratings for user {user_id}")
    
    # 2. Check cold start (should be empty)
    recs = MovieService.get_user_recommendations(user_id)
    print(f"Cold start recs count: {len(recs)}")
    
    # 3. Rate some movies
    # Find some Action movies to rate
    movies_col = get_movies_collection()
    action_movies = list(movies_col.find({'genres': {'$regex': 'Action'}}).limit(5))
    
    if not action_movies:
        print("Error: No Action movies found to rate!")
        return
        
    print(f"Rating {len(action_movies)} Action movies with 5 stars:")
    for movie in action_movies:
        print(f" - {movie['title']}")
        MovieService.add_user_rating(user_id, movie['movieId'], 5)
        
    # 4. Get recommendations again
    recs = MovieService.generate_live_recommendations(user_id)
    print(f"\nGenerated {len(recs)} live recommendations:")
    for movie in recs:
        print(f" - {movie['title']} (Score: {movie.get('recommendation_score')})")
        
    # Verify genres of recommendations
    action_count = 0
    for movie in recs:
        if 'Action' in movie.get('genres', ''):
            action_count += 1
            
    print(f"\nAction movies in recommendations: {action_count}/{len(recs)}")
    
    if len(recs) > 0 and action_count > 0:
        print("SUCCESS: Live recommendations generated relevant movies!")
    else:
        print("FAILURE: No relevant recommendations generated.")

if __name__ == "__main__":
    verify_live_recs()
