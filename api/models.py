from django.db import models

class Trip(models.Model):
    current_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    current_cycle_hours = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_distance = models.FloatField(null=True)
    estimated_duration = models.FloatField(null=True)  # in hours

class LogSheet(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='log_sheets')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status_grid = models.JSONField()  # Stores the 24-hour grid data 