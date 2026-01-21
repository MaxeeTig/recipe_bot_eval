"""
LLM-based recipe parser service.
Refactored from recipe_parser.py with logging support.
"""
import os
import json
from pathlib import Path
from typing import Optional, Union, Any
from dotenv import load_dotenv
import sys

# Add parent directory to path to import from root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from root (for LLM context)
from recipe_models import Recipe
from response_cleanup import clean_llm_response
from patches import get_system_prompt_append
from config_section import (
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
    SYSTEM_PROMPT_FILE,
    LLM_TEMPERATURE,
)
from backend.logging_config import get_logger

# Load environment variables
load_dotenv()

# Try to import OpenAI client for Vercel AI Gateway and DeepSeek AI (optional dependency)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import Mistral AI client (optional dependency)
try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

# Try to import Together AI client
try:
    from together import Together
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False

logger = get_logger(__name__)


def get_system_prompt() -> str:
    """
    Read system prompt from system prompt file and append patches/system_prompt_append.txt if present.
    
    Returns:
        System prompt string for LLM
    """
    prompt_file = Path(__file__).parent.parent.parent / SYSTEM_PROMPT_FILE
    if not prompt_file.exists():
        raise FileNotFoundError(f"System prompt file not found: {prompt_file}")
    
    logger.debug(f"Reading system prompt from: {prompt_file}")
    base = prompt_file.read_text(encoding='utf-8').strip()
    append = get_system_prompt_append()
    if append:
        return base + "\n\n" + append
    return base


def format_recipe_for_llm(raw_data: dict) -> str:
    """
    Format raw recipe data into a clean prompt for LLM.
    
    Args:
        raw_data: Dictionary with recipe data from scraper
        
    Returns:
        Formatted string for LLM input
    """
    title = raw_data.get('title', 'Untitled Recipe')
    url = raw_data.get('url', '')
    recipe_text = raw_data.get('recipe_text', [])
    
    # Combine recipe text into a single string
    recipe_content = '\n'.join(recipe_text)
    
    # Format for LLM
    formatted = f"""Recipe Title: {title}
Source URL: {url}

Recipe Content:
{recipe_content}

Please parse this recipe and extract structured information according to the system instructions."""
    
    return formatted


def get_llm_client(provider: str = None) -> Any:
    """
    Get appropriate LLM client based on provider.
    
    Args:
        provider: Provider name ("together_ai", "vercel_ai", "mistral_ai", or "deepseek_ai"), defaults to LLM_PROVIDER config
        
    Returns:
        Initialized client for the specified provider
        
    Raises:
        ValueError: If provider is invalid or required dependencies are missing
    """
    provider = provider or LLM_PROVIDER
    
    logger.debug(f"Getting LLM client for provider: {provider}")
    
    if provider == "together_ai":
        if not TOGETHER_AVAILABLE:
            raise ValueError(
                "Together AI package is required. "
                "Install it with: pip install together"
            )
        api_key = os.getenv(TOGETHER_AI_API_KEY_ENV_VAR, "")
        if not api_key:
            raise ValueError(
                f"Please set {TOGETHER_AI_API_KEY_ENV_VAR} in your .env file or environment variables."
            )
        from together import Together
        return Together(api_key=api_key)
    
    elif provider == "vercel_ai":
        if not OPENAI_AVAILABLE:
            raise ValueError(
                "OpenAI package is required for Vercel AI Gateway. "
                "Install it with: pip install openai"
            )
        
        # Try both environment variable names
        api_key = os.getenv(VERCEL_AI_API_KEY_ENV_VAR, "") or os.getenv("AI_GATEWAY_API_KEY", "")
        if not api_key:
            raise ValueError(
                f"Please set {VERCEL_AI_API_KEY_ENV_VAR} or AI_GATEWAY_API_KEY "
                "in your .env file or environment variables."
            )
        
        return OpenAI(
            api_key=api_key,
            base_url=VERCEL_AI_API_BASE_URL
        )
    
    elif provider == "mistral_ai":
        if not MISTRAL_AVAILABLE:
            raise ValueError(
                "Mistral AI package is required. "
                "Install it with: pip install mistralai"
            )
        
        api_key = os.getenv(MISTRAL_AI_API_KEY_ENV_VAR, "")
        if not api_key:
            raise ValueError(
                f"Please set {MISTRAL_AI_API_KEY_ENV_VAR} in your .env file or environment variables."
            )
        
        return Mistral(api_key=api_key)
    
    elif provider == "deepseek_ai":
        if not OPENAI_AVAILABLE:
            raise ValueError(
                "OpenAI package is required for DeepSeek AI. "
                "Install it with: pip install openai"
            )
        
        api_key = os.getenv(DEEPSEEK_AI_API_KEY_ENV_VAR, "")
        if not api_key:
            raise ValueError(
                f"Please set {DEEPSEEK_AI_API_KEY_ENV_VAR} in your .env file or environment variables."
            )
        
        return OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_AI_API_BASE_URL
        )
    
    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported providers: 'together_ai', 'vercel_ai', 'mistral_ai', 'deepseek_ai'"
        )


