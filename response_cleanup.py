"""
Cleanup algorithms for processing LLM response text.

This module contains functions for cleaning and normalizing LLM responses
before parsing them into structured data. These algorithms can be modified
by the LLM Error Analysis and Repair System to improve parsing success rates.
"""
import re

from patches import get_cleanup_rules


def _get_cleanup_patches() -> list:
    """Return cleanup rules from patches/cleanup_rules.json."""
    return get_cleanup_rules()


def clean_llm_response(response_text: str) -> str:
    """
    Clean LLM response text by removing markdown code blocks and normalizing whitespace.
    
    This function handles common formatting issues in LLM responses:
    - Removes markdown code block markers (```json, ```)
    - Strips leading and trailing whitespace
    - Handles edge cases for malformed responses
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        Cleaned text ready for JSON parsing
        
    Raises:
        ValueError: If response_text is empty or None after cleaning
    """
    if not response_text:
        raise ValueError("Empty response from LLM")
    
    # Strip leading and trailing whitespace
    response_text = response_text.strip()
    
    # Remove markdown code block markers
    # Handle ```json prefix
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    # Handle generic ``` prefix (if not already removed)
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    
    # Remove closing ``` marker
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    # Final whitespace normalization
    response_text = response_text.strip()

    # Apply patch cleanup rules (find/replace after built-in cleanup)
    for rule in _get_cleanup_patches():
        pattern = rule.get("pattern", "")
        replacement = rule.get("replacement", "")
        if rule.get("regex"):
            try:
                response_text = re.sub(pattern, replacement, response_text)
            except re.error:
                pass
        else:
            response_text = response_text.replace(pattern, replacement)
    response_text = response_text.strip()
    
    if not response_text:
        raise ValueError("Response text is empty after cleaning")
    
    return response_text
