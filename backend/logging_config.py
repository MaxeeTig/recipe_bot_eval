"""
Structured logging configuration with request ID tracking.
"""
import logging
import sys
import uuid
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from contextvars import ContextVar

from backend.config import LOG_LEVEL, LOG_TO_FILE, LOG_DIR

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class RequestIDFilter(logging.Filter):
    """Logging filter to add request ID to log records."""
    
    def filter(self, record):
        request_id = request_id_var.get()
        record.request_id = request_id if request_id else "N/A"
        return True


def get_request_id() -> Optional[str]:
    """Get current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set request ID in context. If None, generates a new UUID.
    
    Args:
        request_id: Optional request ID. If None, generates UUID.
        
    Returns:
        The request ID that was set.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def clear_request_id():
    """Clear request ID from context."""
    request_id_var.set(None)


def setup_logging() -> logging.Logger:
    """
    Set up structured logging with request ID tracking.
    
    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter with structured format
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | [%(request_id)s] | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if LOG_TO_FILE:
        log_file = LOG_DIR / "backend.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging on import
setup_logging()
