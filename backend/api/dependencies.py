"""
FastAPI dependencies for request handling and logging.
"""
from fastapi import Request, Header
from typing import Optional
from backend.logging_config import get_logger, get_request_id, set_request_id

logger = get_logger(__name__)


async def get_request_id_dependency(
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> str:
    """
    FastAPI dependency to get or generate request ID.
    
    Args:
        request: FastAPI request object
        x_request_id: Optional request ID from header
        
    Returns:
        Request ID string
    """
    # Use provided header or generate new one
    request_id = x_request_id or set_request_id()
    
    # Store in request state for access in routes
    request.state.request_id = request_id
    
    # Set in logging context
    set_request_id(request_id)
    
    return request_id


def get_logger_dependency(request: Request):
    """
    FastAPI dependency to get logger with request ID context.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Logger instance
    """
    # Request ID should already be set by middleware or get_request_id_dependency
    return logger
