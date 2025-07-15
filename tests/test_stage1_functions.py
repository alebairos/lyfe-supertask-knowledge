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