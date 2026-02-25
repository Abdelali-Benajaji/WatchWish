# Admin Dashboard

## Overview
The admin dashboard provides administrative users with comprehensive analytics and management capabilities for the WatchWish movie recommendation platform, powered by real data from CSV files and machine learning models.

## Enhanced Features

### Data-Driven Analytics
The dashboard now uses real data from `/data/dashboard_data/`:
- **data_of_all_films.csv**: 27,000+ movies with full financial data (budget, revenue, ROI)
- **users.csv**: User demographics (age groups, gender, occupation)
- **films20m.csv**: Extended movie metadata

### Machine Learning Integration

#### TF-IDF Movie Analyzer
Based on training in `TrainingTF-IDF.ipynb` and `Thinking.ipynb`, the Movie Analyzer provides:
- **Text Vectorization**: TF-IDF analysis of movie descriptions
- **Similarity Matching**: Cosine similarity to find comparable films
- **Metadata Soup**: Combines title, description, and genres for accurate matching
- **Real-Time Predictions**: ROI, revenue, and viability scores based on similar films

#### How It Works
1. User enters a movie concept/pitch
2. System creates TF-IDF vector from the text
3. Compares against 27k+ pre-vectorized movies
4. Returns top 5 most similar films with:
   - Similarity percentage (TF-IDF cosine score)
   - Financial performance (budget, revenue, ROI)
   - Predicted outcomes for the new concept

### Dashboard Features

#### 1. KPI Cards (Real Data)
- **Total Movies**: Count from CSV data
- **Total Revenue**: Aggregated revenue in billions
- **Average ROI**: Mean return on investment across all films
- **Average Rating**: Community ratings

#### 2. Movie Analyzer (AI Powered)
- Input movie concept description
- Select genre and budget tier
- Get AI-powered analysis:
  - Viability score (0-100%)
  - Predicted ROI
  - Estimated revenue
  - Risk assessment (Low/Medium/High)
  - Similar films with match percentages
  - Audience match score

#### 3. ROI vs Budget Charts
- Interactive bar chart and scatter plot
- Real statistics from CSV data
- Click any genre to drill down
- Shows average budget and revenue per genre

#### 4. Genre Performance Analysis
- Top 10 movies by ROI with real data
- Genre-specific statistics
- Market share calculations
- Click any movie for detailed modal

#### 5. Audience Demographics
- Age group distribution from users.csv
- Gender breakdown
- Occupation statistics
- Genre-specific audience insights

### Role-Based Access Control
- Users have a `role` field: 'user' or 'admin'
- Only users with 'admin' role can access the dashboard
- Admin users see a "Dashboard" link in the navigation bar

## Setup Instructions

### 1. Install Dependencies
Ensure you have the ML dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pandas
- numpy
- scikit-learn

### 2. Run Migrations
```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
```

### 3. Seed Admin User
```bash
python backend/manage.py seed_admin
```

Creates admin user with:
- **Username**: admin
- **Email**: admin@watchwish.com
- **Password**: admin123
- **Role**: admin

### 4. Start the Server
```bash
python backend/manage.py runserver
```

The ML analyzer will automatically initialize on startup:
- Loads CSV data
- Trains TF-IDF vectorizer
- Pre-computes similarity matrix
- Caches in memory for fast queries

### 5. Access the Dashboard
1. Navigate to http://localhost:8000/accounts/login/
2. Login with admin credentials
3. Click "Dashboard" or visit http://localhost:8000/dashboard/

## API Endpoints

### Dashboard API
- **Base URL**: `/admin/dashboard/api/`
- **Auth**: Admin role required

#### Endpoints:
1. **KPIs**: `?endpoint=kpis`
   - Returns financial KPIs from CSV data
   
2. **Genre Stats**: `?endpoint=genre_stats`
   - Returns performance metrics per genre
   
3. **Top Movies**: `?endpoint=top_movies&limit=10&genre=Action`
   - Returns top performing movies
   - Optional genre filter
   
4. **Demographics**: `?endpoint=demographics`
   - Returns user demographic data
   
5. **Movie Analyzer** (POST): `?endpoint=simulate`
   - Body: `{"pitch": "movie concept", "genre": "sci-fi", "budget_tier": "mid"}`
   - Returns AI analysis with similar films

## ML Model Details

### TF-IDF Vectorizer Configuration
- **Max Features**: 5000
- **N-gram Range**: (1, 2) - unigrams and bigrams
- **Stop Words**: English
- **Min DF**: 2 - minimum document frequency
- **Max DF**: 0.8 - maximum document frequency

### Metadata Soup Composition
For each movie, combines:
- Title (2x weight)
- Description (full text)
- Genres (2x weight, pipe-separated)

Example:
```
"toy story toy story in a world where toys live their life... family comedy animation adventure family comedy animation adventure"
```

### Performance
- **Initialization**: ~5-10 seconds (one-time on startup)
- **Query Time**: <100ms for similarity search
- **Memory Usage**: ~100-200MB for vectorized data

## Design
The dashboard features:
- Dark cinematic theme
- Gradient accent colors (purple to cyan)
- Sidebar navigation
- Interactive Chart.js visualizations
- Modal overlays for movie details
- Responsive grid layout
- Real-time data updates

## Security
- Access control via `@admin_required` decorator
- CSRF protection on POST endpoints
- Users without admin role are redirected
- Authentication required for all routes

## Implementation Summary

### What Was Built
1. **ML Movie Analyzer Service** - TF-IDF based similarity matching
2. **Dashboard Analytics Service** - Real-time CSV data processing
3. **Enhanced API Endpoints** - KPIs, genre stats, demographics, movie analysis
4. **Auto-initialization** - Background loading on app startup
5. **Real Data Integration** - 27k+ movies, user demographics from CSV

### Files Modified/Created
- `backend/movies/services.py` - Added `MLMovieAnalyzer` and `DashboardAnalytics` classes
- `backend/movies/views.py` - Enhanced dashboard API endpoints with real data
- `backend/movies/apps.py` - Added auto-initialization on startup
- `backend/static/js/admin_dashboard.js` - Enhanced with demographics loading
- `backend/movies/README.md` - Comprehensive documentation
- `README.md` - Added admin dashboard section
- `AGENTS.md` - Added enhancement summary

### How to Use
1. Start server: `python backend/manage.py runserver`
2. Login as admin user
3. Navigate to `/dashboard/`
4. Try the Movie Analyzer:
   - Enter a movie concept
   - See AI-powered predictions
   - View similar films with match scores
5. Explore interactive charts and click genres for details

### Data Flow
1. **On Startup**: CSV data loads → TF-IDF trains → Matrix cached
2. **User Request**: Concept text → Vectorize → Compare → Return top 5
3. **Analysis**: Similar films → Calculate avg metrics → Predict outcomes
4. **Display**: Real data powers KPIs, charts, and tables

## Future Enhancements
- Genre-specific ML models
- Time-series trend analysis
- Collaborative filtering integration
- A/B testing for recommendations
- Real-time streaming analytics
- Neural network models for deeper analysis
- Cast/crew similarity matching
- Box office prediction models
