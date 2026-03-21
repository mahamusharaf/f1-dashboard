from typing import Dict, Any, List
from app.core.models import EventType
from app.core.schemas import EventMessage
from datetime import datetime

class EventAnalyzer:
    def __init__(self):
        # We store the latest known positions and lap times
        # to compare against new lap data and generate events.
        self.previous_positions: Dict[str, int] = {}
        self.best_lap_time: float = float('inf')

    def analyze_lap(self, lap_number: int, current_lap_data: List[Any]) -> List[EventMessage]:
        events = []
        
        # In a real scenario, current_lap_data would be a list of ORM models 
        # or dicts containing timing and telemetry data
        
        # 1. Race/Lap Start Events
        if lap_number == 1:
            events.append(EventMessage(
                event_type=EventType.RACE_START,
                message="Lights out and away we go!",
                lap=lap_number
            ))

        # We will loop through driver data to find overtakes, pit stops, etc.
        for driver_data in current_lap_data:
            driver = driver_data.driver
            pos = driver_data.position
            lap_time = driver_data.lap_time
            
            # Position Changes (Overtakes)
            if driver in self.previous_positions:
                prev_pos = self.previous_positions[driver]
                if pos < prev_pos:
                    events.append(EventMessage(
                        event_type=EventType.OVERTAKE,
                        message=f"{driver} has moved up to P{pos}!",
                        driver=driver,
                        lap=lap_number
                    ))

            # Fastest Lap
            if lap_time < self.best_lap_time:
                self.best_lap_time = lap_time
                events.append(EventMessage(
                    event_type=EventType.FASTEST_LAP,
                    message=f"New fastest lap by {driver}!",
                    driver=driver,
                    lap=lap_number,
                    additional_data={"time": lap_time}
                ))

            # Pit Stops (simplified logic: e.g. pit_stops incremented or tire_age == 1)
            if getattr(driver_data, 'tire_age', 0) == 1 and lap_number > 1:
                 events.append(EventMessage(
                    event_type=EventType.PIT_STOP,
                    message=f"{driver} is in the pits for new tires.",
                    driver=driver,
                    lap=lap_number
                ))

            self.previous_positions[driver] = pos

        return events
