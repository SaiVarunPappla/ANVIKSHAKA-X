"""
risk_analyst.py
---------------
Agent 2 — RiskAnalystAgent (Upgraded with LLM)
"""

import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RiskAnalystAgent(BaseAgent):
    """Analyses mission risk based on threat, weather, duration, and assets."""

    def __init__(self):
        super().__init__()

    def run(self, input_dict: Dict[str, Any], generate_narrative: bool = True) -> Dict[str, Any]:
        threat = input_dict.get("threat_level", "medium").lower()
        weather = input_dict.get("weather", "moderate").lower()
        duration = input_dict.get("duration_hours", 12)
        num_assets = input_dict.get("num_assets", 3)
        mission_type = input_dict.get("mission_type", "Coastal Surveillance")

        risk_score = 20
        threat_contribution = 0
        if threat == "low": risk_score += 10; threat_contribution = 10
        elif threat == "medium": risk_score += 25; threat_contribution = 25
        elif threat == "high": risk_score += 45; threat_contribution = 45

        weather_contribution = 0
        if weather == "moderate": risk_score += 12; weather_contribution = 12
        elif weather == "severe": risk_score += 30; weather_contribution = 30

        duration_contribution = 0
        if duration > 10: risk_score += 15; duration_contribution += 15
        if duration > 20: risk_score += 10; duration_contribution += 10

        risk_score = min(risk_score, 100)
        success_probability = min(max(30, 100 - risk_score + (num_assets * 2)), 98)

        if risk_score < 40: risk_category = "Low"
        elif risk_score < 65: risk_category = "Medium"
        else: risk_category = "High"

        high_risk_zones = self._identify_risk_zones(threat, weather, duration, mission_type)
        route_suggestion = self._route_suggestion(risk_category, weather, mission_type)

        # LLM Enhancement (optional)
        if generate_narrative:
            system_prompt = "Defence risk assessment AI. Analyze mission risk. Military tone. Max 80 words."
            user_prompt = (
                f"Risk: {risk_score}/100 ({risk_category}). "
                f"Threat: {threat}, Weather: {weather}, Duration: {duration}h. "
                f"High-risk zones: {high_risk_zones}. Provide reasoning and mitigation."
            )
            logger.info(f"[RiskAnalystAgent] Requesting AI narrative...")
            ai_narrative = self.call_llm(system_prompt, user_prompt, max_tokens=120)
            logger.info(f"[RiskAnalystAgent] AI narrative received: {len(ai_narrative)} chars")
        else:
            ai_narrative = ""

        return {
            "agent": self.name,
            "status": "completed",
            "risk_score": float(risk_score),
            "risk_category": risk_category,
            "success_probability": float(success_probability),
            "high_risk_zones": high_risk_zones,
            "route_suggestion": route_suggestion,
            "breakdown": {
                "threat_contribution": threat_contribution,
                "weather_contribution": weather_contribution,
                "duration_contribution": duration_contribution,
                "baseline": 20,
            },
            "ai_narrative": ai_narrative
        }

    def _identify_risk_zones(self, threat, weather, duration, mission_type) -> List[str]:
        zones = []
        if weather in ("moderate", "severe"): zones.append("Zone B — weather interference")
        if threat in ("medium", "high"): zones.append("Zone C — hostile activity elevated")
        if duration > 20: zones.append("Zone D — asset endurance limit")
        if not zones: zones.append("No high-risk zones identified")
        return zones

    def _route_suggestion(self, risk_category, weather, mission_type) -> str:
        if risk_category == "High": return "Contingency route: bypass Zone C, reduce exposure."
        elif risk_category == "Medium": return "Proceed with planned route, increase sweep in Zone B."
        return "All zones clear. Standard route execution."