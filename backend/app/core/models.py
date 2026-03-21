from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Float, DateTime, ForeignKey, Interval
from app.core.database import Base
import enum
from datetime import datetime

class SessionType(str, enum.Enum):
    RACE = "Race"
    QUALIFYING = "Qualifying"
    PRACTICE = "Practice"

class EventType(str, enum.Enum):
    RACE_START = "RACE_START"
    LAP_START = "LAP_START"
    POSITION_CHANGE = "POSITION_CHANGE"
    OVERTAKE = "OVERTAKE"
    PIT_STOP = "PIT_STOP"
    FASTEST_LAP = "FASTEST_LAP"
    RADIO_MESSAGE = "RADIO_MESSAGE"
    STRATEGY = "STRATEGY"
    AI_COMMENTARY = "AI_COMMENTARY"
    RACE_END = "RACE_END"

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True, index=True)
    year = Column(Integer, index=True)
    race_name = Column(String)
    session_type = Column(SQLEnum(SessionType))
    circuit_name = Column(String)

class Lap(Base):
    __tablename__ = "laps"
    
    lap_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"))
    driver = Column(String, index=True)
    lap_number = Column(Integer)
    lap_time = Column(Float) # store as seconds for simplicity
    position = Column(Integer)
    tire_compound = Column(String)
    tire_age = Column(Integer)
