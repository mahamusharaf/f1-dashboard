try:
    from app.main import app
    import uvicorn
    print("App import successful")
    # Don't actually run here, just check if it CAN run
except Exception as e:
    import traceback
    traceback.print_exc()
