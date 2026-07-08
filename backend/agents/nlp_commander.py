import re
from typing import Dict, Any


class NLPCommander:
    """Natural Language Command Parser.
    Parses plain English commands into structured mission parameters.
    """

    def parse(self, command: str) -> Dict[str, Any]:
        cmd = command.lower().strip()

        # Mission type
        mission_type = "Coastal Surveillance"
        if "deep sea" in cmd or "deep-sea" in cmd:
            mission_type = "Deep Sea Patrol"
        elif "air" in cmd or "aerial" in cmd:
            mission_type = "Air Patrol"
        elif "anti-submarine" in cmd or "asw" in cmd or "submarine" in cmd:
            mission_type = "Anti-Submarine"
        elif "coastal" in cmd or "coast" in cmd:
            mission_type = "Coastal Surveillance"

        # Numbers
        drones_match = re.search(r"(\d+)\s*drones?", cmd)
        auvs_match = re.search(r"(\d+)\s*auvs?", cmd)
        duration_match = re.search(r"(\d+)\s*(hours?|hrs?|hr)", cmd)

        num_drones = int(drones_match.group(1)) if drones_match else 2
        num_auvs = int(auvs_match.group(1)) if auvs_match else 1
        duration = int(duration_match.group(1)) if duration_match else 12

        # Threat level
        threat_level = "medium"
        if "high threat" in cmd or "severe threat" in cmd:
            threat_level = "high"
        elif "low threat" in cmd:
            threat_level = "low"

        # Weather
        weather = "moderate"
        if "severe weather" in cmd or "storm" in cmd or "rough" in cmd:
            weather = "severe"
        elif "calm" in cmd or "clear weather" in cmd:
            weather = "calm"

        # Name generation
        suffix = str(abs(hash(cmd)) % 1000).zfill(3)
        name = f"Op {mission_type.split()[0]} {suffix}"

        return {
            "name": name,
            "missiontype": mission_type,
            "durationhours": max(1, min(duration, 72)),
            "threatlevel": threat_level,
            "weather": weather,
            "numdrones": max(0, min(num_drones, 10)),
            "numauvs": max(0, min(num_auvs, 5)),
            "numtorpedoes": 0,
            "numlaunchers": 0,
        }