import fastf1
import pandas as pd

def check_drivers():
    fastf1.Cache.enable_cache('f1_cache')
    session = fastf1.get_session(2023, 1, 'R')
    session.load(telemetry=False, weather=False, messages=False)
    
    print("Results Abbreviations:")
    print(session.results[['Abbreviation', 'TeamName', 'TeamColor']].head())
    
    print("\nLaps Driver Codes:")
    print(session.laps['Driver'].unique())

if __name__ == "__main__":
    check_drivers()
