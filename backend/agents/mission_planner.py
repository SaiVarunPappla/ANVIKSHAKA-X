"""
mission_planner.py
------------------
Agent 1 — MissionPlannerAgent (Upgraded with LLM)
"""

import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MissionPlannerAgent(BaseAgent):
    """Plans the mission route, strategy, and timeline."""

    def __init__(self):
        super().__init__()

    def run(self, input_dict: Dict[str, Any], generate_narrative: bool = True) -> Dict[str, Any]:
        mtype = input_dict.get("mission_type", "Coastal Surveillance")
        num_drones = input_dict.get("num_drones", 2)
        num_auvs = input_dict.get("num_auvs", 1)
        duration = input_dict.get("duration_hours", 12)
        threat = input_dict.get("threat_level", "medium")
        weather = input_dict.get("weather", "moderate")

        route = self._generate_route(mtype)
        strategy = self._build_strategy(mtype, num_drones, num_auvs, threat)
        timeline = self._build_timeline(route, duration)
        asset_roles = self._assign_roles(num_drones, num_auvs)
        objective = self._objective_for_type(mtype)

        # LLM Enhancement (optional)
        if generate_narrative:
            system_prompt = "Military mission planner AI. Provide tactical assessment. Professional tone. Max 80 words."
            user_prompt = (
                f"Mission: {mtype}, {num_drones} drones, {num_auvs} AUVs, "
                f"{duration}h, {threat} threat, {weather} weather. "
                f"Route: {route}. Assess tactics and risks."
            )
            logger.info(f"[MissionPlannerAgent] Requesting AI narrative...")
            ai_narrative = self.call_llm(system_prompt, user_prompt, max_tokens=120)
            logger.info(f"[MissionPlannerAgent] AI narrative received: {len(ai_narrative)} chars")
        else:
            ai_narrative = ""

        return {
            "agent": self.name,
            "status": "completed",
            "route": route,
            "strategy": strategy,
            "timeline": timeline,
            "asset_roles": asset_roles,
            "objective": objective,
            "ai_narrative": ai_narrative
        }

    def _generate_route(self, mtype: str) -> list:
        routes = {
            "Coastal Surveillance": ["Zone A (North)", "Zone B (NE)", "Zone C (East)", "Return Base"],
            "Deep Sea Patrol": ["Zone D (Deep Water)", "Zone E (Abyssal)", "Zone F (Shelf)", "Return Base"],
            "Air Patrol": ["Sector 1 (North)", "Sector 2 (East)", "Sector 3 (SE)", "Return Base"],
            "Anti-Submarine": ["ASW Box 1", "ASW Box 2", "ASW Box 3", "Return Base"],
        }
        return routes.get(mtype, routes["Coastal Surveillance"])

    def _build_strategy(self, mtype, num_drones, num_auvs, threat) -> str:
        parts = []
        if num_drones > 0 and num_auvs > 0:
            parts.append(f"Multi-domain: {num_drones} drone(s) aerial, {num_auvs} AUV(s) underwater.")
        elif num_drones > 0: parts.append(f"Aerial surveillance with {num_drones} drone(s).")
        elif num_auvs > 0: parts.append(f"Underwater scan with {num_auvs} AUV(s).")
        else: parts.append("No assets assigned.")
        if threat == "high": parts.append("High threat: armed escort required.")
        elif threat == "medium": parts.append("Moderate threat: maintain awareness.")
        else: parts.append("Low threat: standard patrol.")
        parts.append(f"Profile: {mtype}.")
        return " ".join(parts)

    def _build_timeline(self, route, duration):
        per_leg = round(duration / max(len(route), 1), 1)
        return {f"Phase {i+1}": {"waypoint": wp, "start_hour": i*per_leg, "end_hour": (i+1)*per_leg} for i, wp in enumerate(route)}

    def _assign_roles(self, num_drones, num_auvs):
        roles = {}
        for i in range(num_drones):
            roles[f"Drone {chr(65+i)}"] = "Primary aerial surveillance" if i==0 else "Backup / relay"
        for i in range(num_auvs):
            roles[f"AUV {i+1}"] = "Primary sonar scan" if i==0 else "Deep-water auxiliary"
        return roles

    def _objective_for_type(self, mtype):
        return {
            "Coastal Surveillance": "Coastal surveillance + threat detection",
            "Deep Sea Patrol": "Deep-sea domain awareness + sonar mapping",
            "Air Patrol": "Aerial reconnaissance + airspace monitoring",
            "Anti-Submarine": "Submarine detection, tracking, and interdiction",
        }.get(mtype, "Intelligence gathering")