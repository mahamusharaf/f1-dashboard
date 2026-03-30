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
    # Filter only real races (not testing)
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

@router.get("/races/info")
def get_race_info():
    if not orchestrator.is_initialized:
        return {"status": "none"}
    return {
        "status": "initialized",
        "year": orchestrator.year,
        "round": orchestrator.race_round,
        "session_id": orchestrator.session_id,
        "total_laps": orchestrator.total_laps
    }

@router.post("/races/load")
def load_race(year: int = 2023, race_round: int = 1):
    try:
        orchestrator.initialize_race(year, race_round)
        return {"status": "loaded", "session_id": orchestrator.session_id, "total_laps": orchestrator.total_laps}
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/stream/start")
async def start_stream():
    if not orchestrator.is_initialized:
        return {"status": "error", "message": "Race not initialized"}
    
    await orchestrator.start_stream()
    return {"status": "started"}

@router.post("/stream/pause")
def pause_stream():
    orchestrator.pause_stream()
    return {"status": "paused"}

@router.post("/drivers/{code}/focus")
def focus_driver(code: str):
    return {"focused_driver": code}

@router.get("/analysis/lap/{num}")
def get_lap_analysis(num: int):
    return {"lap": num, "analysis": {}}

@router.post("/races/load")
def load_race(year: int = 2023, race_round: int = 1):
    import traceback
    try:
        orchestrator.initialize_race(year, race_round)
        return {"status": "loaded", "session_id": orchestrator.session_id, "total_laps": orchestrator.total_laps}
    except Exception as e:
        print(f"[LOAD ERROR] {str(e)}")
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
