"""
Logging configuration module.
Provides structured logging with JSON format, file rotation, and request ID support.
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import contextvars
from pythonjsonlogger import jsonlogger
import colorlog

from backend.config import LOG_LEVEL, LOG_DIR, ENABLE_FILE_LOGGING

# Context variable for request ID
request_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'request_id', default=None
)


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = request_id_context.get()
        if request_id:
            record.request_id = request_id
        else:
            record.request_id = None
        return True


def setup_logging():
    """
    Configure root logger with console and file handlers.
    Uses JSON format for file logs and colored console output for development.
    """
    # Ensure log directory exists
    if ENABLE_FILE_LOGGING:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    json_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(module)s %(funcName)s %(lineno)d %(request_id)s',
        timestamp=True
    )
    
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Create request ID filter
    request_id_filter = RequestIDFilter()
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(request_id_filter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (if enabled)
    if ENABLE_FILE_LOGGING:
        log_file = LOG_DIR / "app.log"
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(json_formatter)
        file_handler.addFilter(request_id_filter)
        root_logger.addHandler(file_handler)
    
    # Log startup message
    root_logger.info(
        "Logging initialized",
        extra={
            "log_level": LOG_LEVEL,
            "file_logging": ENABLE_FILE_LOGGING,
            "log_dir": str(LOG_DIR) if ENABLE_FILE_LOGGING else None
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_request_id(request_id: str):
    """Set the request ID in the context for logging."""
    request_id_context.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_context.get()
