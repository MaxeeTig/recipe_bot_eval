"""
Error analysis service using LLM to diagnose parsing failures.
Refactored from analyze_error.py with logging support.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys

# Add parent directory to path to import from root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.parser_service import (
    get_llm_client,
    call_llm,
    get_system_prompt,
)
from config_section import (
    LLM_PROVIDER,
    DEFAULT_ANALYSIS_MODEL,
    ERROR_ANALYSIS_PROMPT_FILE,
    LLM_TEMPERATURE,
    TOGETHER_AI_AVAILABLE_MODELS,
    VERCEL_AI_AVAILABLE_MODELS,
    MISTRAL_AI_AVAILABLE_MODELS,
    DEEPSEEK_AI_AVAILABLE_MODELS,
    MAX_SUCCESSFUL_EXAMPLES,
)
from backend.database import db
from backend.logging_config import get_logger

logger = get_logger(__name__)


def get_error_analysis_prompt() -> str:
    """
    Read error analysis system prompt from file.
    
    Returns:
        Error analysis system prompt string
    """
    prompt_file = Path(__file__).parent.parent.parent / ERROR_ANALYSIS_PROMPT_FILE
    if not prompt_file.exists():
        raise FileNotFoundError(f"Error analysis prompt file not found: {prompt_file}")
    
    logger.debug(f"Reading error analysis prompt from: {prompt_file}")
    return prompt_file.read_text(encoding='utf-8').strip()


def read_code_file(filepath: str) -> str:
    """
    Read a code file and return its contents.
    
    Args:
        filepath: Path to the file (relative to project root)
        
    Returns:
        File contents as string
    """
    file_path = Path(__file__).parent.parent.parent / filepath
    if not file_path.exists():
        logger.warning(f"Code file not found: {filepath}")
        return f"File not found: {filepath}"
    
    logger.debug(f"Reading code file: {filepath}")
    return file_path.read_text(encoding='utf-8')


def get_successful_examples(recipe_id: int, max_examples: int = None) -> List[Dict[str, Any]]:
    """
    Get successful recipe examples for comparison.
    
    Args:
        recipe_id: Current recipe ID (to exclude from examples)
        max_examples: Maximum number of examples to return (defaults to MAX_SUCCESSFUL_EXAMPLES)
        
    Returns:
        List of successful recipe dictionaries
    """
    if max_examples is None:
        max_examples = MAX_SUCCESSFUL_EXAMPLES
    
    logger.debug(f"Getting successful examples (excluding recipe {recipe_id}, max {max_examples})")
    successful_recipes = db.get_recipes_by_status('success')
    
    # Exclude current recipe if it exists
    examples = [r for r in successful_recipes if r.get('id') != recipe_id]
    
    # Return up to max_examples
    result = examples[:max_examples]
    logger.debug(f"Retrieved {len(result)} successful examples")
    return result


def format_analysis_context(recipe_record: Dict[str, Any]) -> str:
    """
    Format all context for error analysis into a prompt for LLM 2.
    
    Args:
        recipe_record: Recipe dictionary from database
        
    Returns:
        Formatted context string for analysis LLM
    """
    recipe_id = recipe_record['id']
    logger.debug(f"Formatting analysis context for recipe {recipe_id}")
    
    # Gather all context
    raw_recipe = {
        'title': recipe_record.get('raw_title', ''),
        'url': recipe_record.get('source_url', ''),
        'recipe_text': recipe_record.get('raw_recipe_text', [])
    }
    
    error_type = recipe_record.get('error_type', 'Unknown')
    error_message = recipe_record.get('error_message', '')
    error_traceback = recipe_record.get('error_traceback', '')
    llm_response_text = recipe_record.get('llm_response_text', '')
    
    # Read code files
    system_prompt = get_system_prompt()  # LLM 1's system prompt
    pydantic_models_code = read_code_file('recipe_models.py')
    cleanup_algorithm_code = read_code_file('response_cleanup.py')
    
    # Get successful examples
    successful_examples = get_successful_examples(recipe_id, MAX_SUCCESSFUL_EXAMPLES)
    
    # Format context
    context = f"""# Error Analysis Request

## Failed Recipe Information

