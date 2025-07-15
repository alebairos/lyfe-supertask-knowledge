"""
Logging configuration module for Lyfe Supertask Knowledge Generator.

This module provides centralized logging configuration with both file and console output.
It uses Python's built-in logging module with proper formatting and level control.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


# Global logger configuration
_LOGGING_CONFIGURED = False
_DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    console_level: Optional[str] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None
) -> None:
    """
    Set up logging configuration with file and console handlers.
    
    Args:
        log_file: Path to log file. If None, only console logging is enabled.
        log_level: Minimum log level for file logging (DEBUG, INFO, WARNING, ERROR).
        console_level: Minimum log level for console logging. If None, uses log_level.
        log_format: Custom log format string. If None, uses default format.
        date_format: Custom date format string. If None, uses default format.
    
    Raises:
        ValueError: If log_level is not a valid logging level.
    """
    global _LOGGING_CONFIGURED
    
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {log_level}. Must be one of: {valid_levels}")
    
    # Set console level to log_level if not specified
    if console_level is None:
        console_level = log_level
    
    # Validate console level
    if console_level.upper() not in valid_levels:
        raise ValueError(f"Invalid console log level: {console_level}. Must be one of: {valid_levels}")
    
    # Use default formats if not provided
    if log_format is None:
        log_format = _DEFAULT_LOG_FORMAT
    if date_format is None:
        date_format = _DEFAULT_DATE_FORMAT
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers if already configured
    if _LOGGING_CONFIGURED:
        root_logger.handlers.clear()
    
    # Set root logger level to the most permissive level
    file_level = getattr(logging, log_level.upper())
    console_log_level = getattr(logging, console_level.upper())
    root_logger.setLevel(min(file_level, console_log_level))
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set up file handler if log_file is provided
    if log_file:
        log_path = Path(log_file)
        
        # Create log directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Mark as configured
    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Name for the logger (typically module name).
        
    Returns:
        Logger instance configured with the current logging setup.
        
    Note:
        setup_logging() should be called before using this function.
    """
    return logging.getLogger(name)


def reset_logging() -> None:
    """
    Reset logging configuration for testing purposes.
    
    This function clears all handlers and resets the configuration flag.
    It's primarily intended for use in tests.
    """
    global _LOGGING_CONFIGURED
    
    # Clear all handlers from root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.WARNING)  # Reset to default level
    
    # Reset configuration flag
    _LOGGING_CONFIGURED = False


def is_logging_configured() -> bool:
    """
    Check if logging has been configured.
    
    Returns:
        True if setup_logging() has been called, False otherwise.
    """
    return _LOGGING_CONFIGURED 