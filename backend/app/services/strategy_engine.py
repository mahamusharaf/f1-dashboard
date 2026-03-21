from typing import List, Any
from app.core.schemas import EventMessage
from app.core.models import EventType
import random

class StrategyEngine:
    def __init__(self):
        self.ai_prompts = [
            "{driver} is managing the tires well to extend this stint.",
            "Expect a pit stop soon from {driver} if this pace drops.",
            "The undercut might be powerful here for {driver}.",
            "{driver} needs to find some clear air to make this strategy work."
        ]
        
    def generate_strategy_insight(self, lap_number: int, current_lap_data: List[Any]) -> List[EventMessage]:
        events = []
        
        # Every 5 laps, generate some AI commentary (simulated)
        if lap_number % 5 == 0 and current_lap_data:
            # Pick a random top 3 driver
            target = random.choice(current_lap_data[:3])
            msg = random.choice(self.ai_prompts).format(driver=target.driver)
            
            events.append(EventMessage(
                event_type=EventType.AI_COMMENTARY,
                message=f"AI Insight: {msg}",
                lap=lap_number,
                driver=target.driver
            ))
            
        # Simulated Strategy Pit Window Warning
        for driver_data in current_lap_data:
            tire_age = getattr(driver_data, 'tire_age', 0)
            if tire_age == 18:  # Arbitrary threshold
                events.append(EventMessage(
                     event_type=EventType.STRATEGY,
                     message=f"Strategy Warning: {driver_data.driver}'s soft tires are reaching the end of their life (Age: {tire_age}).",
                     lap=lap_number,
                     driver=driver_data.driver
                ))

        return events
