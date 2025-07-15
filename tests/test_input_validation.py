"""
Test input validation functionality.

These tests ensure that:
1. Input validation module exists and is importable
2. File existence validation works correctly
3. JSON structure validation detects malformed JSON
4. Required fields validation identifies missing fields
5. Content validation checks minimum requirements
6. Error handling provides clear, actionable messages
7. Edge cases are handled gracefully
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
    from lyfe_kt.input_validation import (
        validate_file_exists,
        validate_json_structure,
        validate_required_fields,
        validate_content_quality,
        validate_input_file,
        InputValidationError
    )
except ImportError:
    # Module doesn't exist yet - tests will fail and guide implementation
    pass


class TestInputValidationModule:
    """Test that input validation module exists and is properly structured."""
    
    def test_input_validation_module_exists(self):
        """Test that input validation module exists and can be imported."""
        module_path = Path("src/lyfe_kt/input_validation.py")
        assert module_path.exists(), "Input validation module src/lyfe_kt/input_validation.py must exist"
        assert module_path.is_file(), "Input validation must be a file, not a directory"
    
    def test_input_validation_module_importable(self):
        """Test that input validation module can be imported without errors."""
        try:
            from lyfe_kt.input_validation import validate_input_file
            assert callable(validate_input_file), "validate_input_file must be callable"
        except ImportError as e:
            pytest.fail(f"Input validation module must be importable: {e}")
    
    def test_input_validation_functions_exist(self):
        """Test that all required validation functions exist."""
        from lyfe_kt.input_validation import (
            validate_file_exists,
            validate_json_structure,
            validate_required_fields,
            validate_content_quality,
            validate_input_file
        )
        
        required_functions = [
            validate_file_exists,
            validate_json_structure,
            validate_required_fields,
            validate_content_quality,
            validate_input_file
        ]
        
        for func in required_functions:
            assert callable(func), f"Function {func.__name__} must be callable"
    
    def test_input_validation_error_exists(self):
        """Test that InputValidationError exception class exists."""
        from lyfe_kt.input_validation import InputValidationError
        assert issubclass(InputValidationError, Exception), "InputValidationError must be an Exception subclass"


class TestFileExistenceValidation:
    """Test file existence validation functionality."""
    
    def test_validate_file_exists_with_valid_file(self):
        """Test file existence validation with valid file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"test": "data"}')
            temp_path = f.name
        
        try:
            from lyfe_kt.input_validation import validate_file_exists
            # Should not raise exception
            validate_file_exists(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_exists_with_missing_file(self):
        """Test file existence validation with missing file."""
        from lyfe_kt.input_validation import validate_file_exists, InputValidationError
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_file_exists("nonexistent_file.json")
        
        assert "does not exist" in str(exc_info.value).lower()
    
    def test_validate_file_exists_with_directory(self):
        """Test file existence validation with directory instead of file."""
        from lyfe_kt.input_validation import validate_file_exists, InputValidationError
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(InputValidationError) as exc_info:
                validate_file_exists(temp_dir)
            
            assert "not a file" in str(exc_info.value).lower()
    
    def test_validate_file_exists_with_empty_path(self):
        """Test file existence validation with empty path."""
        from lyfe_kt.input_validation import validate_file_exists, InputValidationError
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_file_exists("")
        
        assert "path" in str(exc_info.value).lower()


class TestJSONStructureValidation:
    """Test JSON structure validation functionality."""
    
    def test_validate_json_structure_with_valid_json(self):
        """Test JSON structure validation with valid JSON."""
        from lyfe_kt.input_validation import validate_json_structure
        
        valid_json = '{"title": "Test", "content": "Sample content"}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(valid_json)
            temp_path = f.name
        
        try:
            # Should not raise exception
            result = validate_json_structure(temp_path)
            assert isinstance(result, dict), "Valid JSON should return dictionary"
        finally:
            os.unlink(temp_path)
    
    def test_validate_json_structure_with_invalid_json(self):
        """Test JSON structure validation with invalid JSON."""
        from lyfe_kt.input_validation import validate_json_structure, InputValidationError
        
        invalid_json = '{"title": "Test", "content": "Sample content"'  # Missing closing brace
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            temp_path = f.name
        
        try:
            with pytest.raises(InputValidationError) as exc_info:
                validate_json_structure(temp_path)
            
            assert "invalid json" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_validate_json_structure_with_non_object_json(self):
        """Test JSON structure validation with non-object JSON."""
        from lyfe_kt.input_validation import validate_json_structure, InputValidationError
        
        non_object_json = '["array", "instead", "of", "object"]'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(non_object_json)
            temp_path = f.name
        
        try:
            with pytest.raises(InputValidationError) as exc_info:
                validate_json_structure(temp_path)
            
            assert "must be an object" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_validate_json_structure_with_empty_file(self):
        """Test JSON structure validation with empty file."""
        from lyfe_kt.input_validation import validate_json_structure, InputValidationError
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('')
            temp_path = f.name
        
        try:
            with pytest.raises(InputValidationError) as exc_info:
                validate_json_structure(temp_path)
            
            assert "empty" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)


