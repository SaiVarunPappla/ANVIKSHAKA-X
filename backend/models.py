"""

models.py

---------

SQLAlchemy ORM models for all five tables.

"""



from datetime import datetime

from sqlalchemy import (

   Column, Integer, String, Float, DateTime, Text, ForeignKey

)

from database import Base





class Mission(Base):

   """Mission table — stores every mission submitted by the operator."""

   __tablename__ = "missions"



   id = Column(Integer, primary_key=True, index=True)

   name = Column(String(200), nullable=False)

   mission_type = Column(String(100), nullable=False)

   duration_hours = Column(Integer, nullable=False)

   threat_level = Column(String(50), nullable=False)   # low / medium / high

   weather = Column(String(50), nullable=False)        # calm / moderate / severe

   num_drones = Column(Integer, default=0)

   num_auvs = Column(Integer, default=0)

   num_torpedoes = Column(Integer, default=0)

   num_launchers = Column(Integer, default=0)

   status = Column(String(50), default="planned")      # planned / active / completed

   created_at = Column(DateTime, default=datetime.utcnow)





class Asset(Base):

   """Asset table — drones, AUVs, torpedoes, launchers."""

   __tablename__ = "assets"



   id = Column(Integer, primary_key=True, index=True)

   name = Column(String(100), nullable=False)

   asset_type = Column(String(50), nullable=False)     # drone / auv / torpedo / launcher

   battery_health = Column(Float, default=100.0)

   operating_hours = Column(Integer, default=0)

   mission_count = Column(Integer, default=0)

   status = Column(String(50), default="active")       # active / maintenance / offline

   last_maintenance = Column(DateTime, default=datetime.utcnow)





class RiskAssessment(Base):

   """Risk assessment results produced by the RiskAnalystAgent."""

   __tablename__ = "risk_assessments"



   id = Column(Integer, primary_key=True, index=True)

   mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)

   risk_score = Column(Float, default=0.0)

   risk_category = Column(String(50), default="Low")

   success_probability = Column(Float, default=0.0)

   high_risk_zones = Column(Text, default="[]")        # JSON-serialised list

   route_suggestion = Column(Text, default="")

   agent_output_json = Column(Text, default="{}")      # full agent output

   created_at = Column(DateTime, default=datetime.utcnow)





class MaintenancePrediction(Base):

   """Predictive maintenance results from the ML model."""

   __tablename__ = "maintenance_predictions"



   id = Column(Integer, primary_key=True, index=True)

   asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

   failure_probability = Column(Float, default=0.0)

   risk_level = Column(String(50), default="low")      # low / medium / high / critical

   recommended_action = Column(Text, default="")

   predicted_at = Column(DateTime, default=datetime.utcnow)





class AgentLog(Base):

   """Audit trail — one row per agent invocation per mission."""

   __tablename__ = "agent_logs"



   id = Column(Integer, primary_key=True, index=True)

   mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)

   agent_name = Column(String(100), nullable=False)

   input_summary = Column(Text, default="")

   output_json = Column(Text, default="{}")

   created_at = Column(DateTime, default=datetime.utcnow)