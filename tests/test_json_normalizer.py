"""
Tests for JSON normalizer module.

This module tests the JSONNormalizer class and its integration with
the content analyzer for template-compliant JSON normalization.
"""

import json
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lyfe_kt.json_normalizer import (
    JSONNormalizer, 
    JSONNormalizerError,
    get_json_normalizer,
    reset_json_normalizer
)
from src.lyfe_kt.content_analyzer import ContentAnalyzerError


class TestJSONNormalizer:
    """Test cases for JSONNormalizer class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Reset global instance
        reset_json_normalizer()
        
        # Sample configuration
        self.config = {
            'openai': {
                'api_key': 'test-key',
                'model': 'gpt-4',
                'max_tokens': 1000,
                'temperature': 0.7
            },
            'processing': {
                'enable_ai_analysis': True,
                'batch_size': 5,
                'retry_attempts': 3
            },
            'validation': {
                'content': {
                    'min_length': 50,
                    'max_length': 50000
                }
            }
        }
        
        # Sample content analyzer result
        self.sample_analyzer_result = {
            "file_path": "test.json",
            "processed_data": {
                "title": "Test Supertask",
                "description": "A test supertask about habits",
                "language": "portuguese",
                "difficulty_level": "intermediate",
                "archetype": "achiever",
                "dimension": "wellness",
                "content": [
                    {
                        "type": "text",
                        "content": "Este é um conteúdo de teste sobre hábitos saudáveis."
                    },
                    {
                        "type": "quote",
                        "content": "A persistência é o caminho do êxito.",
                        "author": "Charles Chaplin"
                    }
                ],
                "quiz": [
                    {
                        "question": "Qual é a importância dos hábitos?",
                        "options": ["Muito importante", "Pouco importante", "Irrelevante"],
                        "correct_answer": "Muito importante"
                    }
                ],
                "learning_objectives": [
                    "Understand the importance of habits",
                    "Learn to build sustainable routines"
                ],
                "metadata": {
                    "original_source": "test.json",
                    "processing_date": "2024-12-01"
                }
            },
            "ari_analysis": {
                "ari_readiness_score": 0.85,
                "coaching_opportunities": {
                    "habit_formation": ["Tiny habit opportunities"],
                    "behavioral_change": ["Motivation points"],
                    "motivation_points": ["Success stories"],
                    "action_triggers": ["Implementation triggers"]
                },
                "framework_integration": {
                    "tiny_habits": True,
                    "behavioral_design": True,
                    "huberman_protocols": False,
                    "perma_model": True
                },
                "engagement_patterns": {
                    "question_opportunities": ["Transform statements", "Add commitment questions"],
                    "brevity_potential": "high",
                    "progressive_engagement": "extended",
                    "coaching_moments": ["Habit formation", "Motivation", "Action planning"]
                },
                "language_patterns": {
                    "cultural_context": "portuguese",
                    "masculine_forms_needed": True
                }
            },
            "ai_analysis": {
                "basic_analysis": {
                    "tone": "motivational",
                    "themes": ["habits", "productivity", "wellness"],
                    "complexity": "intermediate",
                    "language": "pt",
                    "key_concepts": ["hábitos", "produtividade", "bem-estar"],
                    "estimated_reading_time": 3
                },
                "ari_specific_analysis": {
                    "coaching_potential": "high",
                    "question_transformation_opportunities": [
                        "Transform declarative statements into coaching questions",
                        "Add commitment questions"
                    ],
                    "brevity_recommendations": [
                        "Apply TARS-inspired conciseness",
                        "Use active voice"
                    ],
                    "framework_alignment": [
                        "Tiny Habits methodology applicable",
                        "Behavioral Design principles relevant"
                    ],
                    "engagement_progression": "extended"
                }
            },
            "integrated_analysis": {
                "integrated_insights": {
                    "content_quality_score": 0.8,
                    "ari_integration_readiness": "high",
                    "coaching_transformation_potential": "high",
                    "framework_applicability": ["tiny_habits", "behavioral_design"],
                    "content_enhancement_priorities": ["Enhance habit formation", "Apply coaching style"]
                }
            },
            "ari_preparation": {
                "recommendations": {
                    "voice_adaptation": ["Apply TARS-inspired brevity"],
                    "coaching_enhancement": ["Transform statements into questions", "Add commitment questions"],
                    "framework_integration": ["Integrate Tiny Habits methodology", "Apply Behavioral Design principles"],
                    "engagement_optimization": ["Leverage coaching moments", "Apply brevity improvements"],
                    "content_transformation": ["Enhance with coaching style"],
                    "priority_actions": ["Begin Ari persona integration", "Apply framework integration"]
                },
                "readiness_assessment": "high",
                "transformation_potential": "high",
                "implementation_complexity": "medium"
            },
            "analysis_timestamp": "2024-12-01T10:00:00",
            "analyzer_version": "1.0.0"
        }
    
    def test_initialization_success(self):
        """Test successful JSONNormalizer initialization."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                assert normalizer.config == self.config
                assert normalizer.min_content_length == 50
                assert normalizer.max_content_length == 50000
                mock_analyzer.assert_called_once()
    
    def test_initialization_with_config(self):
        """Test JSONNormalizer initialization with provided config."""
        with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
            mock_analyzer.return_value = Mock()
            
            normalizer = JSONNormalizer(config=self.config)
            
            assert normalizer.config == self.config
            mock_analyzer.assert_called_once_with(self.config)
    
    def test_initialization_failure(self):
        """Test JSONNormalizer initialization failure."""
        with patch('src.lyfe_kt.json_normalizer.get_config', side_effect=Exception("Config error")):
            with pytest.raises(JSONNormalizerError, match="Failed to initialize JSON normalizer"):
                JSONNormalizer()
    
    def test_normalize_single_file_success(self):
        """Test successful single file normalization."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_content_analyzer = Mock()
                mock_content_analyzer.analyze_single_file.return_value = self.sample_analyzer_result
                mock_analyzer.return_value = mock_content_analyzer
                
                normalizer = JSONNormalizer()
                
                result = normalizer.normalize_single_file("test.json")
                
                # Check preserved original structure (not template structure)
                assert "title" in result
                assert "archetype" in result
                assert "dimension" in result
                assert "relatedToType" in result
                assert "relatedToId" in result
                assert "estimatedDuration" in result
                assert "coinsReward" in result
                assert "flexibleItems" in result
                assert "metadata" in result
                
                # Check that flexibleItems are enhanced
                assert isinstance(result["flexibleItems"], list)
                if result["flexibleItems"]:
                    # Check for enhanced content in flexibleItems
                    for item in result["flexibleItems"]:
                        assert isinstance(item, dict)
                        # Enhanced items should have original fields plus enhancements
                        assert "type" in item
    
    def test_normalize_single_file_without_ai(self):
        """Test single file normalization without AI analysis."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_content_analyzer = Mock()
                mock_content_analyzer.analyze_single_file.return_value = self.sample_analyzer_result
                mock_analyzer.return_value = mock_content_analyzer
                
                normalizer = JSONNormalizer()
                
                result = normalizer.normalize_single_file("test.json", include_ai_analysis=False)
                
                # Check preserved original structure
                assert "title" in result
                assert "archetype" in result
                assert "dimension" in result
                assert "flexibleItems" in result
                assert "metadata" in result
                
                # Check that metadata contains normalization info
                assert "_processing_info" in result["metadata"]
                
                mock_content_analyzer.analyze_single_file.assert_called_once_with("test.json", False)
    
    def test_normalize_single_file_content_analyzer_error(self):
        """Test single file normalization with content analyzer error."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_content_analyzer = Mock()
                mock_content_analyzer.analyze_single_file.side_effect = ContentAnalyzerError("Analysis failed")
                mock_analyzer.return_value = mock_content_analyzer
                
                normalizer = JSONNormalizer()
                
                with pytest.raises(JSONNormalizerError, match="Content analysis failed for test.json"):
                    normalizer.normalize_single_file("test.json")
    
    def test_normalize_single_file_unexpected_error(self):
        """Test single file normalization with unexpected error."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_content_analyzer = Mock()
                mock_content_analyzer.analyze_single_file.side_effect = Exception("Unexpected error")
                mock_analyzer.return_value = mock_content_analyzer
                
                normalizer = JSONNormalizer()
                
                with pytest.raises(JSONNormalizerError, match="Unexpected error normalizing test.json"):
                    normalizer.normalize_single_file("test.json")
    
    def test_normalize_directory_success(self):
        """Test successful directory normalization."""
        directory_analysis = {
            "input_directory": "input_dir",
            "output_directory": "output_dir",
            "directory_results": {
                "processed": [
                    {
                        "input_file": "test1.json",
                        "output_file": "test1_processed.json",
                        "title": "Test 1",
                        "language": "portuguese"
                    },
                    {
                        "input_file": "test2.json",
                        "output_file": "test2_processed.json",
                        "title": "Test 2",
                        "language": "portuguese"
                    }
                ]
            }
        }
        
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_content_analyzer = Mock()
                mock_content_analyzer.analyze_directory.return_value = directory_analysis
                mock_analyzer.return_value = mock_content_analyzer
                
                normalizer = JSONNormalizer()
                
                # Mock normalize_single_file to avoid actual file operations
                with patch.object(normalizer, 'normalize_single_file') as mock_normalize:
                    mock_normalize.return_value = {
                        "title": "Test",
                        "language": "portuguese",
                        "description": "Test description",
                        "target_audience": "explorer",
                        "difficulty_level": "intermediate",
                        "learning_objectives": ["Learn", "Apply"],
                        "content": [],
                        "quiz": [],
                        "metadata": {}
                    }
                    
                    # Mock file saving
                    with patch.object(normalizer, '_save_normalized_file'):
                        result = normalizer.normalize_directory("input_dir", "output_dir")
                
                assert result["input_directory"] == "input_dir"
                assert result["output_directory"] == "output_dir"
                assert "directory_analysis" in result
                assert "normalized_files" in result
                assert "failed_files" in result
                assert "directory_summary" in result
                assert "normalization_timestamp" in result
                assert result["normalizer_version"] == "1.0.0"
                
                # Check that files were processed
                assert len(result["normalized_files"]) == 2
                assert len(result["failed_files"]) == 0
                
                mock_content_analyzer.analyze_directory.assert_called_once_with("input_dir", "output_dir", True)
    
    def test_normalize_directory_with_failures(self):
        """Test directory normalization with some failures."""
        directory_analysis = {
            "directory_results": {
                "processed": [
                    {
                        "input_file": "test1.json",
                        "output_file": "test1_processed.json",
                        "title": "Test 1",
                        "language": "portuguese"
                    },
                    {
                        "input_file": "test2.json",
                        "output_file": "test2_processed.json",
                        "title": "Test 2",
                        "language": "portuguese"
                    }
                ]
            }
        }
        
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_content_analyzer = Mock()
                mock_content_analyzer.analyze_directory.return_value = directory_analysis
                mock_analyzer.return_value = mock_content_analyzer
                
                normalizer = JSONNormalizer()
                
                # Mock normalize_single_file to fail for second file
                def mock_normalize_side_effect(file_path, *args, **kwargs):
                    if "test2" in file_path:
                        raise Exception("Normalization failed")
                    return {
                        "title": "Test",
                        "language": "portuguese",
                        "description": "Test description",
                        "target_audience": "explorer",
                        "difficulty_level": "intermediate",
                        "learning_objectives": ["Learn", "Apply"],
                        "content": [],
                        "quiz": [],
                        "metadata": {}
                    }
                
                with patch.object(normalizer, 'normalize_single_file', side_effect=mock_normalize_side_effect):
                    with patch.object(normalizer, '_save_normalized_file'):
                        result = normalizer.normalize_directory("input_dir", "output_dir")
                
                # Check that one file succeeded and one failed
                assert len(result["normalized_files"]) == 1
                assert len(result["failed_files"]) == 1
                assert result["failed_files"][0]["input_file"] == "test2.json"
    
    def test_create_template_compliant_structure(self):
        """Test template-compliant structure creation (now preserves original format)."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                result = normalizer._create_template_compliant_structure(
                    self.sample_analyzer_result["processed_data"],
                    self.sample_analyzer_result["ari_analysis"],
                    self.sample_analyzer_result["ai_analysis"],
                    self.sample_analyzer_result["integrated_analysis"],
                    self.sample_analyzer_result["ari_preparation"]
                )
                
                # Check preserved original structure fields
                required_fields = [
                    "title", "archetype", "dimension", "relatedToType",
                    "relatedToId", "estimatedDuration", "coinsReward", "flexibleItems", "metadata"
                ]
                
                for field in required_fields:
                    assert field in result, f"Missing required field: {field}"
                
                # Check that flexibleItems are enhanced
                assert isinstance(result["flexibleItems"], list)
                if result["flexibleItems"]:
                    # Check for enhanced content in flexibleItems
                    for item in result["flexibleItems"]:
                        assert isinstance(item, dict)
                        # Enhanced items should have original fields plus enhancements
                        assert "type" in item
    
    def test_generate_enhanced_description(self):
        """Test enhanced description generation."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                result = normalizer._generate_enhanced_description(
                    self.sample_analyzer_result["processed_data"],
                    self.sample_analyzer_result["ai_analysis"],
                    self.sample_analyzer_result["ari_analysis"]
                )
                
                assert isinstance(result, str)
                assert len(result) > 0
                assert "A test supertask about habits" in result
    
    def test_determine_target_audience(self):
        """Test target audience determination."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                result = normalizer._determine_target_audience(
                    self.sample_analyzer_result["processed_data"],
                    self.sample_analyzer_result["ari_analysis"],
                    self.sample_analyzer_result["integrated_analysis"]
                )
                
                assert result == "achiever"  # From processed_data
    
    def test_generate_enhanced_learning_objectives(self):
        """Test enhanced learning objectives generation."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                result = normalizer._generate_enhanced_learning_objectives(
                    self.sample_analyzer_result["processed_data"],
                    self.sample_analyzer_result["ari_analysis"],
                    self.sample_analyzer_result["ai_analysis"]
                )
                
                assert isinstance(result, list)
                assert len(result) >= 2
                assert len(result) <= 5
                assert all(isinstance(obj, str) for obj in result)
    
    def test_enhance_content_items(self):
        """Test content items enhancement."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                content_items = self.sample_analyzer_result["processed_data"]["content"]
                
                result = normalizer._enhance_content_items(
                    content_items,
                    self.sample_analyzer_result["ari_analysis"],
                    self.sample_analyzer_result["ari_preparation"]
                )
                
                assert isinstance(result, list)
                assert len(result) == len(content_items)
                
                # Check enhancements
                for item in result:
                    assert "ari_enhancement" in item
                    assert "brevity_suggestions" in item["ari_enhancement"]
                    assert "question_opportunities" in item["ari_enhancement"]
                    assert "coaching_moments" in item["ari_enhancement"]
    
    def test_enhance_quiz_items(self):
        """Test quiz items enhancement."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                quiz_items = self.sample_analyzer_result["processed_data"]["quiz"]
                
                result = normalizer._enhance_quiz_items(
                    quiz_items,
                    self.sample_analyzer_result["ari_analysis"],
                    self.sample_analyzer_result["ari_preparation"]
                )
                
                assert isinstance(result, list)
                assert len(result) == len(quiz_items)
                
                # Check enhancements
                for item in result:
                    assert "ari_coaching_style" in item
                    assert "coaching_style" in item["ari_coaching_style"]
                    assert "action_oriented" in item["ari_coaching_style"]
    
    def test_create_enhanced_metadata(self):
        """Test enhanced metadata creation."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                result = normalizer._create_enhanced_metadata(
                    self.sample_analyzer_result["processed_data"],
                    self.sample_analyzer_result["ari_analysis"],
                    self.sample_analyzer_result["ai_analysis"],
                    self.sample_analyzer_result["integrated_analysis"],
                    self.sample_analyzer_result["ari_preparation"]
                )
                
                assert isinstance(result, dict)
                assert "content_analysis" in result
                assert "content_statistics" in result
                assert "processing_info" in result
                assert "quality_metrics" in result
                
                # Check statistics
                stats = result["content_statistics"]
                assert "content_items_count" in stats
                assert "quiz_items_count" in stats
                assert "ari_readiness_score" in stats
    
    def test_validate_and_enhance_structure(self):
        """Test structure validation and enhancement."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                # Test with incomplete structure
                incomplete_structure = {
                    "title": "Test",
                    "description": "Test description"
                    # Missing required fields
                }
                
                result = normalizer._validate_and_enhance_structure(
                    incomplete_structure,
                    self.sample_analyzer_result
                )
                
                # Check that missing original format fields were added
                required_fields = [
                    "title", "archetype", "dimension", "relatedToType",
                    "relatedToId", "estimatedDuration", "coinsReward", "flexibleItems"
                ]
                
                for field in required_fields:
                    assert field in result, f"Missing required field: {field}"
                
                # Check that flexibleItems is a list
                assert isinstance(result["flexibleItems"], list)
    
    def test_helper_methods(self):
        """Test various helper methods."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                # Test coaching context generation
                coaching_opportunities = {
                    "habit_formation": ["test"],
                    "behavioral_change": ["test"],
                    "motivation_points": ["test"]
                }
                
                context = normalizer._generate_coaching_context(coaching_opportunities)
                assert isinstance(context, str)
                assert "habit" in context.lower()
                
                # Test theme context generation
                themes = ["habits", "productivity", "wellness"]
                theme_context = normalizer._generate_theme_context(themes)
                assert isinstance(theme_context, str)
                assert "habits" in theme_context
                
                # Test duration calculation
                content_items = [{"content": "Test content with some words"}]
                quiz_items = [{"question": "Test question"}]
                
                duration = normalizer._calculate_estimated_duration(content_items, quiz_items)
                assert isinstance(duration, int)
                assert duration >= 60  # Minimum duration
                
                # Test tags generation
                tags = normalizer._generate_tags(
                    self.sample_analyzer_result["ai_analysis"],
                    self.sample_analyzer_result["ari_analysis"]
                )
                assert isinstance(tags, list)
                assert len(tags) <= 10
    
    def test_file_operations(self):
        """Test file operations."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                # Test output path generation
                original_path = "/path/to/file.json"
                normalized_path = normalizer._generate_normalized_output_path(original_path, "normalized")
                assert "normalized" in normalized_path
                assert normalized_path.endswith(".json")
                
                # Test file saving with temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    temp_file = f.name
                
                try:
                    test_data = {"test": "data"}
                    normalizer._save_normalized_file(test_data, temp_file)
                    
                    # Verify file was saved correctly
                    with open(temp_file, 'r') as f:
                        loaded_data = json.load(f)
                    
                    assert loaded_data == test_data
                    
                finally:
                    os.unlink(temp_file)
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                # Test with invalid data
                invalid_data = None
                
                # These should not raise exceptions but return fallback values
                description = normalizer._generate_enhanced_description(
                    invalid_data, {}, {}
                )
                assert isinstance(description, str)
                
                audience = normalizer._determine_target_audience(
                    invalid_data, {}, {}
                )
                assert audience == "explorer"  # Default fallback
                
                objectives = normalizer._generate_enhanced_learning_objectives(
                    invalid_data, {}, {}
                )
                assert isinstance(objectives, list)
                assert len(objectives) >= 3


