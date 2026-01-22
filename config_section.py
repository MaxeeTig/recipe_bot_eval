"""
Configuration file for recipe processing pipeline.
Centralizes all configuration variables for easy management.
"""
from pathlib import Path
from typing import Dict

# ============================================================================
# Database Configuration
# ============================================================================

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "recipes.db"
PATCHES_DIR = Path(__file__).parent / "patches"

# ============================================================================
# LLM/API Configuration
# ============================================================================

# Provider selection: "together_ai", "vercel_ai", "mistral_ai", or "deepseek_ai"
LLM_PROVIDER = "mistral_ai"

# Together AI Configuration
TOGETHER_AI_API_KEY_ENV_VAR = "TOGETHER_AI_API_KEY"
TOGETHER_AI_API_BASE_URL = "https://api.together.xyz"
TOGETHER_AI_AVAILABLE_MODELS: Dict[str, str] = {
    "gpt-oss-20b": "openai/gpt-oss-20b",
    "llama-3.2-3b": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
    "llama-3.2-11b": "meta-llama/Llama-3.2-11B-Instruct-Turbo",
}

# Vercel AI Gateway Configuration
VERCEL_AI_API_KEY_ENV_VAR = "AI_GATEWAY_API_KEY"  # Also supports "AI_GATEWAY_API_KEY"
VERCEL_AI_API_BASE_URL = "https://ai-gateway.vercel.sh/v1"
VERCEL_AI_AVAILABLE_MODELS: Dict[str, str] = {
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "claude-opus": "anthropic/claude-opus-4.5",
    "claude-sonnet": "anthropic/claude-sonnet-4",
}

# Mistral AI Configuration
MISTRAL_AI_API_KEY_ENV_VAR = "MISTRAL_API_KEY"
MISTRAL_AI_API_BASE_URL = "https://api.mistral.ai/v1"
MISTRAL_AI_AVAILABLE_MODELS: Dict[str, str] = {
    "open-mistral-7b": "open-mistral-7b",  # Small/free for recipe parsing
    "mistral-small-latest": "mistral-small-latest",  # For code analysis
    "mistral-medium-latest": "mistral-medium-latest",  # Optional: more powerful
}

# DeepSeek AI Configuration
DEEPSEEK_AI_API_KEY_ENV_VAR = "DEEPSEEK_API_KEY"
DEEPSEEK_AI_API_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_AI_AVAILABLE_MODELS: Dict[str, str] = {
    "deepseek-chat": "deepseek-chat",  # Small/free for recipe parsing
    "deepseek-coder": "deepseek-coder",  # For code analysis
}

# Default model (must exist in the selected provider's available models)
# LLM 1: For recipe parsing
#DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MODEL = "open-mistral-7b"

# LLM 2: For error analysis (should be a larger, more capable model)
# Must exist in the selected provider's available models
# For mistral_ai: "mistral-small-latest" or "mistral-medium-latest"
# For vercel_ai: "gpt-4o" or "claude-opus"
# For together_ai: "llama-3.2-11b"
# For deepseek_ai: "deepseek-coder"
DEFAULT_ANALYSIS_MODEL = "mistral-small-latest"  # For code analysis

# System prompt file paths
SYSTEM_PROMPT_FILE = "system_prompt.txt"  # For LLM 1 (parsing)
ERROR_ANALYSIS_PROMPT_FILE = "error_analysis_prompt.txt"  # For LLM 2 (analysis)

# LLM temperature setting
LLM_TEMPERATURE = 0.1

# Error analysis configuration
AUTO_ANALYZE_FAILURES = False  # Auto-analyze failures during parsing
MAX_SUCCESSFUL_EXAMPLES = 3  # Number of successful examples to include in analysis

# ============================================================================
# Web Scraping Configuration
# ============================================================================

# Base URL for recipe site
BASE_URL = "https://www.russianfood.com"

# Search page URL
SEARCH_URL = "https://www.russianfood.com/search/simple/index.php"

# Selenium wait times (in seconds)
IMPLICIT_WAIT = 7
PAGE_LOAD_WAIT = 2
SEARCH_RESULTS_WAIT = 3
ELEMENT_WAIT_TIMEOUT = 7

# Text extraction thresholds
MIN_TEXT_LENGTH_SHORT = 10
MIN_TEXT_LENGTH_LONG = 20
MAX_LIST_ITEMS = 50
MAX_PARAGRAPHS = 30

# Chrome options (can be extended)
CHROME_HEADLESS = True
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
]

# ============================================================================
# File Output Configuration
# ============================================================================

# Output directory (None means current directory)
OUTPUT_DIR = None

# Timestamp format for filenames
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# ============================================================================
# Recipe Model Configuration
# ============================================================================

# Allowed unit types
ALLOWED_UNITS = ["г", "мл", "шт", "ст.л", "ч.л", "чашка", "л", "кг"]
