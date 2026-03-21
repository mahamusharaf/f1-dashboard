import fastf1

fastf1.Cache.enable_cache('f1_cache')
session = fastf1.get_session(2026, 2, 'R')
session.load(telemetry=False, weather=False, messages=False)

results = session.results
for _, row in results.iterrows():
    print(f"Driver: {row['Abbreviation']} | Team: {row['TeamName']} | TeamColor: {row['TeamColor']} | Headshot: {row.get('HeadshotUrl', 'N/A')}")
