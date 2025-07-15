"""
Tests for content analyzer module.

This module tests the ContentAnalyzer class and its integration with
OpenAI client and Stage 1 functions for comprehensive content analysis.
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

from src.lyfe_kt.content_analyzer import (
    ContentAnalyzer, 
    ContentAnalyzerError,
    get_content_analyzer,
    reset_content_analyzer
)
from src.lyfe_kt.openai_client import OpenAIClientError
from src.lyfe_kt.stage1_functions import Stage1ProcessingError


class TestContentAnalyzer:
    """Test cases for ContentAnalyzer class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Reset global instance
        reset_content_analyzer()
        
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
            }
        }
        
        # Sample processed data
        self.sample_processed_data = {
            "title": "Test Supertask",
            "language": "portuguese",
            "difficulty_level": "intermediate",
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
            ]
        }
        
        # Sample Ari analysis
        self.sample_ari_analysis = {
            "ari_readiness_score": 0.85,
            "coaching_opportunities": {
                "habit_formation": ["Tiny habit opportunities", "Behavioral triggers"],
                "behavioral_change": ["Motivation points", "Action triggers"],
                "motivation_points": ["Success stories", "Progress tracking"]
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
        }
        
        # Sample AI analysis
        self.sample_ai_analysis = {
            "basic_analysis": {
                "tone": "motivational",
                "themes": ["habits", "productivity", "self-improvement"],
                "complexity": "intermediate",
                "language": "pt",
                "key_concepts": ["hábitos", "produtividade", "mudança"],
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
        }
    
    def test_initialization_success(self):
        """Test successful ContentAnalyzer initialization."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                assert analyzer.config == self.config
                assert analyzer.enable_ai_analysis is True
                assert analyzer.batch_size == 5
                mock_client.assert_called_once()
    
    def test_initialization_with_config(self):
        """Test ContentAnalyzer initialization with provided config."""
        with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
            mock_client.return_value = Mock()
            
            analyzer = ContentAnalyzer(config=self.config)
            
            assert analyzer.config == self.config
            mock_client.assert_called_once()
    
    def test_initialization_failure(self):
        """Test ContentAnalyzer initialization failure."""
        with patch('src.lyfe_kt.content_analyzer.get_config', side_effect=Exception("Config error")):
            with pytest.raises(ContentAnalyzerError, match="Failed to initialize content analyzer"):
                ContentAnalyzer()
    
    def test_analyze_single_file_success(self):
        """Test successful single file analysis."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_raw_file') as mock_process:
                    with patch('src.lyfe_kt.content_analyzer.analyze_ari_persona_patterns') as mock_ari:
                        mock_client.return_value = Mock()
                        mock_process.return_value = self.sample_processed_data
                        mock_ari.return_value = self.sample_ari_analysis
                        
                        analyzer = ContentAnalyzer()
                        analyzer._perform_ai_analysis = Mock(return_value=self.sample_ai_analysis)
                        analyzer._integrate_analyses = Mock(return_value={"integrated": "data"})
                        analyzer._generate_ari_preparation_recommendations = Mock(return_value={"recommendations": "data"})
                        
                        result = analyzer.analyze_single_file("test.json")
                        
                        assert result["file_path"] == "test.json"
                        assert result["processed_data"] == self.sample_processed_data
                        assert result["ari_analysis"] == self.sample_ari_analysis
                        assert result["ai_analysis"] == self.sample_ai_analysis
                        assert "analysis_timestamp" in result
                        assert result["analyzer_version"] == "1.0.0"
                        
                        mock_process.assert_called_once_with("test.json")
                        mock_ari.assert_called_once()
    
    def test_analyze_single_file_without_ai(self):
        """Test single file analysis without AI analysis."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_raw_file') as mock_process:
                    with patch('src.lyfe_kt.content_analyzer.analyze_ari_persona_patterns') as mock_ari:
                        mock_client.return_value = Mock()
                        mock_process.return_value = self.sample_processed_data
                        mock_ari.return_value = self.sample_ari_analysis
                        
                        analyzer = ContentAnalyzer()
                        analyzer._integrate_analyses = Mock(return_value={"integrated": "data"})
                        analyzer._generate_ari_preparation_recommendations = Mock(return_value={"recommendations": "data"})
                        
                        result = analyzer.analyze_single_file("test.json", include_ai_analysis=False)
                        
                        assert result["ai_analysis"] == {}
                        mock_process.assert_called_once_with("test.json")
    
    def test_analyze_single_file_stage1_error(self):
        """Test single file analysis with Stage 1 processing error."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_raw_file') as mock_process:
                    mock_client.return_value = Mock()
                    mock_process.side_effect = Stage1ProcessingError("Processing failed")
                    
                    analyzer = ContentAnalyzer()
                    
                    with pytest.raises(ContentAnalyzerError, match="Analysis failed for test.json"):
                        analyzer.analyze_single_file("test.json")
    
    def test_analyze_single_file_openai_error(self):
        """Test single file analysis with OpenAI error."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_raw_file') as mock_process:
                    with patch('src.lyfe_kt.content_analyzer.analyze_ari_persona_patterns') as mock_ari:
                        mock_client.return_value = Mock()
                        mock_process.return_value = self.sample_processed_data
                        mock_ari.return_value = self.sample_ari_analysis
                        
                        analyzer = ContentAnalyzer()
                        analyzer._perform_ai_analysis = Mock(side_effect=OpenAIClientError("OpenAI failed"))
                        
                        with pytest.raises(ContentAnalyzerError, match="Analysis failed for test.json"):
                            analyzer.analyze_single_file("test.json")
    
    def test_analyze_directory_success(self):
        """Test successful directory analysis."""
        directory_results = {
            "total_files": 2,
            "successful": 2,
            "failed_count": 0,
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
            ],
            "ari_persona_analysis": [
                {"ari_analysis": self.sample_ari_analysis},
                {"ari_analysis": self.sample_ari_analysis}
            ],
            "ari_summary": {
                "average_ari_readiness": 0.8,
                "high_readiness_files": 2
            }
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_directory_with_ari_analysis') as mock_process:
                    mock_client.return_value = Mock()
                    mock_process.return_value = directory_results
                    
                    analyzer = ContentAnalyzer()
                    analyzer._enhance_directory_with_ai_analysis = Mock(return_value=directory_results)
                    analyzer._analyze_cross_file_patterns = Mock(return_value={"patterns": "data"})
                    analyzer._generate_comprehensive_ari_preparation = Mock(return_value={"comprehensive": "data"})
                    analyzer._create_analysis_summary = Mock(return_value={"summary": "data"})
                    
                    result = analyzer.analyze_directory("input_dir", "output_dir")
                    
                    assert result["input_directory"] == "input_dir"
                    assert result["output_directory"] == "output_dir"
                    assert result["directory_results"] == directory_results
                    assert "analysis_timestamp" in result
                    assert result["analyzer_version"] == "1.0.0"
                    
                    mock_process.assert_called_once_with("input_dir", "output_dir")
    
    def test_analyze_directory_without_ai(self):
        """Test directory analysis without AI analysis."""
        directory_results = {
            "total_files": 1,
            "successful": 1,
            "failed_count": 0,
            "processed": [],
            "ari_persona_analysis": []
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_directory_with_ari_analysis') as mock_process:
                    mock_client.return_value = Mock()
                    mock_process.return_value = directory_results
                    
                    analyzer = ContentAnalyzer()
                    analyzer._analyze_cross_file_patterns = Mock(return_value={"patterns": "data"})
                    analyzer._generate_comprehensive_ari_preparation = Mock(return_value={"comprehensive": "data"})
                    analyzer._create_analysis_summary = Mock(return_value={"summary": "data"})
                    
                    result = analyzer.analyze_directory("input_dir", "output_dir", include_ai_analysis=False)
                    
                    assert result["directory_results"] == directory_results
                    # AI analysis should not be called
                    assert not hasattr(analyzer, '_enhance_directory_with_ai_analysis_called')
    
    def test_analyze_directory_stage1_error(self):
        """Test directory analysis with Stage 1 processing error."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                with patch('src.lyfe_kt.content_analyzer.process_directory_with_ari_analysis') as mock_process:
                    mock_client.return_value = Mock()
                    mock_process.side_effect = Stage1ProcessingError("Directory processing failed")
                    
                    analyzer = ContentAnalyzer()
                    
                    with pytest.raises(ContentAnalyzerError, match="Directory analysis failed"):
                        analyzer.analyze_directory("input_dir", "output_dir")
    
    def test_perform_ai_analysis_success(self):
        """Test successful AI analysis."""
        content_items = [
            {"content": "Este é um teste sobre hábitos saudáveis."},
            {"content": "A persistência é importante para o sucesso."}
        ]
        quiz_items = [
            {"question": "Qual é a importância dos hábitos?"}
        ]
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_openai_client = Mock()
                mock_openai_client.analyze_content.return_value = self.sample_ai_analysis["basic_analysis"]
                mock_client.return_value = mock_openai_client
                
                analyzer = ContentAnalyzer()
                analyzer._enhance_with_ari_specific_analysis = Mock(return_value=self.sample_ai_analysis["ari_specific_analysis"])
                
                result = analyzer._perform_ai_analysis(content_items, quiz_items)
                
                assert result["basic_analysis"] == self.sample_ai_analysis["basic_analysis"]
                assert result["ari_specific_analysis"] == self.sample_ai_analysis["ari_specific_analysis"]
                assert result["content_items_count"] == 2
                assert result["quiz_items_count"] == 1
                assert result["content_length"] > 0
                
                mock_openai_client.analyze_content.assert_called_once()
    
    def test_perform_ai_analysis_no_content(self):
        """Test AI analysis with no content."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._perform_ai_analysis([], [])
                
                assert result["content_length"] == 0
                assert result["content_items_count"] == 0
                assert result["quiz_items_count"] == 0
                assert "No content available for AI analysis" in result["note"]
    
    def test_perform_ai_analysis_openai_error(self):
        """Test AI analysis with OpenAI error."""
        content_items = [{"content": "Test content"}]
        quiz_items = []
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_openai_client = Mock()
                mock_openai_client.analyze_content.side_effect = OpenAIClientError("API error")
                mock_client.return_value = mock_openai_client
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._perform_ai_analysis(content_items, quiz_items)
                
                assert "analysis_error" in result
                assert result["basic_analysis"]["tone"] == "neutral"  # Fallback values
    
    def test_enhance_with_ari_specific_analysis_success(self):
        """Test successful Ari-specific analysis enhancement."""
        content = "Este é um conteúdo sobre hábitos saudáveis e produtividade."
        basic_analysis = self.sample_ai_analysis["basic_analysis"]
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_openai_client = Mock()
                mock_openai_client.generate_completion.return_value = json.dumps(self.sample_ai_analysis["ari_specific_analysis"])
                mock_client.return_value = mock_openai_client
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._enhance_with_ari_specific_analysis(content, basic_analysis)
                
                assert result == self.sample_ai_analysis["ari_specific_analysis"]
                mock_openai_client.generate_completion.assert_called_once()
    
    def test_enhance_with_ari_specific_analysis_json_error(self):
        """Test Ari-specific analysis with JSON parsing error."""
        content = "Test content"
        basic_analysis = {}
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_openai_client = Mock()
                mock_openai_client.generate_completion.return_value = "Invalid JSON response"
                mock_client.return_value = mock_openai_client
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._enhance_with_ari_specific_analysis(content, basic_analysis)
                
                # Should return fallback values
                assert result["coaching_potential"] == "medium"
                assert "question_transformation_opportunities" in result
                assert "brevity_recommendations" in result
    
    def test_enhance_with_ari_specific_analysis_error(self):
        """Test Ari-specific analysis with general error."""
        content = "Test content"
        basic_analysis = {}
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_openai_client = Mock()
                mock_openai_client.generate_completion.side_effect = Exception("API error")
                mock_client.return_value = mock_openai_client
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._enhance_with_ari_specific_analysis(content, basic_analysis)
                
                # Should return fallback values with error
                assert result["coaching_potential"] == "medium"
                assert "analysis_error" in result
    
    def test_integrate_analyses_success(self):
        """Test successful analysis integration."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._integrate_analyses(
                    self.sample_processed_data,
                    self.sample_ari_analysis,
                    self.sample_ai_analysis
                )
                
                assert "stage1_insights" in result
                assert "ari_insights" in result
                assert "ai_insights" in result
                assert "integrated_insights" in result
                
                # Check stage1 insights
                stage1_insights = result["stage1_insights"]
                assert stage1_insights["title"] == "Test Supertask"
                assert stage1_insights["language"] == "portuguese"
                assert stage1_insights["content_count"] == 2
                assert stage1_insights["quiz_count"] == 1
                
                # Check ari insights
                ari_insights = result["ari_insights"]
                assert ari_insights["readiness_score"] == 0.85
                assert "coaching_opportunities" in ari_insights
                
                # Check ai insights
                ai_insights = result["ai_insights"]
                assert ai_insights["tone"] == "motivational"
                assert "themes" in ai_insights
    
    def test_integrate_analyses_error(self):
        """Test analysis integration with error."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                # Pass invalid data to trigger error
                result = analyzer._integrate_analyses(None, None, None)
                
                assert "integration_error" in result
                assert result["integrated_insights"] == {}
    
    def test_generate_ari_preparation_recommendations_success(self):
        """Test successful Ari preparation recommendations generation."""
        integrated_analysis = {
            "integrated_insights": {
                "content_quality_score": 0.8,
                "ari_integration_readiness": "high",
                "coaching_transformation_potential": "high",
                "framework_applicability": ["tiny_habits", "behavioral_design"],
                "content_enhancement_priorities": ["Enhance habit formation", "Apply coaching style"]
            },
            "ari_insights": self.sample_ari_analysis,
            "ai_insights": self.sample_ai_analysis["ari_specific_analysis"]
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._generate_ari_preparation_recommendations(integrated_analysis)
                
                assert "recommendations" in result
                assert "readiness_assessment" in result
                assert "transformation_potential" in result
                assert "implementation_complexity" in result
                
                recommendations = result["recommendations"]
                assert "voice_adaptation" in recommendations
                assert "coaching_enhancement" in recommendations
                assert "framework_integration" in recommendations
                assert "engagement_optimization" in recommendations
                assert "content_transformation" in recommendations
                assert "priority_actions" in recommendations
    
    def test_generate_ari_preparation_recommendations_error(self):
        """Test Ari preparation recommendations generation with error."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                # Pass invalid data to trigger error
                result = analyzer._generate_ari_preparation_recommendations(None)
                
                assert "generation_error" in result
                assert result["readiness_assessment"] == "medium"
                assert "recommendations" in result
    
    def test_helper_methods(self):
        """Test helper calculation methods."""
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                # Test content quality score calculation
                stage1_insights = {"content_count": 2, "quiz_count": 1}
                ari_insights = {"readiness_score": 0.8}
                ai_insights = {"complexity": "intermediate", "tone": "motivational"}
                
                quality_score = analyzer._calculate_content_quality_score(stage1_insights, ari_insights, ai_insights)
                assert 0.0 <= quality_score <= 1.0
                
                # Test Ari integration readiness assessment
                readiness = analyzer._assess_ari_integration_readiness(ari_insights, {"ari_coaching_potential": "high"})
                assert readiness in ["low", "medium", "high"]
                
                # Test coaching transformation potential
                coaching_potential = analyzer._assess_coaching_transformation_potential(
                    {"coaching_opportunities": {"habit_formation": ["test1", "test2"], "behavioral_change": ["test3"]}},
                    {}
                )
                assert coaching_potential in ["low", "medium", "high"]
                
                # Test framework applicability
                frameworks = analyzer._assess_framework_applicability(
                    {"framework_integration": {"tiny_habits": True, "behavioral_design": True, "perma_model": False}},
                    {}
                )
                assert isinstance(frameworks, list)
                assert len(frameworks) <= 3
    
    def test_cross_file_pattern_analysis(self):
        """Test cross-file pattern analysis."""
        enhanced_results = {
            "ari_persona_analysis": [
                {
                    "ari_analysis": {
                        "framework_integration": {"tiny_habits": True, "behavioral_design": True},
                        "coaching_opportunities": {"habit_formation": ["test1"], "behavioral_change": ["test2"]},
                        "language_patterns": {"cultural_context": "portuguese"}
                    }
                },
                {
                    "ari_analysis": {
                        "framework_integration": {"tiny_habits": True, "perma_model": True},
                        "coaching_opportunities": {"habit_formation": ["test3"], "motivation_points": ["test4"]},
                        "language_patterns": {"cultural_context": "portuguese"}
                    }
                }
            ],
            "ai_analysis": [
                {
                    "ai_analysis": {
                        "basic_analysis": {"tone": "motivational", "complexity": "intermediate"}
                    }
                },
                {
                    "ai_analysis": {
                        "basic_analysis": {"tone": "inspirational", "complexity": "intermediate"}
                    }
                }
            ]
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._analyze_cross_file_patterns(enhanced_results)
                
                assert "framework_patterns" in result
                assert "coaching_patterns" in result
                assert "language_patterns" in result
                assert "ai_patterns" in result
                assert "total_files_analyzed" in result
                assert "pattern_strength" in result
                
                # Check framework patterns
                framework_patterns = result["framework_patterns"]
                assert framework_patterns["tiny_habits"] == 2  # Found in both files
                assert framework_patterns["behavioral_design"] == 1  # Found in one file
                
                # Check coaching patterns
                coaching_patterns = result["coaching_patterns"]
                assert coaching_patterns["habit_formation"] == 2  # Found in both files
    
    def test_comprehensive_ari_preparation(self):
        """Test comprehensive Ari preparation generation."""
        enhanced_results = {
            "ari_summary": {
                "average_ari_readiness": 0.75,
                "high_readiness_files": 2
            }
        }
        
        cross_file_analysis = {
            "framework_patterns": {"tiny_habits": 2, "behavioral_design": 1},
            "coaching_patterns": {"habit_formation": 2, "behavioral_change": 1},
            "pattern_strength": "high"
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._generate_comprehensive_ari_preparation(enhanced_results, cross_file_analysis)
                
                assert "overall_readiness" in result
                assert "framework_integration_strategy" in result
                assert "coaching_transformation_plan" in result
                assert "voice_adaptation_guidelines" in result
                assert "content_enhancement_roadmap" in result
                assert "implementation_phases" in result
    
    def test_analysis_summary_creation(self):
        """Test analysis summary creation."""
        enhanced_results = {
            "total_files": 3,
            "successful": 2,
            "failed_count": 1,
            "ari_summary": {
                "average_ari_readiness": 0.7,
                "high_readiness_files": 1
            }
        }
        
        cross_file_analysis = {
            "framework_patterns": {"tiny_habits": 2, "behavioral_design": 1},
            "coaching_patterns": {"habit_formation": 2, "behavioral_change": 1},
            "pattern_strength": "medium"
        }
        
        comprehensive_ari_preparation = {
            "overall_readiness": "high",
            "implementation_phases": ["Phase 1", "Phase 2", "Phase 3"]
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=self.config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                result = analyzer._create_analysis_summary(enhanced_results, cross_file_analysis, comprehensive_ari_preparation)
                
                assert "processing_summary" in result
                assert "ari_readiness_summary" in result
                assert "pattern_summary" in result
                assert "recommendations_summary" in result
                
                # Check processing summary
                processing_summary = result["processing_summary"]
                assert processing_summary["total_files"] == 3
                assert processing_summary["successful_files"] == 2
                assert processing_summary["failed_files"] == 1
                assert abs(processing_summary["success_rate"] - 66.66666666666667) < 0.0001
                
                # Check pattern summary
                pattern_summary = result["pattern_summary"]
                assert "most_applicable_frameworks" in pattern_summary
                assert "most_common_coaching_opportunities" in pattern_summary


class TestContentAnalyzerGlobalFunctions:
    """Test cases for global content analyzer functions."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_content_analyzer()
    
    def test_get_content_analyzer_singleton(self):
        """Test that get_content_analyzer returns singleton instance."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True}
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer1 = get_content_analyzer()
                analyzer2 = get_content_analyzer()
                
                assert analyzer1 is analyzer2  # Same instance
                assert isinstance(analyzer1, ContentAnalyzer)
    
    def test_get_content_analyzer_with_config(self):
        """Test get_content_analyzer with provided config."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True}
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
            mock_client.return_value = Mock()
            
            analyzer = get_content_analyzer(config)
            
            assert isinstance(analyzer, ContentAnalyzer)
            assert analyzer.config == config
    
    def test_reset_content_analyzer(self):
        """Test reset_content_analyzer function."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True}
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer1 = get_content_analyzer()
                reset_content_analyzer()
                analyzer2 = get_content_analyzer()
                
                assert analyzer1 is not analyzer2  # Different instances after reset


class TestContentAnalyzerIntegration:
    """Integration tests for ContentAnalyzer."""
    
    def setup_method(self):
        """Set up test environment."""
        reset_content_analyzer()
    
    def test_full_single_file_analysis_integration(self):
        """Test full integration of single file analysis."""
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
            'processing': {'enable_ai_analysis': False}  # Disable AI for integration test
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            test_file = f.name
        
        try:
            with patch('src.lyfe_kt.content_analyzer.get_config', return_value=config):
                with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                    mock_client.return_value = Mock()
                    
                    analyzer = ContentAnalyzer()
                    
                    # This should work with actual Stage 1 functions
                    result = analyzer.analyze_single_file(test_file, include_ai_analysis=False)
                    
                    assert result["file_path"] == test_file
                    assert "processed_data" in result
                    assert "ari_analysis" in result
                    assert "integrated_analysis" in result
                    assert "ari_preparation" in result
                    assert "analysis_timestamp" in result
                    
        finally:
            os.unlink(test_file)
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        config = {
            'openai': {'api_key': 'test-key'},
            'processing': {'enable_ai_analysis': True}
        }
        
        with patch('src.lyfe_kt.content_analyzer.get_config', return_value=config):
            with patch('src.lyfe_kt.content_analyzer.get_openai_client') as mock_client:
                mock_client.return_value = Mock()
                
                analyzer = ContentAnalyzer()
                
                # Test with non-existent file
                with pytest.raises(ContentAnalyzerError):
                    analyzer.analyze_single_file("non_existent_file.json")
                
                # Test with non-existent directory
                with pytest.raises(ContentAnalyzerError):
                    analyzer.analyze_directory("non_existent_dir", "output_dir")


if __name__ == "__main__":
    pytest.main([__file__]) 