"""
Test Stage 1 functions for raw content analysis.

These tests ensure that:
1. Stage 1 module exists and is importable
2. JSON loading functions work correctly
3. Content extraction handles various formats
4. Structure normalization produces consistent output
5. Error handling provides clear messages
6. Edge cases are handled gracefully
"""

import sys
import os
import json
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import and load configuration for tests
from lyfe_kt.config_loader import load_config

# Load configuration once at module level
try:
    load_config()
except Exception:
    # If config loading fails, tests will handle it appropriately
    pass

try:
    from lyfe_kt.stage1_functions import (
        load_raw_json,
        extract_content,
        analyze_content_structure,
        normalize_structure,
        process_raw_file,
        Stage1ProcessingError
    )
except ImportError:
    # Module doesn't exist yet - tests will fail and guide implementation
    pass


class TestStage1Module:
    """Test that Stage 1 functions module exists and is properly structured."""
    
    def test_stage1_module_exists(self):
        """Test that Stage 1 functions module exists and can be imported."""
        module_path = Path("src/lyfe_kt/stage1_functions.py")
        assert module_path.exists(), "Stage 1 functions module src/lyfe_kt/stage1_functions.py must exist"
        assert module_path.is_file(), "Stage 1 functions must be a file, not a directory"
    
    def test_stage1_module_importable(self):
        """Test that Stage 1 functions module can be imported without errors."""
        try:
            from lyfe_kt.stage1_functions import process_raw_file
            assert callable(process_raw_file), "process_raw_file must be callable"
        except ImportError as e:
            pytest.fail(f"Stage 1 functions module must be importable: {e}")
    
    def test_stage1_functions_exist(self):
        """Test that all required Stage 1 functions exist."""
        from lyfe_kt.stage1_functions import (
            load_raw_json,
            extract_content,
            analyze_content_structure,
            normalize_structure,
            process_raw_file
        )
        
        required_functions = [
            load_raw_json,
            extract_content,
            analyze_content_structure,
            normalize_structure,
            process_raw_file
        ]
        
        for func in required_functions:
            assert callable(func), f"Function {func.__name__} must be callable"
    
    def test_stage1_error_exists(self):
        """Test that Stage1ProcessingError exception class exists."""
        from lyfe_kt.stage1_functions import Stage1ProcessingError
        assert issubclass(Stage1ProcessingError, Exception), "Stage1ProcessingError must be an Exception subclass"


