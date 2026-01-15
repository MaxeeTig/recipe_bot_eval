# =============================================================================
# CONFIGURATION SECTION - Easy model and provider switching
# =============================================================================

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database Configuration
DATABASE_PATH = BASE_DIR / "data" / "recipes.db"

# Tavily Search Configuration
TAVILY_CONFIG = {
    "api_key": os.getenv("TAVILY_API_KEY", "")
}

# AI Gateway Configuration (for future use)
AI_GATEWAY_CONFIG = {
    "api_key": os.getenv("AI_GATEWAY_API_KEY", ""),
    "base_url": "https://ai-gateway.vercel.sh/v1",
    "timeout": 30.0
}

# Available Models - Add/remove models here for easy switching
AVAILABLE_MODELS = {
    # OpenAI Models
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini", 
    "gpt-4-turbo": "openai/gpt-4-turbo",
    
    # Anthropic Models
    "claude-3-5-sonnet": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-5-haiku": "anthropic/claude-3-5-haiku-20241022",
    "claude-3-opus": "anthropic/claude-3-opus-20240229",
    
    # Mistral Models
    "mistral-large": "mistral/mistral-large-latest",
    "mistral-medium": "mistral/mistral-medium-latest",
    "mistral-small": "mistral/mistral-small-latest",
    
    # Google Models
    "gemini-1.5-pro": "google/gemini-1.5-pro-latest",
    "gemini-1.5-flash": "google/gemini-1.5-flash-latest",
    
    # Meta Models
    "llama-3.1-405b": "meta/llama-3.1-405b-instruct",
    "llama-3.1-70b": "meta/llama-3.1-70b-instruct",
    "llama-3.1-8b": "meta/llama-3.1-8b-instruct",
}

# Default model selection - Change this to switch default model
DEFAULT_MODEL = "gpt-4o-mini"  # Fast and cost-effective
# DEFAULT_MODEL = "claude-3-5-sonnet"  # High quality reasoning
# DEFAULT_MODEL = "mistral-large"  # Good balance

# Model-specific configurations
MODEL_CONFIGS = {
    "openai/gpt-4o": {"max_tokens": 4096, "temperature": 0.3},
    "openai/gpt-4o-mini": {"max_tokens": 2048, "temperature": 0.3},
    "anthropic/claude-3-5-sonnet-20241022": {"max_tokens": 4096, "temperature": 0.3},
    "anthropic/claude-3-5-haiku-20241022": {"max_tokens": 2048, "temperature": 0.3},
    "mistral/mistral-large-latest": {"max_tokens": 2048, "temperature": 0.3},
    "mistral/mistral-small-latest": {"max_tokens": 1024, "temperature": 0.3},
}

# Logging Configuration
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = BASE_DIR / "logs"
ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"

# Map string log level to logging constant
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Convert string to logging level
LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL_STR, logging.INFO)
