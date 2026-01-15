"""
Recipe postprocessing module.

This module handles postprocessing of parsed recipe data after LLM parsing.
For MVP, this is a pass-through function ready for future enhancement.
"""

from backend.models.recipe import Recipe
from backend.logger import get_logger

logger = get_logger(__name__)


def normalize_ingredients(recipe: Recipe) -> Recipe:
    """
    Normalize and standardize ingredients in parsed recipe.
    
    MVP: Returns recipe as-is (pass-through).
    
    Future enhancements may include:
    - Unit conversion (cups to ml, etc.)
    - Ingredient name standardization
    - Amount normalization
    - Merging duplicate ingredients
    - Validating unit consistency
    
    Args:
        recipe: Parsed Recipe object from LLM
        
    Returns:
        Normalized Recipe object
    """
    logger.debug(
        "Normalizing ingredients",
        extra={
            "recipe_title": recipe.title,
            "ingredient_count": len(recipe.ingredients)
        }
    )
    
    # MVP: Pass-through
    normalized_recipe = recipe
    
    logger.debug(
        "Ingredients normalized",
        extra={
            "recipe_title": normalized_recipe.title,
            "ingredient_count": len(normalized_recipe.ingredients)
        }
    )
    
    return normalized_recipe