class TestJSONLoading:
    """Test JSON loading functionality."""
    
    def test_load_raw_json_with_valid_file(self):
        """Test loading valid JSON file."""
        from lyfe_kt.stage1_functions import load_raw_json
        
        test_data = {
            "title": "Test Supertask",
            "dimension": "wellness",
            "archetype": "achiever",
            "flexibleItems": [
                {"type": "content", "content": "Test content"},
                {"type": "quiz", "question": "Test question?"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = load_raw_json(temp_path)
            assert isinstance(result, dict), "Valid JSON should return dictionary"
            assert result["title"] == "Test Supertask"
            assert "flexibleItems" in result
        finally:
            os.unlink(temp_path)
    
    def test_load_raw_json_with_missing_file(self):
        """Test loading missing JSON file."""
        from lyfe_kt.stage1_functions import load_raw_json, Stage1ProcessingError
        
        with pytest.raises(Stage1ProcessingError) as exc_info:
            load_raw_json("nonexistent_file.json")
        
        assert "file not found" in str(exc_info.value).lower()
    
    def test_load_raw_json_with_invalid_json(self):
        """Test loading invalid JSON file."""
        from lyfe_kt.stage1_functions import load_raw_json, Stage1ProcessingError
        
        invalid_json = '{"title": "Test", "incomplete": true'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            temp_path = f.name
        
        try:
            with pytest.raises(Stage1ProcessingError) as exc_info:
                load_raw_json(temp_path)
            
            assert "invalid json" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_load_raw_json_with_empty_file(self):
        """Test loading empty JSON file."""
        from lyfe_kt.stage1_functions import load_raw_json, Stage1ProcessingError
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('')
            temp_path = f.name
        
        try:
            with pytest.raises(Stage1ProcessingError) as exc_info:
                load_raw_json(temp_path)
            
            assert "empty" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)


class TestContentExtraction:
    """Test content extraction functionality."""
    
    def test_extract_content_with_flexible_items(self):
        """Test extracting content from flexible items structure."""
        from lyfe_kt.stage1_functions import extract_content
        
        raw_data = {
            "title": "Test Supertask",
            "dimension": "wellness", 
            "archetype": "achiever",
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "This is the main content about wellness.",
                    "author": "Dr. Smith"
                },
                {
                    "type": "quiz",
                    "question": "What is wellness?",
                    "options": ["Health", "Happiness", "Both", "Neither"],
                    "correctAnswer": 2
                },
                {
                    "type": "content",
                    "content": "Additional content about habits.",
                    "quote": "Success is a habit."
                }
            ]
        }
        
        result = extract_content(raw_data)
        
        assert isinstance(result, dict), "Extracted content should be a dictionary"
        assert "content_items" in result
        assert "quiz_items" in result
        assert "metadata" in result
        
        # Check content items
        content_items = result["content_items"]
        assert len(content_items) == 2
        assert content_items[0]["content"] == "This is the main content about wellness."
        assert content_items[1]["content"] == "Additional content about habits."
        
        # Check quiz items
        quiz_items = result["quiz_items"]
        assert len(quiz_items) == 1
        assert quiz_items[0]["question"] == "What is wellness?"
        assert quiz_items[0]["correctAnswer"] == 2
    
    def test_extract_content_with_missing_flexible_items(self):
        """Test extracting content when flexibleItems is missing."""
        from lyfe_kt.stage1_functions import extract_content, Stage1ProcessingError
        
        raw_data = {
            "title": "Test Supertask",
            "dimension": "wellness",
            "archetype": "achiever"
            # Missing flexibleItems
        }
        
        with pytest.raises(Stage1ProcessingError) as exc_info:
            extract_content(raw_data)
        
        assert "flexibleitems" in str(exc_info.value).lower()
    
    def test_extract_content_with_empty_flexible_items(self):
        """Test extracting content with empty flexibleItems."""
        from lyfe_kt.stage1_functions import extract_content, Stage1ProcessingError
        
        raw_data = {
            "title": "Test Supertask",
            "dimension": "wellness",
            "archetype": "achiever",
            "flexibleItems": []
        }
        
        with pytest.raises(Stage1ProcessingError) as exc_info:
            extract_content(raw_data)
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_extract_content_with_mixed_content_types(self):
        """Test extracting content with various content types."""
        from lyfe_kt.stage1_functions import extract_content
        
        raw_data = {
            "title": "Mixed Content Test",
            "dimension": "productivity",
            "archetype": "builder",
            "flexibleItems": [
                {"type": "content", "content": "Regular content"},
                {"type": "quote", "content": "Inspiring quote", "author": "Famous Person"},
                {"type": "quiz", "question": "Test question?", "options": ["A", "B"], "correctAnswer": 0},
                {"type": "image", "url": "https://example.com/image.jpg"},
                {"type": "unknown", "data": "Should be ignored"}
            ]
        }
        
        result = extract_content(raw_data)
        
        content_items = result["content_items"]
        quiz_items = result["quiz_items"]
        
        # Should extract content and quotes, ignore images and unknown types
        assert len(content_items) == 2  # content + quote
        assert len(quiz_items) == 1
        
        # Check that quote is properly handled
        quote_item = next((item for item in content_items if "author" in item), None)
        assert quote_item is not None
        assert quote_item["author"] == "Famous Person"


