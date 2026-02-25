# Admin Dashboard

## Overview
The admin dashboard provides administrative users with comprehensive analytics and management capabilities for the WatchWish movie recommendation platform.

## Features

### Role-Based Access Control
- Users have a `role` field: 'user' or 'admin'
- Only users with 'admin' role can access the dashboard
- Admin users see a "Dashboard" link in the navigation bar

### Dashboard Analytics
The admin dashboard displays:
- **Total Films**: Number of movies in the database
- **Total Users**: All registered users
- **Admin Users**: Count of admin-level users
- **Regular Users**: Count of standard users
- **Genre Distribution**: Visual treemap showing film distribution across genres
- **Genre Statistics**: Bar chart of top genres by count
- **Recent Movies**: Table of latest movie entries

## Setup Instructions

### 1. Run Migrations
First, create and apply migrations for the custom User model:

```bash
python backend/manage.py makemigrations
python backend/manage.py migrate
```

### 2. Seed Admin User
Use the management command to create an admin user:

```bash
python backend/manage.py seed_admin
```

This creates an admin user with:
- **Username**: admin
- **Email**: admin@watchwish.com
- **Password**: admin123
- **Role**: admin

### 3. Access the Dashboard
1. Start the development server:
   ```bash
   python backend/manage.py runserver
   ```

2. Navigate to http://localhost:8000/accounts/login/

3. Login with the admin credentials

4. Click on "Dashboard" in the navigation bar or visit http://localhost:8000/dashboard/

## API Endpoints

### Dashboard API
- **URL**: `/dashboard/api/?endpoint=stats`
- **Method**: GET
- **Auth**: Admin role required
- **Response**: JSON with film and user statistics

## Design
The dashboard is inspired by the CineMetrics design from `cinema_dashboard.html`, featuring:
- Dark theme with cinematic styling
- Sidebar navigation
- KPI cards with gradients
- Interactive D3.js treemap visualization
- Chart.js bar charts
- Responsive grid layout

## Security
- Access control via `@admin_required` decorator
- Users without admin role are redirected to home page
- Authentication required for all dashboard routes
