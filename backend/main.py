"""
main.py
-------
FastAPI application entry point for ANVIKSHAKA-X.
"""

import os, sys, logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from models import Mission, Asset
from routers import mission, risk, maintenance, dashboard, chat, commander
from agents.base_agent import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ANVIKSHAKA-X", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mission.router)
app.include_router(risk.router)
app.include_router(maintenance.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(commander.router)

@app.on_event("startup")
async def warmup_ollama():
    """Warm up Ollama model on startup (non-blocking)."""
    import asyncio
    
    async def _warmup():
        try:
            agent = BaseAgent()
            if agent.is_ollama_available():
                logger.info("[Startup] Warming up Ollama model...")
                agent.call_llm("You are a test assistant.", "Respond with OK.")
                logger.info("[Startup] Ollama warm-up complete")
        except Exception as e:
            logger.warning(f"[Startup] Ollama warm-up failed: {e}")
    
    # Run warm-up in background without blocking startup
    asyncio.create_task(_warmup())

@app.get("/")
async def root():
    return {"system": "ANVIKSHAKA-X", "status": "online", "version": "2.0.0"}

@app.get("/api/health")
async def health():
    base_agent = BaseAgent()
    ollama_active = base_agent.is_ollama_available()
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "ollama": ollama_active,
        "ai_model": "llama3" if ollama_active else "fallback"
    }

def seed_database():
    db = SessionLocal()
    try:
        if db.query(Asset).count() == 0:
            sample_assets = [
                Asset(name="Drone A", asset_type="drone", battery_health=85.0, operating_hours=120, mission_count=18, status="active"),
                Asset(name="Drone B", asset_type="drone", battery_health=62.0, operating_hours=280, mission_count=35, status="active"),
                Asset(name="Drone C", asset_type="drone", battery_health=91.0, operating_hours=55, mission_count=8, status="active"),
                Asset(name="AUV 1", asset_type="auv", battery_health=78.0, operating_hours=190, mission_count=22, status="active"),
                Asset(name="AUV 2", asset_type="auv", battery_health=45.0, operating_hours=350, mission_count=47, status="maintenance"),
            ]
            db.add_all(sample_assets)
            db.commit()
            print("[SEED] 5 sample assets inserted.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
else:
    seed_database()