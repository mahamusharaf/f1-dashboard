from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import race_routes, websocket_routes

app = FastAPI(
    title="F1 Live Commentary Dashboard",
    description="Real-time race commentary and telemetry",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(race_routes.router, prefix="/api", tags=["race"])
app.include_router(websocket_routes.router, prefix="/api", tags=["websocket"])

@app.get("/")
def read_root():
    return {"message": "Welcome to F1 Live Dashboard API"}
