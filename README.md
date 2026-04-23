---
title: F1 Dashboard Backend
emoji: 🏎️
colorFrom: red
colorTo: black
sdk: docker
app_port: 7860
pinned: false
---

# F1 Live Commentary Dashboard Backend

This is the backend for the F1 Live Commentary Dashboard, built with FastAPI and FastF1.

## Deployment on Hugging Face Spaces

This Space is configured to run a Docker container.

### Local Development

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Run the app:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 7860
   ```

### API Endpoints

- `GET /`: Health check
- `GET /api/race/sessions`: Get available sessions
- `WS /api/websocket`: Real-time race data stream
