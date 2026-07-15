"""
ai_provider.py
--------------
Unified AI provider interface supporting multiple backends:
- Gemini (Google AI) for production/hosted deployments with auto-discovery
- Ollama for local/offline deployments
- Rule-based fallback when no AI is available

Environment Configuration:
- AI_PROVIDER: "gemini", "ollama", "auto", or "rule-based" (default: "auto")
- GEMINI_API_KEY: API key for Google Gemini (REQUIRED for AI features)
- GEMINI_MODEL: Optional model name override (auto-selects if not set)
- OLLAMA_HOST: Ollama server URL (default: "http://localhost:11434")
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
    Unified AI provider with auto-discovery and graceful fallback.
    
    Selection logic when AI_PROVIDER="auto":
    1. If GEMINI_API_KEY is set and Gemini models discovered → use Gemini
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
        """Initialize AI provider with model auto-discovery."""
        self.provider_type = os.getenv("AI_PROVIDER", "auto").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model_override = os.getenv("GEMINI_MODEL", "")  # User override
        self.gemini_model = None  # Will be auto-selected
        self.available_models = []  # Will be populated during discovery
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Preferred models in priority order (best to fallback)
        self.preferred_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash-8b",
            "gemini-pro",
            "gemini-2.0-flash-exp",  # Experimental
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
        ]
        
        # Log configuration at startup
        logger.info(f"[AI] ==================== AI PROVIDER INITIALIZATION ====================")
        logger.info(f"[AI] Provider type: {self.provider_type}")
        logger.info(f"[AI] GEMINI_MODEL override: {self.gemini_model_override or 'none (will auto-select)'}")
        logger.info(f"[AI] GEMINI_API_KEY present: {bool(self.gemini_api_key)}")
        logger.info(f"[AI] GEMINI_AVAILABLE (SDK imported): {GEMINI_AVAILABLE}")
        
        # Initialize Gemini client and discover models
        self.gemini_client = None
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"[AI] ✓ Gemini client initialized successfully")
                
                # Discover available models
                self._discover_gemini_models()
                
            except Exception as e:
                logger.error(f"[AI] ✗ Failed to initialize Gemini client: {type(e).__name__}: {e}")
        elif not self.gemini_api_key:
            logger.warning("[AI] ⚠ GEMINI_API_KEY not set - Gemini will not be available")
        elif not GEMINI_AVAILABLE:
            logger.warning("[AI] ⚠ google-genai library not installed")
        
        self._active_provider = None
        self._select_provider()
        logger.info(f"[AI] ======================================================================")
    
    def _discover_gemini_models(self):
        """Discover available Gemini models for this API key and auto-select best one."""
        if not self.gemini_client:
            return
        
        try:
            logger.info("[AI/Gemini] Discovering available models...")
            
            # List all models
            models_response = self.gemini_client.models.list()
            
            # Parse available models
            for model in models_response:
                model_name = model.name
                # Remove 'models/' prefix if present
                if model_name.startswith("models/"):
                    model_name = model_name[7:]
                
                # Check if supports generateContent
                supported_methods = getattr(model, 'supported_generation_methods', [])
                supports_generation = 'generateContent' in supported_methods if supported_methods else True
                
                self.available_models.append({
                    "name": model_name,
                    "supports_generation": supports_generation,
                    "full_name": model.name
                })
                
                logger.info(f"[AI/Gemini]   • {model_name} - supports_generation: {supports_generation}")
            
            logger.info(f"[AI/Gemini] Found {len(self.available_models)} models")
            
            # Select model
            self._select_gemini_model()
            
        except Exception as e:
            logger.error(f"[AI/Gemini] Model discovery failed: {type(e).__name__}: {e}")
            logger.warning(f"[AI/Gemini] Will attempt to use override model if set")
            
            # If discovery fails but override is set, try using it
            if self.gemini_model_override:
                self.gemini_model = self.gemini_model_override
                logger.info(f"[AI/Gemini] Using override model (unverified): {self.gemini_model}")
    
    def _select_gemini_model(self):
        """Select the best available Gemini model."""
        # If user provided override, try it first
        if self.gemini_model_override:
            # Check if override model is available
            for model in self.available_models:
                if model["name"] == self.gemini_model_override and model["supports_generation"]:
                    self.gemini_model = self.gemini_model_override
                    logger.info(f"[AI/Gemini] ✓ Selected user override model: {self.gemini_model}")
                    return
            
            # Override not found or doesn't support generation
            logger.warning(f"[AI/Gemini] ⚠ Override model '{self.gemini_model_override}' not available or doesn't support generation")
            logger.info(f"[AI/Gemini] Falling back to auto-selection from available models...")
        
        # Auto-select from preferred list
        generation_models = [m for m in self.available_models if m["supports_generation"]]
        
        if not generation_models:
            logger.error(f"[AI/Gemini] ✗ No models support text generation for this API key")
            return
        
        # Try preferred models in order
        for preferred in self.preferred_models:
            for model in generation_models:
                if model["name"] == preferred:
                    self.gemini_model = preferred
                    logger.info(f"[AI/Gemini] ✓ Auto-selected model: {self.gemini_model}")
                    return
        
        # If no preferred model found, use first available generation model
        self.gemini_model = generation_models[0]["name"]
        logger.info(f"[AI/Gemini] ✓ Selected first available model: {self.gemini_model}")
    
    def get_selected_model(self) -> Optional[str]:
        """Get the currently selected Gemini model name."""
        return self.gemini_model
    
    def get_available_models(self) -> list:
        """Get list of available Gemini models."""
        return self.available_models
    
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
        """Check if Gemini is available and configured with a valid model."""
        if not GEMINI_AVAILABLE:
            logger.debug("[AI] Gemini library not available")
            return False
        
        if not self.gemini_api_key:
            logger.debug("[AI] Gemini API key not set")
            return False
        
        if not self.gemini_client:
            logger.debug("[AI] Gemini client not initialized")
            return False
        
        if not self.gemini_model:
            logger.debug("[AI] No Gemini model selected")
            return False
        
        # Check cache
        now = time.time()
        if (AIProvider._cache["gemini_available"] is not None and 
            now - AIProvider._cache["checked_at"] < AIProvider._CACHE_TTL):
            return AIProvider._cache["gemini_available"]
        
        # Client is initialized and model is selected
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
        """Call Google Gemini API using auto-selected model."""
        try:
            logger.info(f"[AI/Gemini] Attempting call with model: '{self.gemini_model}'")
            logger.info(f"[AI/Gemini] Prompt length: {len(user_prompt)} chars, max_tokens: {max_tokens}")
            logger.info(f"[AI/Gemini] API key present: {bool(self.gemini_api_key)}")
            
            if not self.gemini_client:
                logger.error("[AI/Gemini] Client not initialized")
                return ""
            
            if not self.gemini_model:
                logger.error("[AI/Gemini] No model selected")
                return ""
            
            # Build generation config
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            if max_tokens:
                config["max_output_tokens"] = max_tokens
            
            # Call the modern SDK
            logger.info(f"[AI/Gemini] Calling generate_content...")
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=user_prompt,
                config=config if config else None
            )
            
            # Extract text from response
            content = response.text.strip() if hasattr(response, 'text') else ""
            logger.info(f"[AI/Gemini] SUCCESS - Response received: {len(content)} chars")
            return content
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"[AI/Gemini] FAILED - {error_type}: {error_msg}")
            logger.error(f"[AI/Gemini] Model attempted: '{self.gemini_model}'")
            logger.error(f"[AI/Gemini] Configured model override: '{self.gemini_model_override}'")
            logger.error(f"[AI/Gemini] Available models: {[m['name'] for m in self.available_models]}")
            
            # Invalidate cache on failure
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
