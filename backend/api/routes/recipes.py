"""
Recipe API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
import traceback
import time

from backend.models.schemas import (
    RecipeSearchRequest,
    RecipeSearchResponse,
    ParseRequest,
    ParseResponse,
    RecipeListResponse,
    RecipeListItem,
    RecipeDetailResponse,
    RawRecipeResponse,
    ParsedRecipeDetailResponse,
    ParsedRecipeSchema,
    IngredientSchema,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisListResponse,
    DeleteResponse,
    ErrorResponse,
    RecipeStatsResponse,
)
from backend.database import db
from backend.services.scraper_service import search_and_extract_recipe
from backend.services.parser_service import parse_recipe_with_llm
from backend.services.analysis_service import analyze_recipe_error
from patches import apply_patches_from_analysis
from backend.api.dependencies import get_request_id_dependency, get_logger_dependency
from backend.logging_config import get_logger

router = APIRouter(prefix="/api/recipes", tags=["recipes"])
logger = get_logger(__name__)


@router.post("/search", response_model=RecipeSearchResponse, status_code=status.HTTP_201_CREATED)
async def search_recipe(
    request_data: RecipeSearchRequest,
    request: Request,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Search for a recipe on russianfood.com and save it to database.
    
    Args:
        request_data: Search query
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Recipe search response with recipe ID and basic info
    """
    logger.info(f"Search request: {request_data.query}")
    
    start_time = time.time()
    try:
        # Search and extract recipe
        recipe_data = search_and_extract_recipe(request_data.query)
        
        # Save to database
        recipe_id = db.save_raw_recipe(
            recipe_name=request_data.query,
            source_url=recipe_data['url'],
            raw_title=recipe_data['title'],
            raw_recipe_text=recipe_data['recipe_text']
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Recipe saved with ID: {recipe_id} (search duration: {elapsed_time:.2f}s)")
        
        return RecipeSearchResponse(
            recipe_id=recipe_id,
            status="new",
            title=recipe_data['title'],
            url=recipe_data['url']
        )
        
    except ValueError as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Search error: {e} (duration: {elapsed_time:.2f}s)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Unexpected error during search: {e} (duration: {elapsed_time:.2f}s)", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/{recipe_id}/parse", response_model=ParseResponse)
