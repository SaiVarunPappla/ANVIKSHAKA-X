"""

mission.py

----------

POST /api/mission        → create mission + run all 5 agents

GET  /api/missions       → list all missions

GET  /api/agent-logs/{id}→ get agent logs for a mission

"""



import json

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from typing import List



from database import get_db

from models import Mission, Asset, AgentLog, RiskAssessment

from schemas import (

   MissionCreate, MissionResponse, AgentLogResponse,

)

from agents.mission_planner import MissionPlannerAgent

from agents.risk_analyst import RiskAnalystAgent

from agents.resource_optimizer import ResourceOptimizerAgent

from agents.maintenance_analyst import MaintenanceAnalystAgent

from agents.supervisor import SupervisorAgent



router = APIRouter(prefix="/api", tags=["mission"])



# Instantiate agents once

_planner = MissionPlannerAgent()

_risk = RiskAnalystAgent()

_optimizer = ResourceOptimizerAgent()

_maintenance = MaintenanceAnalystAgent()

_supervisor = SupervisorAgent()





# ====================================================================

# POST /api/mission  — create mission and trigger full agent pipeline

# ====================================================================

@router.post("/mission", response_model=dict)

async def create_mission(payload: MissionCreate, generate_narratives: bool = False, db: Session = Depends(get_db)):

   """Create a mission, run all 5 agents, persist results, return brief."""

   # 1. Persist mission

   mission = Mission(

       name=payload.name,

       mission_type=payload.mission_type,

       duration_hours=payload.duration_hours,

       threat_level=payload.threat_level,

       weather=payload.weather,

       num_drones=payload.num_drones,

       num_auvs=payload.num_auvs,

       num_torpedoes=payload.num_torpedoes,

       num_launchers=payload.num_launchers,

       status="planned",

   )

   db.add(mission)

   db.commit()

   db.refresh(mission)



   # 2. Fetch assets from DB

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



   num_assets = payload.num_drones + payload.num_auvs



   # 3. Run agents

   planner_out = _planner.run({

       "mission_type": payload.mission_type,

       "num_drones": payload.num_drones,

       "num_auvs": payload.num_auvs,

       "duration_hours": payload.duration_hours,

       "threat_level": payload.threat_level,

       "weather": payload.weather,

   }, generate_narrative=generate_narratives)



   risk_out = _risk.run({

       "threat_level": payload.threat_level,

       "weather": payload.weather,

       "duration_hours": payload.duration_hours,

       "num_assets": max(num_assets, 1),

       "mission_type": payload.mission_type,

   }, generate_narrative=generate_narratives)



   optimizer_out = _optimizer.run({"assets": asset_list})



   maintenance_out = _maintenance.run({"assets": asset_list}, generate_narrative=generate_narratives)



   supervisor_out = _supervisor.run({

       "mission_planner": planner_out,

       "risk_analyst": risk_out,

       "resource_optimizer": optimizer_out,

       "maintenance_analyst": maintenance_out,

       "mission_name": payload.name,

   }, generate_narrative=generate_narratives)



   # 4. Persist risk assessment

   risk_assessment = RiskAssessment(

       mission_id=mission.id,

       risk_score=risk_out["risk_score"],

       risk_category=risk_out["risk_category"],

       success_probability=risk_out["success_probability"],

       high_risk_zones=json.dumps(risk_out["high_risk_zones"]),

       route_suggestion=risk_out["route_suggestion"],

       agent_output_json=json.dumps(risk_out),

   )

   db.add(risk_assessment)



   # 5. Persist agent logs

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

           input_summary=json.dumps({

               "mission_type": payload.mission_type,

               "duration": payload.duration_hours,

               "threat": payload.threat_level,

               "weather": payload.weather,

           }),

           output_json=json.dumps(output, default=str),

       )

       db.add(log)



   # Update mission status

   mission.status = "active"

   db.commit()



   return {

       "mission_id": mission.id,

       "mission_name": payload.name,

       "supervisor_brief": supervisor_out,

       "agents": {

           "mission_planner": planner_out,

           "risk_analyst": risk_out,

           "resource_optimizer": optimizer_out,

           "maintenance_analyst": maintenance_out,

       },

   }





# ====================================================================

# GET /api/missions — list all missions

# ====================================================================

@router.get("/missions", response_model=List[MissionResponse])

async def list_missions(db: Session = Depends(get_db)):

   missions = db.query(Mission).order_by(Mission.created_at.desc()).all()

   return missions





# ====================================================================

# GET /api/agent-logs/{mission_id}

# ====================================================================

@router.get("/agent-logs/{mission_id}", response_model=List[AgentLogResponse])

async def get_agent_logs(mission_id: int, db: Session = Depends(get_db)):

   logs = db.query(AgentLog).filter(AgentLog.mission_id == mission_id).all()

   if not logs:

       raise HTTPException(status_code=404, detail="No agent logs found for this mission.")

   return logs