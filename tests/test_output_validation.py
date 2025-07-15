"""
Comprehensive tests for the output validation system.

This test suite covers:
- OutputValidator class initialization and configuration
- Schema validation against template requirements
- Content quality assessment and scoring
- Ari persona consistency validation
- Learning objective alignment verification
- Quiz quality and difficulty validation
- Metadata completeness and accuracy checks
- Platform integration compatibility validation
- Batch validation for multiple files
- Validation reporting and error handling
- Global convenience functions

The tests ensure the output validation system provides comprehensive
quality gates for generated knowledge tasks before platform integration.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from lyfe_kt.output_validation import (
    OutputValidator, 
    ValidationResult, 
    OutputValidationError,
    validate_output_file,
    validate_output_directory,
    generate_validation_report
)
from lyfe_kt.config_loader import load_config


class TestOutputValidator:
    """Test the OutputValidator class."""
    
    def setup_method(self):
        """Set up test configuration."""
        load_config()
    
    def test_validator_initialization(self):
        """Test OutputValidator initialization."""
        validator = OutputValidator()
        
        assert validator.config is not None
        assert validator.validation_config is not None
        assert validator.output_config is not None
        assert validator.content_config is not None
        assert validator.schema is not None
        assert validator.quality_thresholds is not None
        assert hasattr(validator, 'openai_client')
        
        # Check quality thresholds
        assert validator.quality_thresholds['minimum_score'] == 7.0
        assert validator.quality_thresholds['content_length_min'] >= 50
        assert validator.quality_thresholds['learning_objectives_min'] == 3
        assert validator.quality_thresholds['quiz_items_min'] == 3
    
    def test_schema_loading(self):
        """Test validation schema loading."""
        validator = OutputValidator()
        schema = validator.schema
        
        assert schema['type'] == 'object'
        assert 'required' in schema
        assert 'properties' in schema
        
        # Check required fields
        required_fields = schema['required']
        expected_fields = [
            'title', 'description', 'target_audience', 'difficulty_level',
            'learning_objectives', 'language', 'content', 'quiz', 'metadata'
        ]
        
        for field in expected_fields:
            assert field in required_fields
        
        # Check properties structure
        properties = schema['properties']
        assert 'title' in properties
        assert 'content' in properties
        assert 'quiz' in properties
        assert 'metadata' in properties
    
    def test_valid_output_validation(self):
        """Test validation of valid output."""
        validator = OutputValidator()
        
        valid_data = {
            "title": "Test Knowledge Task",
            "description": "This is a comprehensive test knowledge task for validation testing purposes.",
            "target_audience": "intermediate learners",
            "difficulty_level": "intermediate",
            "learning_objectives": [
                "Compreender os conceitos fundamentais",
                "Aplicar as técnicas aprendidas na prática",
                "Avaliar os resultados obtidos"
            ],
            "language": "pt",
            "content": [
                {
                    "type": "text",
                    "content": "Este é o conteúdo principal da tarefa de conhecimento."
                },
                {
                    "type": "list",
                    "content": "Item 1\nItem 2\nItem 3"
                }
            ],
            "quiz": [
                {
                    "question": "Qual é o conceito principal?",
                    "options": ["Opção A", "Opção B", "Opção C"],
                    "correct_answer": "Opção A"
                },
                {
                    "question": "Como aplicar na prática?",
                    "options": ["Método 1", "Método 2", "Método 3"],
                    "correct_answer": "Método 1"
                },
                {
                    "question": "Qual é o resultado esperado?",
                    "options": ["Resultado A", "Resultado B", "Resultado C"],
                    "correct_answer": "Resultado A"
                }
            ],
            "metadata": {
                "dimension": "wellness",
                "archetype": "achiever",
                "estimated_duration": 300,
                "tags": ["test", "validation"]
            }
        }
        
        result = validator.validate_single_output(valid_data, "test.json")
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert result.score >= 7.0
        assert len(result.errors) == 0
        assert result.metadata['schema_compliance'] is True
        assert result.metadata['quality_threshold_met'] is True
    
    def test_invalid_output_validation(self):
        """Test validation of invalid output."""
        validator = OutputValidator()
        
        invalid_data = {
            "title": "Test",  # Too short
            "description": "Short",  # Too short
            "target_audience": "beginners",
            "difficulty_level": "invalid_level",  # Invalid enum
            "learning_objectives": ["Too short"],  # Too few and too short
            "language": "pt",
            "content": [],  # Empty content
            "quiz": [],  # Empty quiz
            "metadata": {
                "dimension": "invalid_dimension",  # Invalid dimension
                "archetype": "achiever",
                "estimated_duration": 30  # Too short
            }
        }
        
        result = validator.validate_single_output(invalid_data, "test.json")
        
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert result.score < 7.0
        assert len(result.errors) > 0
        assert result.metadata['schema_compliance'] is False
    
    def test_schema_validation(self):
        """Test schema validation functionality."""
        validator = OutputValidator()
        
        # Test missing required fields
        data_missing_fields = {"title": "Test"}
        errors = validator._validate_schema(data_missing_fields)
        
        assert len(errors) > 0
        assert any("Missing required field" in error for error in errors)
        
        # Test invalid field types
        data_invalid_types = {
            "title": 123,  # Should be string
            "description": "Valid description for testing purposes",
            "target_audience": "beginners",
            "difficulty_level": "beginner",
            "learning_objectives": "Should be array",  # Should be array
            "language": "pt",
            "content": "Should be array",  # Should be array
            "quiz": "Should be array",  # Should be array
            "metadata": "Should be object"  # Should be object
        }
        
        errors = validator._validate_schema(data_invalid_types)
        assert len(errors) > 0
        assert any("must be a string" in error for error in errors)
        assert any("must be an array" in error for error in errors)
        assert any("must be an object" in error for error in errors)
    
    def test_content_quality_validation(self):
        """Test content quality validation."""
        validator = OutputValidator()
        
        # Test high-quality content
        high_quality_data = {
            "title": "Comprehensive Knowledge Task on Wellness",
            "description": "This is a detailed and comprehensive knowledge task that covers all aspects of wellness and personal development.",
            "content": [
                {
                    "type": "text",
                    "content": "Este é um conteúdo abrangente que explica conceitos importantes de bem-estar e desenvolvimento pessoal."
                },
                {
                    "type": "list",
                    "content": "Ponto importante 1\nPonto importante 2\nPonto importante 3"
                },
                {
                    "type": "quote",
                    "content": "Uma citação inspiradora sobre crescimento pessoal."
                }
            ]
        }
        
        score, warnings, suggestions = validator._validate_content_quality(high_quality_data)
        
        assert score >= 7.0
        assert len(warnings) == 0
        assert len(suggestions) <= 2
        
        # Test low-quality content
        low_quality_data = {
            "title": "Test",
            "description": "Short",
            "content": [
                {
                    "type": "text",
                    "content": "Short content"
                }
            ]
        }
        
        score, warnings, suggestions = validator._validate_content_quality(low_quality_data)
        
        assert score < 7.0
        assert len(warnings) > 0
        assert any("too short" in warning.lower() for warning in warnings)
    
    def test_ari_persona_validation(self):
        """Test Ari persona consistency validation."""
        validator = OutputValidator()
        
        # Test content with good Ari persona
        good_persona_data = {
            "title": "Desenvolvendo Hábitos Saudáveis com Ari",
            "description": "Seu treinador Ari vai te ajudar a desenvolver hábitos saudáveis através de pequenos passos.",
            "content": [
                {
                    "type": "text",
                    "content": "Vamos começar juntos essa jornada de transformação. Você pode conseguir através de pequenos passos."
                }
            ],
            "quiz": [
                {
                    "question": "Como podemos começar a mudança?",
                    "options": ["Pequenos passos", "Grandes mudanças", "Esperar o momento certo"],
                    "correct_answer": "Pequenos passos"
                }
            ]
        }
        
        warnings, suggestions = validator._validate_ari_persona(good_persona_data)
        
        assert len(warnings) == 0
        assert len(suggestions) <= 1
        
        # Test content with potential issues
        problematic_data = {
            "title": "Test with Aria",  # Feminine form
            "description": "Ela é sua treinadora.",  # Feminine reference
            "content": [
                {
                    "type": "text",
                    "content": "This is a very long sentence that goes on and on without any breaks or pauses and doesn't follow the TARS-inspired brevity principles that should be maintained."
                }
            ]
        }
        
        warnings, suggestions = validator._validate_ari_persona(problematic_data)
        
        assert len(warnings) > 0 or len(suggestions) > 0
    
    def test_learning_objectives_validation(self):
        """Test learning objectives validation."""
        validator = OutputValidator()
        
        # Test good learning objectives
        good_objectives_data = {
            "learning_objectives": [
                "Identificar os principais conceitos de bem-estar",
                "Aplicar técnicas de mindfulness no dia a dia",
                "Desenvolver hábitos saudáveis de forma sustentável",
                "Avaliar o progresso pessoal regularmente"
            ]
        }
        
        warnings, suggestions = validator._validate_learning_objectives(good_objectives_data)
        
        assert len(warnings) == 0
        assert len(suggestions) <= 1
        
        # Test problematic objectives
        bad_objectives_data = {
            "learning_objectives": [
                "Saber",  # Too short
                "Entender coisas"  # Too vague, no action verb
            ]
        }
        
        warnings, suggestions = validator._validate_learning_objectives(bad_objectives_data)
        
        assert len(warnings) > 0
        assert any("too brief" in warning.lower() for warning in warnings)
    
    def test_quiz_quality_validation(self):
        """Test quiz quality validation."""
        validator = OutputValidator()
        
        # Test good quiz
        good_quiz_data = {
            "quiz": [
                {
                    "question": "Qual é a melhor forma de desenvolver hábitos?",
                    "options": ["Pequenos passos", "Grandes mudanças", "Força de vontade"],
                    "correct_answer": "Pequenos passos"
                },
                {
                    "question": "Como manter a motivação?",
                    "options": ["Celebrar pequenas vitórias", "Ignorar falhas", "Ser muito crítico"],
                    "correct_answer": "Celebrar pequenas vitórias"
                },
                {
                    "question": "Por que a consistência é importante?",
                    "options": ["Cria neuroplasticidade", "É mais fácil", "Todo mundo faz"],
                    "correct_answer": "Cria neuroplasticidade"
                }
            ]
        }
        
        warnings, suggestions = validator._validate_quiz_quality(good_quiz_data)
        
        assert len(warnings) == 0
        assert len(suggestions) <= 2
        
        # Test problematic quiz
        bad_quiz_data = {
            "quiz": [
                {
                    "question": "Test",  # Too short
                    "options": ["A"],  # Too few options
                    "correct_answer": "B"  # Not in options
                },
                {
                    "question": "Another test question",
                    "options": ["Option 1", "Option 1", "Option 2"],  # Duplicate options
                    "correct_answer": "Option 1"
                }
            ]
        }
        
        warnings, suggestions = validator._validate_quiz_quality(bad_quiz_data)
        
        assert len(warnings) > 0
        assert any("too short" in warning.lower() for warning in warnings)
        assert any("duplicate" in warning.lower() for warning in warnings)
    
    def test_metadata_validation(self):
        """Test metadata validation."""
        validator = OutputValidator()
        
        # Test good metadata
        good_metadata_data = {
            "metadata": {
                "dimension": "wellness",
                "archetype": "achiever",
                "estimated_duration": 300,
                "tags": ["wellness", "habits"],
                "difficulty_score": 5
            }
        }
        
        warnings, suggestions = validator._validate_metadata(good_metadata_data)
        
        assert len(warnings) == 0
        assert len(suggestions) <= 1
        
        # Test problematic metadata
        bad_metadata_data = {
            "metadata": {
                "dimension": "invalid_dimension",
                "archetype": "invalid_archetype",
                "estimated_duration": 30  # Too short
            }
        }
        
        warnings, suggestions = validator._validate_metadata(bad_metadata_data)
        
        assert len(warnings) > 0
        assert any("invalid dimension" in warning.lower() for warning in warnings)
        assert any("invalid archetype" in warning.lower() for warning in warnings)
    
    def test_platform_compatibility_validation(self):
        """Test platform compatibility validation."""
        validator = OutputValidator()
        
        # Test compatible content
        compatible_data = {
            "language": "pt",
            "content": [
                {
                    "type": "text",
                    "content": "Conteúdo compatível com a plataforma"
                },
                {
                    "type": "list",
                    "content": "Item 1\nItem 2"
                }
            ]
        }
        
        warnings, suggestions = validator._validate_platform_compatibility(compatible_data)
        
        assert len(warnings) == 0
        assert len(suggestions) <= 1
        
        # Test incompatible content
        incompatible_data = {
            "language": "en",  # Should be Portuguese
            "content": [
                {
                    "type": "unsupported_type",
                    "content": "Content with unsupported type"
                },
                {
                    "type": "text",
                    "content": "Check this link: http://example.com"
                }
            ]
        }
        
        warnings, suggestions = validator._validate_platform_compatibility(incompatible_data)
        
        assert len(warnings) > 0
        assert any("portuguese" in warning.lower() for warning in warnings)
    
    def test_batch_validation(self):
        """Test batch validation functionality."""
        validator = OutputValidator()
        
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create valid JSON file
            valid_data = {
                "title": "Valid Knowledge Task",
                "description": "This is a valid knowledge task for testing batch validation.",
                "target_audience": "intermediate learners",
                "difficulty_level": "intermediate",
                "learning_objectives": [
                    "Compreender conceitos básicos",
                    "Aplicar conhecimentos na prática",
                    "Avaliar resultados obtidos"
                ],
                "language": "pt",
                "content": [
                    {
                        "type": "text",
                        "content": "Este é um conteúdo válido e abrangente para teste de validação que contém informações suficientes para atender aos requisitos mínimos de qualidade."
                    },
                    {
                        "type": "list",
                        "content": "Ponto importante 1\nPonto importante 2\nPonto importante 3"
                    }
                ],
                "quiz": [
                    {
                        "question": "Qual é o conceito principal abordado neste conteúdo?",
                        "options": ["Conceito A", "Conceito B", "Conceito C"],
                        "correct_answer": "Conceito A"
                    },
                    {
                        "question": "Como aplicar os conhecimentos na prática diária?",
                        "options": ["Método 1", "Método 2", "Método 3"],
                        "correct_answer": "Método 1"
                    },
                    {
                        "question": "Qual resultado esperado após aplicar as técnicas?",
                        "options": ["Resultado A", "Resultado B", "Resultado C"],
                        "correct_answer": "Resultado A"
                    }
                ],
                "metadata": {
                    "dimension": "wellness",
                    "archetype": "achiever",
                    "estimated_duration": 300
                }
            }
            
            valid_file = temp_path / "valid.json"
            with open(valid_file, 'w', encoding='utf-8') as f:
                json.dump(valid_data, f, ensure_ascii=False, indent=2)
            
            # Create invalid JSON file
            invalid_data = {
                "title": "Invalid",
                "description": "Short",
                "target_audience": "beginners",
                "difficulty_level": "beginner",
                "learning_objectives": ["Short"],
                "language": "pt",
                "content": [],
                "quiz": [],
                "metadata": {
                    "dimension": "wellness",
                    "archetype": "achiever",
                    "estimated_duration": 30
                }
            }
            
            invalid_file = temp_path / "invalid.json"
            with open(invalid_file, 'w', encoding='utf-8') as f:
                json.dump(invalid_data, f, ensure_ascii=False, indent=2)
            
            # Test batch validation
            results = validator.validate_batch_output(str(temp_path))
            
            assert len(results) == 2
            assert str(valid_file) in results
            assert str(invalid_file) in results
            
            # Check individual results
            valid_result = results[str(valid_file)]
            invalid_result = results[str(invalid_file)]
            
            assert valid_result.is_valid
            assert valid_result.score >= 7.0
            
            assert not invalid_result.is_valid
            assert invalid_result.score < 7.0
    
    def test_validation_report_generation(self):
        """Test validation report generation."""
        validator = OutputValidator()
        
        # Create sample results
        results = {
            "valid.json": ValidationResult(
                is_valid=True,
                score=8.5,
                errors=[],
                warnings=["Minor warning"],
                suggestions=["Small suggestion"],
                metadata={"file_path": "valid.json"}
            ),
            "invalid.json": ValidationResult(
                is_valid=False,
                score=4.2,
                errors=["Critical error"],
                warnings=["Warning message"],
                suggestions=["Improvement suggestion"],
                metadata={"file_path": "invalid.json"}
            )
        }
        
        report = validator.generate_validation_report(results)
        
        assert "Output Validation Report" in report
        assert "Summary" in report
        assert "Total files validated: 2" in report
        assert "Files passed validation: 1" in report
        assert "Files failed validation: 1" in report
        assert "valid.json - ✓ PASSED" in report
        assert "invalid.json - ✗ FAILED" in report
        assert "Critical error" in report
        assert "Minor warning" in report
    
    def test_error_handling(self):
        """Test error handling in validation."""
        validator = OutputValidator()
        
        # Test with invalid JSON structure
        invalid_data = "not a dictionary"
        
        result = validator.validate_single_output(invalid_data, "test.json")
        
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert result.score == 0.0
        assert len(result.errors) > 0
        # The validator handles invalid input gracefully, so no "error" key is added
        assert "error_count" in result.metadata
        assert result.metadata["error_count"] > 0
    
    def test_helper_methods(self):
        """Test helper methods."""
        validator = OutputValidator()
        
        # Test text extraction
        data = {
            "title": "Test Title",
            "description": "Test Description",
            "learning_objectives": ["Objective 1", "Objective 2"],
            "content": [
                {"content": "Content 1"},
                {"content": "Content 2"}
            ],
            "quiz": [
                {
                    "question": "Question 1?",
                    "options": ["Option A", "Option B"]
                }
            ]
        }
        
        extracted_text = validator._extract_all_text(data)
        
        assert "Test Title" in extracted_text
        assert "Test Description" in extracted_text
        assert "Objective 1" in extracted_text
        assert "Content 1" in extracted_text
        assert "Question 1?" in extracted_text
        assert "Option A" in extracted_text
        
        # Test sentence length calculation
        text = "This is a short sentence. This is another sentence with more words."
        avg_length = validator._calculate_average_sentence_length(text)
        assert avg_length > 0
        
        # Test score calculation
        score = validator._calculate_validation_score(8.0, 1, 2, 3)
        assert score < 8.0  # Should be reduced due to errors/warnings


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def setup_method(self):
        """Set up test configuration."""
        load_config()
    
    def test_validate_output_file(self):
        """Test validate_output_file function."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            valid_data = {
                "title": "Test Knowledge Task",
                "description": "This is a test knowledge task for file validation.",
                "target_audience": "intermediate learners",
                "difficulty_level": "intermediate",
                "learning_objectives": [
                    "Compreender conceitos básicos",
                    "Aplicar conhecimentos na prática",
                    "Avaliar resultados obtidos"
                ],
                "language": "pt",
                "content": [
                    {
                        "type": "text",
                        "content": "Este é um conteúdo de teste abrangente para validação que contém informações suficientes para atender aos requisitos mínimos de qualidade."
                    },
                    {
                        "type": "list",
                        "content": "Ponto importante 1\nPonto importante 2\nPonto importante 3"
                    }
                ],
                "quiz": [
                    {
                        "question": "Qual é o conceito principal abordado neste conteúdo?",
                        "options": ["Conceito A", "Conceito B", "Conceito C"],
                        "correct_answer": "Conceito A"
                    },
                    {
                        "question": "Como aplicar os conhecimentos na prática diária?",
                        "options": ["Método 1", "Método 2", "Método 3"],
                        "correct_answer": "Método 1"
                    },
                    {
                        "question": "Qual resultado esperado após aplicar as técnicas?",
                        "options": ["Resultado A", "Resultado B", "Resultado C"],
                        "correct_answer": "Resultado A"
                    }
                ],
                "metadata": {
                    "dimension": "wellness",
                    "archetype": "achiever",
                    "estimated_duration": 300
                }
            }
            
            json.dump(valid_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        try:
            result = validate_output_file(temp_file)
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid
            assert result.score >= 7.0
            
        finally:
            Path(temp_file).unlink()
    
    def test_validate_output_directory(self):
        """Test validate_output_directory function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test JSON file
            test_data = {
                "title": "Directory Test Task",
                "description": "This is a test knowledge task for directory validation.",
                "target_audience": "intermediate learners",
                "difficulty_level": "intermediate",
                "learning_objectives": [
                    "Compreender conceitos básicos",
                    "Aplicar conhecimentos na prática",
                    "Avaliar resultados obtidos"
                ],
                "language": "pt",
                "content": [
                    {
                        "type": "text",
                        "content": "Este é um conteúdo de teste abrangente para validação de diretório que contém informações suficientes para atender aos requisitos mínimos de qualidade."
                    },
                    {
                        "type": "list",
                        "content": "Ponto importante 1\nPonto importante 2\nPonto importante 3"
                    }
                ],
                "quiz": [
                    {
                        "question": "Qual é o conceito principal abordado neste conteúdo?",
                        "options": ["Conceito A", "Conceito B", "Conceito C"],
                        "correct_answer": "Conceito A"
                    },
                    {
                        "question": "Como aplicar os conhecimentos na prática diária?",
                        "options": ["Método 1", "Método 2", "Método 3"],
                        "correct_answer": "Método 1"
                    },
                    {
                        "question": "Qual resultado esperado após aplicar as técnicas?",
                        "options": ["Resultado A", "Resultado B", "Resultado C"],
                        "correct_answer": "Resultado A"
                    }
                ],
                "metadata": {
                    "dimension": "wellness",
                    "archetype": "achiever",
                    "estimated_duration": 300
                }
            }
            
            test_file = temp_path / "test.json"
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            
            results = validate_output_directory(str(temp_path))
            
            assert len(results) == 1
            assert str(test_file) in results
            assert results[str(test_file)].is_valid
    
    def test_generate_validation_report_function(self):
        """Test generate_validation_report function."""
        results = {
            "test.json": ValidationResult(
                is_valid=True,
                score=8.0,
                errors=[],
                warnings=["Test warning"],
                suggestions=["Test suggestion"],
                metadata={"file_path": "test.json"}
            )
        }
        
        report = generate_validation_report(results)
        
        assert "Output Validation Report" in report
        assert "test.json - ✓ PASSED" in report
        assert "Test warning" in report
        assert "Test suggestion" in report
    
    def test_file_error_handling(self):
        """Test error handling for file operations."""
        # Test with non-existent file
        result = validate_output_file("non_existent_file.json")
        
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert result.score == 0.0
        assert len(result.errors) > 0
        assert "file_error" in result.metadata
        
        # Test with non-existent directory
        results = validate_output_directory("non_existent_directory")
        
        assert len(results) == 0 