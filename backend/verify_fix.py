import asyncio
import os
import sys

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orchestrator import RaceOrchestrator

async def verify_fix():
    print("Initializing Orchestrator for 2024 Round 1...")
    orc = RaceOrchestrator()
    try:
        # Load a real session (2024 Bahrain)
        orc.initialize_race(2024, 1)
        
        with open('verification_results.txt', 'w') as f:
            f.write("Checking driver image URLs:\n")
            for abbr in orc.driver_images.keys():
                url = orc._get_driver_image_url(abbr)
                f.write(f"{abbr}: {url}\n")
                
                # Simple check if it looks like a valid URL from our research
                if "media.formula1.com" in url:
                    f.write(f"  [PASS] URL found for {abbr}\n")
                else:
                    f.write(f"  [FAIL] Generic or missing URL for {abbr}\n")
                    
        print("\nVerification results written to verification_results.txt")
                
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_fix())
