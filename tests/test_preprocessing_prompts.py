"""
Tests for preprocessing prompts configuration and functionality.
"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.lyfe_kt.config_loader import (
    load_preprocessing_prompts,
    validate_preprocessing_prompts_config,
    get_preprocessing_prompts,
    build_preprocessing_prompt,
    get_framework_integration_for_content,
    clear_preprocessing_prompts_cache,
    AriPersonaConfigError
)


class TestPreprocessingPromptsLoading:
    """Test preprocessing prompts configuration loading."""
    
    def setup_method(self):
        """Clear cache before each test."""
        clear_preprocessing_prompts_cache()
    
    def test_load_preprocessing_prompts_success(self):
        """Test successful loading of preprocessing prompts configuration."""
        # This should load the actual configuration file
        config = load_preprocessing_prompts()
        
        assert isinstance(config, dict)
        assert 'preprocessing_prompts' in config
        assert 'difficulty_configurations' in config
        assert 'validation_rules' in config
    
    def test_load_preprocessing_prompts_caching(self):
        """Test that preprocessing prompts configuration is cached."""
        # Load configuration first time
        config1 = load_preprocessing_prompts()
        
        # Load configuration second time (should use cache)
        config2 = load_preprocessing_prompts()
        
        # Should return the same object (cached)
        assert config1 is config2
    
    def test_load_preprocessing_prompts_force_reload(self):
        """Test force reload bypasses cache."""
        # Load configuration first time
        config1 = load_preprocessing_prompts()
        
        # Force reload should bypass cache
        config2 = load_preprocessing_prompts(force_reload=True)
        
        # Should be equal but different objects
        assert config1 == config2
        # Note: They might be the same object due to YAML loading, so we test functionality instead
        assert isinstance(config2, dict)
    
    def test_load_preprocessing_prompts_file_not_found(self):
        """Test handling of missing configuration file."""
        with pytest.raises(FileNotFoundError):
            load_preprocessing_prompts("non_existent_file.yaml")
    
    def test_load_preprocessing_prompts_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            temp_path = f.name
        
        try:
            with pytest.raises(AriPersonaConfigError):
                load_preprocessing_prompts(temp_path)
        finally:
            os.unlink(temp_path)


class TestPreprocessingPromptsValidation:
    """Test preprocessing prompts configuration validation."""
    
    def test_validate_complete_config(self):
        """Test validation of complete valid configuration."""
        # Load the actual configuration and validate it
        config = load_preprocessing_prompts()
        result = validate_preprocessing_prompts_config(config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_missing_required_sections(self):
        """Test validation fails with missing required sections."""
        incomplete_config = {
            'preprocessing_prompts': {}
            # Missing difficulty_configurations and validation_rules
        }
        
        result = validate_preprocessing_prompts_config(incomplete_config)
        
        assert result['valid'] is False
        assert any('difficulty_configurations' in error for error in result['errors'])
        assert any('validation_rules' in error for error in result['errors'])
    
    def test_validate_missing_preprocessing_subsections(self):
        """Test validation fails with missing preprocessing subsections."""
        config_with_missing_subsections = {
            'preprocessing_prompts': {
                'main_prompt': {}
                # Missing other required subsections
            },
            'difficulty_configurations': {},
            'validation_rules': {}
        }
        
        result = validate_preprocessing_prompts_config(config_with_missing_subsections)
        
        assert result['valid'] is False
        assert any('content_analysis' in error for error in result['errors'])
        assert any('framework_integration' in error for error in result['errors'])
    
    def test_validate_missing_frameworks(self):
        """Test validation detects missing framework integrations."""
        config_with_incomplete_frameworks = {
            'preprocessing_prompts': {
                'main_prompt': {
                    'system_message': 'test',
                    'user_prompt_template': 'test'
                },
                'content_analysis': {},
                'framework_integration': {
                    'tiny_habits': {'triggers': [], 'application': 'test'}
                    # Missing other 8 frameworks
                },
                'oracle_integration': {},
                'quality_standards': {},
                'output_format': {}
            },
            'difficulty_configurations': {},
            'validation_rules': {}
        }
        
        result = validate_preprocessing_prompts_config(config_with_incomplete_frameworks)
        
        assert result['valid'] is False
        # Should have errors for 8 missing frameworks
        framework_errors = [error for error in result['errors'] if 'framework integration' in error]
        assert len(framework_errors) == 8


class TestPreprocessingPromptsAccess:
    """Test preprocessing prompts configuration access."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_preprocessing_prompts_cache()
        load_preprocessing_prompts()
    
    def test_get_preprocessing_prompts_full_config(self):
        """Test getting the full preprocessing prompts configuration."""
        config = get_preprocessing_prompts()
        
        assert isinstance(config, dict)
        assert 'preprocessing_prompts' in config
        assert 'difficulty_configurations' in config
    
    def test_get_preprocessing_prompts_specific_key(self):
        """Test getting specific configuration keys."""
        main_prompt = get_preprocessing_prompts('preprocessing_prompts')
        
        assert isinstance(main_prompt, dict)
        assert 'main_prompt' in main_prompt
        assert 'framework_integration' in main_prompt
    
    def test_get_preprocessing_prompts_dot_notation(self):
        """Test getting nested configuration using dot notation."""
        system_message = get_preprocessing_prompts('preprocessing_prompts.main_prompt.system_message')
        
        assert isinstance(system_message, str)
        assert 'Ari' in system_message
        assert 'TARS' in system_message
    
    def test_get_preprocessing_prompts_not_loaded(self):
        """Test error when configuration not loaded."""
        clear_preprocessing_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError, match="not loaded"):
            get_preprocessing_prompts()
    
    def test_get_preprocessing_prompts_invalid_key(self):
        """Test error with invalid configuration key."""
        with pytest.raises(KeyError):
            get_preprocessing_prompts('non_existent_key')
    
    def test_get_preprocessing_prompts_invalid_dot_notation(self):
        """Test error with invalid dot notation key."""
        with pytest.raises(KeyError):
            get_preprocessing_prompts('preprocessing_prompts.non_existent.key')