**Recipe ID**: {recipe_id}
**Recipe Title**: {raw_recipe.get('title', 'Unknown')}
**Source URL**: {raw_recipe.get('url', '')}

**Raw Recipe Text**:
{json.dumps(raw_recipe.get('recipe_text', []), ensure_ascii=False, indent=2)}

## Error Information

**Error Type**: {error_type}
**Error Message**: {error_message}

**Full Traceback**:
```
{error_traceback}
```

## LLM Response (Raw, Before Cleaning)

```
{llm_response_text if llm_response_text else 'Not available'}
```

## Current System Prompt (LLM 1)

This is the system prompt currently used by the parsing LLM. Analyze it and suggest improvements:

```
{system_prompt}
```

## Current Pydantic Models Code

```
{pydantic_models_code}
```

## Current Cleanup Algorithm Code

```
{cleanup_algorithm_code}
```

## Successful Examples (for comparison)

"""
    
    if successful_examples:
        for i, example in enumerate(successful_examples, 1):
            parsed_recipe = example.get('parsed_recipe', {})
            context += f"""
### Example {i}: {example.get('raw_title', 'Unknown')}

**Parsed Recipe**:
{json.dumps(parsed_recipe, ensure_ascii=False, indent=2)}

"""
    else:
        context += "No successful examples available for comparison.\n"
    
    context += """
---

Please analyze this failure and provide recommendations to fix the parsing issue.
Return your analysis as a JSON object matching the format specified in the system prompt.
"""
    
    return context


def analyze_recipe_error(recipe_id: int, model: Optional[str] = None, provider: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a failed recipe using LLM 2 (Analysis LLM).
    
    Args:
        recipe_id: Recipe ID to analyze
        model: Analysis model to use (default: DEFAULT_ANALYSIS_MODEL)
        provider: LLM provider to use (default: LLM_PROVIDER from config)
        
    Returns:
        Analysis report dictionary
    """
    logger.info(f"Analyzing failed recipe ID {recipe_id}")
    
    # Get recipe record
    recipe_record = db.get_recipe_by_id(recipe_id)
    if not recipe_record:
        raise ValueError(f"Recipe with ID {recipe_id} not found")
    
    if recipe_record.get('status') != 'failure':
        raise ValueError(f"Recipe ID {recipe_id} has status '{recipe_record.get('status')}', not 'failure'")
    
    logger.info(f"Analyzing recipe: {recipe_record.get('raw_title', 'Unknown')}")
    
    # Determine provider and model
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
        raise ValueError(f"Unknown provider: {provider}")
    
    # Determine model to use
    model_name = model or DEFAULT_ANALYSIS_MODEL
    if model_name not in available_models:
        raise ValueError(
            f"Unknown model '{model_name}' for provider '{provider}'. "
            f"Available models: {', '.join(available_models.keys())}"
        )
    
    model_id = available_models[model_name]
    logger.debug(f"Using analysis model: {model_name} ({model_id})")
    
    # Get LLM client
    client = get_llm_client(provider)
    
    # Get error analysis system prompt
    analysis_system_prompt = get_error_analysis_prompt()
    
    # Format context for analysis
    user_prompt = format_analysis_context(recipe_record)
    
    logger.debug("Calling Analysis LLM")
    
    # Call Analysis LLM
    response_text = call_llm(
        client=client,
        provider=provider,
        model_id=model_id,
        system_prompt=analysis_system_prompt,
        user_prompt=user_prompt,
        temperature=LLM_TEMPERATURE
    )
    
    # Parse response (should be JSON)
    try:
        # Clean response (remove markdown if present)
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:]
        if response_text.strip().startswith("```"):
            response_text = response_text.strip()[3:]
        if response_text.strip().endswith("```"):
            response_text = response_text.strip()[:-3]
        response_text = response_text.strip()
        
        analysis_report = json.loads(response_text)
        
        # Add metadata
        analysis_report['recipe_id'] = recipe_id
        analysis_report['analysis_timestamp'] = datetime.now().isoformat()
        analysis_report['model_used'] = model_name
        
        logger.info(f"Analysis complete for recipe {recipe_id}")
        return analysis_report
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse analysis LLM response as JSON: {e}")
        raise Exception(f"Failed to parse analysis LLM response as JSON: {str(e)}\nResponse: {response_text[:500]}")
