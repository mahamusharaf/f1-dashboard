import fastf1
import pandas as pd

def check_fastf1():
    try:
        # Enable FastF1 cache
        fastf1.Cache.enable_cache('f1_cache') 
        
        # Try to get a recent session list or something quick
        # (getting the schedule for 2023)
        schedule = fastf1.get_event_schedule(2023)
        print("Successfully fetched 2023 schedule.")
        print(f"Number of events: {len(schedule)}")
        
        # Try to load a specific session (Bahrain 2023 Race)
        session = fastf1.get_session(2023, 1, 'R')
        session.load(telemetry=False, weather=False, messages=False)
        print(f"Successfully loaded session: {session.event.EventName}")
        print(f"Drivers: {session.drivers}")
        
    except Exception as e:
        print(f"Error checking FastF1: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_fastf1()
