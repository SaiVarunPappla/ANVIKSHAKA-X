"""
ai_provider.py
--------------
Unified AI provider interface supporting multiple backends:
- Gemini (Google AI) for production/hosted deployments
- Ollama for local/offline deployments
- Rule-based fallback when no AI is available

Environment Configuration:
- AI_PROVIDER: "gemini", "ollama", "auto", or "rule-based" (default: "auto")
- GEMINI_API_KEY: API key for Google Gemini (REQUIRED for AI features)
- GEMINI_MODEL: Optional model name override (default: "gemini-1.5-flash")
- OLLAMA_HOST: Ollama server URL (default: "http://localhost:11434")
- OLLAMA_MODEL: Ollama model name (default: "llama3")
"""

import logging
import os
import time
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)

# Default stable model - known to be widely available
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"

# Try importing providers
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.info("[AI] Ollama library not installed")

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.info("[AI] Google GenAI library not installed")


class AIProviderType(str, Enum):
    """Available AI provider types."""
    GEMINI = "gemini"
    OLLAMA = "ollama"
    AUTO = "auto"
    RULE_BASED = "rule-based"


class AIProvider:
    """
    Unified AI provider with simple, robust Gemini integration.
    
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
        """Initialize AI provider with simple configuration."""
        self.provider_type = os.getenv("AI_PROVIDER", "auto").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        # Use override if set, otherwise use stable default
        self.gemini_model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL
        self.gemini_fallback_attempted = False  # Track if we've tried fallback
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Log configuration at startup
        logger.info(f"[AI] ==================== AI PROVIDER INITIALIZATION ====================")
        logger.info(f"[AI] Provider type: {self.provider_type}")
        logger.info(f"[AI] Gemini model: {self.gemini_model}")
        logger.info(f"[AI] Gemini default: {DEFAULT_GEMINI_MODEL}")
        logger.info(f"[AI] GEMINI_API_KEY present: {bool(self.gemini_api_key)}")
        logger.info(f"[AI] GEMINI_AVAILABLE (SDK imported): {GEMINI_AVAILABLE}")
        
        # Initialize Gemini client if configured
        self.gemini_client = None
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"[AI] ✓ Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"[AI] ✗ Failed to initialize Gemini client: {type(e).__name__}: {e}")
        elif not self.gemini_api_key:
            logger.warning("[AI] ⚠ GEMINI_API_KEY not set - Gemini will not be available")
        elif not GEMINI_AVAILABLE:
            logger.warning("[AI] ⚠ google-genai library not installed")
        
        self._active_provider = None
        self._select_provider()
        logger.info(f"[AI] ======================================================================")
    
    def get_selected_model(self) -> Optional[str]:
        """Get the currently configured Gemini model name."""
        return self.gemini_model
    
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
            logger.debug("[AI] Gemini library not available")
            return False
        
        if not self.gemini_api_key:
            logger.debug("[AI] Gemini API key not set")
            return False
        
        if not self.gemini_client:
            logger.debug("[AI] Gemini client not initialized")
            return False
        
        # Check cache
        now = time.time()
        if (AIProvider._cache["gemini_available"] is not None and 
            now - AIProvider._cache["checked_at"] < AIProvider._CACHE_TTL):
            return AIProvider._cache["gemini_available"]
        
        # Client is initialized and API key is present - consider it available
        # We don't test the actual API call here to avoid startup delays
        try:
            AIProvider._cache["gemini_available"] = True
            logger.debug(f"[AI] Gemini is available (model: {self.gemini_model})")
            return True
        except Exception as e:
            logger.debug(f"[AI] Gemini check failed: {e}")
            AIProvider._cache["gemini_available"] = False
            return False
    
    def _check_ollama(self) -> bool:
        """Check if Ollama server is running and accessible."""
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
        """Call Google Gemini API using simple, robust pattern."""
        try:
            logger.info(f"[AI/Gemini] Attempting call with model: '{self.gemini_model}'")
            logger.info(f"[AI/Gemini] Prompt length: {len(user_prompt)} chars, max_tokens: {max_tokens}")
            logger.info(f"[AI/Gemini] API key present: {bool(self.gemini_api_key)}")
            
            if not self.gemini_client:
                logger.error("[AI/Gemini] Client not initialized")
                return ""
            
            if not self.gemini_model:
                logger.error("[AI/Gemini] No model configured")
                return ""
            
            # Build generation config
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            if max_tokens:
                config["max_output_tokens"] = max_tokens
            
            # Call the Gemini API
            logger.info(f"[AI/Gemini] Calling generate_content...")
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=user_prompt,
                config=config if config else None
            )
            
            # Log raw response structure for debugging
            logger.info(f"[AI/Gemini] Response received - analyzing structure...")
            logger.info(f"[AI/Gemini] Has 'text' attribute: {hasattr(response, 'text')}")
            logger.info(f"[AI/Gemini] Has 'candidates' attribute: {hasattr(response, 'candidates')}")
            
            # Extract text from response - try multiple methods
            content = ""
            
            # Method 1: Try response.text directly
            if hasattr(response, 'text'):
                try:
                    content = response.text
                    if content:
                        logger.info(f"[AI/Gemini] Extracted via response.text: {len(content)} chars")
                except Exception as e:
                    logger.warning(f"[AI/Gemini] Failed to access response.text: {e}")
            
            # Method 2: If text is empty, try candidates
            if not content and hasattr(response, 'candidates'):
                try:
                    candidates = response.candidates
                    logger.info(f"[AI/Gemini] Found {len(candidates)} candidates")
                    
                    if candidates and len(candidates) > 0:
                        candidate = candidates[0]
                        logger.info(f"[AI/Gemini] First candidate type: {type(candidate)}")
                        logger.info(f"[AI/Gemini] Has 'content': {hasattr(candidate, 'content')}")
                        
                        if hasattr(candidate, 'content'):
                            content_obj = candidate.content
                            logger.info(f"[AI/Gemini] Content type: {type(content_obj)}")
                            logger.info(f"[AI/Gemini] Has 'parts': {hasattr(content_obj, 'parts')}")
                            
                            if hasattr(content_obj, 'parts'):
                                parts = content_obj.parts
                                logger.info(f"[AI/Gemini] Found {len(parts)} content parts")
                                
                                # Join all text parts
                                text_parts = []
                                for i, part in enumerate(parts):
                                    if hasattr(part, 'text'):
                                        text_parts.append(part.text)
                                        logger.info(f"[AI/Gemini] Part {i}: {len(part.text)} chars")
                                
                                content = " ".join(text_parts)
                                if content:
                                    logger.info(f"[AI/Gemini] Extracted via candidates[0].content.parts: {len(content)} chars")
                except Exception as e:
                    logger.error(f"[AI/Gemini] Failed to extract from candidates: {type(e).__name__}: {e}")
            
            # Strip and validate
            content = content.strip() if content else ""
            
            if content:
                logger.info(f"[AI/Gemini] SUCCESS - Final content: {len(content)} chars")
                # Reset fallback flag on success
                self.gemini_fallback_attempted = False
                return content
            else:
                logger.warning(f"[AI/Gemini] Response received but no usable text content found")
                logger.warning(f"[AI/Gemini] Response type: {type(response)}")
                logger.warning(f"[AI/Gemini] Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                return ""
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"[AI/Gemini] FAILED - {error_type}: {error_msg}")
            logger.error(f"[AI/Gemini] Model attempted: '{self.gemini_model}'")
            logger.error(f"[AI/Gemini] Default model: '{DEFAULT_GEMINI_MODEL}'")
            
            # Handle 404 NOT_FOUND - try fallback to default model once
            if "404" in error_msg or "NOT_FOUND" in error_msg:
                if not self.gemini_fallback_attempted and self.gemini_model != DEFAULT_GEMINI_MODEL:
                    logger.warning(f"[AI/Gemini] Model '{self.gemini_model}' not found, trying fallback: '{DEFAULT_GEMINI_MODEL}'")
                    self.gemini_model = DEFAULT_GEMINI_MODEL
                    self.gemini_fallback_attempted = True
                    # Recursive call with default model
                    return self._call_gemini(system_prompt, user_prompt, max_tokens)
                else:
                    logger.error(f"[AI/Gemini] Fallback to default model also failed or already attempted")
            
            # Handle rate limiting (429) - don't invalidate cache, just fail this request
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                logger.warning(f"[AI/Gemini] Rate limited - will retry on next request")
                # Don't invalidate cache
                return ""
            
            # Handle server errors (503, 500) - temporary issues
            if "503" in error_msg or "500" in error_msg or "UNAVAILABLE" in error_msg:
                logger.warning(f"[AI/Gemini] Server error - temporary issue")
                # Don't invalidate cache
                return ""
            
            # For other errors (invalid key, permission denied), invalidate cache
            if "401" in error_msg or "403" in error_msg or "PERMISSION_DENIED" in error_msg or "INVALID_ARGUMENT" in error_msg:
                logger.error(f"[AI/Gemini] Authentication/authorization error - marking as unavailable")
                AIProvider._cache["gemini_available"] = False
                AIProvider._cache["checked_at"] = 0
            
            return ""
    
    def _call_ollama(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """Call local Ollama LLM."""
        try:
            logger.info(f"[AI/Ollama] Calling model '{self.ollama_model}' with prompt length: {len(user_prompt)} chars")
            
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
            logger.info(f"[AI/Ollama] Response received: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"[AI/Ollama] Call failed: {type(e).__name__}: {str(e)}")
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
