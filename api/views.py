from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .models import Trip, LogSheet
from .serializers import TripSerializer, LogSheetSerializer
from .services.route_planner import RoutePlanner
from .services.log_generator import LogGenerator

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    @action(detail=False, methods=['post'])
    def plan_route(self, request):
        try:
            # Validate input data
            required_fields = ['current_location', 'pickup_location', 'dropoff_location', 'current_cycle_hours']
            errors = []
            
            # Check for missing fields
            for field in required_fields:
                if field not in request.data:
                    errors.append(f"{field} is required")
            
            # Validate current_cycle_hours
            if 'current_cycle_hours' in request.data:
                try:
                    current_cycle_hours = float(request.data['current_cycle_hours'])
                    if current_cycle_hours < 0:
                        errors.append("Hours must be a positive number")
                except (ValueError, TypeError):
                    errors.append("Hours must be a valid number")

            # Return field errors if any
            if errors:
                return Response(
                    {'errors': errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            planner = RoutePlanner()
            try:
                route_data = planner.calculate_route(
                    request.data['current_location'],
                    request.data['pickup_location'],
                    request.data['dropoff_location'],
                    current_cycle_hours
                )
            except ValueError as e:
                error_message = str(e)
                if "cannot be the same" in error_message:
                    if "Current location and pickup location" in error_message:
                        errors.append("Pickup location must be different from current location")
                    elif "Pickup location and destination" in error_message:
                        errors.append("Destination must be different from pickup location")
                    elif "Current location and destination" in error_message:
                        errors.append("Destination must be different from current location")
                    return Response(
                        {'errors': errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {'errors': ["Location does not exist"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create trip record
            trip_serializer = self.serializer_class(data={
                **request.data,
                'total_distance': route_data['total_distance'],
                'estimated_duration': route_data['total_duration']
            })
            
            if trip_serializer.is_valid():
                trip = trip_serializer.save()
                # Generate log sheets
                log_generator = LogGenerator()
                log_sheets = log_generator.generate_logs(trip, route_data)
                
                return Response({
                    'trip': trip_serializer.data,
                    'route': route_data,
                    'log_sheets': LogSheetSerializer(log_sheets, many=True).data
                })
            
            # Return serializer validation errors
            return Response(
                {'errors': list(trip_serializer.errors.values())},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            return Response(
                {'errors': ["Location does not exist"]},
                status=status.HTTP_400_BAD_REQUEST
            )

class LogSheetViewSet(viewsets.ModelViewSet):
    queryset = LogSheet.objects.all()
    serializer_class = LogSheetSerializer

    def get_queryset(self):
        queryset = LogSheet.objects.all()
        trip_id = self.request.query_params.get('trip', None)
        if trip_id is not None:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset