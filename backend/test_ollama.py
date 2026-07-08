"""
test_ollama.py
--------------
Quick test script to verify Ollama integration
"""

import sys
sys.path.insert(0, '.')

from agents.base_agent import BaseAgent
from agents.mission_planner import MissionPlannerAgent
from agents.risk_analyst import RiskAnalystAgent

def test_base_agent():
    print("=" * 60)
    print("TEST 1: BaseAgent Ollama Detection")
    print("=" * 60)
    agent = BaseAgent()
    available = agent.is_ollama_available()
    print(f"Ollama Available: {available}")
    print()

def test_llm_call():
    print("=" * 60)
    print("TEST 2: Direct LLM Call")
    print("=" * 60)
    agent = BaseAgent()
    response = agent.call_llm(
        system_prompt="You are a helpful AI assistant.",
        user_prompt="Say 'Hello from Ollama!' in exactly 5 words."
    )
    print(f"Response: '{response}'")
    print(f"Response Length: {len(response)} chars")
    print()

def test_mission_planner():
    print("=" * 60)
    print("TEST 3: MissionPlannerAgent AI Narrative")
    print("=" * 60)
    planner = MissionPlannerAgent()
    result = planner.run({
        "mission_type": "Coastal Surveillance",
        "num_drones": 2,
        "num_auvs": 1,
        "duration_hours": 12,
        "threat_level": "medium",
        "weather": "moderate"
    })
    ai_narrative = result.get("ai_narrative", "")
    print(f"AI Narrative: '{ai_narrative[:200]}...'")
    print(f"AI Narrative Length: {len(ai_narrative)} chars")
    print()

def test_risk_analyst():
    print("=" * 60)
    print("TEST 4: RiskAnalystAgent AI Narrative")
    print("=" * 60)
    analyst = RiskAnalystAgent()
    result = analyst.run({
        "threat_level": "high",
        "weather": "severe",
        "duration_hours": 24,
        "num_assets": 5,
        "mission_type": "Deep Sea Patrol"
    })
    ai_narrative = result.get("ai_narrative", "")
    print(f"AI Narrative: '{ai_narrative[:200]}...'")
    print(f"AI Narrative Length: {len(ai_narrative)} chars")
    print()

if __name__ == "__main__":
    print("\nANVIKSHAKA-X Ollama Integration Test")
    print("=" * 60)
    print()
    
    test_base_agent()
    
    # Only continue if Ollama is available
    agent = BaseAgent()
    if agent.is_ollama_available():
        test_llm_call()
        test_mission_planner()
        test_risk_analyst()
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
    else:
        print("⚠ Ollama not available. Skipping LLM tests.")
        print("  To enable AI features:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Run: ollama pull llama3")
        print("  3. Verify: ollama list")
        print("=" * 60)
