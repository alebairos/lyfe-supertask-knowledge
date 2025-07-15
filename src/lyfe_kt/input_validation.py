"""
Input validation module for Lyfe Supertask Knowledge Generator.

This module provides comprehensive input validation functions to ensure
data quality and consistency throughout the processing pipeline.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .config_loader import get_config


class InputValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_file_exists(file_path: str) -> None:
    """
    Validate that a file exists and is accessible.
    
    Args:
        file_path: Path to the file to validate.
        
    Raises:
        InputValidationError: If file doesn't exist or is not accessible.
    """
    if not file_path or not file_path.strip():
        raise InputValidationError("File path cannot be empty")
    
    path = Path(file_path)
    
    if not path.exists():
        raise InputValidationError(f"File does not exist: {file_path}")
    
    if not path.is_file():
        raise InputValidationError(f"Path is not a file: {file_path}")
    
    if not os.access(file_path, os.R_OK):
        raise InputValidationError(f"File is not readable: {file_path}")


def validate_json_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate that a file contains valid JSON structure.
    
    Args:
        file_path: Path to the JSON file to validate.
        
    Returns:
        Dictionary containing the parsed JSON data.
        
    Raises:
        InputValidationError: If file contains invalid JSON or is not an object.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            if not content:
                raise InputValidationError(f"File is empty: {file_path}")
            
            data = json.loads(content)
            
            if not isinstance(data, dict):
                raise InputValidationError(f"JSON must be an object, not {type(data).__name__}: {file_path}")
            
            return data
            
    except json.JSONDecodeError as e:
        raise InputValidationError(f"Invalid JSON in file {file_path}: {e}")
    except UnicodeDecodeError as e:
        raise InputValidationError(f"File encoding error in {file_path}: {e}")


def validate_required_fields(data: Dict[str, Any], required_fields: Optional[List[str]] = None) -> None:
    """
    Validate that all required fields are present and not empty.
    
    Args:
        data: Dictionary to validate.
        required_fields: List of required field names. If None, uses config defaults.
        
    Raises:
        InputValidationError: If required fields are missing or empty.
    """
    if required_fields is None:
        config = get_config('validation.input')
        required_fields = config.get('required_fields', [])
    
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields:
        raise InputValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    if empty_fields:
        raise InputValidationError(f"Required fields are null or empty: {', '.join(empty_fields)}")


def validate_content_quality(data: Dict[str, Any]) -> None:
    """
    Validate the quality and completeness of content.
    
    Args:
        data: Dictionary containing content to validate.
        
    Raises:
        InputValidationError: If content quality is insufficient.
    """
    config = get_config('validation.content')
    min_length = config.get('min_length', 50)
    
    # Check for essential content fields with different minimum lengths
    content_field_requirements = {
        'title': 5,           # Minimum 5 characters for title
        'description': 20,    # Minimum 20 characters for description
        'content': min_length # Use configured minimum for main content
    }
    
    for field, min_field_length in content_field_requirements.items():
        if field not in data:
            raise InputValidationError(f"Content quality validation failed: missing '{field}' field")
        
        if not isinstance(data[field], str):
            continue
            
        content = data[field].strip()
        if len(content) < min_field_length:
            raise InputValidationError(
                f"Content quality validation failed: '{field}' is too short "
                f"(minimum {min_field_length} characters, got {len(content)})"
            )


def validate_file_size(file_path: str) -> None:
    """
    Validate that file size is within acceptable limits.
    
    Args:
        file_path: Path to the file to validate.
        
    Raises:
        InputValidationError: If file size exceeds limits.
    """
    config = get_config('validation.input')
    max_size_mb = config.get('max_file_size', 10)
    max_size_bytes = max_size_mb * 1024 * 1024
    
    file_size = Path(file_path).stat().st_size
    
    if file_size > max_size_bytes:
        size_mb = file_size / (1024 * 1024)
        raise InputValidationError(
            f"File size {size_mb:.2f}MB exceeds maximum allowed size of {max_size_mb}MB: {file_path}"
        )


def validate_file_extension(file_path: str) -> None:
    """
    Validate that file has an allowed extension.
    
    Args:
        file_path: Path to the file to validate.
        
    Raises:
        InputValidationError: If file extension is not allowed.
    """
    config = get_config('validation.input')
    allowed_extensions = config.get('allowed_extensions', ['.json', '.md', '.markdown'])
    
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise InputValidationError(
            f"File extension '{file_extension}' is not allowed. "
            f"Allowed extensions: {', '.join(allowed_extensions)}"
        )


def validate_input_file(file_path: str) -> Dict[str, Any]:
    """
    Comprehensive validation of an input file.
    
    This function performs all validation checks in sequence:
    1. File existence and accessibility
    2. File size limits
    3. File extension validation
    4. JSON structure validation
    5. Required fields validation
    6. Content quality validation
    
    Args:
        file_path: Path to the input file to validate.
        
    Returns:
        Dictionary containing the validated and parsed data.
        
    Raises:
        InputValidationError: If any validation check fails.
    """
    try:
        # Step 1: Validate file exists and is accessible
        validate_file_exists(file_path)
        
        # Step 2: Validate file size
        validate_file_size(file_path)
        
        # Step 3: Validate file extension (for JSON files)
        file_extension = Path(file_path).suffix.lower()
        if file_extension in ['.json']:
            validate_file_extension(file_path)
        
        # Step 4: Validate JSON structure
        data = validate_json_structure(file_path)
        
        # Step 5: Validate required fields
        validate_required_fields(data)
        
        # Step 6: Validate content quality
        validate_content_quality(data)
        
        return data
        
    except InputValidationError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        # Wrap unexpected errors in InputValidationError
        raise InputValidationError(f"Unexpected error during validation of {file_path}: {e}")


def validate_batch_input(file_paths: List[str]) -> Dict[str, Union[Dict[str, Any], InputValidationError]]:
    """
    Validate multiple input files in batch.
    
    Args:
        file_paths: List of file paths to validate.
        
    Returns:
        Dictionary mapping file paths to either validated data or validation errors.
    """
    results = {}
    
    for file_path in file_paths:
        try:
            results[file_path] = validate_input_file(file_path)
        except InputValidationError as e:
            results[file_path] = e
    
    return results


def get_validation_summary(file_path: str) -> Dict[str, Any]:
    """
    Get a summary of validation results without raising exceptions.
    
    Args:
        file_path: Path to the file to validate.
        
    Returns:
        Dictionary containing validation summary with status and details.
    """
    summary = {
        'file_path': file_path,
        'valid': False,
        'errors': [],
        'warnings': [],
        'data': None
    }
    
    try:
        data = validate_input_file(file_path)
        summary['valid'] = True
        summary['data'] = data
        
        # Add any warnings for non-critical issues
        if isinstance(data.get('title'), str) and len(data['title']) < 10:
            summary['warnings'].append("Title is quite short (less than 10 characters)")
        
        if isinstance(data.get('description'), str) and len(data['description']) < 50:
            summary['warnings'].append("Description is quite short (less than 50 characters)")
            
    except InputValidationError as e:
        summary['errors'].append(str(e))
    except Exception as e:
        summary['errors'].append(f"Unexpected error: {e}")
    
    return summary 