class TestContentStructureAnalysis:
    """Test content structure analysis functionality."""
    
    def test_analyze_content_structure_basic(self):
        """Test basic content structure analysis."""
        from lyfe_kt.stage1_functions import analyze_content_structure
        
        extracted_content = {
            "content_items": [
                {"content": "This is about morning routines and habits.", "type": "content"},
                {"content": "Exercise is important for health.", "type": "content"}
            ],
            "quiz_items": [
                {"question": "What is a habit?", "options": ["A", "B", "C", "D"], "correctAnswer": 0}
            ],
            "metadata": {
                "title": "Morning Routine",
                "dimension": "wellness",
                "archetype": "achiever"
            }
        }
        
        result = analyze_content_structure(extracted_content)
        
        assert isinstance(result, dict), "Analysis result should be a dictionary"
        assert "tone" in result
        assert "complexity" in result
        assert "themes" in result
        assert "language" in result
        
        # Check basic analysis results
        assert isinstance(result["themes"], list)
        assert len(result["themes"]) > 0
        assert result["complexity"] in ["beginner", "intermediate", "advanced"]
    
    def test_analyze_content_structure_with_quotes(self):
        """Test content structure analysis with quotes."""
        from lyfe_kt.stage1_functions import analyze_content_structure
        
        extracted_content = {
            "content_items": [
                {
                    "content": "Success is not final, failure is not fatal.",
                    "type": "quote",
                    "author": "Winston Churchill"
                }
            ],
            "quiz_items": [],
            "metadata": {
                "title": "Motivational Quotes",
                "dimension": "mindfulness",
                "archetype": "explorer"
            }
        }
        
        result = analyze_content_structure(extracted_content)
        
        assert result["tone"] == "inspirational"
        assert "motivation" in result["themes"]
    
    def test_analyze_content_structure_with_insufficient_content(self):
        """Test content structure analysis with insufficient content."""
        from lyfe_kt.stage1_functions import analyze_content_structure, Stage1ProcessingError
        
        extracted_content = {
            "content_items": [],
            "quiz_items": [],
            "metadata": {
                "title": "Empty Content",
                "dimension": "wellness",
                "archetype": "achiever"
            }
        }
        
        with pytest.raises(Stage1ProcessingError) as exc_info:
            analyze_content_structure(extracted_content)
        
        assert "insufficient content" in str(exc_info.value).lower()


class TestStructureNormalization:
    """Test structure normalization functionality."""
    
    def test_normalize_structure_basic(self):
        """Test basic structure normalization."""
        from lyfe_kt.stage1_functions import normalize_structure
        
        extracted_content = {
            "content_items": [
                {"content": "Morning routine content", "type": "content"},
                {"content": "Exercise content", "type": "content"}
            ],
            "quiz_items": [
                {"question": "What time to wake up?", "options": ["5AM", "6AM", "7AM", "8AM"], "correctAnswer": 1}
            ],
            "metadata": {
                "title": "Morning Routine",
                "dimension": "wellness",
                "archetype": "achiever"
            }
        }
        
        analysis = {
            "tone": "motivational",
            "complexity": "beginner",
            "themes": ["morning", "routine", "habits"],
            "language": "english"
        }
        
        result = normalize_structure(extracted_content, analysis)
        
        assert isinstance(result, dict), "Normalized structure should be a dictionary"
        
        # Check required fields for preprocessed JSON
        required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
        for field in required_fields:
            assert field in result, f"Normalized structure must contain {field}"
        
        # Check that values are properly assigned
        assert result["title"] == "Morning Routine"
        assert result["difficulty_level"] == "beginner"
        assert result["target_audience"] == "achiever"
        
        # Check that content is preserved
        assert "content" in result
        assert "quiz" in result
        assert len(result["content"]) == 2
        assert len(result["quiz"]) == 1
    
    def test_normalize_structure_with_quotes(self):
        """Test structure normalization with quotes."""
        from lyfe_kt.stage1_functions import normalize_structure
        
        extracted_content = {
            "content_items": [
                {
                    "content": "The way to get started is to quit talking and begin doing.",
                    "type": "quote",
                    "author": "Walt Disney"
                }
            ],
            "quiz_items": [],
            "metadata": {
                "title": "Motivational Quotes",
                "dimension": "mindfulness",
                "archetype": "explorer"
            }
        }
        
        analysis = {
            "tone": "inspirational",
            "complexity": "intermediate",
            "themes": ["motivation", "action"],
            "language": "english"
        }
        
        result = normalize_structure(extracted_content, analysis)
        
        # Check that quotes are properly formatted
        content_item = result["content"][0]
        assert "author" in content_item
        assert content_item["author"] == "Walt Disney"
        assert "quote" in content_item["content"].lower()
    
    def test_normalize_structure_with_multilingual_content(self):
        """Test structure normalization with multilingual content."""
        from lyfe_kt.stage1_functions import normalize_structure
        
        extracted_content = {
            "content_items": [
                {"content": "Bom dia! Vamos começar o dia com energia.", "type": "content"}
            ],
            "quiz_items": [
                {"question": "Qual é a melhor hora para acordar?", "options": ["5h", "6h", "7h", "8h"], "correctAnswer": 1}
            ],
            "metadata": {
                "title": "Rotina Matinal",
                "dimension": "wellness",
                "archetype": "warrior"
            }
        }
        
        analysis = {
            "tone": "motivational",
            "complexity": "intermediate",
            "themes": ["morning", "routine"],
            "language": "portuguese"
        }
        
        result = normalize_structure(extracted_content, analysis)
        
        # Check that language is preserved
        assert "language" in result
        assert result["language"] == "portuguese"
        
        # Check that content is preserved in original language
        assert "energia" in result["content"][0]["content"]
        assert "Qual é" in result["quiz"][0]["question"]


