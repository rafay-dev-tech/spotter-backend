# backend/api/services/route_planner.py
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import os
import time
from urllib.parse import quote

class RoutePlanner:
    def __init__(self):
        self.OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
        self.MAX_DRIVING_HOURS = 11
        self.MAX_ON_DUTY_HOURS = 14
        self.REQUIRED_REST_HOURS = 10
        
        # Comprehensive list of major US cities with their coordinates
        self.CITY_COORDINATES = {
            # Northeast
            "new york": {"lat": 40.7128, "lng": -74.0060},
            "boston": {"lat": 42.3601, "lng": -71.0589},
            "philadelphia": {"lat": 39.9526, "lng": -75.1652},
            
            # South
            "houston": {"lat": 29.7604, "lng": -95.3698},
            "dallas": {"lat": 32.7767, "lng": -96.7970},
            "san antonio": {"lat": 29.4241, "lng": -98.4936},
            "austin": {"lat": 30.2672, "lng": -97.7431},
            "miami": {"lat": 25.7617, "lng": -80.1918},
            "atlanta": {"lat": 33.7490, "lng": -84.3880},
            
            # Midwest
            "chicago": {"lat": 41.8781, "lng": -87.6298},
            "detroit": {"lat": 42.3314, "lng": -83.0458},
            "cleveland": {"lat": 41.4993, "lng": -81.6944},
            
            # West
            "los angeles": {"lat": 34.0522, "lng": -118.2437},
            "san francisco": {"lat": 37.7749, "lng": -122.4194},
            "seattle": {"lat": 47.6062, "lng": -122.3321},
            "portland": {"lat": 45.5155, "lng": -122.6789},
            "las vegas": {"lat": 36.1699, "lng": -115.1398},
            "phoenix": {"lat": 33.4484, "lng": -112.0740},
            "denver": {"lat": 39.7392, "lng": -104.9903},
            
            # Additional cities
            "washington dc": {"lat": 38.9072, "lng": -77.0369},
            "baltimore": {"lat": 39.2904, "lng": -76.6122},
            "charlotte": {"lat": 35.2271, "lng": -80.8431},
            "orlando": {"lat": 28.5383, "lng": -81.3792},
            "nashville": {"lat": 36.1627, "lng": -86.7816},
            "salt lake city": {"lat": 40.7608, "lng": -111.8910},
            "oklahoma city": {"lat": 35.4676, "lng": -97.5164},
            "kansas city": {"lat": 39.0997, "lng": -94.5786},
            "st louis": {"lat": 38.6270, "lng": -90.1994},
            "minneapolis": {"lat": 44.9778, "lng": -93.2650}
        }

    def _normalize_location(self, location: str) -> str:
        """Normalize location string for matching"""
        return location.lower().replace(',', '').replace('usa', '').strip()

    def _get_coordinates(self, location: str) -> tuple:
        """Get coordinates from predefined city list"""
        normalized_location = self._normalize_location(location)
        
        # Try to match the location with our predefined cities
        for city, coords in self.CITY_COORDINATES.items():
            if city in normalized_location or normalized_location in city:
                return (coords["lat"], coords["lng"])
        
        # If no match found, try to extract the city name before the state
        city_parts = normalized_location.split()
        if len(city_parts) >= 1:
            city_name = city_parts[0]
            for known_city, coords in self.CITY_COORDINATES.items():
                if city_name in known_city or known_city in city_name:
                    return (coords["lat"], coords["lng"])
        
        raise ValueError(f"Location not found in database: {location}. Please use a major US city name.")

    def calculate_route(self, origin: str, pickup: str, destination: str, current_hours: float) -> Dict:
        try:
            # Get coordinates
            origin_coords = self._get_coordinates(origin)
            pickup_coords = self._get_coordinates(pickup)
            dest_coords = self._get_coordinates(destination)

            if not all([origin_coords, pickup_coords, dest_coords]):
                raise ValueError("Could not find coordinates for one or more locations")

            # Calculate routes
            waypoints = [
                f"{origin_coords[1]},{origin_coords[0]}",
                f"{pickup_coords[1]},{pickup_coords[0]}",
                f"{dest_coords[1]},{dest_coords[0]}"
            ]

            url = f"{self.OSRM_URL}/{';'.join(waypoints)}"
            response = requests.get(url)
            route_data = response.json()

            if route_data.get('code') != 'Ok':
                raise ValueError(f"Route calculation failed: {route_data.get('message', 'Unknown error')}")

            # Extract distance and duration
            total_distance = route_data['routes'][0]['distance'] / 1609.34  # Convert meters to miles
            total_duration = route_data['routes'][0]['duration'] / 3600  # Convert seconds to hours

            # Calculate required stops
            remaining_hours = self.MAX_DRIVING_HOURS - current_hours
            stops = self._calculate_required_stops(total_duration, remaining_hours)

            return {
                'total_distance': round(total_distance, 2),
                'total_duration': round(total_duration, 2),
                'required_stops': stops,
                'waypoints': [
                    {'lat': origin_coords[0], 'lng': origin_coords[1]},
                    {'lat': pickup_coords[0], 'lng': pickup_coords[1]},
                    {'lat': dest_coords[0], 'lng': dest_coords[1]}
                ]
            }
            
        except Exception as e:
            raise ValueError(f"Route calculation failed: {str(e)}")

    def _calculate_required_stops(self, total_duration: float, remaining_hours: float) -> List[Dict]:
        stops = []
        current_time = datetime.now()
        hours_driven = 0
        
        while hours_driven < total_duration:
            if hours_driven + remaining_hours >= total_duration:
                break
                
            hours_driven += remaining_hours
            current_time += timedelta(hours=remaining_hours)
            
            # Add required rest stop
            stops.append({
                'type': 'rest',
                'duration': self.REQUIRED_REST_HOURS,
                'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'hours_completed': round(hours_driven, 2)
            })
            
            current_time += timedelta(hours=self.REQUIRED_REST_HOURS)
            remaining_hours = self.MAX_DRIVING_HOURS

        return stops