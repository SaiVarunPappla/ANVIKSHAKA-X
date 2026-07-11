"""
chat.py
-------
POST /api/chat — ANVIKSHA AI chat assistant endpoint
"""

import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])
base_agent = BaseAgent()

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

@router.post("/chat")
async def chat(payload: ChatRequest):
    """Process chat message via AI (Gemini/Ollama) or fallback rule-based logic."""
    system_prompt = (
        "You are ANVIKSHA, an AI military intelligence assistant embedded in the "
        "ANVIKSHAKA-X platform. You help operators analyze missions, interpret risk "
        "data, and understand asset health. Be helpful, professional, and concise. "
        "Always ground answers in the defence/naval domain."
    )
    
    user_prompt = payload.message
    if payload.context:
        user_prompt = f"Context: {payload.context}\n\nQuestion: {payload.message}"

    logger.info(f"[Chat] Checking AI provider availability...")
    ai_available = base_agent.is_ai_available()
    ai_provider = base_agent.get_ai_provider_name()
    logger.info(f"[Chat] AI provider: {ai_provider}, available: {ai_available}")
    
    if ai_available:
        logger.info(f"[Chat] Calling AI for message: {payload.message[:50]}...")
        response_text = base_agent.call_llm(system_prompt, user_prompt, max_tokens=80)
        logger.info(f"[Chat] AI response length: {len(response_text)} chars")
        if response_text:
            return {"response": response_text, "model": ai_provider, "ai_powered": True}
        else:
            logger.warning(f"[Chat] AI returned empty response, falling back")

    # Fallback logic
    logger.info(f"[Chat] Using fallback logic")
    msg = payload.message.lower()
    if "risk" in msg:
        resp = "Risk is calculated based on threat level, weather, and duration. High threat and severe weather significantly increase the risk score. Check the Risk Dashboard for detailed breakdowns."
    elif "maintenance" in msg or "asset" in msg:
        resp = "Asset health is monitored via our RandomForest ML model. AUV 2 currently has critical battery degradation. I recommend immediate maintenance before deploying it."
    elif "mission" in msg:
        resp = "Missions are planned via the 5-agent pipeline. You can create one from the Mission Planner or use the Natural Language Commander below."
    elif "hello" in msg or "hi" in msg:
        resp = "Greetings, Commander. I am ANVIKSHA. State your request."
    else:
        resp = "I am currently operating in limited mode without AI assistance. I can still help you navigate mission parameters and basic asset status."
        
    return {"response": resp, "model": "rule-based", "ai_powered": False}