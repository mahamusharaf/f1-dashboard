import asyncio
import websockets
import requests
import json
import time

async def verify_pause_broadcast():
    uri = "ws://localhost:8000/api/race/live"
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # 1. Load Race
            print("Initializing race...")
            requests.post("http://localhost:8000/api/races/load?year=2023&race_round=1")
            
            # 2. Start Stream
            print("Starting stream...")
            requests.post("http://localhost:8000/api/stream/start")
            
            # 3. Wait for ACTIVE message
            print("Waiting for active stream...")
            start_time = time.time()
            while time.time() - start_time < 30:
                msg = await websocket.recv()
                data = json.loads(msg)
                active = data.get('summary', {}).get('is_active')
                print(f"Received message. Active: {active}")
                if active == True:
                    print("Stream is active. Ready to pause.")
                    break
            else:
                print("FAILED: Timed out waiting for active stream")
                return
            
            # 4. Wait for a second of active stream
            await asyncio.sleep(1)
            
            # 5. Pause Stream
            print("Pausing stream...")
            requests.post("http://localhost:8000/api/stream/pause")
            
            # 6. Wait for pause broadcast
            print("Waiting for pause broadcast...")
            start_time = time.time()
            while time.time() - start_time < 10:
                msg = await websocket.recv()
                data = json.loads(msg)
                active = data.get('summary', {}).get('is_active')
                print(f"Received message. Active: {active}")
                if active == False:
                    print("SUCCESS: Received is_active: False broadcast!")
                    return
            
            print("FAILED: Timed out waiting for is_active: False broadcast")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_pause_broadcast())
