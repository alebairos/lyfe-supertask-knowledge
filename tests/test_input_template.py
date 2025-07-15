"""
Test input template functionality and structure.

These tests ensure that:
1. Input template file exists and is readable
2. Template contains proper frontmatter with required fields
3. Markdown structure is valid and follows expected format
4. Template provides clear guidance for content creation
5. All required sections are present and properly formatted
"""

import sys
import re
from pathlib import Path
import pytest
import yaml


def test_input_template_file_exists():
    """Test that input template file exists and is readable."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    assert template_path.exists(), "Input template file src/templates/knowledge_task_input_template.md must exist"
    assert template_path.is_file(), "Input template must be a file, not a directory"
    
    # Check file is readable
    assert template_path.stat().st_size > 0, "Input template file must not be empty"


def test_input_template_readable():
    """Test that input template can be read and contains content."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    
    try:
        content = template_path.read_text(encoding='utf-8')
        assert len(content.strip()) > 0, "Template content must not be empty"
    except UnicodeDecodeError:
        pytest.fail("Template file must be valid UTF-8 encoded text")


def test_frontmatter_structure():
    """Test that template contains valid YAML frontmatter."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    content = template_path.read_text(encoding='utf-8')
    
    # Check for frontmatter delimiters
    assert content.startswith('---'), "Template must start with YAML frontmatter delimiter (---)"
    
    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    assert frontmatter_match, "Template must contain valid frontmatter block"
    
    frontmatter_content = frontmatter_match.group(1)
    
    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_content)
        assert isinstance(frontmatter, dict), "Frontmatter must be a valid YAML dictionary"
    except yaml.YAMLError as e:
        pytest.fail(f"Frontmatter must be valid YAML: {e}")


def test_required_frontmatter_fields():
    """Test that frontmatter contains all required fields."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    content = template_path.read_text(encoding='utf-8')
    
    # Extract and parse frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    # Required fields for knowledge task input
    required_fields = [
        'title',
        'description', 
        'target_audience',
        'difficulty_level',
        'estimated_time',
        'learning_objectives',
        'prerequisites',
        'tags'
    ]
    
    for field in required_fields:
        assert field in frontmatter, f"Frontmatter must contain required field: {field}"
        assert frontmatter[field] is not None, f"Required field '{field}' must not be null"


def test_frontmatter_field_types():
    """Test that frontmatter fields have correct types."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    content = template_path.read_text(encoding='utf-8')
    
    # Extract and parse frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    
    # Check field types
    assert isinstance(frontmatter['title'], str), "Title must be a string"
    assert isinstance(frontmatter['description'], str), "Description must be a string"
    assert isinstance(frontmatter['target_audience'], str), "Target audience must be a string"
    assert isinstance(frontmatter['difficulty_level'], str), "Difficulty level must be a string"
    assert isinstance(frontmatter['estimated_time'], str), "Estimated time must be a string"
    assert isinstance(frontmatter['learning_objectives'], list), "Learning objectives must be a list"
    assert isinstance(frontmatter['prerequisites'], list), "Prerequisites must be a list"
    assert isinstance(frontmatter['tags'], list), "Tags must be a list"


def test_markdown_structure():
    """Test that template has proper markdown structure."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    content = template_path.read_text(encoding='utf-8')
    
    # Remove frontmatter for markdown analysis
    content_without_frontmatter = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # Check for main sections
    required_sections = [
        '# Content',
        '## Overview',
        '## Main Content',
        '## Key Concepts',
        '## Examples',
        '## Summary'
    ]
    
    for section in required_sections:
        assert section in content_without_frontmatter, f"Template must contain section: {section}"


def test_template_guidance():
    """Test that template provides clear guidance for content creation."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    content = template_path.read_text(encoding='utf-8')
    
    # Check for guidance indicators
    guidance_indicators = [
        '[Replace with',
        '[Provide',
        '[List',
        '[Explain',
        '[Include'
    ]
    
    guidance_found = any(indicator in content for indicator in guidance_indicators)
    assert guidance_found, "Template must contain guidance for content creation"


def test_template_completeness():
    """Test that template is comprehensive and well-structured."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    content = template_path.read_text(encoding='utf-8')
    
    # Check minimum content length (should be substantial)
    assert len(content) > 500, "Template should be comprehensive (>500 characters)"
    
    # Check for multiple sections
    section_count = len(re.findall(r'^#+\s', content, re.MULTILINE))
    assert section_count >= 6, "Template should have at least 6 sections"


def test_template_directory_structure():
    """Test that template is in correct directory structure."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    
    # Check directory exists
    templates_dir = template_path.parent
    assert templates_dir.exists(), "src/templates directory must exist"
    assert templates_dir.is_dir(), "src/templates must be a directory"
    
    # Check it's in the correct location
    assert templates_dir.name == "templates", "Template must be in 'templates' directory"
    assert templates_dir.parent.name == "src", "Templates directory must be in 'src' directory"


def test_template_encoding():
    """Test that template uses proper encoding and formatting."""
    template_path = Path("src/templates/knowledge_task_input_template.md")
    
    # Read as bytes to check encoding
    with open(template_path, 'rb') as f:
        raw_content = f.read()
    
    # Should be valid UTF-8
    try:
        content = raw_content.decode('utf-8')
    except UnicodeDecodeError:
        pytest.fail("Template must use UTF-8 encoding")
    
    # Check for proper line endings (should be consistent)
    assert '\r\n' not in content or '\n' not in content.replace('\r\n', ''), \
        "Template should use consistent line endings" 