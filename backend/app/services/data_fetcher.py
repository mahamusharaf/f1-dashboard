import fastf1
from sqlalchemy.orm import Session
from app.core import models

def load_session(db: Session, year: int, race_round: int, session_type: str):
    # Enable FastF1 cache
    fastf1.Cache.enable_cache('f1_cache') 
    
    # Load session data using FastF1
    session = fastf1.get_session(year, race_round, session_type)
    session.load()
    
    # Store session metadata in DB
    db_session = models.Session(
        session_id=f"{year}_{race_round}_{session_type}",
        year=year,
        race_name=session.event.EventName,
        session_type=models.SessionType(session_type),
        circuit_name=session.event.Location
    )
    
    db.merge(db_session)
    db.commit()
    
    return db_session

def get_lap_data(db: Session, session_id: str, lap_number: int):
    return db.query(models.Lap).filter(
        models.Lap.session_id == session_id,
        models.Lap.lap_number == lap_number
    ).all()
