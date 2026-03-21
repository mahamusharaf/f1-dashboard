import asyncio
import os
import sys
import pandas as pd

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orchestrator import RaceOrchestrator

async def crash_test():
    print("Initializing Orchestrator for 2026 Round 1...")
    orc = RaceOrchestrator()
    try:
        orc.initialize_race(2026, 1)
        print("Initialization Successful!")
        print(f"Total Laps: {orc.total_laps}")
        print(f"Drivers: {len(orc.drivers)}")
        
        # Check telemetry for first driver
        if orc.drivers:
            first_driver = orc.drivers[0]
            try:
                tel = orc.session.laps.pick_driver(first_driver).get_telemetry()
                print(f"Telemetry for {first_driver}: {len(tel)} points")
                if not tel.empty:
                    print(f"Sample Coord: X={tel.X.iloc[0]}, Y={tel.Y.iloc[0]}")
            except Exception as tel_e:
                print(f"No Telemetry for {first_driver}: {tel_e}")
        
        # Check image URLs for quality fix
        if orc.driver_images:
            first_abbr = list(orc.driver_images.keys())[0]
            print(f"Sample Image URL ({first_abbr}): {orc.driver_images[first_abbr]}")
            
    except Exception as e:
        print(f"CRASH during initialization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(crash_test())
