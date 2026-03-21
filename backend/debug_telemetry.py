import fastf1
import pandas as pd
import datetime

def debug_data():
    fastf1.Cache.enable_cache('f1_cache')
    session = fastf1.get_session(2023, 1, 'R')
    session.load(telemetry=True, weather=False, messages=False)
    
    # Check track length
    try:
        track_length = session.laps.pick_fastest().get_telemetry()['Distance'].max()
        print(f"Track Length: {track_length}")
    except Exception as e:
        print(f"Error picking fastest: {e}")

    # Check a driver's telemetry
    driver = 'VER'
    tel = session.laps.pick_driver(driver).get_telemetry()
    print(f"\nTelemetry sample for {driver}:")
    print(tel[['SessionTime', 'Distance']].head())
    print(tel[['SessionTime', 'Distance']].tail())

    # Check if distance resets
    # Laps
    laps = session.laps.pick_driver(driver)
    for i in range(1, 4):
        lap_tel = laps.pick_lap(i).get_telemetry()
        print(f"Lap {i} Max Distance: {lap_tel['Distance'].max()}")

if __name__ == "__main__":
    debug_data()