class TestRequiredFieldsValidation:
    """Test required fields validation functionality."""
    
    def test_validate_required_fields_with_all_fields(self):
        """Test required fields validation with all required fields present."""
        from lyfe_kt.input_validation import validate_required_fields
        
        data = {
            "title": "Test Title",
            "description": "Test Description",
            "target_audience": "Test Audience",
            "difficulty_level": "beginner",
            "learning_objectives": ["Objective 1", "Objective 2"]
        }
        
        required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
        
        # Should not raise exception
        validate_required_fields(data, required_fields)
    
    def test_validate_required_fields_with_missing_fields(self):
        """Test required fields validation with missing fields."""
        from lyfe_kt.input_validation import validate_required_fields, InputValidationError
        
        data = {
            "title": "Test Title",
            "description": "Test Description"
            # Missing other required fields
        }
        
        required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error_msg = str(exc_info.value).lower()
        assert "missing required fields" in error_msg
        assert "target_audience" in error_msg
        assert "difficulty_level" in error_msg
        assert "learning_objectives" in error_msg
    
    def test_validate_required_fields_with_null_values(self):
        """Test required fields validation with null values."""
        from lyfe_kt.input_validation import validate_required_fields, InputValidationError
        
        data = {
            "title": "Test Title",
            "description": None,  # Null value
            "target_audience": "Test Audience",
            "difficulty_level": "beginner",
            "learning_objectives": ["Objective 1"]
        }
        
        required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error_msg = str(exc_info.value).lower()
        assert "null or empty" in error_msg
        assert "description" in error_msg
    
    def test_validate_required_fields_with_empty_strings(self):
        """Test required fields validation with empty strings."""
        from lyfe_kt.input_validation import validate_required_fields, InputValidationError
        
        data = {
            "title": "",  # Empty string
            "description": "Test Description",
            "target_audience": "Test Audience",
            "difficulty_level": "beginner",
            "learning_objectives": ["Objective 1"]
        }
        
        required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error_msg = str(exc_info.value).lower()
        assert "null or empty" in error_msg
        assert "title" in error_msg


class TestContentQualityValidation:
    """Test content quality validation functionality."""
    
    def test_validate_content_quality_with_sufficient_content(self):
        """Test content quality validation with sufficient content."""
        from lyfe_kt.input_validation import validate_content_quality
        
        data = {
            "title": "Test Title",
            "description": "This is a comprehensive description that provides detailed information about the content and its purpose.",
            "content": "This is the main content section that contains substantial information for learning purposes. It includes multiple sentences and detailed explanations."
        }
        
        # Should not raise exception
        validate_content_quality(data)
    
    def test_validate_content_quality_with_insufficient_content(self):
        """Test content quality validation with insufficient content."""
        from lyfe_kt.input_validation import validate_content_quality, InputValidationError
        
        data = {
            "title": "Test",
            "description": "Short",
            "content": "Too short"
        }
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_content_quality(data)
        
        error_msg = str(exc_info.value).lower()
        assert "content quality" in error_msg or "minimum length" in error_msg
    
    def test_validate_content_quality_with_missing_content_fields(self):
        """Test content quality validation with missing content fields."""
        from lyfe_kt.input_validation import validate_content_quality, InputValidationError
        
        data = {
            "title": "Test Title"
            # Missing description and content
        }
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_content_quality(data)
        
        error_msg = str(exc_info.value).lower()
        assert "content" in error_msg


