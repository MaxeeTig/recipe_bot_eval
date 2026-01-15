"""
LLM service for recipe parsing using OpenAI API via Vercel AI Gateway.
"""

import json
from typing import Dict, Any, Optional
from openai import OpenAI
from backend.config import AI_GATEWAY_CONFIG, DEFAULT_MODEL, MODEL_CONFIGS, AVAILABLE_MODELS
from backend.logger import get_logger
from backend.models.recipe import Recipe

logger = get_logger(__name__)


def get_openai_client() -> OpenAI:
    """
    Create and configure OpenAI client for Vercel AI Gateway.
    
    Returns:
        Configured OpenAI client
    """
    api_key = AI_GATEWAY_CONFIG.get("api_key")
    base_url = AI_GATEWAY_CONFIG.get("base_url")
    timeout = AI_GATEWAY_CONFIG.get("timeout", 30.0)
    
    if not api_key:
        logger.error("AI_GATEWAY_API_KEY not found in environment variables")
        raise ValueError("AI_GATEWAY_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout
    )
    
    logger.debug(
        "OpenAI client configured",
        extra={
            "base_url": base_url,
            "timeout": timeout
        }
    )
    
    return client


def parse_recipe_with_llm(
    text: str,
    model: str = None,
    system_prompt: str = None
) -> Dict[str, Any]:
    """
    Parse recipe text using LLM via Vercel AI Gateway.
    
    Args:
        text: Preprocessed recipe text to parse
        model: Model name from AVAILABLE_MODELS (default: DEFAULT_MODEL)
        system_prompt: System prompt for LLM (optional)
        
    Returns:
        Dictionary containing parsed recipe data
        
    Raises:
        ValueError: If API key is missing or parsing fails
        Exception: For API errors
    """
    if model is None:
        model = AVAILABLE_MODELS.get(DEFAULT_MODEL, DEFAULT_MODEL)
    
    # Get model config
    model_config = MODEL_CONFIGS.get(model, {})
    temperature = model_config.get("temperature", 0.3)
    max_tokens = model_config.get("max_tokens", 2048)
    
    logger.info(
        "Starting LLM recipe parsing",
        extra={
            "model": model,
            "text_length": len(text),
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    )
    
    try:
        client = get_openai_client()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": f"Распарси следующий рецепт:\n\n{text}"
        })
        
        logger.debug("Calling OpenAI API", extra={"model": model})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # Request JSON response
        )
        
        # Extract response content
        content = response.choices[0].message.content
        
        if not content:
            raise ValueError("Empty response from LLM")
        
        logger.debug(
            "LLM response received",
            extra={
                "model": model,
                "response_length": len(content),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            }
        )
        
        # Parse JSON response
        try:
            parsed_data = json.loads(content)
            logger.info(
                "Recipe parsed successfully",
                extra={
                    "model": model,
                    "has_title": "title" in parsed_data,
                    "ingredient_count": len(parsed_data.get("ingredients", []))
                }
            )
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse LLM response as JSON",
                exc_info=True,
                extra={
                    "model": model,
                    "response_preview": content[:200] if content else None,
                    "error": str(e)
                }
            )
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
            
    except Exception as e:
        logger.error(
            "LLM recipe parsing failed",
            exc_info=True,
            extra={
                "model": model,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )
        raise
