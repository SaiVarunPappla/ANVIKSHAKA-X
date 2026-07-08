"""
risk.py
-------
POST /api/risk-analysis  → compute (or retrieve) risk assessment for a mission
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Mission, RiskAssessment, Asset
from schemas import RiskAnalysisRequest
from agents.risk_analyst import RiskAnalystAgent

router = APIRouter(prefix="/api", tags=["risk"])
_risk_agent = RiskAnalystAgent()


@router.post("/risk-analysis")
async def risk_analysis(payload: RiskAnalysisRequest, db: Session = Depends(get_db)):
    """Compute a fresh risk assessment for the given mission."""
    mission = db.query(Mission).filter(Mission.id == payload.mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    num_assets = mission.num_drones + mission.num_auvs + mission.num_torpedoes + mission.num_launchers

    result = _risk_agent.run({
        "threat_level": mission.threat_level,
        "weather": mission.weather,
        "duration_hours": mission.duration_hours,
        "num_assets": max(num_assets, 1),
        "mission_type": mission.mission_type,
    })

    # Persist
    ra = RiskAssessment(
        mission_id=mission.id,
        risk_score=result["risk_score"],
        risk_category=result["risk_category"],
        success_probability=result["success_probability"],
        high_risk_zones=json.dumps(result["high_risk_zones"]),
        route_suggestion=result["route_suggestion"],
        agent_output_json=json.dumps(result),
    )
    db.add(ra)
    db.commit()
    db.refresh(ra)

    return {
        "id": ra.id,
        "mission_id": mission.id,
        "risk_score": result["risk_score"],
        "risk_category": result["risk_category"],
        "success_probability": result["success_probability"],
        "high_risk_zones": result["high_risk_zones"],
        "route_suggestion": result["route_suggestion"],
        "breakdown": result.get("breakdown", {}),
    }
