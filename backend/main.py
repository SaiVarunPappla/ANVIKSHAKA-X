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

app = FastAPI(title="ANVIKSHAKA-X", version="2.0.0")

# CORS - allow frontend origins
# For development: http://localhost:5173
# For production: FRONTEND_URL environment variable
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:5173",  # Local dev
    "http://localhost:3000",  # Alternative local dev
    "https://anvikshaka-x-frontend.vercel.app",  # Production frontend
]

# Add custom frontend URL if provided
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)
    logger.info(f"[CORS] Added custom frontend URL: {frontend_url}")

logger.info(f"[CORS] Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
async def startup_init():
    """Initialize on startup - serverless compatible."""
    logger.info("[Startup] ANVIKSHAKA-X backend initializing...")
    # Create tables if they don't exist (idempotent)
    try:
        Base.metadata.create_all(bind=engine)
        # Only seed if explicitly enabled (avoid on serverless cold starts)
        if os.getenv("SEED_DATABASE", "false").lower() == "true":
            seed_database()
            logger.info("[Startup] Database seeded")
    except Exception as e:
        logger.warning(f"[Startup] Initialization failed: {e}")

@app.get("/")
async def root():
    return {"system": "ANVIKSHAKA-X", "status": "online", "version": "2.0.0"}

@app.get("/api/health")
async def health():
    base_agent = BaseAgent()
    ai_available = base_agent.is_ai_available()
    ai_provider = base_agent.get_ai_provider_name()
    
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "ai_provider": ai_provider,
        "ai_available": ai_available
    }

def seed_database():
    """Seed database with sample data (idempotent)."""
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
            logger.info("[SEED] 5 sample assets inserted.")
    finally:
        db.close()

if __name__ == "__main__":
    # Local development only
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)