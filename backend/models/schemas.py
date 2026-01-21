"""
Pydantic schemas for API request and response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Request Schemas

class RecipeSearchRequest(BaseModel):
    """Request schema for recipe search."""
    query: str = Field(..., description="Recipe name to search for")


class ParseRequest(BaseModel):
    """Request schema for recipe parsing."""
    model: Optional[str] = Field(None, description="Optional LLM model override")
    provider: Optional[str] = Field(None, description="Optional LLM provider override")


class AnalysisRequest(BaseModel):
    """Request schema for error analysis."""
    model: Optional[str] = Field(None, description="Optional LLM model override")
    provider: Optional[str] = Field(None, description="Optional LLM provider override")
    apply_patches: bool = Field(False, description="Merge patches from analysis report into patches/ after saving")
    reparse: bool = Field(False, description="After applying patches, re-parse the recipe and update DB; implies apply_patches when True")


# Response Schemas

class RecipeSearchResponse(BaseModel):
    """Response schema for recipe search."""
    recipe_id: int = Field(..., description="ID of the saved recipe")
    status: str = Field(..., description="Recipe status (new)")
    title: str = Field(..., description="Recipe title")
    url: str = Field(..., description="Source URL")


class IngredientSchema(BaseModel):
    """Schema for ingredient in parsed recipe."""
    name: str
    amount: float
    unit: str
    original_text: str


class ParsedRecipeSchema(BaseModel):
    """Schema for parsed recipe."""
    title: str
    ingredients: List[IngredientSchema]
    instructions: List[str]
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    source_url: str


class ParseResponse(BaseModel):
    """Response schema for recipe parsing."""
    recipe_id: int
    status: str
    parsed_recipe: Optional[ParsedRecipeSchema] = None
    error: Optional[Dict[str, Any]] = None


class RecipeListItem(BaseModel):
    """Schema for recipe list item."""
    id: int
    recipe_name: str
    source_url: str
    raw_title: str
    status: str
    created_at: str
    updated_at: str
    parsed_at: Optional[str] = None


class RecipeListResponse(BaseModel):
    """Response schema for recipe list."""
    recipes: List[RecipeListItem]
    total: int


class RecipeDetailResponse(BaseModel):
    """Response schema for full recipe details."""
    id: int
    recipe_name: str
    source_url: str
    raw_title: str
    raw_recipe_text: List[str]
    status: str
    parsed_recipe: Optional[Dict[str, Any]] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    llm_response_text: Optional[str] = None
    created_at: str
    updated_at: str
    parsed_at: Optional[str] = None


class RawRecipeResponse(BaseModel):
    """Response schema for raw recipe text."""
    title: str
    recipe_text: List[str]
    url: str


class ParsedRecipeDetailResponse(BaseModel):
    """Response schema for parsed recipe or error details."""
    parsed_recipe: Optional[ParsedRecipeSchema] = None
    error: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Response schema for error analysis."""
    analysis_id: int
    recipe_id: int
    analysis_report: Dict[str, Any]
    recommendations_summary: Optional[str] = None
    created_at: str
    # When reparse=True: result of re-parse after apply_patches
    reparse_result: Optional[Dict[str, Any]] = Field(
        None,
        description="When reparse=True: {status, parsed_recipe?, error?}"
    )


class AnalysisListResponse(BaseModel):
    """Response schema for analysis list."""
    analyses: List[AnalysisResponse]


class DeleteResponse(BaseModel):
    """Response schema for recipe deletion."""
    message: str
    recipe_id: int


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    timestamp: str


class RecipeStatsResponse(BaseModel):
    """Response schema for recipe statistics."""
    total: int = Field(..., description="Total number of recipes")
    by_status: Dict[str, int] = Field(..., description="Counts by status: new, success, failure")
    by_error_type: Optional[Dict[str, int]] = Field(None, description="For status=failure: counts by error_type")
