"""

schemas.py

----------

Pydantic v2 request / response schemas for every API endpoint.

"""



from datetime import datetime

from typing import List, Optional, Any

from pydantic import BaseModel, Field





# -------------------------------------------------------------------

# Mission schemas

# -------------------------------------------------------------------

class MissionCreate(BaseModel):

   name: str = Field(..., min_length=1, max_length=200)

   mission_type: str

   duration_hours: int = Field(..., ge=1, le=72)

   threat_level: str   # low / medium / high

   weather: str        # calm / moderate / severe

   num_drones: int = Field(0, ge=0, le=20)

   num_auvs: int = Field(0, ge=0, le=10)

   num_torpedoes: int = Field(0, ge=0, le=10)

   num_launchers: int = Field(0, ge=0, le=10)





class MissionResponse(BaseModel):

   id: int

   name: str

   mission_type: str

   duration_hours: int

   threat_level: str

   weather: str

   num_drones: int

   num_auvs: int

   num_torpedoes: int

   num_launchers: int

   status: str

   created_at: datetime



   model_config = {"from_attributes": True}





# -------------------------------------------------------------------

# Risk schemas

# -------------------------------------------------------------------

class RiskAnalysisRequest(BaseModel):

   mission_id: int





class RiskAnalysisResponse(BaseModel):

   id: int

   mission_id: int

   risk_score: float

   risk_category: str

   success_probability: float

   high_risk_zones: List[str]

   route_suggestion: str



   model_config = {"from_attributes": True}





# -------------------------------------------------------------------

# Maintenance schemas

# -------------------------------------------------------------------

class MaintenanceRequest(BaseModel):

   asset_ids: Optional[List[int]] = None  # None ⇒ predict for all assets





class MaintenancePredictionResponse(BaseModel):

   id: int

   asset_id: int

   failure_probability: float

   risk_level: str

   recommended_action: str

   asset_name: Optional[str] = None

   asset_type: Optional[str] = None



   model_config = {"from_attributes": True}





# -------------------------------------------------------------------

# Asset schemas

# -------------------------------------------------------------------

class AssetResponse(BaseModel):

   id: int

   name: str

   asset_type: str

   battery_health: float

   operating_hours: int

   mission_count: int

   status: str

   last_maintenance: datetime



   model_config = {"from_attributes": True}





# -------------------------------------------------------------------

# Agent log schemas

# -------------------------------------------------------------------

class AgentLogResponse(BaseModel):

   id: int

   mission_id: int

   agent_name: str

   input_summary: str

   output_json: str

   created_at: datetime



   model_config = {"from_attributes": True}





# -------------------------------------------------------------------

# Dashboard schemas

# -------------------------------------------------------------------

class DashboardResponse(BaseModel):

   total_missions: int

   active_missions: int

   overall_risk_score: float

   overall_risk_category: str

   fleet_health_pct: float

   assets_needing_maintenance: int

   total_assets: int

   recent_missions: List[dict]

   mission_success_by_type: List[dict]

   fleet_health_trend: List[dict]