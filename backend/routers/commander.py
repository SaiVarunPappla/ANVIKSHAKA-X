"""
commander.py
------------
POST /api/commander — Natural language mission creation
"""

import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import Mission, Asset, AgentLog, RiskAssessment
from agents.nlp_commander import NLPCommander
from agents.mission_planner import MissionPlannerAgent
from agents.risk_analyst import RiskAnalystAgent
from agents.resource_optimizer import ResourceOptimizerAgent
from agents.maintenance_analyst import MaintenanceAnalystAgent
from agents.supervisor import SupervisorAgent

router = APIRouter(prefix="/api", tags=["commander"])

nlp = NLPCommander()
_planner = MissionPlannerAgent()
_risk = RiskAnalystAgent()
_optimizer = ResourceOptimizerAgent()
_maintenance = MaintenanceAnalystAgent()
_supervisor = SupervisorAgent()


class CommandRequest(BaseModel):
    command: str


@router.post("/commander")
async def parse_command(payload: CommandRequest, db: Session = Depends(get_db)):
    """Parse natural language and execute mission."""
    mission_data = nlp.parse(payload.command)

    mission = Mission(
        name=mission_data["name"],
        mission_type=mission_data["missiontype"],
        duration_hours=mission_data["durationhours"],
        threat_level=mission_data["threatlevel"],
        weather=mission_data["weather"],
        num_drones=mission_data["numdrones"],
        num_auvs=mission_data["numauvs"],
        num_torpedoes=mission_data["numtorpedoes"],
        num_launchers=mission_data["numlaunchers"],
        status="planned",
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)

    assets_db = db.query(Asset).all()
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

    num_assets = mission_data["numdrones"] + mission_data["numauvs"]

    planner_out = _planner.run({
        "missiontype": mission_data["missiontype"],
        "numdrones": mission_data["numdrones"],
        "numauvs": mission_data["numauvs"],
        "durationhours": mission_data["durationhours"],
        "threatlevel": mission_data["threatlevel"],
        "weather": mission_data["weather"],
    })

    risk_out = _risk.run({
        "threatlevel": mission_data["threatlevel"],
        "weather": mission_data["weather"],
        "durationhours": mission_data["durationhours"],
        "numassets": max(num_assets, 1),
        "missiontype": mission_data["missiontype"],
    })

    optimizer_out = _optimizer.run({
        "assets": asset_list
    })

    maintenance_out = _maintenance.run({
        "assets": asset_list
    })

    supervisor_out = _supervisor.run({
        "missionplanner": planner_out,
        "riskanalyst": risk_out,
        "resourceoptimizer": optimizer_out,
        "maintenanceanalyst": maintenance_out,
        "missionname": mission_data["name"],
    })

    risk_score = risk_out.get("riskscore", risk_out.get("risk_score", 0))
    risk_category = risk_out.get("riskcategory", risk_out.get("risk_category", "Unknown"))
    success_probability = risk_out.get("successprobability", risk_out.get("success_probability", 0))
    high_risk_zones = risk_out.get("highriskzones", risk_out.get("high_risk_zones", []))
    route_suggestion = risk_out.get("routesuggestion", risk_out.get("route_suggestion", "No route suggestion available."))

    print("RISK OUT DEBUG:", risk_out)
    ra = RiskAssessment(
    mission_id=mission.id,
    risk_score=risk_score,
    risk_category=risk_category,
    success_probability=success_probability,
    high_risk_zones=json.dumps(high_risk_zones),
    route_suggestion=route_suggestion,
    agent_output_json=json.dumps(risk_out, default=str),
)
    db.add(ra)

    for agent_name, output in [
        ("MissionPlannerAgent", planner_out),
        ("RiskAnalystAgent", risk_out),
        ("ResourceOptimizerAgent", optimizer_out),
        ("MaintenanceAnalystAgent", maintenance_out),
        ("SupervisorAgent", supervisor_out),
    ]:
        log = AgentLog(
            mission_id=mission.id,
            agent_name=agent_name,
            input_summary=json.dumps(mission_data),
            output_json=json.dumps(output, default=str),
        )
        db.add(log)

    mission.status = "active"
    db.commit()

    return {
        "mission_id": mission.id,
        "missionid": mission.id,
        "mission_name": mission_data["name"],
        "missionname": mission_data["name"],
        "parsed_params": mission_data,
        "parsedparams": mission_data,
        "supervisor_brief": supervisor_out,
        "supervisorbrief": supervisor_out,
        "agents": {
            "mission_planner": planner_out,
            "risk_analyst": risk_out,
            "resource_optimizer": optimizer_out,
            "maintenance_analyst": maintenance_out,
        },
    }