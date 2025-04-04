from datetime import datetime, timedelta
from typing import Dict, List
from ..models import Trip, LogSheet

class LogGenerator:
    def __init__(self):
        self.STATUS_OFF_DUTY = 'OFF'
        self.STATUS_SLEEPER = 'SB'
        self.STATUS_DRIVING = 'D'
        self.STATUS_ON_DUTY = 'ON'

    def generate_logs(self, trip: Trip, route_data: Dict) -> List[LogSheet]:
        log_sheets = []
        current_time = datetime.now()
        remaining_duration = route_data['total_duration']
        
        while remaining_duration > 0:
            # Create daily log sheet
            status_grid = self._initialize_status_grid()
            start_time = current_time.replace(hour=0, minute=0, second=0)
            
            # Fill status grid based on driving and rest periods
            hours_in_day = min(24, remaining_duration)
            current_hour = current_time.hour
            
            while current_hour < 24 and hours_in_day > 0:
                if hours_in_day >= 1:
                    status_grid[current_hour] = self.STATUS_DRIVING
                    hours_in_day -= 1
                current_hour += 1
            
            log_sheet = LogSheet.objects.create(
                trip=trip,
                date=current_time.date(),
                start_time=start_time.time(),
                end_time=(start_time + timedelta(hours=24)).time(),
                status_grid=status_grid
            )
            log_sheets.append(log_sheet)
            
            remaining_duration -= 24
            current_time += timedelta(days=1)
        
        return log_sheets

    def _initialize_status_grid(self) -> Dict[int, str]:
        return {hour: self.STATUS_OFF_DUTY for hour in range(24)} 