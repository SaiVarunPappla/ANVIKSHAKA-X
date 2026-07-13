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
    logger.info("[Startup] ========================================")
    logger.info("[Startup] ANVIKSHAKA-X backend initializing...")
    logger.info("[Startup] ========================================")
    logger.info(f"[Startup] Database URL prefix: {os.getenv('DATABASE_URL', 'sqlite:///./anvikshaka.db')[:30]}")
    
    # Log AI configuration
    logger.info(f"[Startup] AI_PROVIDER: {os.getenv('AI_PROVIDER', 'auto')}")
    logger.info(f"[Startup] GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
    logger.info(f"[Startup] GEMINI_MODEL: {os.getenv('GEMINI_MODEL', 'gemini-pro')}")
    
    # Initialize AI provider to trigger configuration logging
    try:
        base_agent = BaseAgent()
        logger.info(f"[Startup] Active AI provider: {base_agent.get_ai_provider_name()}")
        logger.info(f"[Startup] AI available: {base_agent.is_ai_available()}")
    except Exception as e:
        logger.error(f"[Startup] AI initialization failed: {e}")
    
    # Create tables if they don't exist (idempotent)
    try:
        logger.info("[Startup] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("[Startup] Database tables created successfully")
        
        # Only seed if explicitly enabled (avoid on serverless cold starts)
        if os.getenv("SEED_DATABASE", "false").lower() == "true":
            seed_database()
            logger.info("[Startup] Database seeded")
        else:
            logger.info("[Startup] Database seeding disabled (SEED_DATABASE not set)")
    except Exception as e:
        logger.error(f"[Startup] Initialization failed: {e}", exc_info=True)
        # Don't crash the app - let individual endpoints handle DB errors
    
    logger.info("[Startup] ========================================")
    logger.info("[Startup] Initialization complete")
    logger.info("[Startup] ========================================")

@app.get("/")
async def root():
    return {"system": "ANVIKSHAKA-X", "status": "online", "version": "2.0.0"}

@app.get("/api/routes")
async def list_routes():
    """Debug endpoint to list all registered routes."""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": sorted(routes, key=lambda x: x["path"])}

@app.get("/api/health")
async def health():
    """Health check endpoint with database connectivity test."""
    from sqlalchemy import text
    
    health_status = {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Test AI provider
    try:
        base_agent = BaseAgent()
        health_status["ai_provider"] = base_agent.get_ai_provider_name()
        health_status["ai_available"] = base_agent.is_ai_available()
    except Exception as e:
        logger.error(f"[Health] AI provider check failed: {e}")
        health_status["ai_provider"] = "error"
        health_status["ai_available"] = False
        health_status["ai_error"] = str(e)
    
    # Test database connectivity
    try:
        db = SessionLocal()
        # SQLAlchemy 2.x requires text() wrapper for raw SQL
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"[Health] Database check failed: {e}")
        health_status["database"] = "error"
        health_status["database_error"] = str(e)
        health_status["status"] = "degraded"
    
    return health_status

@app.post("/api/seed")
async def trigger_seed():
    """Manually trigger database seeding (for production setup)."""
    try:
        seed_database()
        return {
            "status": "success",
            "message": "Database seeded with sample data",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"[Seed] Failed to seed database: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

def seed_database():
    """Seed database with sample data (idempotent)."""
    db = SessionLocal()
    try:
        # Seed assets
        if db.query(Asset).count() == 0:
            sample_assets = [
                Asset(name="Drone Alpha", asset_type="drone", battery_health=85.0, operating_hours=120, mission_count=18, status="active"),
                Asset(name="Drone Bravo", asset_type="drone", battery_health=62.0, operating_hours=280, mission_count=35, status="active"),
                Asset(name="Drone Charlie", asset_type="drone", battery_health=91.0, operating_hours=55, mission_count=8, status="active"),
                Asset(name="AUV-01 Neptune", asset_type="auv", battery_health=78.0, operating_hours=190, mission_count=22, status="active"),
                Asset(name="AUV-02 Poseidon", asset_type="auv", battery_health=45.0, operating_hours=350, mission_count=47, status="maintenance"),
                Asset(name="Torpedo T-90", asset_type="torpedo", battery_health=100.0, operating_hours=5, mission_count=2, status="active"),
                Asset(name="Launcher VLS-01", asset_type="launcher", battery_health=95.0, operating_hours=80, mission_count=12, status="active"),
            ]
            db.add_all(sample_assets)
            db.commit()
            logger.info("[SEED] 7 sample assets inserted.")
        
        # Seed sample missions
        if db.query(Mission).count() == 0:
            from datetime import datetime, timedelta
            sample_missions = [
                Mission(
                    name="Operation Sea Hawk",
                    mission_type="Reconnaissance",
                    duration_hours=6,
                    threat_level="medium",
                    weather="moderate",
                    num_drones=2,
                    num_auvs=1,
                    num_torpedoes=0,
                    num_launchers=0,
                    status="completed",
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                Mission(
                    name="Coastal Patrol Alpha",
                    mission_type="Patrol",
                    duration_hours=12,
                    threat_level="low",
                    weather="calm",
                    num_drones=3,
                    num_auvs=1,
                    num_torpedoes=0,
                    num_launchers=0,
                    status="active",
                    created_at=datetime.utcnow() - timedelta(days=1)
                ),
                Mission(
                    name="Strike Mission Delta",
                    mission_type="Strike",
                    duration_hours=4,
                    threat_level="high",
                    weather="severe",
                    num_drones=1,
                    num_auvs=0,
                    num_torpedoes=2,
                    num_launchers=1,
                    status="planned",
                    created_at=datetime.utcnow() - timedelta(hours=6)
                ),
            ]
            db.add_all(sample_missions)
            db.commit()
            logger.info("[SEED] 3 sample missions inserted.")
            
    except Exception as e:
        logger.error(f"[SEED] Failed to seed database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Local development only
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)