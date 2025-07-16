"""
Tests for Stage 3 Generation Pipeline module.

This module tests the Stage 3 generation pipeline that converts filled markdown
templates into supertask JSON files with exact test.json structure compliance.

Test Coverage:
1. TemplateProcessor: Template parsing and validation
2. JSONGenerator: AI-powered JSON generation
3. GenerationPipeline: Main orchestration and reporting
4. Global functions: Convenience functions
5. Error handling: Comprehensive error scenarios
6. Integration: End-to-end pipeline testing
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from lyfe_kt.stage3_generation import (
    TemplateProcessor,
    JSONGenerator,
    GenerationPipeline,
    create_generation_pipeline,
    generate_from_template,
    generate_from_directory,
    generate_generation_report,
    GenerationError
)


class TestTemplateProcessor:
    """Test template processing functionality."""
    
    @pytest.fixture
    def template_processor(self):
        """Create TemplateProcessor instance with mocked dependencies."""
        with patch('lyfe_kt.stage3_generation.load_generation_prompts') as mock_load:
            mock_load.return_value = {
                'generation_prompts': {
                    'main_prompt': {
                        'system_message': 'Test system message',
                        'user_prompt_template': 'Test user prompt'
                    }
                }
            }
            return TemplateProcessor()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_parse_template_success(self, template_processor, temp_dir):
        """Test successful template parsing."""
        # Create test template
        template_content = """---
title: "Test Habit Formation"
dimension: "physicalHealth"
archetype: "warrior"
difficulty: "beginner"
estimated_duration: 300
coins_reward: 50
---

# Test Habit Formation

## Content Section
This is the main educational content about habit formation.

## Quiz Section
1. What is the first step?
   a) Option A
   b) Option B
   c) Option C
   d) Option D

Correct: b) Option B
Explanation: This is the explanation.
"""
        
        template_file = Path(temp_dir) / "test_template.md"
        template_file.write_text(template_content)
        
        result = template_processor.parse_template(str(template_file))
        
        # Verify structure
        assert 'frontmatter' in result
        assert 'content' in result
        assert 'sections' in result
        assert 'metadata' in result
        assert 'file_path' in result
        assert 'file_name' in result
        
        # Verify frontmatter
        frontmatter = result['frontmatter']
        assert frontmatter['title'] == "Test Habit Formation"
        assert frontmatter['dimension'] == "physicalHealth"
        assert frontmatter['archetype'] == "warrior"
        assert frontmatter['difficulty'] == "beginner"
        assert frontmatter['estimated_duration'] == 300
        assert frontmatter['coins_reward'] == 50
        
        # Verify sections
        sections = result['sections']
        assert 'main_content' in sections
        assert 'quiz_items' in sections
        assert len(sections['main_content']) > 0
        assert len(sections['quiz_items']) > 0
    
    def test_parse_template_invalid_format(self, template_processor, temp_dir):
        """Test template parsing with invalid format."""
        # Create template without frontmatter
        template_content = """# Test Content
This is content without frontmatter."""
        
        template_file = Path(temp_dir) / "invalid_template.md"
        template_file.write_text(template_content)
        
        with pytest.raises(GenerationError, match="no frontmatter found"):
            template_processor.parse_template(str(template_file))
    
    def test_parse_template_invalid_yaml(self, template_processor, temp_dir):
        """Test template parsing with invalid YAML frontmatter."""
        # Create template with invalid YAML
        template_content = """---
