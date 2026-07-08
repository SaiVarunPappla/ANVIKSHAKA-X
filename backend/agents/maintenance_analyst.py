"""
maintenance_analyst.py
----------------------
Agent 4 — MaintenanceAnalystAgent (Upgraded with LLM)
"""

import sys, os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path: sys.path.insert(0, _PROJECT_ROOT)

try:
    from ml.predict import predict_failure
except Exception:
    predict_failure = None

class MaintenanceAnalystAgent(BaseAgent):
    """Predicts failure probability per asset using the ML model."""

    def __init__(self):
        super().__init__()

    def run(self, input_dict: Dict[str, Any], generate_narrative: bool = True) -> Dict[str, Any]:
        assets: List[dict] = input_dict.get("assets", [])
        predictions = []

        for asset in assets:
            prob = self._predict(asset)
            risk_level = self._classify(prob)
            action = self._recommend_action(asset, prob, risk_level)
            predictions.append({
                "asset_name": asset.get("name", "Unknown"),
                "asset_type": asset.get("asset_type", "unknown"),
                "battery_health": asset.get("battery_health", 0),
                "operating_hours": asset.get("operating_hours", 0),
                "mission_count": asset.get("mission_count", 0),
                "failure_probability": round(prob, 4),
                "risk_level": risk_level,
                "recommended_action": action,
            })

        critical_count = sum(1 for p in predictions if p["risk_level"] in ("critical", "high"))
        summary = f"Analysed {len(predictions)} asset(s). {critical_count} require immediate attention."

        # LLM Enhancement (optional)
        if generate_narrative:
            system_prompt = "Defence maintenance AI. Analyze asset health and failure predictions. Technical tone. Max 80 words."
            pred_summary = [{"name": p["asset_name"], "failure_prob": p["failure_probability"], "risk_level": p["risk_level"]} for p in predictions]
            user_prompt = (
                f"Assets: {critical_count} critical. "
                f"Data: {pred_summary}. "
                f"Provide maintenance priority reasoning."
            )
            ai_narrative = self.call_llm(system_prompt, user_prompt, max_tokens=100)
        else:
            ai_narrative = ""

        return {
            "agent": self.name,
            "status": "completed",
            "predictions": predictions,
            "summary": summary,
            "critical_count": critical_count,
            "ai_narrative": ai_narrative
        }

    def _predict(self, asset: dict) -> float:
        features = {
            "battery_health": asset.get("battery_health", 80),
            "operating_hours": asset.get("operating_hours", 100),
            "mission_count": asset.get("mission_count", 10),
            "temperature": asset.get("temperature", 30),
            "humidity": asset.get("humidity", 55),
            "vibration_level": asset.get("vibration_level", 3.0),
            "pressure": asset.get("pressure", 1.0),
        }
        if predict_failure is not None:
            try: return float(predict_failure(features))
            except: pass
        prob = 0.0
        if features["battery_health"] < 40: prob += 0.4
        if features["operating_hours"] > 400: prob += 0.3
        if features["mission_count"] > 50: prob += 0.2
        return min(prob, 0.95)

    def _classify(self, prob: float) -> str:
        if prob > 0.7: return "critical"
        if prob > 0.5: return "high"
        if prob > 0.3: return "medium"
        return "low"

    def _recommend_action(self, asset, prob, risk_level) -> str:
        name = asset.get("name", "asset")
        if risk_level == "critical": return f"CRITICAL — {name} immediate maintenance. Ground until cleared."
        if risk_level == "high": return f"WARNING — {name} schedule maintenance within 48h."
        if risk_level == "medium": return f"CAUTION — {name} include in next maintenance cycle."
        return f"{name} nominal. No action required."