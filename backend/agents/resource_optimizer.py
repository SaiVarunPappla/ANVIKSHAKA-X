"""

resource_optimizer.py

---------------------

Agent 3 — ResourceOptimizerAgent



Allocates assets to mission roles based on battery health and operating

hours. Top 60 % by health → primary; bottom 40 % → backup / standby.

Assets below 50 % battery are flagged limited-duty.

"""



from typing import Dict, Any, List





class ResourceOptimizerAgent:

   """Optimises asset allocation for the mission."""



   def __init__(self):

       self.name = "ResourceOptimizerAgent"



   # -----------------------------------------------------------------

   def run(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:

       """

       Parameters

       ----------

       input_dict : dict

           assets : list of dicts each with keys

                    name, asset_type, battery_health, operating_hours,

                    mission_count, status



       Returns

       -------

       dict with keys: allocation (dict per asset), summary, coverage_pct

       """

       assets: List[dict] = input_dict.get("assets", [])

       if not assets:

           return {

               "agent": self.name,

               "status": "completed",

               "allocation": {},

               "summary": "No assets available for allocation.",

               "coverage_pct": 0.0,

           }



       # Sort by battery_health descending

       sorted_assets = sorted(

           assets, key=lambda a: a.get("battery_health", 0), reverse=True

       )



       split_idx = max(1, int(len(sorted_assets) * 0.6))

       primary = sorted_assets[:split_idx]

       backup = sorted_assets[split_idx:]



       allocation = {}



       for i, asset in enumerate(primary):

           role = "Primary"

           detail = self._primary_detail(asset, i)

           if asset.get("battery_health", 100) < 50:

               role = "Limited-Duty Primary"

               detail += " ⚠ Battery below 50 % — restrict to short-duration tasks."

           allocation[asset["name"]] = {

               "role": role,

               "detail": detail,

               "battery": asset.get("battery_health", 0),

               "operating_hours": asset.get("operating_hours", 0),

           }



       for asset in backup:

           role = "Backup / Standby"

           detail = "Held in reserve; deploy if primary asset is compromised or fatigued."

           if asset.get("battery_health", 100) < 50:

               role = "Limited-Duty Reserve"

               detail = "⚠ Battery critically low — maintenance recommended before deployment."

           allocation[asset["name"]] = {

               "role": role,

               "detail": detail,

               "battery": asset.get("battery_health", 0),

               "operating_hours": asset.get("operating_hours", 0),

           }



       # Coverage estimate

       healthy_primary = sum(

           1 for a in primary if a.get("battery_health", 0) >= 50

       )

       coverage_pct = round(

           (healthy_primary / max(len(sorted_assets), 1)) * 100, 1

       )



       summary = (

           f"{len(primary)} asset(s) assigned primary roles, "

           f"{len(backup)} held as backup. Estimated coverage: {coverage_pct}%."

       )



       return {

           "agent": self.name,

           "status": "completed",

           "allocation": allocation,

           "summary": summary,

           "coverage_pct": coverage_pct,

       }



   # -----------------------------------------------------------------

   def _primary_detail(self, asset, index) -> str:

       atype = asset.get("asset_type", "drone")

       if atype == "drone":

           zones = ["Zone A + Zone C", "Zone B", "Zone D"]

           return f"Aerial surveillance — {zones[index % len(zones)]}"

       elif atype == "auv":

           tasks = ["Deep sonar scan — Zone A", "Shallow patrol — Zone B", "Reserve sonar grid"]

           return tasks[index % len(tasks)]

       elif atype == "torpedo":

           return "Standby weapons platform — armed readiness"

       elif atype == "launcher":

           return "Deployment platform — launch-ready posture"

       return "General purpose asset"
