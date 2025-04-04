from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Trip, LogSheet
from datetime import date, time
import json

class TripViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.trip_url = reverse('trip-list')
        self.plan_route_url = reverse('trip-plan-route')
        
        # Sample valid trip data
        self.valid_trip_data = {
            'current_location': 'New York, NY',
            'pickup_location': 'Boston, MA',
            'dropoff_location': 'Philadelphia, PA',
            'current_cycle_hours': 5.5
        }

    def test_create_trip(self):
        """Test creating a new trip"""
        response = self.client.post(self.trip_url, self.valid_trip_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trip.objects.count(), 1)
        self.assertEqual(Trip.objects.get().current_location, 'New York, NY')

    def test_plan_route_success(self):
        """Test successful route planning"""
        response = self.client.post(self.plan_route_url, self.valid_trip_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('trip', response.data)
        self.assertIn('route', response.data)
        self.assertIn('log_sheets', response.data)
        
        # Check trip was created
        self.assertEqual(Trip.objects.count(), 1)
        
        # Check log sheets were created
        trip = Trip.objects.first()
        self.assertTrue(LogSheet.objects.filter(trip=trip).exists())

    def test_plan_route_missing_fields(self):
        """Test route planning with missing required fields"""
        invalid_data = {
            'current_location': 'New York, NY',
            'pickup_location': 'Boston, MA'
            # Missing dropoff_location and current_cycle_hours
        }
        
        response = self.client.post(self.plan_route_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_plan_route_invalid_cycle_hours(self):
        """Test route planning with invalid current_cycle_hours"""
        invalid_data = {
            **self.valid_trip_data,
            'current_cycle_hours': 'invalid'
        }
        
        response = self.client.post(self.plan_route_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_trip_list(self):
        """Test retrieving list of trips"""
        # Create a trip first
        Trip.objects.create(**self.valid_trip_data)
        
        response = self.client.get(self.trip_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_trip_detail(self):
        """Test retrieving a single trip"""
        trip = Trip.objects.create(**self.valid_trip_data)
        url = reverse('trip-detail', args=[trip.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_location'], trip.current_location)

class LogSheetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.trip = Trip.objects.create(
            current_location='New York, NY',
            pickup_location='Boston, MA',
            dropoff_location='Philadelphia, PA',
            current_cycle_hours=5.5
        )
        
        self.valid_log_data = {
            'trip': self.trip.id,
            'date': date.today(),
            'start_time': time(8, 0),
            'end_time': time(16, 0),
            'status_grid': json.dumps({
                'hours': [0] * 24,
                'status': ['off_duty'] * 24
            })
        }

    def test_create_log_sheet(self):
        """Test creating a new log sheet"""
        response = self.client.post(reverse('logsheet-list'), self.valid_log_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LogSheet.objects.count(), 1)
        
        log_sheet = LogSheet.objects.first()
        self.assertEqual(log_sheet.trip, self.trip)
        self.assertEqual(log_sheet.date, date.today())

    def test_get_log_sheets_for_trip(self):
        """Test retrieving log sheets for a specific trip"""
        # Create a log sheet
        LogSheet.objects.create(
            trip=self.trip,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(16, 0),
            status_grid={'hours': [0] * 24, 'status': ['off_duty'] * 24}
        )
        
        url = reverse('logsheet-list')
        response = self.client.get(url, {'trip': self.trip.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 