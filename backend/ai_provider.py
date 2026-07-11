"""
ai_provider.py
--------------
Unified AI provider interface supporting multiple backends:
- Gemini (Google AI) for production/hosted deployments
- Ollama for local/offline deployments
- Rule-based fallback when no AI is available

Environment Configuration:
- AI_PROVIDER: "gemini", "ollama", "auto", or "rule-based" (default: "auto")
- GEMINI_API_KEY: API key for Google Gemini
- GEMINI_MODEL: Model name (default: "gemini-1.5-flash")
- OLLAMA_HOST: Ollama server URL (used by ollama-python library, default: "http://localhost:11434")
- OLLAMA_MODEL: Ollama model name (default: "llama3")
"""

import logging
import os
import time
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)

# Try importing providers
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.info("[AI] Ollama library not installed")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.info("[AI] Google Generative AI library not installed")


class AIProviderType(str, Enum):
    """Available AI provider types."""
    GEMINI = "gemini"
    OLLAMA = "ollama"
    AUTO = "auto"
    RULE_BASED = "rule-based"


class AIProvider:
    """
    Unified AI provider that handles multiple backends with graceful fallback.
    
    Selection logic when AI_PROVIDER="auto":
    1. If GEMINI_API_KEY is set and Gemini is available → use Gemini
    2. Else if Ollama is running locally → use Ollama
    3. Else → use rule-based fallback (no AI)
    """
    
    # Class-level cache for provider status
    _cache = {
        "provider": None,
        "ollama_available": None,
        "gemini_available": None,
        "checked_at": 0
    }
    _CACHE_TTL = 10  # seconds
    
    def __init__(self):
        """Initialize AI provider based on environment configuration."""
        self.provider_type = os.getenv("AI_PROVIDER", "auto").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Initialize Gemini if configured
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_api_key)
                logger.info(f"[AI] Gemini configured with model: {self.gemini_model}")
            except Exception as e:
                logger.warning(f"[AI] Failed to configure Gemini: {e}")
        
        self._active_provider = None
        self._select_provider()
    
    def _select_provider(self) -> str:
        """
        Select the active AI provider based on configuration and availability.
        Returns: "gemini", "ollama", or "rule-based"
        """
        now = time.time()
        
        # Use cached provider if still valid
        if (AIProvider._cache["provider"] is not None and 
            now - AIProvider._cache["checked_at"] < AIProvider._CACHE_TTL):
            self._active_provider = AIProvider._cache["provider"]
            return self._active_provider
        
        # Explicit provider selection
        if self.provider_type == AIProviderType.GEMINI:
            if self._check_gemini():
                self._active_provider = "gemini"
            else:
                logger.warning("[AI] Gemini requested but not available, falling back to rule-based")
                self._active_provider = "rule-based"
        
        elif self.provider_type == AIProviderType.OLLAMA:
            if self._check_ollama():
                self._active_provider = "ollama"
            else:
                logger.warning("[AI] Ollama requested but not available, falling back to rule-based")
                self._active_provider = "rule-based"
        
        elif self.provider_type == AIProviderType.RULE_BASED:
            self._active_provider = "rule-based"
        
        else:  # auto mode
            if self._check_gemini():
                self._active_provider = "gemini"
            elif self._check_ollama():
                self._active_provider = "ollama"
            else:
                self._active_provider = "rule-based"
        
        # Cache the result
        AIProvider._cache["provider"] = self._active_provider
        AIProvider._cache["checked_at"] = now
        
        logger.info(f"[AI] Active provider: {self._active_provider}")
        return self._active_provider
    
    def _check_gemini(self) -> bool:
        """Check if Gemini is available and configured."""
        if not GEMINI_AVAILABLE:
            return False
        
        if not self.gemini_api_key:
            return False
        
        # Check cache
        now = time.time()
        if (AIProvider._cache["gemini_available"] is not None and 
            now - AIProvider._cache["checked_at"] < AIProvider._CACHE_TTL):
            return AIProvider._cache["gemini_available"]
        
        # Quick validation - just check if we can create a model instance
        try:
            genai.GenerativeModel(self.gemini_model)
            AIProvider._cache["gemini_available"] = True
            logger.debug("[AI] Gemini is available")
            return True
        except Exception as e:
            logger.debug(f"[AI] Gemini not available: {e}")
            AIProvider._cache["gemini_available"] = False
            return False
    
    def _check_ollama(self) -> bool:
        """
        Check if Ollama server is running and accessible.
        
        Note: ollama-python library uses OLLAMA_HOST environment variable to connect.
        Set OLLAMA_HOST=http://custom:port if using a non-default Ollama server.
        """
        if not OLLAMA_AVAILABLE:
            return False
        
        # Check cache
        now = time.time()
        if (AIProvider._cache["ollama_available"] is not None and 
            now - AIProvider._cache["checked_at"] < AIProvider._CACHE_TTL):
            return AIProvider._cache["ollama_available"]
        
        # Check if server is running
        try:
            ollama.list()
            AIProvider._cache["ollama_available"] = True
            logger.debug("[AI] Ollama is available")
            return True
        except Exception as e:
            logger.debug(f"[AI] Ollama not available: {e}")
            AIProvider._cache["ollama_available"] = False
            return False
    
    def get_active_provider(self) -> str:
        """Get the currently active provider name."""
        if self._active_provider is None:
            self._select_provider()
        return self._active_provider
    
    def is_ai_available(self) -> bool:
        """Check if any AI provider (Gemini or Ollama) is available."""
        provider = self.get_active_provider()
        return provider in ["gemini", "ollama"]
    
    def call_ai(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Call the active AI provider with prompts.
        Returns AI-generated text or empty string on failure/unavailability.
        
        Args:
            system_prompt: System instruction for the AI
            user_prompt: User query/task for the AI
            max_tokens: Maximum tokens to generate (optional)
        
        Returns:
            str: AI-generated response or empty string
        """
        provider = self.get_active_provider()
        
        if provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt, max_tokens)
        elif provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt, max_tokens)
        else:
            logger.debug("[AI] No AI provider available, returning empty response")
            return ""
    
    def _call_gemini(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """Call Google Gemini API."""
        try:
            logger.info(f"[AI/Gemini] Calling with prompt length: {len(user_prompt)} chars")
            
            # Create model instance
            model = genai.GenerativeModel(
                model_name=self.gemini_model,
                system_instruction=system_prompt
            )
            
            # Configure generation
            generation_config = {}
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Generate response
            response = model.generate_content(
                user_prompt,
                generation_config=generation_config if generation_config else None
            )
            
            content = response.text.strip()
            logger.info(f"[AI/Gemini] Response length: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.warning(f"[AI/Gemini] Call failed: {e}")
            # Invalidate cache on failure
            AIProvider._cache["gemini_available"] = False
            AIProvider._cache["checked_at"] = 0
            return ""
    
    def _call_ollama(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Call local Ollama LLM.
        
        Note: ollama-python library uses OLLAMA_HOST environment variable.
        Set OLLAMA_HOST=http://custom:port if not using default localhost:11434.
        """
        try:
            logger.info(f"[AI/Ollama] Calling with prompt length: {len(user_prompt)} chars")
            
            # Build options dict
            options = {"keep_alive": "5m"}
            if max_tokens:
                options["num_predict"] = max_tokens
            
            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options=options
            )
            
            content = response.get("message", {}).get("content", "").strip()
            logger.info(f"[AI/Ollama] Response length: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.warning(f"[AI/Ollama] Call failed: {e}")
            # Invalidate cache on failure
            AIProvider._cache["ollama_available"] = False
            AIProvider._cache["checked_at"] = 0
            return ""


# Global AI provider instance
_ai_provider_instance = None

def get_ai_provider() -> AIProvider:
    """Get or create the global AI provider instance."""
    global _ai_provider_instance
    if _ai_provider_instance is None:
        _ai_provider_instance = AIProvider()
    return _ai_provider_instance
