"""
Recipe preprocessing module.

This module handles preprocessing of raw recipe text before LLM parsing.
For MVP, this is a pass-through function ready for future enhancement.
"""

from backend.logger import get_logger

logger = get_logger(__name__)


def preprocess_recipe_text(recipe_text: str) -> str:
    """
    Preprocess recipe text before LLM parsing.
    
    MVP: Returns input as-is (pass-through).
    
    Future enhancements may include:
    - Removing HTML tags and formatting
    - Normalizing whitespace
    - Extracting structured sections
    - Cleaning special characters
    - Language detection and normalization
    
    Args:
        recipe_text: Raw recipe text from source
        
    Returns:
        Cleaned/preprocessed recipe text
    """
    logger.debug(
        "Preprocessing recipe text",
        extra={"input_length": len(recipe_text)}
    )
    
    # MVP: Pass-through
    cleaned_text = recipe_text
    
    logger.debug(
        "Recipe text preprocessed",
        extra={
            "input_length": len(recipe_text),
            "output_length": len(cleaned_text)
        }
    )
    
    return cleaned_text
