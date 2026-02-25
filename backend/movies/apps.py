from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
    
    def ready(self):
        from .services import MLMovieAnalyzer, DashboardAnalytics
        import threading
        
        def init_ml():
            try:
                print("Initializing ML Movie Analyzer...")
                MLMovieAnalyzer.initialize()
                print("ML Movie Analyzer initialized successfully")
                
                print("Loading Dashboard Analytics data...")
                DashboardAnalytics.load_data()
                print("Dashboard Analytics loaded successfully")
            except Exception as e:
                print(f"ML initialization warning: {e}")
        
        thread = threading.Thread(target=init_ml, daemon=True)
        thread.start()
