"""
supervisor.py
-------------
Agent 5 — SupervisorAgent (Upgraded with LLM)
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent

class SupervisorAgent(BaseAgent):
    """Consolidates all agent outputs into a final mission brief."""

    def __init__(self):
        super().__init__()

    def run(self, input_dict: Dict[str, Any], generate_narrative: bool = True) -> Dict[str, Any]:
        planner = input_dict.get("mission_planner", {})
        risk = input_dict.get("risk_analyst", {})
        optimizer = input_dict.get("resource_optimizer", {})
        maintenance = input_dict.get("maintenance_analyst", {})
        mission_name = input_dict.get("mission_name", "Unnamed Mission")

        base_sp = risk.get("success_probability", 75)
        coverage = optimizer.get("coverage_pct", 80)
        critical = maintenance.get("critical_count", 0)

        sp = max(30, min(base_sp - (critical * 4), 98))

        plan_a = f"Execute full route: {' → '.join(planner.get('route', []))}. Strategy: {planner.get('strategy', 'Standard patrol.')}"
        plan_b = self._build_plan_b(risk, planner)
        alerts = self._collect_alerts(risk, maintenance)
        brief = self._build_brief(mission_name, planner, risk, optimizer, maintenance, sp, coverage)

        # LLM Enhancement (optional)
        if generate_narrative:
            system_prompt = "Supreme command AI. Synthesize agent reports into final command brief. Military commander tone. Max 100 words."
            user_prompt = (
                f"Mission: {mission_name}. Risk: {risk.get('risk_score', 0)} ({risk.get('risk_category', 'Medium')}). "
                f"Success: {sp:.1f}%. Critical assets: {critical}. Coverage: {coverage}%. "
                f"Planner: {planner.get('strategy', '')}. Risk zones: {risk.get('high_risk_zones', [])}. "
                f"Resources: {optimizer.get('summary', '')}. Generate brief."
            )
            ai_narrative = self.call_llm(system_prompt, user_prompt, max_tokens=140)
        else:
            ai_narrative = ""

        return {
            "agent": self.name,
            "status": "completed",
            "mission_name": mission_name,
            "success_probability": round(sp, 1),
            "coverage_pct": coverage,
            "risk_category": risk.get("risk_category", "Medium"),
            "risk_score": risk.get("risk_score", 50),
            "plan_a": plan_a,
            "plan_b": plan_b,
            "alerts": alerts,
            "consolidated_brief": brief,
            "ai_narrative": ai_narrative,
            "agent_summary": {
                "MissionPlannerAgent": planner.get("status", "n/a"),
                "RiskAnalystAgent": risk.get("status", "n/a"),
                "ResourceOptimizerAgent": optimizer.get("status", "n/a"),
                "MaintenanceAnalystAgent": maintenance.get("status", "n/a"),
            }
        }

    def _build_plan_b(self, risk, planner) -> str:
        cat = risk.get("risk_category", "Medium")
        if cat == "High": return "Contingency: Skip high-risk zones, reduce exposure by 30%."
        elif cat == "Medium": return "Contingency: Maintain route, increase sweep frequency."
        return "Contingency: Standard fallback. All assets nominal."

    def _collect_alerts(self, risk, maintenance) -> list:
        alerts = []
        for zone in risk.get("high_risk_zones", []): alerts.append({"type": "risk", "message": zone})
        for pred in maintenance.get("predictions", []):
            if pred["risk_level"] in ("critical", "high"):
                alerts.append({"type": "maintenance", "message": f"{pred['asset_name']}: {pred['recommended_action']}"})
        if not alerts: alerts.append({"type": "info", "message": "No critical alerts. Systems nominal."})
        return alerts

    def _build_brief(self, name, planner, risk, optimizer, maintenance, sp, coverage) -> str:
        return (
            f"═══ MISSION BRIEF: {name} ═══\n"
            f"Objective: {planner.get('objective', 'Intelligence gathering')}\n"
            f"Route: {' → '.join(planner.get('route', []))}\n"
            f"Risk Score: {risk.get('risk_score', 0):.0f}/100 ({risk.get('risk_category', 'Unknown')})\n"
            f"Success Probability: {sp:.1f}%\n"
            f"Coverage: {coverage}%\n"
            f"Resource Allocation: {optimizer.get('summary', 'N/A')}\n"
            f"Maintenance: {maintenance.get('summary', 'N/A')}"
        )