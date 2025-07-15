"""
Test configuration system functionality.

These tests ensure that:
1. Configuration file exists and is readable
2. YAML structure is valid and contains required sections
3. OpenAI settings are properly configured
4. Processing parameters are defined with correct types
5. Validation rules are comprehensive and well-structured
6. Configuration values are within acceptable ranges
"""

import sys
import os
from pathlib import Path
import pytest
import yaml
from unittest.mock import patch


def test_config_file_exists():
    """Test that config.yaml file exists and is readable."""
    config_path = Path("src/config/config.yaml")
    assert config_path.exists(), "Configuration file src/config/config.yaml must exist"
    assert config_path.is_file(), "Configuration must be a file, not a directory"
    
    # Check file is readable and not empty
    assert config_path.stat().st_size > 0, "Configuration file must not be empty"


def test_config_file_readable():
    """Test that config file can be read and parsed as YAML."""
    config_path = Path("src/config/config.yaml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content.strip()) > 0, "Configuration content must not be empty"
    except UnicodeDecodeError:
        pytest.fail("Configuration file must be valid UTF-8 encoded text")


def test_yaml_structure():
    """Test that configuration file contains valid YAML structure."""
    config_path = Path("src/config/config.yaml")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        assert isinstance(config, dict), "Configuration must be a valid YAML dictionary"
    except yaml.YAMLError as e:
        pytest.fail(f"Configuration must be valid YAML: {e}")


def test_required_config_sections():
    """Test that configuration contains all required sections."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    required_sections = [
        'openai',
        'processing',
        'validation',
        'logging',
        'output'
    ]
    
    for section in required_sections:
        assert section in config, f"Configuration must contain section: {section}"
        assert isinstance(config[section], dict), f"Section '{section}' must be a dictionary"


def test_openai_configuration():
    """Test that OpenAI configuration is properly structured."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    openai_config = config['openai']
    
    # Required OpenAI fields
    required_fields = ['model', 'max_tokens', 'temperature', 'timeout']
    for field in required_fields:
        assert field in openai_config, f"OpenAI config must contain field: {field}"
    
    # Type validation
    assert isinstance(openai_config['model'], str), "OpenAI model must be a string"
    assert isinstance(openai_config['max_tokens'], int), "max_tokens must be an integer"
    assert isinstance(openai_config['temperature'], (int, float)), "temperature must be a number"
    assert isinstance(openai_config['timeout'], int), "timeout must be an integer"
    
    # Value validation
    assert openai_config['max_tokens'] > 0, "max_tokens must be positive"
    assert 0 <= openai_config['temperature'] <= 2, "temperature must be between 0 and 2"
    assert openai_config['timeout'] > 0, "timeout must be positive"


def test_processing_configuration():
    """Test that processing configuration is properly structured."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    processing_config = config['processing']
    
    # Required processing fields
    required_fields = ['stages', 'retry_attempts', 'retry_delay', 'batch_size']
    for field in required_fields:
        assert field in processing_config, f"Processing config must contain field: {field}"
    
    # Type validation
    assert isinstance(processing_config['stages'], list), "stages must be a list"
    assert isinstance(processing_config['retry_attempts'], int), "retry_attempts must be an integer"
    assert isinstance(processing_config['retry_delay'], (int, float)), "retry_delay must be a number"
    assert isinstance(processing_config['batch_size'], int), "batch_size must be an integer"
    
    # Value validation
    assert len(processing_config['stages']) > 0, "stages list must not be empty"
    assert processing_config['retry_attempts'] >= 0, "retry_attempts must be non-negative"
    assert processing_config['retry_delay'] >= 0, "retry_delay must be non-negative"
    assert processing_config['batch_size'] > 0, "batch_size must be positive"


def test_validation_configuration():
    """Test that validation configuration is properly structured."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    validation_config = config['validation']
    
    # Required validation fields
    required_fields = ['input', 'output', 'content']
    for field in required_fields:
        assert field in validation_config, f"Validation config must contain field: {field}"
        assert isinstance(validation_config[field], dict), f"Validation {field} must be a dictionary"
    
    # Input validation rules
    input_validation = validation_config['input']
    assert 'required_fields' in input_validation, "Input validation must have required_fields"
    assert isinstance(input_validation['required_fields'], list), "required_fields must be a list"
    
    # Output validation rules
    output_validation = validation_config['output']
    assert 'schema' in output_validation, "Output validation must have schema"
    
    # Content validation rules
    content_validation = validation_config['content']
    assert 'min_length' in content_validation, "Content validation must have min_length"
    assert isinstance(content_validation['min_length'], int), "min_length must be an integer"


def test_logging_configuration():
    """Test that logging configuration is properly structured."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    logging_config = config['logging']
    
    # Required logging fields
    required_fields = ['level', 'format', 'file_path']
    for field in required_fields:
        assert field in logging_config, f"Logging config must contain field: {field}"
    
    # Type validation
    assert isinstance(logging_config['level'], str), "logging level must be a string"
    assert isinstance(logging_config['format'], str), "logging format must be a string"
    assert isinstance(logging_config['file_path'], str), "logging file_path must be a string"
    
    # Value validation
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    assert logging_config['level'] in valid_levels, f"logging level must be one of: {valid_levels}"


def test_output_configuration():
    """Test that output configuration is properly structured."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    output_config = config['output']
    
    # Required output fields
    required_fields = ['format', 'directory', 'filename_pattern']
    for field in required_fields:
        assert field in output_config, f"Output config must contain field: {field}"
    
    # Type validation
    assert isinstance(output_config['format'], str), "output format must be a string"
    assert isinstance(output_config['directory'], str), "output directory must be a string"
    assert isinstance(output_config['filename_pattern'], str), "filename_pattern must be a string"


def test_config_directory_structure():
    """Test that configuration is in correct directory structure."""
    config_path = Path("src/config/config.yaml")
    
    # Check directory exists
    config_dir = config_path.parent
    assert config_dir.exists(), "src/config directory must exist"
    assert config_dir.is_dir(), "src/config must be a directory"
    
    # Check it's in the correct location
    assert config_dir.name == "config", "Config must be in 'config' directory"
    assert config_dir.parent.name == "src", "Config directory must be in 'src' directory"


def test_config_completeness():
    """Test that configuration is comprehensive and well-structured."""
    config_path = Path("src/config/config.yaml")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
        config = yaml.safe_load(content)
    
    # Check minimum content length (should be substantial)
    assert len(content) > 200, "Configuration should be comprehensive (>200 characters)"
    
    # Check for comments (good practice)
    assert '#' in content, "Configuration should contain explanatory comments"
    
    # Check nested structure depth
    def get_max_depth(d, depth=0):
        if isinstance(d, dict):
            return max([get_max_depth(v, depth + 1) for v in d.values()] + [depth])
        return depth
    
    max_depth = get_max_depth(config)
    assert max_depth >= 2, "Configuration should have nested structure (depth >= 2)"


def test_config_encoding():
    """Test that configuration uses proper encoding."""
    config_path = Path("src/config/config.yaml")
    
    # Read as bytes to check encoding
    with open(config_path, 'rb') as f:
        raw_content = f.read()
    
    # Should be valid UTF-8
    try:
        content = raw_content.decode('utf-8')
    except UnicodeDecodeError:
        pytest.fail("Configuration must use UTF-8 encoding")
    
    # Check for proper line endings
    assert '\r\n' not in content or '\n' not in content.replace('\r\n', ''), \
        "Configuration should use consistent line endings" 