def call_llm(
    client: Any,
    provider: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = None
) -> str:
    """
    Call LLM API with provider-specific implementation.
    
    Args:
        client: LLM client instance
        provider: Provider name ("together_ai", "vercel_ai", "mistral_ai", or "deepseek_ai")
        model_id: Model identifier for the provider
        system_prompt: System prompt text
        user_prompt: User prompt text
        temperature: Temperature setting (defaults to LLM_TEMPERATURE)
        
    Returns:
        Response text from LLM
    """
    temperature = temperature or LLM_TEMPERATURE
    logger.debug(f"Calling LLM: provider={provider}, model={model_id}, temperature={temperature}")
    
    if provider == "together_ai":
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return response.choices[0].message.content
    
    elif provider == "vercel_ai":
        # Vercel AI Gateway uses OpenAI-compatible API
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return response.choices[0].message.content
    
    elif provider == "mistral_ai":
        # Mistral AI SDK uses chat.complete() method
        response = client.chat.complete(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return response.choices[0].message.content
    
    elif provider == "deepseek_ai":
        # DeepSeek AI uses OpenAI-compatible API
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return response.choices[0].message.content
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def parse_recipe_with_llm(raw_recipe_data: dict, model: str = None, provider: str = None) -> Recipe:
    """
    Parse raw recipe data using LLM via configured provider.
    
    Args:
        raw_recipe_data: Dictionary with raw recipe data from scraper
        model: Model name to use (default: DEFAULT_MODEL)
        provider: Provider name ("together_ai", "vercel_ai", "mistral_ai", or "deepseek_ai"), defaults to LLM_PROVIDER config
        
    Returns:
        Recipe Pydantic model with structured data
        
    Raises:
        ValueError: If API key is missing or invalid, or model/provider is unknown
        Exception: For API errors or parsing failures
    """
    logger.info(f"Parsing recipe: {raw_recipe_data.get('title', 'Unknown')}")
    
    # Determine provider to use
    provider = provider or LLM_PROVIDER
    
    # Get available models for the selected provider
    if provider == "together_ai":
        available_models = TOGETHER_AI_AVAILABLE_MODELS
    elif provider == "vercel_ai":
        available_models = VERCEL_AI_AVAILABLE_MODELS
    elif provider == "mistral_ai":
        available_models = MISTRAL_AI_AVAILABLE_MODELS
    elif provider == "deepseek_ai":
        available_models = DEEPSEEK_AI_AVAILABLE_MODELS
    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported providers: 'together_ai', 'vercel_ai', 'mistral_ai', 'deepseek_ai'"
        )
    
    # Determine model to use
    model_name = model or DEFAULT_MODEL
    if model_name not in available_models:
        raise ValueError(
            f"Unknown model '{model_name}' for provider '{provider}'. "
            f"Available models: {', '.join(available_models.keys())}"
        )
    
    model_id = available_models[model_name]
    logger.debug(f"Using model: {model_name} ({model_id})")
    
    # Get LLM client
    client = get_llm_client(provider)
    
    # Get system prompt
    system_prompt = get_system_prompt()
    
    # Format recipe for LLM
    user_prompt = format_recipe_for_llm(raw_recipe_data)
    
    # Add instruction to return JSON in the user prompt
    json_prompt = user_prompt + "\n\nPlease return the parsed recipe as a valid JSON object matching the Recipe schema. The JSON should have the following structure: {\"title\": \"...\", \"ingredients\": [{\"name\": \"...\", \"amount\": ..., \"unit\": \"...\", \"original_text\": \"...\"}, ...], \"instructions\": [\"...\", ...], \"cooking_time\": ..., \"servings\": ..., \"source_url\": \"...\"}"
    
    try:
        # Call LLM with provider-specific implementation
        logger.debug("Calling LLM API")
        raw_response_text = call_llm(
            client=client,
            provider=provider,
            model_id=model_id,
            system_prompt=system_prompt,
            user_prompt=json_prompt,
            temperature=LLM_TEMPERATURE
        )
        
        # Store raw response before cleaning (for error analysis)
        # Clean response text using dedicated cleanup function
        logger.debug("Cleaning LLM response")
        response_text = clean_llm_response(raw_response_text)
        
        logger.debug("Parsing JSON response")
        recipe_dict = json.loads(response_text)
        recipe = Recipe(**recipe_dict)
        
        if not isinstance(recipe, Recipe):
            raise ValueError("LLM response did not match Recipe model structure")
        
        logger.info(f"Successfully parsed recipe: {recipe.title}")
        return recipe
        
    except json.JSONDecodeError as e:
        # Attach raw response to exception for error analysis
        error = Exception(f"Failed to parse LLM response as JSON: {str(e)}\nResponse text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
        error.raw_llm_response = raw_response_text if 'raw_response_text' in locals() else None
        logger.error(f"JSON decode error: {e}", exc_info=True)
        raise error from e
    except ValueError as e:
        # Attach raw response to exception for error analysis
        error = Exception(f"Validation error: {str(e)}")
        error.raw_llm_response = raw_response_text if 'raw_response_text' in locals() else None
        logger.error(f"Validation error: {e}", exc_info=True)
        raise error from e
    except Exception as e:
        # Attach raw response to exception for error analysis
        if 'raw_response_text' in locals():
            e.raw_llm_response = raw_response_text
        logger.error(f"Error parsing recipe: {e}", exc_info=True)
        raise
