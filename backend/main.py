"""
FastAPI application entry point.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid

from backend.config import API_HOST, API_PORT
from backend.logging_config import setup_logging, get_logger, set_request_id, clear_request_id
from backend.api.routes import recipes
from backend.models.schemas import HealthResponse, ErrorResponse

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Recipe Search and Management API",
    description="API for searching, parsing, and managing recipes from russianfood.com",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Middleware to set request ID for logging."""
    # Get or generate request ID
    request_id_header = request.headers.get("X-Request-ID")
    request_id = request_id_header or str(uuid.uuid4())
    
    # Set in context
    set_request_id(request_id)
    
    # Store in request state
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response header
    response.headers["X-Request-ID"] = request_id
    
    # Clear context
    clear_request_id()
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    request_id = getattr(request.state, 'request_id', None)
    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={"request_id": request_id})
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            request_id=request_id
        ).model_dump()
    )


# Register routes
app.include_router(recipes.router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Recipe Search and Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
