"""
Recipe parser orchestrator.

This module orchestrates the two-stage recipe parsing process:
1. Code-based preprocessing
2. LLM-based parsing with postprocessing
"""

from typing import Optional
from backend.models.recipe import Recipe
from backend.recipe_preprocessing import preprocess_recipe_text
from backend.recipe_postprocessing import normalize_ingredients
from backend.llm_service import parse_recipe_with_llm
from backend.prompts.recipe_parsing_prompt import get_recipe_parsing_system_prompt
from backend.logger import get_logger

logger = get_logger(__name__)


def parse_recipe(
    recipe_text: str,
    source_url: str,
    model: Optional[str] = None
) -> Recipe:
    """
    Parse recipe text into structured Recipe object.
    
    This function orchestrates the two-stage parsing process:
    1. Preprocessing (code-based)
    2. LLM parsing with postprocessing
    
    Args:
        recipe_text: Raw recipe text from source
        source_url: URL of the recipe source
        model: Optional model name override
        
    Returns:
        Parsed Recipe object
        
    Raises:
        ValueError: If parsing fails or validation fails
        Exception: For other errors
    """
    logger.info(
        "Starting recipe parsing",
        extra={
            "source_url": source_url,
            "text_length": len(recipe_text),
            "model": model
        }
    )
    
    try:
        # Stage 1: Preprocessing
        logger.debug("Stage 1: Preprocessing recipe text")
        cleaned_text = preprocess_recipe_text(recipe_text)
        
        # Stage 2: LLM parsing
        logger.debug("Stage 2: LLM parsing")
        system_prompt = get_recipe_parsing_system_prompt()
        llm_response = parse_recipe_with_llm(
            text=cleaned_text,
            model=model,
            system_prompt=system_prompt
        )
        
        # Ensure source_url is set
        if "source_url" not in llm_response or not llm_response["source_url"]:
            llm_response["source_url"] = source_url
        
        # Parse into Pydantic model
        logger.debug("Parsing LLM response into Recipe model")
        recipe = Recipe.model_validate(llm_response)
        
        # Stage 3: Postprocessing
        logger.debug("Stage 3: Postprocessing")
        recipe = normalize_ingredients(recipe)
        
        logger.info(
            "Recipe parsed successfully",
            extra={
                "recipe_title": recipe.title,
                "ingredient_count": len(recipe.ingredients),
                "instruction_count": len(recipe.instructions),
                "source_url": recipe.source_url
            }
        )
        
        return recipe
        
    except ValueError as e:
        logger.error(
            "Recipe parsing validation error",
            exc_info=True,
            extra={
                "source_url": source_url,
                "error": str(e)
            }
        )
        raise
    except Exception as e:
        logger.error(
            "Recipe parsing failed",
            exc_info=True,
            extra={
                "source_url": source_url,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )
        raise
