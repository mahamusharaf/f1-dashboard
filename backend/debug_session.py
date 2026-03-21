import fastf1
import pandas as pd

def check_session(year, round_num):
    fastf1.Cache.enable_cache('f1_cache')
    session = fastf1.get_session(year, round_num, 'R')
    session.load(telemetry=False, weather=False, messages=False)
    laps = session.laps
    print(f"Total laps in session: {laps['LapNumber'].max()}")
    print(f"Unique lap numbers: {sorted(laps['LapNumber'].unique())}")
    print(f"Driver lineup: {session.drivers}")
    print(f"Sample results:\n{session.results[['Abbreviation', 'TeamName', 'TeamColor']].head(10)}")

if __name__ == "__main__":
    check_session(2023, 1) # Bahrain 2023
