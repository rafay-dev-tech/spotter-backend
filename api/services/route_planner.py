import requests
from datetime import datetime, timedelta
from typing import Dict, List
import os
import json

class RoutePlanner:
    def __init__(self):
        self.OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
        self.MAX_DRIVING_HOURS = 11
        self.MAX_ON_DUTY_HOURS = 14
        self.REQUIRED_REST_HOURS = 10

    def _validate_location(self, location: str) -> bool:
        """Validate if a location string is reasonable"""
        # Check if location is too short or contains only numbers
        if len(location.strip()) < 2 or location.strip().isdigit():
            return False
        return True

    def _are_coordinates_same(self, coords1: tuple, coords2: tuple, tolerance: float = 0.0001) -> bool:
        """Check if two coordinate pairs are the same within a small tolerance"""
        return (abs(coords1[0] - coords2[0]) < tolerance and 
                abs(coords1[1] - coords2[1]) < tolerance)

    def _get_coordinates(self, location: str) -> tuple:
        try:
            # Using Nominatim for geocoding
            url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
            headers = {
                'User-Agent': 'ELD Backend/1.0'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                raise ValueError("Location does not exist")
            
            # Get the first result
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            return lat, lon
        except Exception:
            raise ValueError("Location does not exist")

    def calculate_route(self, origin: str, pickup: str, destination: str, current_hours: float) -> Dict:
        try:
            # Validate locations
            if not all([self._validate_location(loc) for loc in [origin, pickup, destination]]):
                raise ValueError("One or more locations are invalid")

            # Get coordinates
            origin_coords = self._get_coordinates(origin)
            pickup_coords = self._get_coordinates(pickup)
            dest_coords = self._get_coordinates(destination)

            if not all([origin_coords, pickup_coords, dest_coords]):
                raise ValueError("Could not find coordinates for one or more locations")

            # Check for duplicate locations
            if origin == pickup:
                raise ValueError("Current location and pickup location cannot be the same")
            if pickup == destination:
                raise ValueError("Pickup location and destination cannot be the same")
            if origin == destination:
                raise ValueError("Current location and destination cannot be the same")

            # Calculate routes
            waypoints = [
                f"{origin_coords[1]},{origin_coords[0]}",
                f"{pickup_coords[1]},{pickup_coords[0]}",
                f"{dest_coords[1]},{dest_coords[0]}"
            ]

            url = f"{self.OSRM_URL}/{';'.join(waypoints)}"
            response = requests.get(url)
            
            if response.status_code == 400:
                raise ValueError("Location does not exist")
            
            response.raise_for_status()
            route_data = response.json()

            if route_data.get('code') != 'Ok':
                raise ValueError("Location does not exist")

            # Extract distance and duration
            total_distance = route_data['routes'][0]['distance'] / 1609.34  # Convert meters to miles
            total_duration = route_data['routes'][0]['duration'] / 3600  # Convert seconds to hours

            # Calculate required stops
            remaining_hours = self.MAX_DRIVING_HOURS - current_hours
            stops = self._calculate_required_stops(total_duration, remaining_hours)

            return {
                'total_distance': total_distance,
                'total_duration': total_duration,
                'required_stops': stops,
                'waypoints': [
                    {'lat': origin_coords[0], 'lng': origin_coords[1]},
                    {'lat': pickup_coords[0], 'lng': pickup_coords[1]},
                    {'lat': dest_coords[0], 'lng': dest_coords[1]}
                ]
            }
        except ValueError as e:
            raise e
        except Exception:
            raise ValueError("Location does not exist")

    def _calculate_required_stops(self, total_duration: float, remaining_hours: float) -> List[Dict]:
        try:
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
                    'time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                current_time += timedelta(hours=self.REQUIRED_REST_HOURS)
                remaining_hours = self.MAX_DRIVING_HOURS

            return stops
        except Exception:
            raise ValueError("Location does not exist") 