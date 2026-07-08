"""
maintenance.py
--------------
POST /api/maintenance  → run predictive maintenance for all (or selected) assets
GET  /api/assets       → list all assets
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Asset, MaintenancePrediction
from schemas import MaintenanceRequest, AssetResponse, MaintenancePredictionResponse
from agents.maintenance_analyst import MaintenanceAnalystAgent

router = APIRouter(prefix="/api", tags=["maintenance"])
_maint_agent = MaintenanceAnalystAgent()


# ====================================================================
# GET /api/assets — list all assets
# ====================================================================
@router.get("/assets", response_model=List[AssetResponse])
async def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).order_by(Asset.id).all()


# ====================================================================
# POST /api/maintenance — run predictive maintenance
# ====================================================================
@router.post("/maintenance", response_model=List[MaintenancePredictionResponse])
async def run_maintenance(payload: MaintenanceRequest, db: Session = Depends(get_db)):
    """Run the ML-based predictive maintenance for all or selected assets."""
    query = db.query(Asset)
    if payload.asset_ids:
        query = query.filter(Asset.id.in_(payload.asset_ids))
    assets_db = query.all()

    if not assets_db:
        raise HTTPException(status_code=404, detail="No assets found.")

    asset_list = [
        {
            "name": a.name,
            "asset_type": a.asset_type,
            "battery_health": a.battery_health,
            "operating_hours": a.operating_hours,
            "mission_count": a.mission_count,
            "status": a.status,
        }
        for a in assets_db
    ]

    result = _maint_agent.run({"assets": asset_list})
    predictions = result["predictions"]

    # Persist predictions
    response = []
    for pred, asset in zip(predictions, assets_db):
        mp = MaintenancePrediction(
            asset_id=asset.id,
            failure_probability=pred["failure_probability"],
            risk_level=pred["risk_level"],
            recommended_action=pred["recommended_action"],
        )
        db.add(mp)
        db.commit()
        db.refresh(mp)

        response.append(MaintenancePredictionResponse(
            id=mp.id,
            asset_id=asset.id,
            failure_probability=mp.failure_probability,
            risk_level=mp.risk_level,
            recommended_action=mp.recommended_action,
            asset_name=asset.name,
            asset_type=asset.asset_type,
        ))

    return response