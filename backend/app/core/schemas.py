from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.core.models import EventType

class EventMessage(BaseModel):
    event_type: EventType
    message: str
    driver: Optional[str] = None
    lap: int
    additional_data: Optional[Any] = None
    timestamp: datetime = datetime.now()

class PaceAnalysis(BaseModel):
    driver: str
    average_pace: float
    recent_pace: float
    tire_compound: str
    tire_age: int
    degradation_rate: float
    predicted_stint_length: int

class DriverTiming(BaseModel):
    driver: str
    position: int
    lap_time: float
    gap_to_leader: float
    interval_ahead: float
    tire_compound: str
    tire_age: int
    pit_stops: int
    team_color: str
    team_logo_url: str
    driver_image_url: str
    status: str # "Running", "DNF", "Finished", etc.
    lap_progress: float # 0.0 to 1.0 progress on current lap

class LapUpdate(BaseModel):
    lap_number: int
    events: List[EventMessage]
    timing: List[DriverTiming]
    positions: Any # e.g. track coordinates
    circuit_path: Optional[str] = None
    summary: Any
