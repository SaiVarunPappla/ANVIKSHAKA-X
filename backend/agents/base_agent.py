"""
base_agent.py
-------------
Abstract base class for all AI-powered agents.
Handles Ollama LLM integration with graceful fallback.
"""

import logging
import time
from typing import Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class providing LLM capabilities to agents."""
    
    # Class-level cache for Ollama availability (shared across all agents)
    _ollama_cache = {"available": None, "checked_at": 0}
    _CACHE_TTL = 5  # seconds
    
    def __init__(self):
        self.name = self.__class__.__name__

    def is_ollama_available(self) -> bool:
        """Check if Ollama server is running and accessible (with short-lived caching)."""
        if not OLLAMA_AVAILABLE:
            logger.debug(f"[{self.name}] Ollama library not installed")
            return False
        
        # Check cache first
        now = time.time()
        if (BaseAgent._ollama_cache["available"] is not None and 
            now - BaseAgent._ollama_cache["checked_at"] < BaseAgent._CACHE_TTL):
            logger.debug(f"[{self.name}] Using cached Ollama status: {BaseAgent._ollama_cache['available']}")
            return BaseAgent._ollama_cache["available"]
        
        # Cache miss or expired - check again
        try:
            ollama.list()
            BaseAgent._ollama_cache["available"] = True
            BaseAgent._ollama_cache["checked_at"] = now
            logger.debug(f"[{self.name}] Ollama server is available")
            return True
        except Exception as e:
            BaseAgent._ollama_cache["available"] = False
            BaseAgent._ollama_cache["checked_at"] = now
            logger.debug(f"[{self.name}] Ollama server not available: {e}")
            return False

    def call_llm(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Call local LLM via Ollama.
        Returns empty string on any failure (silent fallback).
        
        Args:
            system_prompt: System instruction for the LLM
            user_prompt: User query/task for the LLM
            max_tokens: Maximum tokens to generate (optional, uses Ollama's num_predict)
        """
        if not self.is_ollama_available():
            logger.info(f"[{self.name}] Ollama not available, skipping LLM call")
            return ""
        
        try:
            logger.info(f"[{self.name}] Calling LLM with prompt length: {len(user_prompt)} chars")
            
            # Build options dict
            options = {"keep_alive": "5m"}
            if max_tokens:
                options["num_predict"] = max_tokens
                logger.debug(f"[{self.name}] Setting max tokens: {max_tokens}")
            
            response = ollama.chat(
                model="llama3",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options=options
            )
            content = response.get("message", {}).get("content", "").strip()
            logger.info(f"[{self.name}] LLM response length: {len(content)} chars")
            return content
        except Exception as e:
            logger.warning(f"[{self.name}] LLM call failed: {e}")
            return ""