class TestIntegratedProcessing:
    """Test integrated Stage 1 processing functionality."""
    
    def test_process_raw_file_with_valid_supertask(self):
        """Test processing a valid supertask file."""
        from lyfe_kt.stage1_functions import process_raw_file
        
        supertask_data = {
            "title": "Levantar da Cama",
            "dimension": "physicalHealth",
            "archetype": "warrior",
            "relatedToType": "HABITBP",
            "relatedToId": "wake-up-early",
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "Acordar cedo é fundamental para ter um dia produtivo.",
                    "author": "Especialista em Produtividade"
                },
                {
                    "type": "quiz",
                    "question": "Qual é o benefício de acordar cedo?",
                    "options": ["Mais tempo", "Mais energia", "Menos stress", "Todos os anteriores"],
                    "correctAnswer": 3
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(supertask_data, f)
            temp_path = f.name
        
        try:
            result = process_raw_file(temp_path)
            
            assert isinstance(result, dict), "Process result should be a dictionary"
            
            # Check required fields
            required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
            for field in required_fields:
                assert field in result, f"Result must contain {field}"
            
            # Check that content is processed
            assert "content" in result
            assert "quiz" in result
            assert len(result["content"]) > 0
            assert len(result["quiz"]) > 0
            
            # Check metadata preservation
            assert result["title"] == "Levantar da Cama"
            assert result["target_audience"] == "warrior"
            
        finally:
            os.unlink(temp_path)
    
    def test_process_raw_file_with_missing_file(self):
        """Test processing missing file."""
        from lyfe_kt.stage1_functions import process_raw_file, Stage1ProcessingError
        
        with pytest.raises(Stage1ProcessingError) as exc_info:
            process_raw_file("nonexistent_file.json")
        
        assert "file not found" in str(exc_info.value).lower()
    
    def test_process_raw_file_with_invalid_structure(self):
        """Test processing file with invalid structure."""
        from lyfe_kt.stage1_functions import process_raw_file, Stage1ProcessingError
        
        invalid_data = {
            "title": "Invalid Structure",
            # Missing required fields like dimension, archetype, flexibleItems
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(Stage1ProcessingError) as exc_info:
                process_raw_file(temp_path)
            
            error_msg = str(exc_info.value).lower()
            assert "missing" in error_msg or "invalid" in error_msg
            
        finally:
            os.unlink(temp_path)
    
    def test_process_raw_file_creates_valid_preprocessed_json(self):
        """Test that processing creates valid preprocessed JSON structure."""
        from lyfe_kt.stage1_functions import process_raw_file
        
        supertask_data = {
            "title": "Test Task",
            "dimension": "productivity",
            "archetype": "builder",
            "relatedToType": "GENERIC",
            "relatedToId": "general-productivity",
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "Time management is crucial for productivity."
                },
                {
                    "type": "quiz",
                    "question": "What helps with time management?",
                    "options": ["Planning", "Prioritizing", "Both", "Neither"],
                    "correctAnswer": 2
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(supertask_data, f)
            temp_path = f.name
        
        try:
            result = process_raw_file(temp_path)
            
            # Validate against expected preprocessed JSON structure
            assert isinstance(result["title"], str)
            assert isinstance(result["description"], str)
            assert isinstance(result["target_audience"], str)
            assert isinstance(result["difficulty_level"], str)
            assert isinstance(result["learning_objectives"], list)
            assert isinstance(result["content"], list)
            assert isinstance(result["quiz"], list)
            
            # Check that content items have required structure
            for content_item in result["content"]:
                assert "content" in content_item
                assert isinstance(content_item["content"], str)
            
            # Check that quiz items have required structure
            for quiz_item in result["quiz"]:
                assert "question" in quiz_item
                assert "options" in quiz_item
                assert "correctAnswer" in quiz_item
                assert isinstance(quiz_item["options"], list)
                assert isinstance(quiz_item["correctAnswer"], int)
            
        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_stage1_error_message_clarity(self):
        """Test that error messages are clear and actionable."""
        from lyfe_kt.stage1_functions import Stage1ProcessingError
        
        error = Stage1ProcessingError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_processing_with_unicode_content(self):
        """Test processing with unicode content."""
        from lyfe_kt.stage1_functions import process_raw_file
        
        unicode_data = {
            "title": "Título com Acentos",
            "dimension": "wellness",
            "archetype": "nurturer",
            "relatedToType": "HABITBP",
            "relatedToId": "self-care",
            "flexibleItems": [
                {
                    "type": "content",
                    "content": "Cuidar de si mesmo é essencial para o bem-estar.",
                    "author": "Especialista em Bem-Estar"
                },
                {
                    "type": "quiz",
                    "question": "O que é autocuidado?",
                    "options": ["Egoísmo", "Necessidade", "Luxo", "Opcional"],
                    "correctAnswer": 1
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(unicode_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            result = process_raw_file(temp_path)
            
            # Should handle unicode content correctly
            assert isinstance(result, dict)
            assert "Título" in result["title"]
            assert "bem-estar" in result["content"][0]["content"]
            
        finally:
            os.unlink(temp_path)
    
    def test_processing_with_large_content(self):
        """Test processing with large content."""
        from lyfe_kt.stage1_functions import process_raw_file
        
        large_content = "This is a very long content section. " * 1000
        
        large_data = {
            "title": "Large Content Test",
            "dimension": "productivity",
            "archetype": "achiever",
            "relatedToType": "GENERIC",
            "relatedToId": "large-content",
            "flexibleItems": [
                {
                    "type": "content",
                    "content": large_content
                },
                {
                    "type": "quiz",
                    "question": "What is the main topic?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 0
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_data, f)
            temp_path = f.name
        
        try:
            result = process_raw_file(temp_path)
            
            # Should handle large content correctly
            assert isinstance(result, dict)
            assert len(result["content"][0]["content"]) > 1000
            
        finally:
            os.unlink(temp_path) 


class TestAriPersonaAnalysis:
    """Test Ari persona analysis functions."""
    
    def test_analyze_ari_persona_patterns_basic(self):
        """Test basic Ari persona pattern analysis."""
        from lyfe_kt.stage1_functions import analyze_ari_persona_patterns
        
        # Test data with coaching opportunities
        content_items = [
            {"content": "Estabelecer uma rotina matinal é importante para criar hábitos saudáveis", "type": "content"},
            {"content": "Você deve preparar o ambiente na noite anterior", "type": "content"},
            {"content": "Pequenos passos levam a grandes mudanças", "type": "content"}
        ]
        
        quiz_items = [
            {"question": "Qual é o benefício de acordar cedo?", "options": ["A", "B"], "correctAnswer": 0}
        ]
        
        result = analyze_ari_persona_patterns(content_items, quiz_items)
        
        # Check structure
        assert "coaching_opportunities" in result
        assert "framework_integration" in result
        assert "engagement_patterns" in result
        assert "language_patterns" in result
        assert "ari_readiness_score" in result
        assert "enhancement_recommendations" in result
        
        # Check coaching opportunities
        assert len(result["coaching_opportunities"]["habit_formation"]) > 0
        assert len(result["coaching_opportunities"]["behavioral_change"]) > 0
        
        # Check framework integration
        assert result["framework_integration"]["tiny_habits"] == True
        assert result["framework_integration"]["behavioral_design"] == True
        
        # Check language patterns
        assert result["language_patterns"]["portuguese_detected"] == True
        
        # Check readiness score
        assert 0.0 <= result["ari_readiness_score"] <= 1.0
        
        # Check recommendations
        assert len(result["enhancement_recommendations"]) > 0
    
    def test_analyze_ari_persona_patterns_with_huberman_content(self):
        """Test Ari persona analysis with Huberman Protocol content."""
        from lyfe_kt.stage1_functions import analyze_ari_persona_patterns
        
        content_items = [
            {"content": "A luz da manhã é fundamental para regular o ritmo circadiano", "type": "content"},
            {"content": "O sono de qualidade melhora a neuroplasticidade", "type": "content"}
        ]
        
        quiz_items = []
        
        result = analyze_ari_persona_patterns(content_items, quiz_items)
        
        # Check Huberman protocol detection
        assert result["framework_integration"]["huberman_protocols"] == True
        
        # Check recommendations include Huberman
        recommendations = result["enhancement_recommendations"]
        huberman_recommendation = any("Huberman" in rec for rec in recommendations)
        assert huberman_recommendation == True
    
    def test_analyze_ari_persona_patterns_with_motivational_content(self):
        """Test Ari persona analysis with motivational content."""
        from lyfe_kt.stage1_functions import analyze_ari_persona_patterns
        
        content_items = [
            {"content": "O sucesso vem da perseverança diária", "type": "content"},
            {"content": "Cada vitória pequena é um passo para o desafio maior", "type": "content"}
        ]
        
        quiz_items = []
        
        result = analyze_ari_persona_patterns(content_items, quiz_items)
        
        # Check motivation detection
        assert len(result["coaching_opportunities"]["motivation_points"]) > 0
        
        # Check coaching moments
        coaching_moments = result["engagement_patterns"]["coaching_moments"]
        motivational_moments = [moment for moment in coaching_moments if "Motivational" in moment]
        assert len(motivational_moments) > 0
    
    def test_analyze_ari_persona_patterns_with_action_content(self):
        """Test Ari persona analysis with action-oriented content."""
        from lyfe_kt.stage1_functions import analyze_ari_persona_patterns
        
        content_items = [
            {"content": "Prepare sua roupa na noite anterior", "type": "content"},
            {"content": "Defina um horário fixo para acordar", "type": "content"},
            {"content": "Comece com pequenos passos", "type": "content"}
        ]
        
        quiz_items = []
        
        result = analyze_ari_persona_patterns(content_items, quiz_items)
        
        # Check action trigger detection
        assert len(result["coaching_opportunities"]["action_triggers"]) > 0
        
        # Check question opportunities
        question_opportunities = result["engagement_patterns"]["question_opportunities"]
        commitment_questions = [q for q in question_opportunities if "When will you start?" in q]
        assert len(commitment_questions) > 0
        
        # Check coaching moments
        coaching_moments = result["engagement_patterns"]["coaching_moments"]
        action_moments = [moment for moment in coaching_moments if "Action content" in moment]
        assert len(action_moments) > 0
    
    def test_analyze_ari_persona_patterns_with_tips(self):
        """Test Ari persona analysis with tips sections."""
        from lyfe_kt.stage1_functions import analyze_ari_persona_patterns
        
        content_items = [
            {
                "content": "Para facilitar o processo",
                "type": "content",
                "tips": ["Deixe a cortina entreaberta", "Coloque o despertador longe"]
            }
        ]
        
        quiz_items = []
        
        result = analyze_ari_persona_patterns(content_items, quiz_items)
        
        # Check coaching moments for tips
        coaching_moments = result["engagement_patterns"]["coaching_moments"]
        tips_moments = [moment for moment in coaching_moments if "Tips section" in moment]
        assert len(tips_moments) > 0
    
    def test_analyze_ari_persona_patterns_error_handling(self):
        """Test Ari persona analysis error handling."""
        from lyfe_kt.stage1_functions import analyze_ari_persona_patterns
        
        # Test with invalid data that might cause errors
        content_items = [{"invalid": "structure"}]
        quiz_items = [{"also_invalid": "structure"}]
        
        result = analyze_ari_persona_patterns(content_items, quiz_items)
        
        # Should return basic structure even with errors
        assert "coaching_opportunities" in result
        assert "framework_integration" in result
        assert "engagement_patterns" in result
        assert "language_patterns" in result
        assert "ari_readiness_score" in result
        assert "enhancement_recommendations" in result
        
        # Check for error indication
        if "analysis_error" in result:
            assert isinstance(result["analysis_error"], str)
    
    def test_process_directory_with_ari_analysis_basic(self):
        """Test directory processing with Ari analysis."""
        from lyfe_kt.stage1_functions import process_directory_with_ari_analysis
        import tempfile
        import json
        import os
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                # Create test JSON file
                test_data = {
                    "title": "Test Supertask",
                    "flexibleItems": [
                        {"type": "content", "content": "Estabelecer uma rotina é importante"},
                        {"type": "quiz", "question": "Qual é o benefício?", "options": ["A", "B"], "correctAnswer": 0}
                    ]
                }
                
                test_file = os.path.join(input_dir, "test.json")
                with open(test_file, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f)
                
                # Process directory
                result = process_directory_with_ari_analysis(input_dir, output_dir)
                
                # Check basic processing results
                assert result["successful"] == 1
                assert result["failed_count"] == 0
                assert len(result["processed"]) == 1
                
                # Check Ari analysis results
                assert "ari_persona_analysis" in result
                assert len(result["ari_persona_analysis"]) == 1
                
                ari_analysis = result["ari_persona_analysis"][0]
                assert "file" in ari_analysis
                assert "title" in ari_analysis
                assert "ari_analysis" in ari_analysis
                
                # Check Ari summary
                assert "ari_summary" in result
                assert "total_files_analyzed" in result["ari_summary"]
                assert "average_ari_readiness" in result["ari_summary"]
                assert "high_readiness_files" in result["ari_summary"]
                assert "medium_readiness_files" in result["ari_summary"]
                assert "low_readiness_files" in result["ari_summary"]
    
    def test_process_directory_with_ari_analysis_multiple_files(self):
        """Test directory processing with multiple files."""
        from lyfe_kt.stage1_functions import process_directory_with_ari_analysis
        import tempfile
        import json
        import os
        
        # Create temporary directories
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                # Create multiple test JSON files
                test_files = [
                    {
                        "name": "habit_formation.json",
                        "data": {
                            "title": "Habit Formation",
                            "flexibleItems": [
                                {"type": "content", "content": "Criar hábitos pequenos é fundamental"},
                                {"type": "content", "content": "A rotina matinal transforma sua vida"}
                            ]
                        }
                    },
                    {
                        "name": "sleep_protocol.json",
                        "data": {
                            "title": "Sleep Protocol",
                            "flexibleItems": [
                                {"type": "content", "content": "A luz da manhã regula o ritmo circadiano"},
                                {"type": "content", "content": "O sono melhora a neuroplasticidade"}
                            ]
                        }
                    }
                ]
                
                for test_file_info in test_files:
                    test_file = os.path.join(input_dir, test_file_info["name"])
                    with open(test_file, 'w', encoding='utf-8') as f:
                        json.dump(test_file_info["data"], f)
                
                # Process directory
                result = process_directory_with_ari_analysis(input_dir, output_dir)
                
                # Check processing results
                assert result["successful"] == 2
                assert result["failed_count"] == 0
                assert len(result["processed"]) == 2
                
                # Check Ari analysis results
                assert len(result["ari_persona_analysis"]) == 2
                
                # Check different framework integrations
                analyses = [item["ari_analysis"] for item in result["ari_persona_analysis"]]
                
                # Should have at least one with tiny_habits and one with huberman_protocols
                tiny_habits_detected = any(analysis["framework_integration"]["tiny_habits"] for analysis in analyses)
                huberman_detected = any(analysis["framework_integration"]["huberman_protocols"] for analysis in analyses)
                
                assert tiny_habits_detected == True
                assert huberman_detected == True
                
                # Check summary statistics
                assert result["ari_summary"]["total_files_analyzed"] == 2
                assert result["ari_summary"]["average_ari_readiness"] > 0
    
    def test_ari_readiness_score_calculation(self):
        """Test Ari readiness score calculation."""
        from lyfe_kt.stage1_functions import _calculate_ari_readiness_score
        
        # Test high readiness
        coaching_opportunities = {
            "habit_formation": ["present"],
            "behavioral_change": ["present"],
            "motivation_points": ["present"],
            "action_triggers": ["present"],
            "micro_habits": ["present"]
        }
        
        framework_integration = {
            "tiny_habits": True,
            "behavioral_design": True,
            "huberman_protocols": True
        }
        
        engagement_patterns = {
            "question_opportunities": ["present"],
            "coaching_moments": ["present"]
        }
        
        score = _calculate_ari_readiness_score(coaching_opportunities, framework_integration, engagement_patterns)
        
        # Should be high score (5 * 0.15 + 3 * 0.1 + 2 * 0.2 = 1.45, capped at 1.0)
        assert score == 1.0
        
        # Test low readiness
        empty_opportunities = {key: [] for key in coaching_opportunities.keys()}
        empty_framework = {key: False for key in framework_integration.keys()}
        empty_engagement = {"question_opportunities": [], "coaching_moments": []}
        
        low_score = _calculate_ari_readiness_score(empty_opportunities, empty_framework, empty_engagement)
        assert low_score == 0.0
    
    def test_enhancement_recommendations_generation(self):
        """Test enhancement recommendations generation."""
        from lyfe_kt.stage1_functions import _generate_enhancement_recommendations
        
        # Test with various opportunities
        coaching_opportunities = {
            "habit_formation": ["present"],
            "behavioral_change": ["present"],
            "motivation_points": [],
            "action_triggers": ["present"],
            "micro_habits": ["present"]
        }
        
        framework_integration = {
            "tiny_habits": True,
            "behavioral_design": False,
            "huberman_protocols": True
        }
        
        recommendations = _generate_enhancement_recommendations(coaching_opportunities, framework_integration)
        
        # Should include specific recommendations
        assert len(recommendations) > 0
        
        # Check for specific recommendations
        tiny_habits_rec = any("Tiny Habits" in rec for rec in recommendations)
        habit_formation_rec = any("habit formation" in rec for rec in recommendations)
        huberman_rec = any("Huberman" in rec for rec in recommendations)
        
        assert tiny_habits_rec == True
        assert habit_formation_rec == True
        assert huberman_rec == True
        
        # Test with empty opportunities
        empty_opportunities = {key: [] for key in coaching_opportunities.keys()}
        empty_framework = {key: False for key in framework_integration.keys()}
        
        empty_recommendations = _generate_enhancement_recommendations(empty_opportunities, empty_framework)
        
        # Should still provide default recommendations
        assert len(empty_recommendations) >= 2
        assert any("basic Ari persona enhancement" in rec for rec in empty_recommendations)
        assert any("TARS-inspired brevity" in rec for rec in empty_recommendations) 