from fastapi import APIRouter
from app.services.orchestrator import orchestrator
import asyncio
import fastf1
import os

# Create cache directory once at startup
os.makedirs('f1_cache', exist_ok=True)
fastf1.Cache.enable_cache('f1_cache')

router = APIRouter()

@router.get("/races/schedule")
def get_schedule(year: int = 2024):
    schedule = fastf1.get_event_schedule(year)
    races = schedule[schedule['EventFormat'] != 'testing']
    
    result = []
    for _, event in races.iterrows():
        result.append({
            "round": int(event['RoundNumber']),
            "name": event['EventName'],
            "location": event['Location'],
            "date": str(event['EventDate'])
        })
    return {"year": year, "races": result}

# ... rest of your routes unchanged
