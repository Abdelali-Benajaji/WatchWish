import csv
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from movies.models import Movie


class Command(BaseCommand):
    help = 'Import movies from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing movie data'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        self.stdout.write(self.style.SUCCESS(f'Starting import from {csv_file}'))
        
        imported_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Parse date
                        release_date = None
                        if row.get('release_date'):
                            try:
                                release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
                            except ValueError:
                                pass
                        
                        # Parse JSON fields
                        genres = json.loads(row.get('genres', '[]')) if row.get('genres') else []
                        production_companies = json.loads(row.get('production_companies', '[]')) if row.get('production_companies') else []
                        production_countries = json.loads(row.get('production_countries', '[]')) if row.get('production_countries') else []
                        spoken_languages = json.loads(row.get('spoken_languages', '[]')) if row.get('spoken_languages') else []
                        keywords = json.loads(row.get('keywords', '[]')) if row.get('keywords') else []
                        
                        # Check if movie already exists
                        movie_id = row.get('id') or row.get('tmdb_id')
                        if movie_id and Movie.objects.filter(tmdb_id=movie_id).exists():
                            skipped_count += 1
                            continue
                        
                        # Create movie
                        movie = Movie.objects.create(
                            title=row.get('title', ''),
                            original_title=row.get('original_title', ''),
                            tagline=row.get('tagline', ''),
                            overview=row.get('overview', ''),
                            release_date=release_date,
                            release_year=int(row.get('release_year') or 0) if row.get('release_year') else None,
                            status=row.get('status', ''),
                            runtime=int(row.get('runtime') or 0) if row.get('runtime') else None,
                            vote_average=float(row.get('vote_average') or 0),
                            vote_count=int(row.get('vote_count') or 0),
                            popularity=float(row.get('popularity') or 0),
                            budget=int(row.get('budget') or 0),
                            revenue=int(row.get('revenue') or 0),
                            genres=genres,
                            original_language=row.get('original_language', ''),
                            spoken_languages=spoken_languages,
                            production_companies=production_companies,
                            production_countries=production_countries,
                            imdb_id=row.get('imdb_id', ''),
                            tmdb_id=int(movie_id) if movie_id else None,
                            poster_path=row.get('poster_path', ''),
                            backdrop_path=row.get('backdrop_path', ''),
                            homepage=row.get('homepage', ''),
                            keywords=keywords,
                            adult=row.get('adult', 'False').lower() == 'true',
                            video=row.get('video', 'False').lower() == 'true',
                        )
                        
                        imported_count += 1
                        
                        if imported_count % 100 == 0:
                            self.stdout.write(f'Imported {imported_count} movies...')
                    
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'Error importing movie: {str(e)}')
                        )
                        continue
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nImport completed!\n'
                    f'Imported: {imported_count}\n'
                    f'Skipped: {skipped_count}\n'
                    f'Errors: {error_count}'
                )
            )
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading file: {str(e)}')
            )
