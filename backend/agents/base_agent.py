"""
base_agent.py
-------------
Abstract base class for all AI-powered agents.
Uses unified AI provider supporting Gemini, Ollama, or rule-based fallback.
"""

import logging
from typing import Optional
from ai_provider import get_ai_provider

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class providing AI capabilities to agents via unified provider."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.ai_provider = get_ai_provider()

    def is_ai_available(self) -> bool:
        """Check if any AI provider (Gemini or Ollama) is available."""
        return self.ai_provider.is_ai_available()
    
    def get_ai_provider_name(self) -> str:
        """Get the name of the active AI provider."""
        return self.ai_provider.get_active_provider()

    def call_llm(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Call AI provider (Gemini, Ollama, or none).
        Returns empty string on any failure (silent fallback to rule-based logic).
        
        Args:
            system_prompt: System instruction for the AI
            user_prompt: User query/task for the AI
            max_tokens: Maximum tokens to generate (optional)
        """
        if not self.is_ai_available():
            logger.info(f"[{self.name}] No AI provider available, using rule-based logic")
            return ""
        
        logger.info(f"[{self.name}] Calling AI via {self.get_ai_provider_name()}")
        return self.ai_provider.call_ai(system_prompt, user_prompt, max_tokens)
    
    # Backward compatibility alias
    def is_ollama_available(self) -> bool:
        """Deprecated: Use is_ai_available() instead. Checks if AI is available."""
        return self.is_ai_available()