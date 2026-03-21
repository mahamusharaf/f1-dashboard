import sys
import os
sys.path.append(r'c:\Users\Maha\.gemini\antigravity\scratch\f1-dashboard\backend')
try:
    from app.services.orchestrator import orchestrator
    print("Orchestrator imported successfully")
except Exception as e:
    print(f"Error importing orchestrator: {e}")
    import traceback
    traceback.print_exc()
