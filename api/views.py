from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
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
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {'error': f'Missing required field: {field}'}, 
                        status=400
                    )
            
            try:
                current_cycle_hours = float(request.data['current_cycle_hours'])
            except (ValueError, TypeError):
                return Response(
                    {'error': 'current_cycle_hours must be a valid number'}, 
                    status=400
                )

            planner = RoutePlanner()
            route_data = planner.calculate_route(
                request.data['current_location'],
                request.data['pickup_location'],
                request.data['dropoff_location'],
                current_cycle_hours
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
            return Response(trip_serializer.errors, status=400)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'}, 
                status=500
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