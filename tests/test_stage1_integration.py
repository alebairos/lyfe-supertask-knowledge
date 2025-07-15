"""
Comprehensive tests for the Stage 1 integration module.

This test suite covers:
- Stage1Pipeline class initialization and configuration
- Single file processing with complete pipeline
- Directory processing with batch capabilities
- Error handling and recovery mechanisms
- Progress reporting and callback functionality
- Cross-file analysis and pattern recognition
- Validation summary and quality assessment
- Report generation and formatting
- Global convenience functions

The tests ensure the Stage 1 integration provides reliable
orchestration of all Stage 1 components with proper error handling
and comprehensive reporting capabilities.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from lyfe_kt.stage1_integration import (
    Stage1Pipeline,
    Stage1IntegrationError,
    create_stage1_pipeline,
    process_single_file_stage1,
    process_directory_stage1,
    generate_stage1_report
)
from lyfe_kt.config_loader import load_config


class TestStage1Pipeline:
    """Test the Stage1Pipeline class."""
    
    def setup_method(self):
        """Set up test configuration."""
        load_config()
    
    def test_pipeline_initialization(self):
        """Test Stage1Pipeline initialization."""
        pipeline = Stage1Pipeline()
        
        assert pipeline.config is not None
        assert pipeline.content_analyzer is not None
        assert pipeline.json_normalizer is not None
        assert pipeline.output_validator is not None
        assert pipeline.pipeline_config is not None
        assert pipeline.progress_callback is None
        assert pipeline.current_progress == 0
        assert pipeline.total_files == 0
        
        # Check default configuration
        assert pipeline.enable_ai_analysis is True
        assert pipeline.enable_validation is True
        assert pipeline.batch_size >= 1
    
    def test_pipeline_initialization_with_config(self):
        """Test pipeline initialization with custom config."""
        custom_config = {
            'processing': {
                'enable_ai_analysis': False,
                'enable_validation': False,
                'batch_size': 5
            }
        }
        
        pipeline = Stage1Pipeline(custom_config)
        
        assert pipeline.enable_ai_analysis is False
        assert pipeline.enable_validation is False
        assert pipeline.batch_size == 5
    
    def test_progress_callback_setting(self):
        """Test setting progress callback."""
        pipeline = Stage1Pipeline()
        
        callback = Mock()
        pipeline.set_progress_callback(callback)
        
        assert pipeline.progress_callback == callback
        
        # Test progress reporting
        pipeline._report_progress(5, 10, "Test message")
        
        assert pipeline.current_progress == 5
        assert pipeline.total_files == 10
        callback.assert_called_once_with(5, 10, "Test message")
    
    @patch('lyfe_kt.stage1_integration.ContentAnalyzer')
    @patch('lyfe_kt.stage1_integration.get_json_normalizer')
    @patch('lyfe_kt.stage1_integration.OutputValidator')
    def test_process_single_file_success(self, mock_validator, mock_normalizer, mock_analyzer):
        """Test successful single file processing."""
        # Mock components
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_single_file.return_value = {
            "analysis_summary": {"common_themes": ["test"]},
            "status": "success"
        }
        
        mock_normalizer_instance = Mock()
        mock_normalizer.return_value = mock_normalizer_instance
        mock_normalizer_instance.normalize_single_file.return_value = {
            "title": "Test Task",
            "content": [{"type": "text", "content": "Test content"}],
            "quiz": [{"question": "Test?", "options": ["A", "B"], "correct_answer": "A"}]
        }
        
        mock_validator_instance = Mock()
        mock_validator.return_value = mock_validator_instance
        
        # Mock validation result
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.score = 8.5
        mock_validation_result.metadata = {"quality_score": 8.5}
        
        with patch('lyfe_kt.stage1_integration.validate_output_file', return_value=mock_validation_result):
            pipeline = Stage1Pipeline()
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
                json.dump({"flexibleItems": [{"type": "content", "content": "Test"}]}, input_file)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
                output_path = output_file.name
            
            try:
                result = pipeline.process_single_file(input_path, output_path)
                
                assert result["status"] == "success"
                assert result["input_file"] == input_path
                assert result["output_file"] == output_path
                assert "processing_time_seconds" in result
                assert result["validation_passed"] is True
                assert result["quality_score"] == 8.5
                assert result["components_used"]["content_analyzer"] is True
                assert result["components_used"]["json_normalizer"] is True
                assert result["components_used"]["output_validator"] is True
                
                # Verify component calls
                mock_analyzer_instance.analyze_single_file.assert_called_once()
                mock_normalizer_instance.normalize_single_file.assert_called_once()
                
            finally:
                Path(input_path).unlink()
                Path(output_path).unlink()
    
    @patch('lyfe_kt.stage1_integration.ContentAnalyzer')
    def test_process_single_file_error_handling(self, mock_analyzer):
        """Test error handling in single file processing."""
        # Mock analyzer to raise error
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_single_file.side_effect = Exception("Test error")
        
        pipeline = Stage1Pipeline()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            json.dump({"flexibleItems": [{"type": "content", "content": "Test"}]}, input_file)
            input_path = input_file.name
        
        try:
            result = pipeline.process_single_file(input_path, "output.json")
            
            assert result["status"] == "error"
            assert result["error_type"] == "UnexpectedError"
            assert "Test error" in result["error_message"]
            assert "processing_time_seconds" in result
            
        finally:
            Path(input_path).unlink()
    
    @patch('lyfe_kt.stage1_integration.ContentAnalyzer')
    @patch('lyfe_kt.stage1_integration.get_json_normalizer')
    @patch('lyfe_kt.stage1_integration.OutputValidator')
    def test_process_directory_success(self, mock_validator, mock_normalizer, mock_analyzer):
        """Test successful directory processing."""
        # Mock components
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_single_file.return_value = {
            "analysis_summary": {
                "common_themes": ["test"],
                "primary_language": "portuguese",
                "average_difficulty": "intermediate",
                "primary_archetype": "achiever"
            },
            "status": "success"
        }
        
        mock_normalizer_instance = Mock()
        mock_normalizer.return_value = mock_normalizer_instance
        mock_normalizer_instance.normalize_single_file.return_value = {
            "title": "Test Task",
            "content": [{"type": "text", "content": "Test content"}],
            "quiz": [{"question": "Test?", "options": ["A", "B"], "correct_answer": "A"}]
        }
        
        mock_validator_instance = Mock()
        mock_validator.return_value = mock_validator_instance
        
        # Mock validation result
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.score = 8.5
        mock_validation_result.metadata = {"quality_score": 8.5}
        
        with patch('lyfe_kt.stage1_integration.validate_output_file', return_value=mock_validation_result):
            pipeline = Stage1Pipeline()
            
            # Create temporary directory with test files
            with tempfile.TemporaryDirectory() as temp_dir:
                input_dir = Path(temp_dir) / "input"
                output_dir = Path(temp_dir) / "output"
                input_dir.mkdir()
                output_dir.mkdir()
                
                # Create test JSON files
                for i in range(3):
                    test_file = input_dir / f"test_{i}.json"
                    with open(test_file, 'w') as f:
                        json.dump({
                            "flexibleItems": [{"type": "content", "content": f"Test content {i}"}]
                        }, f)
                
                result = pipeline.process_directory(str(input_dir), str(output_dir))
                
                assert result["status"] == "completed"
                assert result["statistics"]["total_files"] == 3
                assert result["statistics"]["successful_files"] == 3
                assert result["statistics"]["failed_files"] == 0
                assert result["statistics"]["success_rate"] == 1.0
                assert len(result["individual_results"]) == 3
                assert len(result["successful_files"]) == 3
                assert len(result["failed_files"]) == 0
                assert result["cross_file_analysis"]["status"] == "completed"
                assert result["validation_summary"]["status"] == "completed"
    
    def test_process_directory_no_files(self):
        """Test directory processing with no JSON files."""
        pipeline = Stage1Pipeline()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / "input"
            output_dir = Path(temp_dir) / "output"
            input_dir.mkdir()
            
            with pytest.raises(Stage1IntegrationError) as exc_info:
                pipeline.process_directory(str(input_dir), str(output_dir))
            
            assert "No JSON files found" in str(exc_info.value)
    
    def test_process_directory_missing_input(self):
        """Test directory processing with missing input directory."""
        pipeline = Stage1Pipeline()
        
        with pytest.raises(Stage1IntegrationError) as exc_info:
            pipeline.process_directory("nonexistent_dir", "output_dir")
        
        assert "Input directory not found" in str(exc_info.value)
    
    def test_cross_file_analysis(self):
        """Test cross-file analysis functionality."""
        pipeline = Stage1Pipeline()
        
        # Mock individual results
        individual_results = [
            {
                "status": "success",
                "analysis_result": {
                    "analysis_summary": {
                        "common_themes": ["habit", "routine"],
                        "primary_language": "portuguese",
                        "average_difficulty": "intermediate",
                        "primary_archetype": "achiever"
                    }
                }
            },
            {
                "status": "success",
                "analysis_result": {
                    "analysis_summary": {
                        "common_themes": ["motivation", "habit"],
                        "primary_language": "portuguese",
                        "average_difficulty": "beginner",
                        "primary_archetype": "nurturer"
                    }
                }
            }
        ]
        
        cross_analysis = pipeline._perform_cross_file_analysis(individual_results)
        
        assert cross_analysis["status"] == "completed"
        assert cross_analysis["files_analyzed"] == 2
        assert cross_analysis["dominant_patterns"]["language"] == "portuguese"
        assert "habit" in [theme[0] for theme in cross_analysis["dominant_patterns"]["themes"]]
        assert cross_analysis["ari_persona_insights"]["content_readiness"] == "medium"
        assert cross_analysis["ari_persona_insights"]["cultural_context"] == "portuguese"
    
    def test_validation_summary_creation(self):
        """Test validation summary creation."""
        pipeline = Stage1Pipeline()
        
        # Mock individual results with validation
        individual_results = [
            {
                "status": "success",
                "validation_passed": True,
                "quality_score": 8.5,
                "validation_result": {
                    "errors": [],
                    "warnings": ["Content is too short"],
                    "suggestions": ["Add more content variety"]
                }
            },
            {
                "status": "success",
                "validation_passed": False,
                "quality_score": 6.0,
                "validation_result": {
                    "errors": ["Missing required field"],
                    "warnings": ["Content is too short"],
                    "suggestions": ["Fix schema compliance"]
                }
            }
        ]
        
        validation_summary = pipeline._create_validation_summary(individual_results)
        
        assert validation_summary["status"] == "completed"
        assert validation_summary["total_files_validated"] == 2
        assert validation_summary["passed_validation"] == 1
        assert validation_summary["failed_validation"] == 1
        assert validation_summary["validation_success_rate"] == 0.5
        assert validation_summary["average_quality_score"] == 7.25
        assert validation_summary["quality_distribution"]["good"] == 1
        assert validation_summary["quality_distribution"]["fair"] == 1
        assert len(validation_summary["improvement_recommendations"]) > 0
    
    def test_report_generation(self):
        """Test processing report generation."""
        pipeline = Stage1Pipeline()
        
        # Mock results
        results = {
            "input_directory": "test_input",
            "output_directory": "test_output",
            "processing_time_seconds": 45.5,
            "statistics": {
                "total_files": 5,
                "successful_files": 4,
                "failed_files": 1,
                "success_rate": 0.8
            },
            "cross_file_analysis": {
                "status": "completed",
                "dominant_patterns": {
                    "language": "portuguese",
                    "difficulty": "intermediate",
                    "archetype": "achiever",
                    "themes": [("habit", 3), ("routine", 2)]
                }
            },
            "validation_summary": {
                "status": "completed",
                "total_files_validated": 4,
                "validation_success_rate": 0.75,
                "average_quality_score": 7.8,
                "quality_distribution": {
                    "excellent": 1,
                    "good": 2,
                    "fair": 1,
                    "poor": 0
                },
                "improvement_recommendations": ["Improve content quality"]
            },
            "failed_files": [
                {"file": "test.json", "error": "Processing failed"}
            ]
        }
        
        report = pipeline.generate_processing_report(results)
        
        assert "Stage 1 Processing Report" in report
        assert "Processing Summary" in report
        assert "Total Files: 5" in report
        assert "Successful: 4" in report
        assert "Failed: 1" in report
        assert "Success Rate: 80.0%" in report
        assert "Cross-File Analysis" in report
        assert "Dominant Language: portuguese" in report
        assert "Validation Summary" in report
        assert "Failed Files" in report
        assert "test.json: Processing failed" in report
        assert "Improvement Recommendations" in report
    
    def test_improvement_recommendations_generation(self):
        """Test improvement recommendations generation."""
        pipeline = Stage1Pipeline()
        
        error_frequency = {
            "Missing content field": 3,
            "Invalid quiz structure": 2,
            "Schema validation failed": 1
        }
        
        warning_frequency = {
            "Content is too short": 4,
            "Ari persona inconsistency": 2,
            "Learning objectives too brief": 1
        }
        
        recommendations = pipeline._generate_improvement_recommendations(
            error_frequency, warning_frequency
        )
        
        assert len(recommendations) > 0
        assert any("content quality" in rec.lower() for rec in recommendations)
        assert any("ari persona" in rec.lower() for rec in recommendations)
        assert any("structure compliance" in rec.lower() for rec in recommendations)


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def setup_method(self):
        """Set up test configuration."""
        load_config()
    
    def test_create_stage1_pipeline(self):
        """Test create_stage1_pipeline function."""
        pipeline = create_stage1_pipeline()
        
        assert isinstance(pipeline, Stage1Pipeline)
        assert pipeline.config is not None
    
    def test_create_stage1_pipeline_with_config(self):
        """Test create_stage1_pipeline with custom config."""
        custom_config = {
            'processing': {
                'enable_ai_analysis': False,
                'batch_size': 3
            }
        }
        
        pipeline = create_stage1_pipeline(custom_config)
        
        assert isinstance(pipeline, Stage1Pipeline)
        assert pipeline.enable_ai_analysis is False
        assert pipeline.batch_size == 3
    
    @patch('lyfe_kt.stage1_integration.Stage1Pipeline')
    def test_process_single_file_stage1(self, mock_pipeline_class):
        """Test process_single_file_stage1 function."""
        # Mock pipeline instance
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.process_single_file.return_value = {"status": "success"}
        
        # Mock progress callback
        progress_callback = Mock()
        
        result = process_single_file_stage1(
            "input.json",
            "output.json",
            include_ai_analysis=True,
            include_validation=True,
            progress_callback=progress_callback
        )
        
        assert result["status"] == "success"
        mock_pipeline.set_progress_callback.assert_called_once_with(progress_callback)
        mock_pipeline.process_single_file.assert_called_once_with(
            "input.json", "output.json", True, True
        )
    
    @patch('lyfe_kt.stage1_integration.Stage1Pipeline')
    def test_process_directory_stage1(self, mock_pipeline_class):
        """Test process_directory_stage1 function."""
        # Mock pipeline instance
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.process_directory.return_value = {"status": "completed"}
        
        # Mock progress callback
        progress_callback = Mock()
        
        result = process_directory_stage1(
            "input_dir",
            "output_dir",
            include_ai_analysis=False,
            include_validation=False,
            progress_callback=progress_callback
        )
        
        assert result["status"] == "completed"
        mock_pipeline.set_progress_callback.assert_called_once_with(progress_callback)
        mock_pipeline.process_directory.assert_called_once_with(
            "input_dir", "output_dir", False, False
        )
    
    @patch('lyfe_kt.stage1_integration.Stage1Pipeline')
    def test_generate_stage1_report(self, mock_pipeline_class):
        """Test generate_stage1_report function."""
        # Mock pipeline instance
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.generate_processing_report.return_value = "Test report"
        
        results = {"status": "completed"}
        
        report = generate_stage1_report(results)
        
        assert report == "Test report"
        mock_pipeline.generate_processing_report.assert_called_once_with(results)


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def setup_method(self):
        """Set up test configuration."""
        load_config()
    
    @patch('lyfe_kt.stage1_integration.ContentAnalyzer')
    def test_initialization_error(self, mock_analyzer):
        """Test initialization error handling."""
        mock_analyzer.side_effect = Exception("Initialization failed")
        
        with pytest.raises(Stage1IntegrationError) as exc_info:
            Stage1Pipeline()
        
        assert "Failed to initialize Stage 1 pipeline" in str(exc_info.value)
    
    def test_cross_file_analysis_error_handling(self):
        """Test cross-file analysis error handling."""
        pipeline = Stage1Pipeline()
        
        # Test with malformed results
        malformed_results = [{"invalid": "data"}]
        
        cross_analysis = pipeline._perform_cross_file_analysis(malformed_results)
        
        assert cross_analysis["status"] == "error"
        assert "error" in cross_analysis
    
    def test_validation_summary_error_handling(self):
        """Test validation summary error handling."""
        pipeline = Stage1Pipeline()
        
        # Test with malformed results
        malformed_results = [{"invalid": "data"}]
        
        validation_summary = pipeline._create_validation_summary(malformed_results)
        
        assert validation_summary["status"] == "no_validation_data"
        assert "status" in validation_summary
    
    def test_report_generation_error_handling(self):
        """Test report generation error handling."""
        pipeline = Stage1Pipeline()
        
        # Test with malformed results
        malformed_results = {"invalid": "data"}
        
        report = pipeline.generate_processing_report(malformed_results)
        
        # The method gracefully handles malformed data by using .get() with defaults
        # So it should generate a report even with malformed data
        assert "# Stage 1 Processing Report" in report
        assert "Processing Summary" in report


class TestIntegrationScenarios:
    """Test integration scenarios with real components."""
    
    def setup_method(self):
        """Set up test configuration."""
        load_config()
    
    def test_end_to_end_processing(self):
        """Test end-to-end processing with mocked components."""
        # This test would require actual component integration
        # For now, we'll test the basic flow
        
        pipeline = Stage1Pipeline()
        
        # Test that all components are properly initialized
        assert pipeline.content_analyzer is not None
        assert pipeline.json_normalizer is not None
        assert pipeline.output_validator is not None
        
        # Test configuration is properly loaded
        assert pipeline.config is not None
        assert pipeline.pipeline_config is not None
    
    def test_progress_reporting_integration(self):
        """Test progress reporting integration."""
        pipeline = Stage1Pipeline()
        
        progress_calls = []
        
        def progress_callback(current, total, message):
            progress_calls.append((current, total, message))
        
        pipeline.set_progress_callback(progress_callback)
        
        # Test progress reporting
        pipeline._report_progress(1, 5, "Step 1")
        pipeline._report_progress(2, 5, "Step 2")
        
        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 5, "Step 1")
        assert progress_calls[1] == (2, 5, "Step 2")
        assert pipeline.current_progress == 2
        assert pipeline.total_files == 5 