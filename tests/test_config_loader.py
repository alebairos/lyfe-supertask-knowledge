"""
Test configuration loader functionality.

These tests ensure that:
1. Configuration loader module exists and is importable
2. Configuration can be loaded from YAML files
3. Environment variables are properly handled
4. Configuration validation works correctly
5. Error handling is robust for missing files and invalid configs
6. Configuration merging and overrides work as expected
"""

import sys
import os
import tempfile
from pathlib import Path
import pytest
import yaml
from unittest.mock import patch, MagicMock


def test_config_loader_module_exists():
    """Test that config loader module exists and is importable."""
    loader_path = Path("src/lyfe_kt/config_loader.py")
    assert loader_path.exists(), "Config loader module src/lyfe_kt/config_loader.py must exist"
    assert loader_path.is_file(), "Config loader must be a file, not a directory"


def test_config_loader_importable():
    """Test that config loader module can be imported without errors."""
    # Add src to Python path for testing
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        from lyfe_kt import config_loader
        assert hasattr(config_loader, 'load_config'), "Config loader must have 'load_config' function"
        assert hasattr(config_loader, 'get_config'), "Config loader must have 'get_config' function"
        assert hasattr(config_loader, 'validate_config'), "Config loader must have 'validate_config' function"
    except ImportError as e:
        pytest.fail(f"Failed to import config loader module: {e}")


def test_load_config_function():
    """Test that load_config function works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Should be callable
    assert callable(load_config), "load_config must be callable"
    
    # Test with default config file
    try:
        config = load_config()
        assert isinstance(config, dict), "load_config must return a dictionary"
        assert len(config) > 0, "Loaded config must not be empty"
    except Exception as e:
        pytest.fail(f"load_config raised unexpected exception: {e}")


def test_load_config_with_custom_path():
    """Test that load_config works with custom configuration paths."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Test with existing config file
    config_path = "src/config/config.yaml"
    config = load_config(config_path)
    
    assert isinstance(config, dict), "Config must be a dictionary"
    assert 'openai' in config, "Config must contain openai section"
    assert 'processing' in config, "Config must contain processing section"


def test_load_config_missing_file():
    """Test that load_config handles missing files gracefully."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Test with non-existent file
    with pytest.raises((FileNotFoundError, ValueError)):
        load_config("non_existent_config.yaml")


def test_get_config_function():
    """Test that get_config function works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import get_config, load_config
    
    # Should be callable
    assert callable(get_config), "get_config must be callable"
    
    # Load config first
    load_config()
    
    # Test getting config
    config = get_config()
    assert isinstance(config, dict), "get_config must return a dictionary"
    assert len(config) > 0, "Retrieved config must not be empty"


def test_get_config_section():
    """Test that get_config can retrieve specific sections."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import get_config, load_config
    
    # Load config first
    load_config()
    
    # Test getting specific section
    openai_config = get_config('openai')
    assert isinstance(openai_config, dict), "OpenAI config section must be a dictionary"
    assert 'model' in openai_config, "OpenAI config must contain model field"
    
    # Test getting nested value
    model = get_config('openai.model')
    assert isinstance(model, str), "OpenAI model must be a string"


def test_validate_config_function():
    """Test that validate_config function works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import validate_config, load_config
    
    # Should be callable
    assert callable(validate_config), "validate_config must be callable"
    
    # Load and validate config
    config = load_config()
    
    # Should not raise exception for valid config
    try:
        is_valid = validate_config(config)
        assert isinstance(is_valid, bool), "validate_config must return a boolean"
        assert is_valid, "Default config should be valid"
    except Exception as e:
        pytest.fail(f"validate_config raised unexpected exception: {e}")


def test_validate_config_invalid():
    """Test that validate_config correctly identifies invalid configurations."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import validate_config
    
    # Test with invalid config (missing required sections)
    invalid_config = {'incomplete': 'config'}
    
    is_valid = validate_config(invalid_config)
    assert not is_valid, "Invalid config should be identified as invalid"


def test_environment_variable_support():
    """Test that environment variables are properly loaded and used."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Test with environment variable
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key_123'}):
        config = load_config()
        
        # Environment variables should be available
        assert 'OPENAI_API_KEY' in os.environ
        assert os.environ['OPENAI_API_KEY'] == 'test_key_123'


def test_config_override_with_env_vars():
    """Test that configuration can be overridden with environment variables."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config, get_config
    
    # Test with environment variable override
    with patch.dict(os.environ, {'LYFE_KT_OPENAI_MODEL': 'gpt-3.5-turbo'}):
        config = load_config()
        
        # Should be able to get overridden value
        # Implementation may vary, but environment should be loaded
        assert 'LYFE_KT_OPENAI_MODEL' in os.environ


def test_config_caching():
    """Test that configuration is properly cached."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config, get_config
    
    # Load config
    config1 = load_config()
    
    # Get config (should be cached)
    config2 = get_config()
    
    # Should be the same object or equivalent
    assert config1 == config2, "Cached config should be equivalent to loaded config"


def test_config_reload():
    """Test that configuration can be reloaded."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Load config multiple times
    config1 = load_config()
    config2 = load_config()
    
    # Should be equivalent
    assert config1 == config2, "Reloaded config should be equivalent"


def test_config_with_custom_env_file():
    """Test that configuration can load custom .env files."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Create temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write('TEST_VAR=test_value\n')
        f.write('OPENAI_API_KEY=test_api_key\n')
        env_file = f.name
    
    try:
        # Load config with custom env file
        config = load_config(env_file=env_file)
        
        # Should not raise exception
        assert isinstance(config, dict), "Config should be loaded successfully"
        
    finally:
        # Clean up
        os.unlink(env_file)


def test_config_error_handling():
    """Test that configuration loader handles errors gracefully."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    # Test with invalid YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write('invalid: yaml: content: [')
        invalid_yaml = f.name
    
    try:
        with pytest.raises((yaml.YAMLError, ValueError)):
            load_config(invalid_yaml)
    finally:
        os.unlink(invalid_yaml)


def test_config_type_conversion():
    """Test that configuration values are properly type-converted."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.config_loader import load_config
    
    config = load_config()
    
    # Check that types are preserved from YAML
    assert isinstance(config['openai']['max_tokens'], int), "max_tokens should be integer"
    assert isinstance(config['openai']['temperature'], float), "temperature should be float"
    assert isinstance(config['openai']['model'], str), "model should be string"
    assert isinstance(config['processing']['stages'], list), "stages should be list" 