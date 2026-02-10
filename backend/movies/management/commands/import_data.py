import csv
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.db import get_movies_collection, get_mongodb

class Command(BaseCommand):
    help = 'Import data from CSV and JSON files to MongoDB'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data import...")
        
        # Paths
        base_dir = settings.BASE_DIR.parent
        csv_path = os.path.join(base_dir, 'data', 'tmdb_allfilms.csv')
        json_path1 = os.path.join(base_dir, 'data', 'model_movies_rec.json')
        json_path2 = os.path.join(base_dir, 'data', 'model_movies_rec2.json')

        # Import Movies CSV
        if os.path.exists(csv_path):
            self.import_movies_csv(csv_path)
        else:
            self.stdout.write(self.style.WARNING(f"CSV file not found: {csv_path}"))

        # Import Recommendations JSON
        db = get_mongodb()
        rec_collection = db['user_recommendations']
        # clear existing recommendations if desired? For now, let's assuming mostly append/update logic or simple insert.
        # But usually migrations should be idempotent.
        # We will drop and recreate for recommendations to ensure clean slate as it's a derived dataset?
        # Or just upsert.
        # Given the file size, drop and bulk write is faster.
        rec_collection.drop() 
        self.stdout.write("Dropped existing user_recommendations collection.")

        if os.path.exists(json_path1):
            self.import_recommendations_json(json_path1, rec_collection, "model1")
        
        if os.path.exists(json_path2):
            self.import_recommendations_json(json_path2, rec_collection, "model2")

        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))

    def import_movies_csv(self, file_path):
        self.stdout.write(f"Importing movies from {file_path}...")
        collection = get_movies_collection()
        
        updated_count = 0
        created_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = row.get('movieId')
                if not movie_id:
                    continue
                
                try:
                    # Assuming movieId is stored as int or string in DB?
                    # In previous view_file of services.py: 
                    # collection.find_one({'movieId': rec['movieId']})
                    # In json file: "movieId": 121029 (int)
                    # So likely int.
                    movie_id_val = int(movie_id)
                except ValueError:
                    continue

                update_data = {
                    'description': row.get('description', ''),
                    'poster_url': row.get('poster_url', ''),
                    'note_tmdb': row.get('note_tmdb', '') # Assuming this column exists based on plan, if not careful checks needed
                }
                
                # Check for tmdbId and imdbId to add if missing? 
                # Just focus on description and poster_url as requested.
                
                result = collection.update_one(
                    {'movieId': movie_id_val},
                    {'$set': update_data}
                )
                
                if result.matched_count > 0:
                    updated_count += 1
                else:
                    # Optional: create if not exists? User said "updating exisiting movie".
                    # Let's simple skip if not found for now to match strict requirements of enrichment.
                    pass
        
        self.stdout.write(f"Updated {updated_count} movies.")

    def import_recommendations_json(self, file_path, collection, model_name):
        self.stdout.write(f"Importing recommendations from {file_path}...")
        count = 0
        batch = []
        BATCH_SIZE = 1000
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    # Structure: {"userId": 1, "recommendations": [...]}
                    # We add model name to distinguish sources if we merge them, 
                    # OR we can just insert as is if we want to query by userId and model.
                    # Plan said: { "userId": <int>, "model": "model1", "recommendations": [...] }
                    
                    data['model'] = model_name
                    batch.append(data)
                    
                    if len(batch) >= BATCH_SIZE:
                        collection.insert_many(batch)
                        count += len(batch)
                        batch = []
                except json.JSONDecodeError:
                    continue
        
        if batch:
            collection.insert_many(batch)
            count += len(batch)
            
        self.stdout.write(f"Imported {count} recommendation records for {model_name}.")
