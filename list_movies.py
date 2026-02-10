import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.db import get_movies_collection

def list_popular_movies():
    print("Fetching movies from DB...")
    collection = get_movies_collection()
    # just get 10 movies, maybe sort by something if possible, or just first 10
    movies = list(collection.find({}, {'title': 1}).limit(20))
    
    print(f"Found {len(movies)} movies. Examples:")
    for m in movies:
        print(f"- {m.get('title')}")

if __name__ == "__main__":
    list_popular_movies()