class TestJSONNormalizerGlobalFunctions:
    """Test cases for global JSON normalizer functions."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_json_normalizer()
    
    def test_get_json_normalizer_singleton(self):
        """Test that get_json_normalizer returns singleton instance."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True},
            'validation': {'content': {'min_length': 50}}
        }
        
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer1 = get_json_normalizer()
                normalizer2 = get_json_normalizer()
                
                assert normalizer1 is normalizer2  # Same instance
                assert isinstance(normalizer1, JSONNormalizer)
    
    def test_get_json_normalizer_with_config(self):
        """Test get_json_normalizer with provided config."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True},
            'validation': {'content': {'min_length': 50}}
        }
        
        with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
            mock_analyzer.return_value = Mock()
            
            normalizer = get_json_normalizer(config)
            
            assert isinstance(normalizer, JSONNormalizer)
            assert normalizer.config == config
    
    def test_reset_json_normalizer(self):
        """Test reset_json_normalizer function."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True},
            'validation': {'content': {'min_length': 50}}
        }
        
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer1 = get_json_normalizer()
                reset_json_normalizer()
                normalizer2 = get_json_normalizer()
                
                assert normalizer1 is not normalizer2  # Different instances after reset


class TestJSONNormalizerIntegration:
    """Integration tests for JSONNormalizer."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_json_normalizer()
    
    def test_full_normalization_integration(self):
        """Test full integration of normalization process."""
        # Create temporary test file
        test_data = {
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "Este é um teste sobre hábitos saudáveis."
                },
                {
                    "type": "quiz",
                    "question": "Qual é a importância dos hábitos?",
                    "options": ["Muito importante", "Pouco importante"],
                    "correctAnswer": "Muito importante"
                }
            ]
        }
        
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': False},  # Disable AI for integration test
            'validation': {'content': {'min_length': 50}}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            test_file = f.name
        
        try:
            with patch('src.lyfe_kt.json_normalizer.get_config', return_value=config):
                with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                    # Mock content analyzer to return realistic data
                    mock_content_analyzer = Mock()
                    mock_content_analyzer.analyze_single_file.return_value = {
                        "processed_data": {
                            "title": "Test Content",
                            "description": "Test description",
                            "language": "portuguese",
                            "difficulty_level": "intermediate",
                            "content": [{"type": "text", "content": "Test content"}],
                            "quiz": [{"question": "Test?", "options": ["Yes", "No"], "correct_answer": "Yes"}],
                            "learning_objectives": ["Learn", "Apply"],
                            "metadata": {}
                        },
                        "ari_analysis": {
                            "ari_readiness_score": 0.7,
                            "coaching_opportunities": {},
                            "framework_integration": {},
                            "engagement_patterns": {}
                        },
                        "ai_analysis": {
                            "basic_analysis": {
                                "tone": "neutral",
                                "themes": ["test"],
                                "complexity": "intermediate",
                                "key_concepts": ["test"]
                            },
                            "ari_specific_analysis": {}
                        },
                        "integrated_analysis": {
                            "integrated_insights": {
                                "content_quality_score": 0.6,
                                "ari_integration_readiness": "medium"
                            }
                        },
                        "ari_preparation": {
                            "recommendations": {},
                            "readiness_assessment": "medium"
                        }
                    }
                    mock_analyzer.return_value = mock_content_analyzer
                    
                    normalizer = JSONNormalizer()
                    
                    # This should work with actual integration
                    result = normalizer.normalize_single_file(test_file, include_ai_analysis=False)
                    
                    # Check preserved original structure
                    assert "title" in result
                    assert "archetype" in result
                    assert "dimension" in result
                    assert "flexibleItems" in result
                    assert "metadata" in result
                    
                    # Check that metadata contains normalization info
                    assert "_processing_info" in result["metadata"]
                    
                    # Check that normalization was successful
                    assert result["metadata"]["_processing_info"]["source_file"] == test_file
                    
        finally:
            os.unlink(test_file)
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True},
            'validation': {'content': {'min_length': 50}}
        }
        
        with patch('src.lyfe_kt.json_normalizer.get_config', return_value=config):
            with patch('src.lyfe_kt.json_normalizer.get_content_analyzer') as mock_analyzer:
                mock_analyzer.return_value = Mock()
                
                normalizer = JSONNormalizer()
                
                # Test with non-existent file
                with pytest.raises(JSONNormalizerError):
                    normalizer.normalize_single_file("non_existent_file.json")
                
                # Test with non-existent directory
                with pytest.raises(JSONNormalizerError):
                    normalizer.normalize_directory("non_existent_dir", "output_dir")


if __name__ == "__main__":
    pytest.main([__file__]) 