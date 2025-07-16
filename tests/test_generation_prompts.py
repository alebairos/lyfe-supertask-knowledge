"""
Tests for generation prompts configuration and functionality.
"""

import pytest
import yaml
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.lyfe_kt.config_loader import (
    load_generation_prompts,
    validate_generation_prompts_config,
    get_generation_prompts,
    build_generation_prompt,
    get_difficulty_configuration,
    get_generation_preset,
    validate_generated_json_structure,
    clear_generation_prompts_cache,
    AriPersonaConfigError
)


class TestGenerationPromptsLoading:
    """Test generation prompts configuration loading."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_generation_prompts_cache()
    
    def test_load_generation_prompts_success(self):
        """Test successful loading of generation prompts configuration."""
        # This should load the actual configuration file
        config = load_generation_prompts()
        
        assert isinstance(config, dict)
        assert 'generation_prompts' in config
        assert 'generation_presets' in config
        assert 'output_formatting' in config
    
    def test_load_generation_prompts_caching(self):
        """Test that generation prompts configuration is cached."""
        # Load configuration first time
        config1 = load_generation_prompts()
        
        # Load configuration second time (should use cache)
        config2 = load_generation_prompts()
        
        # Should return the same object (cached)
        assert config1 is config2
    
    def test_load_generation_prompts_force_reload(self):
        """Test force reload bypasses cache."""
        # Load configuration first time
        config1 = load_generation_prompts()
        
        # Force reload should bypass cache
        config2 = load_generation_prompts(force_reload=True)
        
        # Should be equal but different objects
        assert config1 == config2
        assert isinstance(config2, dict)
    
    def test_load_generation_prompts_file_not_found(self):
        """Test handling of missing configuration file."""
        with pytest.raises(FileNotFoundError):
            load_generation_prompts("non_existent_file.yaml")
    
    def test_load_generation_prompts_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            temp_path = f.name
        
        try:
            with pytest.raises(AriPersonaConfigError):
                load_generation_prompts(temp_path)
        finally:
            os.unlink(temp_path)


class TestGenerationPromptsValidation:
    """Test generation prompts configuration validation."""
    
    def test_validate_complete_config(self):
        """Test validation of complete valid configuration."""
        # Load the actual configuration and validate it
        config = load_generation_prompts()
        result = validate_generation_prompts_config(config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_missing_required_sections(self):
        """Test validation fails with missing required sections."""
        incomplete_config = {
            'generation_prompts': {}
            # Missing generation_presets and output_formatting
        }
        
        result = validate_generation_prompts_config(incomplete_config)
        
        assert result['valid'] is False
        assert any('generation_presets' in error for error in result['errors'])
        assert any('output_formatting' in error for error in result['errors'])
    
    def test_validate_missing_generation_subsections(self):
        """Test validation fails with missing generation subsections."""
        config_with_missing_subsections = {
            'generation_prompts': {
                'main_prompt': {}
                # Missing other required subsections
            },
            'generation_presets': {},
            'output_formatting': {}
        }
        
        result = validate_generation_prompts_config(config_with_missing_subsections)
        
        assert result['valid'] is False
        assert any('content_conversion' in error for error in result['errors'])
        assert any('difficulty_generation' in error for error in result['errors'])
    
    def test_validate_missing_difficulties(self):
        """Test validation detects missing difficulty configurations."""
        config_with_incomplete_difficulties = {
            'generation_prompts': {
                'main_prompt': {
                    'system_message': 'test',
                    'user_prompt_template': 'test'
                },
                'content_conversion': {},
                'difficulty_generation': {
                    'beginner': {'title_suffix': ' - Beginner'}
                    # Missing advanced
                },
                'ari_voice_integration': {},
                'json_structure_validation': {},
                'quality_standards': {}
            },
            'generation_presets': {},
            'output_formatting': {}
        }
        
        result = validate_generation_prompts_config(config_with_incomplete_difficulties)
        
        assert result['valid'] is False
        # Should have error for missing advanced difficulty
        difficulty_errors = [error for error in result['errors'] if 'difficulty configuration' in error]
        assert len(difficulty_errors) == 1
        assert 'advanced' in difficulty_errors[0]


class TestGenerationPromptsAccess:
    """Test generation prompts configuration access."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_generation_prompts_cache()
        load_generation_prompts()
    
    def test_get_generation_prompts_full_config(self):
        """Test getting the full generation prompts configuration."""
        config = get_generation_prompts()
        
        assert isinstance(config, dict)
        assert 'generation_prompts' in config
        assert 'generation_presets' in config
    
    def test_get_generation_prompts_specific_key(self):
        """Test getting specific configuration keys."""
        main_prompt = get_generation_prompts('generation_prompts')
        
        assert isinstance(main_prompt, dict)
        assert 'main_prompt' in main_prompt
        assert 'difficulty_generation' in main_prompt
    
    def test_get_generation_prompts_dot_notation(self):
        """Test getting nested configuration using dot notation."""
        system_message = get_generation_prompts('generation_prompts.main_prompt.system_message')
        
        assert isinstance(system_message, str)
        assert 'Ari' in system_message
        assert 'JSON' in system_message
    
    def test_get_generation_prompts_not_loaded(self):
        """Test error when configuration not loaded."""
        clear_generation_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError, match="not loaded"):
            get_generation_prompts()
    
    def test_get_generation_prompts_invalid_key(self):
        """Test error with invalid configuration key."""
        with pytest.raises(KeyError):
            get_generation_prompts('non_existent_key')
    
    def test_get_generation_prompts_invalid_dot_notation(self):
        """Test error with invalid dot notation key."""
        with pytest.raises(KeyError):
            get_generation_prompts('generation_prompts.non_existent.key')


