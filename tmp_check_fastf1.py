import fastf1
import pandas as pd

def check_driver_data():
    fastf1.Cache.enable_cache('f1_cache')
    # Use a recent session to see what's available
    session = fastf1.get_session(2024, 1, 'R')
    session.load(telemetry=False, weather=False, messages=False)
    
    print("Columns in session.results:")
    print(session.results.columns.tolist())
    
    print("\nFirst row of session.results:")
    print(session.results.iloc[0])
    
    # Check if there's any image related data
    for col in session.results.columns:
        if 'url' in col.lower() or 'image' in col.lower():
            print(f"Found potential column: {col}")

if __name__ == "__main__":
    check_driver_data()
