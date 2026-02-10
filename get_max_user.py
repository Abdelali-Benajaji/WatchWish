import os
import django
import sys
import pymongo

# Setup Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from movies.db import get_user_ratings_collection

def get_max_user_id():
    print("Finding max user ID...")
    collection = get_user_ratings_collection()
    
    # Try to find max userId
    # Assuming userId is integer
    max_user = collection.find_one(sort=[("userId", pymongo.DESCENDING)])
    
    if max_user:
        print(f"Max User ID found: {max_user.get('userId')}")
    else:
        print("No users found in ratings collection.")

if __name__ == "__main__":
    get_max_user_id()