class TestBuildGenerationPrompt:
    """Test building generation prompts for template conversion."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_generation_prompts_cache()
        load_generation_prompts()
    
    def test_build_generation_prompt_basic(self):
        """Test building basic generation prompt."""
        filled_template = """---
title: "Test Supertask - Beginner"
dimension: "physicalHealth"
---

# Content
Test content about habits."""
        
        result = build_generation_prompt(filled_template)
        
        assert isinstance(result, dict)
        assert 'system_message' in result
        assert 'user_message' in result
        assert 'Ari' in result['system_message']
        assert 'Test content about habits' in result['user_message']
        assert 'beginner' in result['user_message']
    
    def test_build_generation_prompt_with_difficulty(self):
        """Test building generation prompt with specific difficulty."""
        filled_template = "Advanced template content"
        
        result = build_generation_prompt(
            filled_template,
            target_difficulty="advanced",
            target_audience="advanced"
        )
        
        assert 'advanced' in result['user_message']
        assert 'Advanced template content' in result['user_message']
    
    def test_build_generation_prompt_with_custom_params(self):
        """Test building generation prompt with custom parameters."""
        filled_template = "Custom template"
        
        result = build_generation_prompt(
            filled_template,
            target_difficulty="beginner",
            target_audience="beginner",
            estimated_duration=600,
            suggested_coins=20
        )
        
        assert '600' in result['user_message']
        assert '20' in result['user_message']
        assert 'Custom template' in result['user_message']
    
    def test_build_generation_prompt_with_target_json(self):
        """Test that generation prompt includes target JSON structure."""
        filled_template = "Template with JSON target"
        
        result = build_generation_prompt(filled_template)
        
        # Should include target JSON structure in user message
        assert 'flexibleItems' in result['user_message']
        assert 'metadata' in result['user_message']
    
    def test_build_generation_prompt_configuration_error(self):
        """Test error handling when configuration is invalid."""
        clear_generation_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError):
            build_generation_prompt("test template")


class TestDifficultyConfiguration:
    """Test difficulty-specific configuration access."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_generation_prompts_cache()
        load_generation_prompts()
    
    def test_get_difficulty_configuration_beginner(self):
        """Test getting beginner difficulty configuration."""
        config = get_difficulty_configuration("beginner")
        
        assert isinstance(config, dict)
        assert 'title_suffix' in config
        assert 'characteristics' in config
        assert 'content_guidelines' in config
        assert config['title_suffix'] == " - Beginner"
    
    def test_get_difficulty_configuration_advanced(self):
        """Test getting advanced difficulty configuration."""
        config = get_difficulty_configuration("advanced")
        
        assert isinstance(config, dict)
        assert 'title_suffix' in config
        assert 'characteristics' in config
        assert 'content_guidelines' in config
        assert config['title_suffix'] == " - Advanced"
    
    def test_get_difficulty_configuration_invalid(self):
        """Test error with invalid difficulty level."""
        with pytest.raises(KeyError):
            get_difficulty_configuration("invalid_difficulty")
    
    def test_get_difficulty_configuration_not_loaded(self):
        """Test error when configuration not loaded."""
        clear_generation_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError):
            get_difficulty_configuration("beginner")