async def parse_recipe(
    recipe_id: int,
    request_data: ParseRequest = ParseRequest(),
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Parse a recipe using LLM.
    
    Args:
        recipe_id: Recipe ID to parse
        request_data: Optional parse request with model override
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Parse response with parsed recipe or error details
    """
    logger.info(f"Parse request for recipe ID: {recipe_id}")
    
    # Get recipe from database
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    # Reconstruct raw recipe data dict for parser
    raw_recipe_data = {
        'title': recipe['raw_title'],
        'url': recipe['source_url'],
        'recipe_text': recipe['raw_recipe_text']
    }
    
    try:
        # Parse with LLM
        parsed_recipe = parse_recipe_with_llm(
            raw_recipe_data,
            model=request_data.model,
            provider=request_data.provider
        )
        
        # Update database with success
        db.update_recipe_success(recipe_id, parsed_recipe)
        
        logger.info(f"Recipe {recipe_id} parsed successfully")
        
        # Convert to response schema
        parsed_schema = ParsedRecipeSchema(
            title=parsed_recipe.title,
            ingredients=[
                IngredientSchema(
                    name=ing.name,
                    amount=ing.amount,
                    unit=ing.unit,
                    original_text=ing.original_text
                )
                for ing in parsed_recipe.ingredients
            ],
            instructions=parsed_recipe.instructions,
            cooking_time=parsed_recipe.cooking_time,
            servings=parsed_recipe.servings,
            source_url=parsed_recipe.source_url
        )
        
        return ParseResponse(
            recipe_id=recipe_id,
            status="success",
            parsed_recipe=parsed_schema,
            error=None
        )
        
    except Exception as e:
        # Extract error information
        error_type = type(e).__name__
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        # Extract raw LLM response if available
        llm_response_text = getattr(e, 'raw_llm_response', None)
        
        logger.error(f"Error parsing recipe {recipe_id}: {error_message}")
        
        # Update database with failure
        db.update_recipe_failure(
            recipe_id,
            error_type,
            error_message,
            error_traceback,
            llm_response_text
        )
        
        return ParseResponse(
            recipe_id=recipe_id,
            status="failure",
            parsed_recipe=None,
            error={
                "type": error_type,
                "message": error_message,
                "traceback": error_traceback
            }
        )


@router.get("/stats", response_model=RecipeStatsResponse)
async def get_recipe_stats(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Get recipe statistics: total, by status, and by error_type for failures.
    
    Args:
        date_from: Optional ISO date/datetime; filter created_at >= date_from
        date_to: Optional ISO date/datetime (inclusive); if date-only, end of day is used
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Recipe stats: total, by_status, by_error_type
    """
    logger.debug(f"Stats request (date_from={date_from}, date_to={date_to})")
    stats = db.get_recipe_stats(date_from=date_from, date_to=date_to)
    return RecipeStatsResponse(**stats)


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    status_filter: Optional[str] = None,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Get list of recipes, optionally filtered by status.
    
    Args:
        status_filter: Optional status filter (new, success, failure)
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        List of recipes
    """
    logger.debug(f"List recipes request (status={status_filter or 'all'})")
    
    recipes = db.get_recipes_by_status(status_filter)
    
    recipe_items = [
        RecipeListItem(
            id=r['id'],
            recipe_name=r['recipe_name'],
            source_url=r['source_url'],
            raw_title=r['raw_title'],
            status=r['status'],
            created_at=r['created_at'],
            updated_at=r['updated_at'],
            parsed_at=r.get('parsed_at')
        )
        for r in recipes
    ]
    
    return RecipeListResponse(
        recipes=recipe_items,
        total=len(recipe_items)
    )


@router.get("/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe(
    recipe_id: int,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Get full recipe details by ID.
    
    Args:
        recipe_id: Recipe ID
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Full recipe details
    """
    logger.debug(f"Get recipe request: {recipe_id}")
    
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    return RecipeDetailResponse(**recipe)


@router.get("/{recipe_id}/raw", response_model=RawRecipeResponse)
async def get_raw_recipe(
    recipe_id: int,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Get raw recipe text.
    
    Args:
        recipe_id: Recipe ID
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Raw recipe text (title, recipe_text, url)
    """
    logger.debug(f"Get raw recipe request: {recipe_id}")
    
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    return RawRecipeResponse(
        title=recipe['raw_title'],
        recipe_text=recipe['raw_recipe_text'],
        url=recipe['source_url']
    )


@router.get("/{recipe_id}/parsed", response_model=ParsedRecipeDetailResponse)
async def get_parsed_recipe(
    recipe_id: int,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Get parsed recipe or error details.
    
    Args:
        recipe_id: Recipe ID
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Parsed recipe if status=success, error details if status=failure
    """
    logger.debug(f"Get parsed recipe request: {recipe_id}")
    
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    if recipe['status'] == 'success':
        # Return parsed recipe
        parsed_recipe_dict = recipe.get('parsed_recipe', {})
        if parsed_recipe_dict:
            parsed_schema = ParsedRecipeSchema(**parsed_recipe_dict)
            return ParsedRecipeDetailResponse(
                parsed_recipe=parsed_schema,
                error=None
            )
        else:
            return ParsedRecipeDetailResponse(
                parsed_recipe=None,
                error=None
            )
    elif recipe['status'] == 'failure':
        # Return error details
        return ParsedRecipeDetailResponse(
            parsed_recipe=None,
            error={
                "type": recipe.get('error_type'),
                "message": recipe.get('error_message'),
                "traceback": recipe.get('error_traceback')
            }
        )
    else:
        # Status is 'new', not parsed yet
        return ParsedRecipeDetailResponse(
            parsed_recipe=None,
            error={"message": "Recipe not parsed yet"}
        )


@router.post("/{recipe_id}/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_recipe(
    recipe_id: int,
    request_data: AnalysisRequest = AnalysisRequest(),
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Launch error analysis for a failed recipe.
    
    Args:
        recipe_id: Recipe ID to analyze
        request_data: Optional analysis request with model override
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Analysis response with analysis report
    """
    logger.info(f"Analysis request for recipe ID: {recipe_id}")
    
    # Get recipe from database
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    if recipe['status'] != 'failure':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe ID {recipe_id} has status '{recipe['status']}', not 'failure'. Analysis can only be performed on failed recipes."
        )
    
    try:
        # Analyze recipe error
        analysis_report = analyze_recipe_error(
            recipe_id,
            model=request_data.model,
            provider=request_data.provider
        )
        
        # Apply patches from analysis when requested (reparse implies apply_patches)
        do_apply = request_data.apply_patches or request_data.reparse
        if do_apply:
            apply_patches_from_analysis(analysis_report)
            logger.info(f"Patches from analysis applied for recipe {recipe_id}")
        
        reparse_result = None
        if request_data.reparse:
            raw_recipe_data = {
                'title': recipe['raw_title'],
                'url': recipe['source_url'],
                'recipe_text': recipe['raw_recipe_text']
            }
            try:
                parsed_recipe = parse_recipe_with_llm(
                    raw_recipe_data,
                    model=request_data.model,
                    provider=request_data.provider
                )
                db.update_recipe_success(recipe_id, parsed_recipe)
                logger.info(f"Recipe {recipe_id} re-parsed successfully after apply_patches")
                parsed_schema = ParsedRecipeSchema(
                    title=parsed_recipe.title,
                    ingredients=[
                        IngredientSchema(
                            name=ing.name,
                            amount=ing.amount,
                            unit=ing.unit,
                            original_text=ing.original_text
                        )
                        for ing in parsed_recipe.ingredients
                    ],
                    instructions=parsed_recipe.instructions,
                    cooking_time=parsed_recipe.cooking_time,
                    servings=parsed_recipe.servings,
                    source_url=parsed_recipe.source_url
                )
                reparse_result = {
                    "status": "success",
                    "parsed_recipe": parsed_schema.model_dump(),
                    "error": None
                }
            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                error_traceback = traceback.format_exc()
                llm_response_text = getattr(e, 'raw_llm_response', None)
                db.update_recipe_failure(
                    recipe_id,
                    error_type,
                    error_message,
                    error_traceback,
                    llm_response_text
                )
                logger.warning(f"Recipe {recipe_id} re-parse failed after apply_patches: {error_message}")
                reparse_result = {
                    "status": "failure",
                    "parsed_recipe": None,
                    "error": {
                        "type": error_type,
                        "message": error_message,
                        "traceback": error_traceback
                    }
                }
        
        # Store reparse_result in analysis_report for tracking corrections
        if reparse_result is not None:
            analysis_report['reparse_result'] = reparse_result
        
        # Save analysis to database (with reparse_result if available)
        recommendations_summary = analysis_report.get('root_cause', '')
        analysis_id = db.save_error_analysis(
            recipe_id,
            analysis_report,
            recommendations_summary
        )
        
        logger.info(f"Analysis saved with ID: {analysis_id}")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            recipe_id=recipe_id,
            analysis_report=analysis_report,
            recommendations_summary=recommendations_summary,
            created_at=analysis_report.get('analysis_timestamp', ''),
            reparse_result=reparse_result
        )
        
    except ValueError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{recipe_id}/analyses", response_model=AnalysisListResponse)
async def get_analyses(
    recipe_id: int,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Get all error analyses for a recipe.
    
    Args:
        recipe_id: Recipe ID
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        List of analyses
    """
    logger.debug(f"Get analyses request for recipe: {recipe_id}")
    
    # Verify recipe exists
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    analyses = db.get_error_analyses_by_recipe_id(recipe_id)
    
    analysis_responses = [
        AnalysisResponse(
            analysis_id=a['id'],
            recipe_id=a['recipe_id'],
            analysis_report=a['analysis_report'],
            recommendations_summary=a.get('recommendations_summary'),
            created_at=a['created_at']
        )
        for a in analyses
    ]
    
    return AnalysisListResponse(analyses=analysis_responses)


@router.post("/{recipe_id}/analyses/{analysis_id}/apply-patches", status_code=status.HTTP_200_OK)
async def apply_patches_from_analysis_id(
    recipe_id: int,
    analysis_id: int,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Apply patches from a specific analysis without re-running analysis.
    
    Args:
        recipe_id: Recipe ID
        analysis_id: Analysis ID to get patches from
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Success response with status and message
    """
    logger.info(f"Apply patches request for recipe {recipe_id}, analysis {analysis_id}")
    
    # Verify recipe exists
    recipe = db.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    # Get analysis
    analysis = db.get_error_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Verify analysis belongs to this recipe
    if analysis['recipe_id'] != recipe_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis {analysis_id} does not belong to recipe {recipe_id}"
        )
    
    try:
        # Apply patches from analysis
        apply_patches_from_analysis(analysis['analysis_report'])
        logger.info(f"Patches from analysis {analysis_id} applied for recipe {recipe_id}")
        
        return {
            "status": "success",
            "message": "Patches applied successfully"
        }
    except Exception as e:
        logger.error(f"Error applying patches from analysis {analysis_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error applying patches: {str(e)}"
        )


@router.delete("/{recipe_id}", response_model=DeleteResponse)
async def delete_recipe(
    recipe_id: int,
    request: Request = None,
    request_id: str = Depends(get_request_id_dependency)
):
    """
    Delete a recipe and its associated analyses.
    
    Args:
        recipe_id: Recipe ID to delete
        request: FastAPI request object
        request_id: Request ID for logging
        
    Returns:
        Deletion confirmation
    """
    logger.info(f"Delete recipe request: {recipe_id}")
    
    deleted = db.delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found"
        )
    
    return DeleteResponse(
        message="Recipe deleted successfully",
        recipe_id=recipe_id
    )
