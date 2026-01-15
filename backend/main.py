from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import traceback
from datetime import datetime

from backend.database import (
    init_database,
    create_recipe,
    get_recipe,
    get_all_recipes,
    delete_recipe as db_delete_recipe
)
from backend.tavily_service import search_recipes, select_best_result
from backend.logger import setup_logging, get_logger, set_request_id, get_request_id

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Recipe Bot API", version="1.0.0")

# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and track request IDs."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or get request ID from header
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)
        
        # Log incoming request
        logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
                "request_id": request_id
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response header
        response.headers["X-Request-ID"] = request_id
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "request_id": request_id
            }
        )
        
        return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with logging."""
    request_id = get_request_id()
    
    logger.error(
        "Unhandled exception",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    request_id = get_request_id()
    
    logger.warning(
        "Request validation error",
        extra={
            "method": request.method,
            "path": request.url.path,
            "request_id": request_id,
            "errors": exc.errors()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "request_id": request_id
        }
    )


# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware (should be after CORS)
app.add_middleware(RequestIDMiddleware)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Recipe Bot API")
    init_database()
    logger.info("Database initialized successfully")


# Request/Response models
class SearchRequest(BaseModel):
    query: str


class RecipeResponse(BaseModel):
    id: str
    query: str
    tavily_response: dict
    selected_result_index: int
    status: str
    created_at: str
    updated_at: str


# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "recipe-bot-api"}


@app.post("/api/recipes/search", response_model=RecipeResponse)
async def search_recipe(request: SearchRequest):
    """
    Search for a recipe using Tavily API.
    Selects the most relevant result and stores raw data in database.
    """
    logger.info(
        "Recipe search requested",
        extra={"query": request.query}
    )
    
    try:
        # Search Tavily
        logger.debug("Searching Tavily API", extra={"query": request.query})
        tavily_response = search_recipes(request.query)
        
        # Select best result
        selected_index, selected_result = select_best_result(tavily_response)
        
        if selected_result is None:
            logger.warning(
                "No results found for query",
                extra={"query": request.query}
            )
            raise HTTPException(
                status_code=404,
                detail="No results found for the query"
            )
        
        # Generate recipe ID
        recipe_id = str(uuid.uuid4())
        logger.debug(
            "Creating recipe entry",
            extra={"recipe_id": recipe_id, "selected_index": selected_index}
        )
        
        # Store in database
        recipe = create_recipe(
            recipe_id=recipe_id,
            query=request.query,
            tavily_response=tavily_response,
            selected_result_index=selected_index,
            status="stored"
        )
        
        logger.info(
            "Recipe search completed successfully",
            extra={"recipe_id": recipe_id, "query": request.query}
        )
        
        # Parse JSON string back to dict (database stores it as JSON string)
        recipe_dict = dict(recipe)
        recipe_dict["tavily_response"] = json.loads(recipe_dict["tavily_response"])
        
        return RecipeResponse(**recipe_dict)
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(
            "Value error during recipe search",
            exc_info=True,
            extra={"query": request.query, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error during recipe search",
            exc_info=True,
            extra={"query": request.query, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error searching recipes: {str(e)}")


@app.get("/api/recipes", response_model=List[RecipeResponse])
async def list_recipes():
    """Get all recipes (excluding deleted ones)."""
    logger.debug("Listing all recipes")
    
    try:
        recipes = get_all_recipes(exclude_deleted=True)
        
        # Parse JSON strings back to dicts
        result = []
        for recipe in recipes:
            recipe_dict = dict(recipe)
            recipe_dict["tavily_response"] = json.loads(recipe_dict["tavily_response"])
            result.append(RecipeResponse(**recipe_dict))
        
        logger.info(
            "Recipes listed successfully",
            extra={"count": len(result)}
        )
        
        return result
    except Exception as e:
        logger.error(
            "Error listing recipes",
            exc_info=True,
            extra={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error listing recipes: {str(e)}")


@app.get("/api/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_by_id(recipe_id: str):
    """Get a single recipe by ID."""
    logger.debug("Getting recipe by ID", extra={"recipe_id": recipe_id})
    
    try:
        recipe = get_recipe(recipe_id)
        
        if not recipe:
            logger.warning(
                "Recipe not found",
                extra={"recipe_id": recipe_id}
            )
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Parse JSON string back to dict
        recipe_dict = dict(recipe)
        recipe_dict["tavily_response"] = json.loads(recipe_dict["tavily_response"])
        
        logger.info(
            "Recipe retrieved successfully",
            extra={"recipe_id": recipe_id}
        )
        
        return RecipeResponse(**recipe_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving recipe",
            exc_info=True,
            extra={"recipe_id": recipe_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error retrieving recipe: {str(e)}")


@app.delete("/api/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str):
    """Soft delete a recipe (mark as deleted)."""
    logger.info("Deleting recipe", extra={"recipe_id": recipe_id})
    
    try:
        success = db_delete_recipe(recipe_id)
        
        if not success:
            logger.warning(
                "Recipe not found for deletion",
                extra={"recipe_id": recipe_id}
            )
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        logger.info(
            "Recipe deleted successfully",
            extra={"recipe_id": recipe_id}
        )
        
        return {"message": "Recipe deleted successfully", "id": recipe_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error deleting recipe",
            exc_info=True,
            extra={"recipe_id": recipe_id, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Error deleting recipe: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
