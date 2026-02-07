import json
from django.core.management.base import BaseCommand
from movies.db import get_movies_collection


class Command(BaseCommand):
    help = 'Load movie recommendation data from JSON file into MongoDB'

    def handle(self, *args, **kwargs):
        collection = get_movies_collection()
        
        collection.delete_many({})
        self.stdout.write('Cleared existing movie data')
        
        with open('data/model_movies_rec.json', 'r', encoding='utf-8') as f:
            all_movies = {}
            for line in f:
                user_data = json.loads(line.strip())
                for movie in user_data['recommendations']:
                    movie_id = movie['movieId']
                    if movie_id not in all_movies:
                        all_movies[movie_id] = {
                            'movieId': movie_id,
                            'title': movie['title'],
                            'genres': movie['genres']
                        }
            
            if all_movies:
                collection.insert_many(list(all_movies.values()))
                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(all_movies)} movies'))
            else:
                self.stdout.write(self.style.WARNING('No movies found in data'))