class TestGenerationPresets:
    """Test generation preset access."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_generation_prompts_cache()
        load_generation_prompts()
    
    def test_get_generation_preset_default_beginner(self):
        """Test getting default beginner preset."""
        preset = get_generation_preset("default_beginner")
        
        assert isinstance(preset, dict)
        assert preset['target_difficulty'] == "beginner"
        assert preset['target_audience'] == "beginner"
        assert 'estimated_duration' in preset
        assert 'suggested_coins' in preset
    
    def test_get_generation_preset_default_advanced(self):
        """Test getting default advanced preset."""
        preset = get_generation_preset("default_advanced")
        
        assert isinstance(preset, dict)
        assert preset['target_difficulty'] == "advanced"
        assert preset['target_audience'] == "advanced"
        assert 'estimated_duration' in preset
        assert 'suggested_coins' in preset
    
    def test_get_generation_preset_habit_specific(self):
        """Test getting habit-specific preset."""
        preset = get_generation_preset("habit_specific")
        
        assert isinstance(preset, dict)
        assert preset['relatedToType'] == "HABITBP"
        assert 'focus' in preset
    
    def test_get_generation_preset_invalid(self):
        """Test error with invalid preset name."""
        with pytest.raises(KeyError):
            get_generation_preset("invalid_preset")
    
    def test_get_generation_preset_not_loaded(self):
        """Test error when configuration not loaded."""
        clear_generation_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError):
            get_generation_preset("default_beginner")


class TestJSONStructureValidation:
    """Test JSON structure validation functionality."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_generation_prompts_cache()
        load_generation_prompts()
    
    def test_validate_generated_json_valid(self):
        """Test validation of valid JSON structure."""
        valid_json = {
            "title": "Test Supertask",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "test-habit",
            "estimatedDuration": 300,
            "coinsReward": 15,
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "Test content"
                },
                {
                    "type": "quiz",
                    "question": "Test question?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 0,
                    "explanation": "Test explanation"
                }
            ],
            "metadata": {
                "language": "portuguese",
                "region": "Brazil",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "version": "1.0"
            }
        }
        
        result = validate_generated_json_structure(valid_json)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_generated_json_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        invalid_json = {
            "title": "Test Supertask"
            # Missing many required fields
        }
        
        result = validate_generated_json_structure(invalid_json)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('Missing required field' in error for error in result['errors'])
    
    def test_validate_generated_json_invalid_flexible_items(self):
        """Test validation fails with invalid flexibleItems structure."""
        invalid_json = {
            "title": "Test Supertask",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "test-habit",
            "estimatedDuration": 300,
            "coinsReward": 15,
            "flexibleItems": [
                {
                    "type": "invalid_type",
                    "content": "Test content"
                }
            ],
            "metadata": {}
        }
        
        result = validate_generated_json_structure(invalid_json)
        
        assert result['valid'] is False
        assert any('invalid type' in error for error in result['errors'])
    
    def test_validate_generated_json_missing_metadata_fields(self):
        """Test validation fails with missing metadata fields."""
        invalid_json = {
            "title": "Test Supertask",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "test-habit",
            "estimatedDuration": 300,
            "coinsReward": 15,
            "flexibleItems": [],
            "metadata": {
                "language": "portuguese"
                # Missing other required metadata fields
            }
        }
        
        result = validate_generated_json_structure(invalid_json)
        
        assert result['valid'] is False
        assert any('Missing required metadata field' in error for error in result['errors'])
    
    def test_validate_generated_json_wrong_data_types(self):
        """Test validation fails with wrong data types."""
        invalid_json = {
            "title": "Test Supertask",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "test-habit",
            "estimatedDuration": "should_be_number",  # Wrong type
            "coinsReward": "also_should_be_number",  # Wrong type
            "flexibleItems": "should_be_array",  # Wrong type
            "metadata": {}
        }
        
        result = validate_generated_json_structure(invalid_json)
        
        assert result['valid'] is False
        assert any('must be an integer' in error for error in result['errors'])
        assert any('must be an array' in error for error in result['errors'])
    
    def test_validate_generated_json_configuration_error(self):
        """Test error handling when configuration is not loaded."""
        clear_generation_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError):
            validate_generated_json_structure({"test": "data"})


class TestGenerationPromptsIntegration:
    """Integration tests for generation prompts functionality."""
    
    def test_full_configuration_loading_and_access(self):
        """Test complete workflow of loading and accessing configuration."""
        # Clear cache to start fresh
        clear_generation_prompts_cache()
        
        # Load configuration
        config = load_generation_prompts()
        assert config is not None
        
        # Validate configuration
        validation = validate_generation_prompts_config(config)
        assert validation['valid'] is True
        
        # Access specific elements
        main_prompt = get_generation_prompts('generation_prompts.main_prompt')
        assert 'system_message' in main_prompt
        
        # Build actual prompt
        prompt = build_generation_prompt("Test template")
        assert 'system_message' in prompt
        assert 'user_message' in prompt
        
        # Get difficulty configuration
        beginner_config = get_difficulty_configuration("beginner")
        assert isinstance(beginner_config, dict)
        
        # Get generation preset
        preset = get_generation_preset("default_beginner")
        assert isinstance(preset, dict)
    
    def test_error_propagation(self):
        """Test that errors are properly propagated through the system."""
        clear_generation_prompts_cache()
        
        # All functions should fail when configuration is not loaded
        with pytest.raises(AriPersonaConfigError):
            get_generation_prompts()
        
        with pytest.raises(AriPersonaConfigError):
            build_generation_prompt("content")
        
        with pytest.raises(AriPersonaConfigError):
            get_difficulty_configuration("beginner")
        
        with pytest.raises(AriPersonaConfigError):
            get_generation_preset("default_beginner")
        
        with pytest.raises(AriPersonaConfigError):
            validate_generated_json_structure({"test": "data"})
    
    def test_cache_management(self):
        """Test cache management across multiple operations."""
        # Load configuration
        load_generation_prompts()
        
        # Configuration should be cached
        config1 = get_generation_prompts()
        config2 = get_generation_prompts()
        assert config1 is config2
        
        # Clear cache
        clear_generation_prompts_cache()
        
        # Should fail after cache clear
        with pytest.raises(AriPersonaConfigError):
            get_generation_prompts() 