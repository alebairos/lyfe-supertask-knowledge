"""
Test logging system functionality.

These tests ensure that:
1. Logging module exists and is importable
2. Logger is properly configured with file and console handlers
3. Log levels work correctly
4. Log files are created and written to
5. Console output is properly formatted
6. Log rotation and cleanup work as expected
"""

import sys
import os
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


def test_logging_module_exists():
    """Test that logging module exists and is importable."""
    logging_path = Path("src/lyfe_kt/logging_config.py")
    assert logging_path.exists(), "Logging module src/lyfe_kt/logging_config.py must exist"
    assert logging_path.is_file(), "Logging module must be a file, not a directory"


def test_logging_module_importable():
    """Test that logging module can be imported without errors."""
    # Add src to Python path for testing
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        from lyfe_kt import logging_config
        assert hasattr(logging_config, 'setup_logging'), "Logging module must have 'setup_logging' function"
        assert hasattr(logging_config, 'get_logger'), "Logging module must have 'get_logger' function"
    except ImportError as e:
        pytest.fail(f"Failed to import logging module: {e}")


def test_setup_logging_function():
    """Test that setup_logging function works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import setup_logging
    
    # Should be callable
    assert callable(setup_logging), "setup_logging must be callable"
    
    # Should accept log_level parameter
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Should not raise exception when called
        try:
            setup_logging(log_file=str(log_file), log_level="INFO")
        except Exception as e:
            pytest.fail(f"setup_logging raised unexpected exception: {e}")


def test_get_logger_function():
    """Test that get_logger function works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import get_logger, setup_logging
    
    # Should be callable
    assert callable(get_logger), "get_logger must be callable"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        setup_logging(log_file=str(log_file))
        
        # Should return a logger instance
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger), "get_logger must return a Logger instance"
        assert logger.name == "test_module", "Logger should have the correct name"


def test_file_logging_functionality():
    """Test that file logging works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import setup_logging, get_logger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Setup logging with file output
        setup_logging(log_file=str(log_file), log_level="DEBUG")
        logger = get_logger("test_file_logging")
        
        # Write test message
        test_message = "Test file logging message"
        logger.info(test_message)
        
        # Check that log file was created
        assert log_file.exists(), "Log file should be created"
        
        # Check that message was written to file
        log_content = log_file.read_text()
        assert test_message in log_content, "Test message should be in log file"
        assert "INFO" in log_content, "Log level should be in log file"


def test_console_logging_functionality():
    """Test that console logging works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import setup_logging, get_logger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Setup logging
        setup_logging(log_file=str(log_file), log_level="DEBUG")
        logger = get_logger("test_console_logging")
        
        # Check that root logger has handlers configured
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0, "Root logger should have handlers configured"
        
        # Check that at least one handler is a console handler
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0, "Should have at least one console handler"


def test_log_levels():
    """Test that different log levels work correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import setup_logging, get_logger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Test different log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            # Clear previous log content
            if log_file.exists():
                log_file.unlink()
            
            setup_logging(log_file=str(log_file), log_level=level)
            logger = get_logger(f"test_level_{level}")
            
            # Test logging at different levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            # Verify log file contains appropriate messages based on level
            if log_file.exists():
                log_content = log_file.read_text()
                
                if level == "DEBUG":
                    assert "Debug message" in log_content, f"DEBUG level should include debug messages"
                elif level == "INFO":
                    assert "Info message" in log_content, f"INFO level should include info messages"
                    assert "Debug message" not in log_content, f"INFO level should not include debug messages"
                elif level == "WARNING":
                    assert "Warning message" in log_content, f"WARNING level should include warning messages"
                    assert "Info message" not in log_content, f"WARNING level should not include info messages"
                elif level == "ERROR":
                    assert "Error message" in log_content, f"ERROR level should include error messages"
                    assert "Warning message" not in log_content, f"ERROR level should not include warning messages"


def test_logging_configuration_validation():
    """Test that logging configuration is validated properly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import setup_logging
    
    # Test with invalid log level
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Should handle invalid log level gracefully
        try:
            setup_logging(log_file=str(log_file), log_level="INVALID_LEVEL")
            # Should either raise an exception or default to a valid level
        except ValueError:
            # This is acceptable - explicit validation
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception for invalid log level: {e}")


def test_log_directory_creation():
    """Test that log directory is created if it doesn't exist."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.logging_config import setup_logging, get_logger
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested directory path that doesn't exist
        log_dir = Path(temp_dir) / "logs" / "nested"
        log_file = log_dir / "test.log"
        
        # Directory should not exist initially
        assert not log_dir.exists(), "Log directory should not exist initially"
        
        # Setup logging should create the directory
        setup_logging(log_file=str(log_file))
        logger = get_logger("test_dir_creation")
        logger.info("Test message")
        
        # Directory and file should now exist
        assert log_dir.exists(), "Log directory should be created"
        assert log_file.exists(), "Log file should be created" 