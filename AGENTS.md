1→# Agent Guide
2→
3→## Setup & Commands
4→- **Setup**: `python -m venv venv` → Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix) → `pip install -r requirements.txt`
5→- **Build**: N/A (Django doesn't require build step)
6→- **Lint**: No linter configured
7→- **Tests**: `python backend/manage.py test`
8→- **Dev Server**: `python backend/manage.py runserver` or `docker-compose up`
9→
10→## Tech Stack
11→- **Backend**: Django 5.2 + Djongo (MongoDB ORM)
12→- **Database**: MongoDB (via docker-compose)
13→- **ML Libraries**: scikit-learn, pandas, numpy
14→- **Architecture**: Standard Django structure with `config` (project settings) and `movies` (app)
15→
16→## Structure
17→- `backend/config/`: Django project settings, URLs, WSGI/ASGI
18→- `backend/movies/`: Main app with models, views, tests
19→- `requirements.txt`: Python dependencies at repo root
20→- `venv/`: Virtual environment (gitignored)
21→
22→## Code Style
23→- Standard Django conventions
24→- No comments unless complex logic requires explanation
25→