class TestIntegratedInputValidation:
    """Test integrated input validation functionality."""
    
    def test_validate_input_file_with_valid_file(self):
        """Test integrated input validation with valid file."""
        from lyfe_kt.input_validation import validate_input_file
        
        valid_data = {
            "title": "Test Knowledge Task",
            "description": "This is a comprehensive test description that provides detailed information about the knowledge task and its learning objectives.",
            "target_audience": "intermediate learners",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Understand core concepts", "Apply knowledge practically"],
            "content": "This is the main content section that contains substantial information for learning purposes. It includes multiple sentences and detailed explanations that help learners understand the topic thoroughly."
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_data, f)
            temp_path = f.name
        
        try:
            # Should not raise exception
            result = validate_input_file(temp_path)
            assert isinstance(result, dict), "Valid input should return dictionary"
        finally:
            os.unlink(temp_path)
    
    def test_validate_input_file_with_missing_file(self):
        """Test integrated input validation with missing file."""
        from lyfe_kt.input_validation import validate_input_file, InputValidationError
        
        with pytest.raises(InputValidationError) as exc_info:
            validate_input_file("nonexistent_file.json")
        
        assert "does not exist" in str(exc_info.value).lower()
    
    def test_validate_input_file_with_invalid_json(self):
        """Test integrated input validation with invalid JSON."""
        from lyfe_kt.input_validation import validate_input_file, InputValidationError
        
        invalid_json = '{"title": "Test", "incomplete": true'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(invalid_json)
            temp_path = f.name
        
        try:
            with pytest.raises(InputValidationError) as exc_info:
                validate_input_file(temp_path)
            
            assert "invalid json" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_validate_input_file_with_missing_required_fields(self):
        """Test integrated input validation with missing required fields."""
        from lyfe_kt.input_validation import validate_input_file, InputValidationError
        
        incomplete_data = {
            "title": "Test Title"
            # Missing other required fields
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(incomplete_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(InputValidationError) as exc_info:
                validate_input_file(temp_path)
            
            error_msg = str(exc_info.value).lower()
            assert "missing required fields" in error_msg
        finally:
            os.unlink(temp_path)
    
    def test_validate_input_file_with_poor_content_quality(self):
        """Test integrated input validation with poor content quality."""
        from lyfe_kt.input_validation import validate_input_file, InputValidationError
        
        poor_quality_data = {
            "title": "Test",
            "description": "Short",
            "target_audience": "users",
            "difficulty_level": "easy",
            "learning_objectives": ["learn"],
            "content": "Brief"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(poor_quality_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(InputValidationError) as exc_info:
                validate_input_file(temp_path)
            
            error_msg = str(exc_info.value).lower()
            assert "content quality" in error_msg or "minimum length" in error_msg
        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_input_validation_error_message_clarity(self):
        """Test that error messages are clear and actionable."""
        from lyfe_kt.input_validation import InputValidationError
        
        error = InputValidationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_validation_with_unicode_content(self):
        """Test validation with unicode content."""
        from lyfe_kt.input_validation import validate_input_file
        
        unicode_data = {
            "title": "Título com Acentos",
            "description": "Descrição com caracteres especiais: ção, ñ, ü, é",
            "target_audience": "usuários brasileiros",
            "difficulty_level": "intermediário",
            "learning_objectives": ["Aprender conceitos", "Aplicar conhecimento"],
            "content": "Conteúdo principal com informações detalhadas sobre o tópico. Inclui múltiplas frases e explicações detalhadas que ajudam os aprendizes a entender o tema completamente."
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(unicode_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # Should not raise exception
            result = validate_input_file(temp_path)
            assert isinstance(result, dict), "Unicode content should be handled correctly"
        finally:
            os.unlink(temp_path)
    
    def test_validation_with_large_content(self):
        """Test validation with large content."""
        from lyfe_kt.input_validation import validate_input_file
        
        large_content = "This is a very long content section. " * 1000  # Create large content
        
        large_data = {
            "title": "Large Content Test",
            "description": "This is a test with large content to ensure the validation can handle substantial amounts of text.",
            "target_audience": "advanced learners",
            "difficulty_level": "advanced",
            "learning_objectives": ["Handle large datasets", "Process extensive information"],
            "content": large_content
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(large_data, f)
            temp_path = f.name
        
        try:
            # Should not raise exception
            result = validate_input_file(temp_path)
            assert isinstance(result, dict), "Large content should be handled correctly"
        finally:
            os.unlink(temp_path) 