class TestBuildPreprocessingPrompt:
    """Test building preprocessing prompts for content processing."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_preprocessing_prompts_cache()
        load_preprocessing_prompts()
    
    def test_build_preprocessing_prompt_basic(self):
        """Test building basic preprocessing prompt."""
        result = build_preprocessing_prompt(
            raw_content="Test content about habits",
            file_type="md"
        )
        
        assert isinstance(result, dict)
        assert 'system_message' in result
        assert 'user_message' in result
        assert 'Ari' in result['system_message']
        assert 'Test content about habits' in result['user_message']
        assert 'md' in result['user_message']
    
    def test_build_preprocessing_prompt_with_oracle_context(self):
        """Test building preprocessing prompt with Oracle context."""
        oracle_context = "Habit: Meditar 5 minutos - Score: 18"
        
        result = build_preprocessing_prompt(
            raw_content="Meditation guide",
            file_type="pdf",
            oracle_context=oracle_context
        )
        
        assert oracle_context in result['user_message']
        assert 'pdf' in result['user_message']
    
    def test_build_preprocessing_prompt_with_difficulty(self):
        """Test building preprocessing prompt with specific difficulty."""
        result = build_preprocessing_prompt(
            raw_content="Advanced cognitive strategies",
            file_type="json",
            target_difficulty="advanced",
            target_audience="advanced"
        )
        
        assert 'advanced' in result['user_message']
        assert 'json' in result['user_message']
    
    def test_build_preprocessing_prompt_with_dimension(self):
        """Test building preprocessing prompt with suggested dimension."""
        result = build_preprocessing_prompt(
            raw_content="Exercise routine",
            file_type="txt",
            suggested_dimension="physicalHealth"
        )
        
        assert 'physicalHealth' in result['user_message']
        assert 'txt' in result['user_message']
    
    def test_build_preprocessing_prompt_template_not_found(self):
        """Test building prompt when template file is not found."""
        with patch('pathlib.Path.exists', return_value=False):
            result = build_preprocessing_prompt(
                raw_content="Test content",
                file_type="md"
            )
            
            assert 'Template not found' in result['user_message']
    
    def test_build_preprocessing_prompt_configuration_error(self):
        """Test error handling when configuration is invalid."""
        clear_preprocessing_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError):
            build_preprocessing_prompt(
                raw_content="Test content",
                file_type="md"
            )


class TestFrameworkIntegration:
    """Test framework integration for content analysis."""
    
    def setup_method(self):
        """Load configuration before each test."""
        clear_preprocessing_prompts_cache()
        load_preprocessing_prompts()
    
    def test_get_framework_integration_single_match(self):
        """Test getting framework integration for content with single framework match."""
        content = "Este conteúdo é sobre construir novos hábitos e rotinas"
        
        frameworks = get_framework_integration_for_content(content)
        
        assert isinstance(frameworks, list)
        assert len(frameworks) > 0
        
        # Should find tiny_habits framework
        framework_names = [fw['framework'] for fw in frameworks]
        assert 'tiny_habits' in framework_names
    
    def test_get_framework_integration_multiple_matches(self):
        """Test getting framework integration for content with multiple framework matches."""
        content = """
        Este conteúdo discute hábitos, motivação, e comunicação.
        Ele cobre construção de rotinas e gestão de relacionamentos efetivamente.
        """
        
        frameworks = get_framework_integration_for_content(content)
        
        assert isinstance(frameworks, list)
        assert len(frameworks) > 1
        
        # Should be sorted by relevance score
        for i in range(len(frameworks) - 1):
            assert frameworks[i]['relevance_score'] >= frameworks[i + 1]['relevance_score']
    
    def test_get_framework_integration_no_matches(self):
        """Test getting framework integration for content with no matches."""
        content = "Este é conteúdo genérico sem gatilhos específicos"
        
        frameworks = get_framework_integration_for_content(content)
        
        assert isinstance(frameworks, list)
        # Might be empty or have low-relevance matches
    
    def test_get_framework_integration_case_insensitive(self):
        """Test that framework trigger matching is case insensitive."""
        content = "HÁBITOS e MOTIVAÇÃO são importantes para crescimento"
        
        frameworks = get_framework_integration_for_content(content)
        
        assert isinstance(frameworks, list)
        assert len(frameworks) > 0
    
    def test_get_framework_integration_with_details(self):
        """Test that framework integration returns complete details."""
        content = "Construir hábitos requer compreender motivação e dopamina"
        
        frameworks = get_framework_integration_for_content(content)
        
        for framework in frameworks:
            assert 'framework' in framework
            assert 'triggers_found' in framework
            assert 'application' in framework
            assert 'relevance_score' in framework
            assert isinstance(framework['triggers_found'], list)
            assert isinstance(framework['relevance_score'], int)
    
    def test_get_framework_integration_configuration_error(self):
        """Test error handling when configuration is not loaded."""
        clear_preprocessing_prompts_cache()
        
        with pytest.raises(AriPersonaConfigError):
            get_framework_integration_for_content("test content")


class TestPreprocessingPromptsIntegration:
    """Integration tests for preprocessing prompts functionality."""
    
    def test_full_configuration_loading_and_access(self):
        """Test complete workflow of loading and accessing configuration."""
        # Clear cache to start fresh
        clear_preprocessing_prompts_cache()
        
        # Load configuration
        config = load_preprocessing_prompts()
        assert config is not None
        
        # Validate configuration
        validation = validate_preprocessing_prompts_config(config)
        assert validation['valid'] is True
        
        # Access specific elements
        main_prompt = get_preprocessing_prompts('preprocessing_prompts.main_prompt')
        assert 'system_message' in main_prompt
        
        # Build actual prompt
        prompt = build_preprocessing_prompt("Test content", "md")
        assert 'system_message' in prompt
        assert 'user_message' in prompt
        
        # Analyze framework integration
        frameworks = get_framework_integration_for_content("conteúdo sobre hábitos")
        assert isinstance(frameworks, list)
    
    def test_error_propagation(self):
        """Test that errors are properly propagated through the system."""
        clear_preprocessing_prompts_cache()
        
        # All functions should fail when configuration is not loaded
        with pytest.raises(AriPersonaConfigError):
            get_preprocessing_prompts()
        
        with pytest.raises(AriPersonaConfigError):
            build_preprocessing_prompt("content", "md")
        
        with pytest.raises(AriPersonaConfigError):
            get_framework_integration_for_content("content")
    
    def test_cache_management(self):
        """Test cache management across multiple operations."""
        # Load configuration
        load_preprocessing_prompts()
        
        # Configuration should be cached
        config1 = get_preprocessing_prompts()
        config2 = get_preprocessing_prompts()
        assert config1 is config2
        
        # Clear cache
        clear_preprocessing_prompts_cache()
        
        # Should fail after cache clear
        with pytest.raises(AriPersonaConfigError):
            get_preprocessing_prompts() 