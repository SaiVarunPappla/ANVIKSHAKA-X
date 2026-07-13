"""
maintenance.py
--------------
POST /api/maintenance  → run predictive maintenance for all (or selected) assets
GET  /api/maintenance/predictions → list recent predictions
GET  /api/assets       → list all assets
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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
# GET /api/maintenance/predictions — list recent predictions
# ====================================================================
@router.get("/maintenance/predictions", response_model=List[MaintenancePredictionResponse])
async def list_predictions(db: Session = Depends(get_db)):
    """Get the most recent maintenance predictions for all assets."""
    # Get the latest prediction for each asset
    subquery = (
        db.query(
            MaintenancePrediction.asset_id,
            func.max(MaintenancePrediction.predicted_at).label('max_predicted_at')
        )
        .group_by(MaintenancePrediction.asset_id)
        .subquery()
    )
    
    predictions = (
        db.query(MaintenancePrediction)
        .join(
            subquery,
            (MaintenancePrediction.asset_id == subquery.c.asset_id) &
            (MaintenancePrediction.predicted_at == subquery.c.max_predicted_at)
        )
        .join(Asset, MaintenancePrediction.asset_id == Asset.id)
        .all()
    )
    
    response = []
    for mp in predictions:
        asset = db.query(Asset).filter(Asset.id == mp.asset_id).first()
        response.append(MaintenancePredictionResponse(
            id=mp.id,
            asset_id=mp.asset_id,
            failure_probability=mp.failure_probability,
            risk_level=mp.risk_level,
            recommended_action=mp.recommended_action,
            asset_name=asset.name if asset else "Unknown",
            asset_type=asset.asset_type if asset else "Unknown",
        ))
    
    return response


# ====================================================================
# POST /api/maintenance — run predictive maintenance
# ====================================================================
@router.post("/maintenance", response_model=List[MaintenancePredictionResponse])
async def run_maintenance(payload: MaintenanceRequest, db: Session = Depends(get_db)):
    """Run the ML-based predictive maintenance for all or selected assets."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[Maintenance] POST /api/maintenance called with payload: {payload}")
    
    query = db.query(Asset)
    if payload.asset_ids:
        query = query.filter(Asset.id.in_(payload.asset_ids))
    assets_db = query.all()

    if not assets_db:
        logger.warning("[Maintenance] No assets found in database")
        raise HTTPException(status_code=404, detail="No assets found.")

    logger.info(f"[Maintenance] Found {len(assets_db)} assets to analyze")
    
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

    logger.info("[Maintenance] Running maintenance agent...")
    result = _maint_agent.run({"assets": asset_list})
    predictions = result["predictions"]
    logger.info(f"[Maintenance] Agent returned {len(predictions)} predictions")

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

    logger.info(f"[Maintenance] Returning {len(response)} prediction responses")
    return response