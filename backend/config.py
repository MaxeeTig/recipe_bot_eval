"""
Configuration loader for FastAPI backend.
Imports settings from config_section.py and adds FastAPI-specific configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add parent directory to path to import config_section
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all config from config_section
from config_section import (
    DATA_DIR,
    DB_PATH,
    LLM_PROVIDER,
    TOGETHER_AI_API_KEY_ENV_VAR,
    TOGETHER_AI_API_BASE_URL,
    TOGETHER_AI_AVAILABLE_MODELS,
    VERCEL_AI_API_KEY_ENV_VAR,
    VERCEL_AI_API_BASE_URL,
    VERCEL_AI_AVAILABLE_MODELS,
    MISTRAL_AI_API_KEY_ENV_VAR,
    MISTRAL_AI_API_BASE_URL,
    MISTRAL_AI_AVAILABLE_MODELS,
    DEEPSEEK_AI_API_KEY_ENV_VAR,
    DEEPSEEK_AI_API_BASE_URL,
    DEEPSEEK_AI_AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_ANALYSIS_MODEL,
    SYSTEM_PROMPT_FILE,
    ERROR_ANALYSIS_PROMPT_FILE,
    LLM_TEMPERATURE,
    AUTO_ANALYZE_FAILURES,
    MAX_SUCCESSFUL_EXAMPLES,
    BASE_URL,
    SEARCH_URL,
    IMPLICIT_WAIT,
    PAGE_LOAD_WAIT,
    SEARCH_RESULTS_WAIT,
    ELEMENT_WAIT_TIMEOUT,
    MIN_TEXT_LENGTH_SHORT,
    MIN_TEXT_LENGTH_LONG,
    MAX_LIST_ITEMS,
    MAX_PARAGRAPHS,
    CHROME_HEADLESS,
    CHROME_OPTIONS,
    OUTPUT_DIR,
    TIMESTAMP_FORMAT,
    ALLOWED_UNITS,
)

# Load environment variables
load_dotenv()

# FastAPI-specific settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8003"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
LOG_DIR = Path(__file__).parent.parent / "log"
LOG_DIR.mkdir(exist_ok=True)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# File paths (relative to project root)
SYSTEM_PROMPT_PATH = PROJECT_ROOT / SYSTEM_PROMPT_FILE
ERROR_ANALYSIS_PROMPT_PATH = PROJECT_ROOT / ERROR_ANALYSIS_PROMPT_FILE