title: "Test Title"
invalid_yaml: [unclosed array
---

# Test Content
"""
        
        template_file = Path(temp_dir) / "invalid_yaml_template.md"
        template_file.write_text(template_content)
        
        with pytest.raises(GenerationError, match="Failed to parse frontmatter"):
            template_processor.parse_template(str(template_file))
    
    def test_validate_template_success(self, template_processor):
        """Test successful template validation."""
        template_data = {
            'frontmatter': {
                'title': 'Test Title',
                'dimension': 'physicalHealth',
                'archetype': 'warrior',
                'difficulty': 'beginner',
                'estimated_duration': 300,
                'coins_reward': 50
            },
            'sections': {
                'main_content': ['Some content'],
                'quiz_items': ['Some quiz']
            }
        }
        
        result = template_processor.validate_template(template_data)
        assert result is True
    
    def test_validate_template_missing_fields(self, template_processor):
        """Test template validation with missing required fields."""
        template_data = {
            'frontmatter': {
                'title': 'Test Title',
                'dimension': 'physicalHealth'
                # Missing required fields
            },
            'sections': {
                'main_content': ['Some content']
            }
        }
        
        result = template_processor.validate_template(template_data)
        assert result is False
    
    def test_validate_template_invalid_dimension(self, template_processor):
        """Test template validation with invalid dimension."""
        template_data = {
            'frontmatter': {
                'title': 'Test Title',
                'dimension': 'invalid_dimension',
                'archetype': 'warrior',
                'difficulty': 'beginner',
                'estimated_duration': 300,
                'coins_reward': 50
            },
            'sections': {
                'main_content': ['Some content']
            }
        }
        
        result = template_processor.validate_template(template_data)
        assert result is False
    
    def test_validate_template_invalid_types(self, template_processor):
        """Test template validation with invalid field types."""
        template_data = {
            'frontmatter': {
                'title': 'Test Title',
                'dimension': 'physicalHealth',
                'archetype': 'warrior',
                'difficulty': 'beginner',
                'estimated_duration': 'not_a_number',  # Invalid type
                'coins_reward': 50
            },
            'sections': {
                'main_content': ['Some content']
            }
        }
        
        result = template_processor.validate_template(template_data)
        assert result is False


class TestJSONGenerator:
    """Test JSON generation functionality."""
    
    @pytest.fixture
    def json_generator(self):
        """Create JSONGenerator instance with mocked dependencies."""
        with patch('lyfe_kt.stage3_generation.get_openai_client') as mock_client, \
             patch('lyfe_kt.config_loader.load_generation_prompts') as mock_load, \
             patch('lyfe_kt.config_loader.build_generation_prompt') as mock_build, \
             patch('lyfe_kt.config_loader.get_generation_prompts') as mock_get:
            
            # Mock OpenAI client
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            # Mock generation prompts config
            mock_config = {
                'generation_prompts': {
                    'main_prompt': {
                        'system_message': 'Test system message',
                        'user_prompt_template': 'Test user prompt'
                    }
                }
            }
            mock_load.return_value = mock_config
            mock_get.return_value = mock_config
            
            # Mock build_generation_prompt
            mock_build.return_value = {
                'system_message': 'Test system message',
                'user_message': 'Test user message'
            }
            
            generator = JSONGenerator()
            generator.openai_client = mock_client_instance
            return generator
    
    def test_generate_supertask_success(self, json_generator):
        """Test successful supertask generation."""
        # Mock OpenAI response
        mock_json_response = {
            "title": "Test Habit Formation",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "test_habit",
            "estimatedDuration": 300,
            "coinsReward": 50,
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "Test content",
                    "author": "Ari"
                }
            ],
            "metadata": {}
        }
        
        json_generator.openai_client.generate_completion.return_value = json.dumps(mock_json_response)
        
        # Mock validation
        with patch.object(json_generator, 'validate_json_structure', return_value=True):
            template_data = {
                'content': 'Test content',
                'frontmatter': {'title': 'Test Title'},
                'metadata': {'source_file': 'test.md'},
                'file_name': 'test.md'
            }
            
            result = json_generator.generate_supertask(template_data, "beginner")
            
            # Verify structure
            assert result['title'] == "Test Habit Formation - Beginner"
            assert result['dimension'] == "physicalHealth"
            assert result['archetype'] == "warrior"
            assert 'metadata' in result
            assert result['metadata']['difficulty_level'] == "beginner"
            assert result['metadata']['ari_persona_applied'] is True
    
    def test_generate_supertask_invalid_json(self, json_generator):
        """Test supertask generation with invalid JSON response."""
        # Mock invalid JSON response
        json_generator.openai_client.generate_completion.return_value = "Invalid JSON response"
        
        template_data = {
            'content': 'Test content',
            'frontmatter': {'title': 'Test Title'},
            'metadata': {'source_file': 'test.md'},
            'file_name': 'test.md'
        }
        
        with pytest.raises(GenerationError, match="Failed to parse generated JSON"):
            json_generator.generate_supertask(template_data, "beginner")
    
    def test_generate_supertask_validation_failure(self, json_generator):
        """Test supertask generation with validation failure."""
        # Mock valid JSON but validation failure
        mock_json_response = {"title": "Test Title"}
        json_generator.openai_client.generate_completion.return_value = json.dumps(mock_json_response)
        
        # Mock validation failure
        with patch.object(json_generator, 'validate_json_structure', return_value=False):
            template_data = {
                'content': 'Test content',
                'frontmatter': {'title': 'Test Title'},
                'metadata': {'source_file': 'test.md'},
                'file_name': 'test.md'
            }
            
            with pytest.raises(GenerationError, match="does not match required structure"):
                json_generator.generate_supertask(template_data, "beginner")
    
    def test_generate_multiple_supertasks(self, json_generator):
        """Test generation of multiple supertasks."""
        # Mock successful generation for both difficulties
        mock_json_response = {
            "title": "Test Title",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "test_habit",
            "estimatedDuration": 300,
            "coinsReward": 50,
            "flexibleItems": [],
            "metadata": {}
        }
        
        json_generator.openai_client.generate_completion.return_value = json.dumps(mock_json_response)
        
        # Mock validation
        with patch.object(json_generator, 'validate_json_structure', return_value=True):
            template_data = {
                'content': 'Test content',
                'frontmatter': {'title': 'Test Title'},
                'metadata': {'source_file': 'test.md'},
                'file_name': 'test.md'
            }
            
            result = json_generator.generate_multiple_supertasks(template_data)
            
            # Verify both versions generated
            assert len(result) == 2
            assert result[0]['metadata']['difficulty_level'] == "beginner"
            assert result[1]['metadata']['difficulty_level'] == "advanced"
    
    def test_validate_json_structure_success(self, json_generator):
        """Test successful JSON structure validation."""
        with patch('lyfe_kt.stage3_generation.validate_generated_json_structure') as mock_validate:
            mock_validate.return_value = {'valid': True}
            
            json_data = {"title": "Test Title"}
            result = json_generator.validate_json_structure(json_data)
            
            assert result is True
            mock_validate.assert_called_once_with(json_data)
    
    def test_validate_json_structure_failure(self, json_generator):
        """Test JSON structure validation failure."""
        with patch('lyfe_kt.stage3_generation.validate_generated_json_structure') as mock_validate:
            mock_validate.return_value = {'valid': False, 'errors': ['Missing field']}
            
            json_data = {"title": "Test Title"}
            result = json_generator.validate_json_structure(json_data)
            
            assert result is False


class TestGenerationPipeline:
    """Test generation pipeline orchestration."""
    
    @pytest.fixture
    def generation_pipeline(self):
        """Create GenerationPipeline instance with mocked dependencies."""
        with patch('lyfe_kt.stage3_generation.get_config') as mock_config, \
             patch('lyfe_kt.stage3_generation.TemplateProcessor') as mock_template_processor, \
             patch('lyfe_kt.stage3_generation.JSONGenerator') as mock_json_generator:
            
            # Mock configuration
            mock_config.return_value = {
                'processing': {
                    'enable_validation': True,
                    'batch_size': 10
                }
            }
            
            # Mock components
            mock_template_processor_instance = Mock()
            mock_json_generator_instance = Mock()
            
            mock_template_processor.return_value = mock_template_processor_instance
            mock_json_generator.return_value = mock_json_generator_instance
            
            pipeline = GenerationPipeline()
            pipeline.template_processor = mock_template_processor_instance
            pipeline.json_generator = mock_json_generator_instance
            
            return pipeline
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_process_template_success(self, generation_pipeline, temp_dir):
        """Test successful template processing."""
        # Mock template processor
        template_data = {
            'frontmatter': {'title': 'Test Title'},
            'content': 'Test content',
            'metadata': {'source_file': 'test.md'},
            'file_name': 'test.md'
        }
        generation_pipeline.template_processor.parse_template.return_value = template_data
        generation_pipeline.template_processor.validate_template.return_value = True
        
        # Mock JSON generator
        mock_json = {
            'title': 'Test Title - Beginner',
            'metadata': {'difficulty_level': 'beginner'}
        }
        generation_pipeline.json_generator.generate_multiple_supertasks.return_value = [mock_json]
        
        # Create test template file
        template_file = Path(temp_dir) / "test_template.md"
        template_file.write_text("---\ntitle: Test\n---\n# Content")
        
        result = generation_pipeline.process_template(str(template_file), temp_dir)
        
        # Verify result structure
        assert result['status'] == 'success'
        assert result['input_template'] == str(template_file)
        assert result['output_directory'] == temp_dir
        assert 'generated_files' in result
        assert 'processing_time_seconds' in result
        assert result['generated_count'] == 1
        
        # Verify file was created
        output_files = result['generated_files']
        assert len(output_files) == 1
        assert Path(output_files[0]).exists()
    
    def test_process_template_validation_failure(self, generation_pipeline, temp_dir):
        """Test template processing with validation failure."""
        # Mock template processor with validation failure
        template_data = {'frontmatter': {}, 'content': 'Test content'}
        generation_pipeline.template_processor.parse_template.return_value = template_data
        generation_pipeline.template_processor.validate_template.return_value = False
        
        # Create test template file
        template_file = Path(temp_dir) / "test_template.md"
        template_file.write_text("---\ntitle: Test\n---\n# Content")
        
        with pytest.raises(GenerationError, match="Template validation failed"):
            generation_pipeline.process_template(str(template_file), temp_dir)
    
    def test_process_directory_success(self, generation_pipeline, temp_dir):
        """Test successful directory processing."""
        # Create test template files
        template1 = Path(temp_dir) / "template1.md"
        template2 = Path(temp_dir) / "template2.md"
        template1.write_text("---\ntitle: Test1\n---\n# Content1")
        template2.write_text("---\ntitle: Test2\n---\n# Content2")
        
        # Mock successful processing
        with patch.object(generation_pipeline, 'process_template') as mock_process:
            mock_process.return_value = {
                'status': 'success',
                'generated_files': ['output1.json'],
                'generated_count': 1,
                'processing_time_seconds': 1.0
            }
            
            result = generation_pipeline.process_directory(temp_dir, temp_dir)
            
            # Verify result structure
            assert result['status'] == 'completed'
            assert result['total_files'] == 2
            assert result['successful_files'] == 2
            assert result['failed_files'] == 0
            assert result['success_rate'] == 1.0
            assert 'processing_time_seconds' in result
            assert len(result['individual_results']) == 2
    
    def test_process_directory_mixed_results(self, generation_pipeline, temp_dir):
        """Test directory processing with mixed success/failure results."""
        # Create test template files
        template1 = Path(temp_dir) / "template1.md"
        template2 = Path(temp_dir) / "template2.md"
        template1.write_text("---\ntitle: Test1\n---\n# Content1")
        template2.write_text("---\ntitle: Test2\n---\n# Content2")
        
        # Mock mixed results
        with patch.object(generation_pipeline, 'process_template') as mock_process:
            def side_effect(template_path, output_dir, generate_both=True):
                if 'template1' in template_path:
                    return {
                        'status': 'success',
                        'generated_files': ['output1.json'],
                        'generated_count': 1,
                        'processing_time_seconds': 1.0
                    }
                else:
                    raise GenerationError("Processing failed")
            
            mock_process.side_effect = side_effect
            
            result = generation_pipeline.process_directory(temp_dir, temp_dir)
            
            # Verify mixed results
            assert result['status'] == 'completed'
            assert result['total_files'] == 2
            assert result['successful_files'] == 1
            assert result['failed_files'] == 1
            assert result['success_rate'] == 0.5
            assert len(result['failed_files_list']) == 1
    
    def test_process_directory_no_templates(self, generation_pipeline, temp_dir):
        """Test directory processing with no template files."""
        # Create non-template file
        non_template = Path(temp_dir) / "not_template.txt"
        non_template.write_text("This is not a template")
        
        with pytest.raises(GenerationError, match="No template files"):
            generation_pipeline.process_directory(temp_dir, temp_dir)
    
    def test_generate_report(self, generation_pipeline):
        """Test report generation."""
        results = {
            'input_directory': 'input/',
            'output_directory': 'output/',
            'total_files': 2,
            'successful_files': 1,
            'failed_files': 1,
            'success_rate': 0.5,
            'processing_time_seconds': 10.5,
            'successful_files_list': ['template1.md'],
            'failed_files_list': [{'file': 'template2.md', 'error': 'Test error'}],
            'individual_results': [
                {'status': 'success', 'generated_count': 2, 'processing_time_seconds': 5.0},
                {'status': 'error', 'error_message': 'Test error'}
            ],
            'generate_both_difficulties': True
        }
        
        report = generation_pipeline.generate_report(results)
        
        # Verify report content
        assert "# Stage 3 Generation Pipeline Report" in report
        assert "Total Files**: 2" in report
        assert "Successful**: 1" in report
        assert "Failed**: 1" in report
        assert "Success Rate**: 50.0%" in report
        assert "Processing Time**: 10.50 seconds" in report
        assert "✅ template1.md" in report
        assert "❌ template2.md" in report
        assert "Test error" in report


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def test_create_generation_pipeline(self):
        """Test generation pipeline creation."""
        with patch('lyfe_kt.stage3_generation.GenerationPipeline') as mock_pipeline:
            mock_instance = Mock()
            mock_pipeline.return_value = mock_instance
            
            result = create_generation_pipeline()
            
            assert result == mock_instance
            mock_pipeline.assert_called_once_with(None)
    
    def test_generate_from_template(self):
        """Test template generation function."""
        with patch('lyfe_kt.stage3_generation.create_generation_pipeline') as mock_create:
            mock_pipeline = Mock()
            mock_create.return_value = mock_pipeline
            
            mock_pipeline.process_template.return_value = {'status': 'success'}
            
            result = generate_from_template('template.md', 'output/', True)
            
            assert result == {'status': 'success'}
            mock_pipeline.process_template.assert_called_once_with('template.md', 'output/', True)
    
    def test_generate_from_directory(self):
        """Test directory generation function."""
        with patch('lyfe_kt.stage3_generation.create_generation_pipeline') as mock_create:
            mock_pipeline = Mock()
            mock_create.return_value = mock_pipeline
            
            mock_pipeline.process_directory.return_value = {'status': 'completed'}
            
            result = generate_from_directory('input/', 'output/', True)
            
            assert result == {'status': 'completed'}
            mock_pipeline.process_directory.assert_called_once_with('input/', 'output/', True)
    
    def test_generate_generation_report(self):
        """Test report generation function."""
        with patch('lyfe_kt.stage3_generation.create_generation_pipeline') as mock_create:
            mock_pipeline = Mock()
            mock_create.return_value = mock_pipeline
            
            mock_pipeline.generate_report.return_value = "Test report"
            
            result = generate_generation_report({'test': 'data'})
            
            assert result == "Test report"
            mock_pipeline.generate_report.assert_called_once_with({'test': 'data'})


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_generation_error_inheritance(self):
        """Test GenerationError exception inheritance."""
        error = GenerationError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_template_processor_initialization_error(self):
        """Test TemplateProcessor initialization error."""
        with patch('lyfe_kt.stage3_generation.load_generation_prompts') as mock_load:
            mock_load.side_effect = Exception("Config load failed")
            
            with pytest.raises(GenerationError, match="Failed to initialize template processor"):
                TemplateProcessor()
    
    def test_json_generator_initialization_error(self):
        """Test JSONGenerator initialization error."""
        with patch('lyfe_kt.stage3_generation.get_openai_client') as mock_client:
            mock_client.side_effect = Exception("Client init failed")
            
            with pytest.raises(GenerationError, match="Failed to initialize JSON generator"):
                JSONGenerator()
    
    def test_generation_pipeline_initialization_error(self):
        """Test GenerationPipeline initialization error."""
        with patch('lyfe_kt.stage3_generation.get_config') as mock_config:
            mock_config.side_effect = Exception("Config failed")
            
            with patch('lyfe_kt.stage3_generation.load_config') as mock_load:
                mock_load.side_effect = Exception("Load failed")
                
                with pytest.raises(GenerationError, match="Failed to initialize generation pipeline"):
                    GenerationPipeline()


class TestIntegrationScenarios:
    """Test integration scenarios with realistic workflows."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_end_to_end_template_processing(self, temp_dir):
        """Test complete end-to-end template processing."""
        # Create realistic template
        template_content = """---
title: "Morning Routine Habits"
dimension: "physicalHealth"
archetype: "warrior"
difficulty: "beginner"
estimated_duration: 300
coins_reward: 50
---

# Morning Routine Habits

## Content Section
Building a morning routine is essential for starting your day with intention and energy.

## Quiz Section
1. What is the most important aspect of a morning routine?
   a) Waking up early
   b) Consistency
   c) Complexity
   d) Duration

Correct: b) Consistency
Explanation: Consistency is key to forming lasting habits.
"""
        
        template_file = Path(temp_dir) / "morning_routine.md"
        template_file.write_text(template_content)
        
        # Mock all dependencies for integration test
        with patch('lyfe_kt.stage3_generation.load_generation_prompts') as mock_load_prompts, \
             patch('lyfe_kt.stage3_generation.get_openai_client') as mock_client, \
             patch('lyfe_kt.stage3_generation.build_generation_prompt') as mock_build, \
             patch('lyfe_kt.stage3_generation.validate_generated_json_structure') as mock_validate:
            
            # Mock generation prompts
            mock_load_prompts.return_value = {
                'generation_prompts': {
                    'main_prompt': {
                        'system_message': 'Test system message',
                        'user_prompt_template': 'Test user prompt'
                    }
                }
            }
            
            # Mock OpenAI client
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            # Mock successful JSON generation
            mock_json_response = {
                "title": "Morning Routine Habits - Beginner",
                "dimension": "physicalHealth",
                "archetype": "warrior",
                "relatedToType": "HABITBP",
                "relatedToId": "morning_routine",
                "estimatedDuration": 300,
                "coinsReward": 50,
                "flexibleItems": [
                    {
                        "type": "content",
                        "content": "Building a morning routine is essential for starting your day with intention and energy.",
                        "author": "Ari"
                    },
                    {
                        "type": "quiz",
                        "content": "What is the most important aspect of a morning routine?",
                        "options": [
                            "Waking up early",
                            "Consistency",
                            "Complexity",
                            "Duration"
                        ],
                        "correctAnswer": 1,
                        "explanation": "Consistency is key to forming lasting habits."
                    }
                ],
                "metadata": {}
            }
            
            mock_client_instance.generate_completion.return_value = json.dumps(mock_json_response)
            
            # Mock build_generation_prompt
            mock_build.return_value = {
                'system_message': 'Test system message',
                'user_message': 'Test user message'
            }
            
            # Mock validation
            mock_validate.return_value = {'valid': True}
            
            # Run end-to-end processing
            result = generate_from_template(str(template_file), temp_dir, True)
            
            # Verify successful processing
            assert result['status'] == 'success'
            assert result['generated_count'] == 2  # Both beginner and advanced
            assert len(result['generated_files']) == 2
            
            # Verify generated files exist
            for file_path in result['generated_files']:
                assert Path(file_path).exists()
                
                # Verify JSON structure
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                    assert 'title' in json_data
                    assert 'dimension' in json_data
                    assert 'flexibleItems' in json_data
                    assert 'metadata' in json_data
                    assert json_data['metadata']['ari_persona_applied'] is True 