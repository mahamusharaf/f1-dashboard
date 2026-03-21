import fastf1
import pandas as pd
import os

def check_driver_data():
    try:
        fastf1.Cache.enable_cache('f1_cache')
    except Exception as e:
        pass
    
    try:
        session = fastf1.get_session(2024, 1, 'R')
        session.load(telemetry=False, weather=False, messages=False)
        
        with open('driver_data_output.txt', 'w') as f:
            f.write("Columns in session.results:\n")
            f.write(str(session.results.columns.tolist()) + "\n\n")
            
            ver = session.results[session.results['Abbreviation'] == 'VER']
            if not ver.empty:
                f.write("Max Verstappen Data:\n")
                f.write(str(ver.iloc[0].to_dict()) + "\n")
            else:
                f.write("First row Data:\n")
                f.write(str(session.results.iloc[0].to_dict()) + "\n")
                
    except Exception as e:
        with open('driver_data_output.txt', 'w') as f:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    check_driver_data()
