# ELD Trip Planner - Backend

A Django-based backend API for the ELD (Electronic Logging Device) Trip Planner system. This service handles route calculations, HOS compliance, and log sheet generation.

## Features

- Route calculation with rest stops
- HOS (Hours of Service) compliance verification
- Electronic log sheet generation
- Trip data persistence
- Geocoding service integration
- OSRM route planning integration

## Tech Stack

- Python 3.8+
- Django 4.2.7
- Django REST Framework 3.14.0
- SQLite database
- OpenStreetMap/OSRM for routing
- Nominatim for geocoding

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd eld-trip-planner/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
DJANGO_SECRET_KEY='your-secret-key'
DEBUG=True
GOOGLE_MAPS_API_KEY='your-google-maps-api-key'
```

5. Apply database migrations:
```bash
python manage.py makemigrations api
python manage.py migrate
```

6. Run the development server:
```bash
python manage.py runserver
```


7. Run the Test Cases:
```bash
python manage.py test api.tests.test_views
```

## Project Structure

The `api/` directory contains all the api files :

- **migrations/**: Database migrations
- **services/**: Business logic services
- **eld_backend/**: Project settings
- **requirements.txt**: Python dependencies
- **models.py**: Database models
- **serializers.py**: API serializers
- **views.py**: API views
- **manage.py**: Django management script


## Models

### Trip
```python
class Trip(models.Model):
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours = models.FloatField()
    total_distance = models.FloatField(null=True)
    estimated_duration = models.FloatField(null=True)
```

### LogSheet
```python
class LogSheet(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status_grid = models.JSONField()
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code.

## Deployment

1. Set DEBUG=False in production
2. Configure proper database (PostgreSQL recommended)
3. Set up proper CORS settings
4. Use proper web server (Gunicorn/uWSGI)
5. Set up static files serving
