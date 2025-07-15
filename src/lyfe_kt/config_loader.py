"""
Configuration loader module for Lyfe Supertask Knowledge Generator.

This module provides functions to load, validate, and access configuration
from YAML files with support for environment variables and caching.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv


# Global configuration cache
_config_cache: Optional[Dict[str, Any]] = None
_default_config_path = "src/config/config.yaml"


def load_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable support.
    
    Args:
        config_path: Path to configuration YAML file. If None, uses default path.
        env_file: Path to .env file to load. If None, looks for .env in current directory.
        
    Returns:
        Dictionary containing loaded configuration.
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist.
        yaml.YAMLError: If YAML file is invalid.
        ValueError: If configuration is invalid.
    """
    global _config_cache
    
    # Use default config path if none provided
    if config_path is None:
        config_path = _default_config_path
    
    # Load environment variables
    _load_environment_variables(env_file)
    
    # Load YAML configuration
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in configuration file: {e}")
    
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    
    # Apply environment variable overrides
    config = _apply_environment_overrides(config)
    
    # Validate configuration
    if not validate_config(config):
        raise ValueError("Configuration validation failed")
    
    # Cache the configuration
    _config_cache = config
    
    return config


def get_config(key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
    """
    Get configuration value(s) from cached configuration.
    
    Args:
        key: Configuration key to retrieve. If None, returns entire config.
             Supports dot notation for nested values (e.g., 'openai.model').
             
    Returns:
        Configuration value or entire configuration dictionary.
        
    Raises:
        ValueError: If configuration hasn't been loaded yet.
        KeyError: If requested key doesn't exist.
    """
    global _config_cache
    
    if _config_cache is None:
        raise ValueError("Configuration not loaded. Call load_config() first.")
    
    if key is None:
        return _config_cache
    
    # Handle dot notation for nested keys
    if '.' in key:
        keys = key.split('.')
        value = _config_cache
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                raise KeyError(f"Configuration key not found: {key}")
            value = value[k]
        return value
    else:
        if key not in _config_cache:
            raise KeyError(f"Configuration key not found: {key}")
        return _config_cache[key]


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary to validate.
        
    Returns:
        True if configuration is valid, False otherwise.
    """
    if not isinstance(config, dict):
        return False
    
    # Required sections
    required_sections = ['openai', 'processing', 'validation', 'logging', 'output']
    for section in required_sections:
        if section not in config:
            return False
        if not isinstance(config[section], dict):
            return False
    
    # Validate OpenAI section
    openai_config = config['openai']
    required_openai_fields = ['model', 'max_tokens', 'temperature', 'timeout']
    for field in required_openai_fields:
        if field not in openai_config:
            return False
    
    # Validate OpenAI field types and ranges
    if not isinstance(openai_config['model'], str):
        return False
    if not isinstance(openai_config['max_tokens'], int) or openai_config['max_tokens'] <= 0:
        return False
    if not isinstance(openai_config['temperature'], (int, float)):
        return False
    if not (0 <= openai_config['temperature'] <= 2):
        return False
    if not isinstance(openai_config['timeout'], int) or openai_config['timeout'] <= 0:
        return False
    
    # Validate processing section
    processing_config = config['processing']
    required_processing_fields = ['stages', 'retry_attempts', 'retry_delay', 'batch_size']
    for field in required_processing_fields:
        if field not in processing_config:
            return False
    
    # Validate processing field types and ranges
    if not isinstance(processing_config['stages'], list) or len(processing_config['stages']) == 0:
        return False
    if not isinstance(processing_config['retry_attempts'], int) or processing_config['retry_attempts'] < 0:
        return False
    if not isinstance(processing_config['retry_delay'], (int, float)) or processing_config['retry_delay'] < 0:
        return False
    if not isinstance(processing_config['batch_size'], int) or processing_config['batch_size'] <= 0:
        return False
    
    # Validate validation section
    validation_config = config['validation']
    required_validation_sections = ['input', 'output', 'content']
    for section in required_validation_sections:
        if section not in validation_config:
            return False
        if not isinstance(validation_config[section], dict):
            return False
    
    # Validate input validation section
    input_validation = validation_config['input']
    if 'required_fields' not in input_validation:
        return False
    if not isinstance(input_validation['required_fields'], list):
        return False
    
    # Validate output validation section
    output_validation = validation_config['output']
    if 'schema' not in output_validation:
        return False
    
    # Validate content validation section
    content_validation = validation_config['content']
    if 'min_length' not in content_validation:
        return False
    if not isinstance(content_validation['min_length'], int):
        return False
    
    # Validate logging section
    logging_config = config['logging']
    required_logging_fields = ['level', 'format', 'file_path']
    for field in required_logging_fields:
        if field not in logging_config:
            return False
    
    # Validate logging field types
    if not isinstance(logging_config['level'], str):
        return False
    if not isinstance(logging_config['format'], str):
        return False
    if not isinstance(logging_config['file_path'], str):
        return False
    
    # Validate logging level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if logging_config['level'] not in valid_levels:
        return False
    
    # Validate output section
    output_config = config['output']
    required_output_fields = ['format', 'directory', 'filename_pattern']
    for field in required_output_fields:
        if field not in output_config:
            return False
    
    # Validate output field types
    if not isinstance(output_config['format'], str):
        return False
    if not isinstance(output_config['directory'], str):
        return False
    if not isinstance(output_config['filename_pattern'], str):
        return False
    
    return True


def _load_environment_variables(env_file: Optional[str] = None) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file. If None, looks for .env in current directory.
    """
    if env_file:
        # Load specific env file
        load_dotenv(env_file)
    else:
        # Load default .env file if it exists
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)


def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.
    
    Args:
        config: Configuration dictionary to modify.
        
    Returns:
        Modified configuration dictionary.
    """
    # Create a copy to avoid modifying the original
    config = config.copy()
    
    # Check for environment variable overrides
    # Format: LYFE_KT_SECTION_KEY (e.g., LYFE_KT_OPENAI_MODEL)
    for env_key, env_value in os.environ.items():
        if env_key.startswith('LYFE_KT_'):
            # Parse the key
            key_parts = env_key[8:].lower().split('_')  # Remove LYFE_KT_ prefix
            if len(key_parts) >= 2:
                section = key_parts[0]
                field = '_'.join(key_parts[1:])
                
                # Apply override if section exists
                if section in config and isinstance(config[section], dict):
                    # Try to convert value to appropriate type
                    converted_value = _convert_env_value(env_value)
                    config[section][field] = converted_value
    
    return config


def _convert_env_value(value: str) -> Union[str, int, float, bool]:
    """
    Convert environment variable string value to appropriate type.
    
    Args:
        value: String value from environment variable.
        
    Returns:
        Converted value with appropriate type.
    """
    # Try boolean conversion
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # Try integer conversion
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float conversion
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def reload_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Reload configuration, clearing cache first.
    
    Args:
        config_path: Path to configuration YAML file.
        env_file: Path to .env file to load.
        
    Returns:
        Reloaded configuration dictionary.
    """
    global _config_cache
    _config_cache = None
    return load_config(config_path, env_file)


def clear_config_cache() -> None:
    """Clear the configuration cache."""
    global _config_cache
    _config_cache = None 