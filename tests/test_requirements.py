"""
Test requirements.txt file structure and dependencies.

These tests ensure that:
1. requirements.txt exists in the project root
2. File contains the minimal required dependencies
3. Dependencies follow proper format (package>=version)
4. No unnecessary or conflicting dependencies are included
"""

import os
import pytest
from pathlib import Path


def test_requirements_file_exists():
    """Test that requirements.txt exists in project root."""
    requirements_path = Path("requirements.txt")
    assert requirements_path.exists(), "requirements.txt file must exist in project root"
    assert requirements_path.is_file(), "requirements.txt must be a file, not a directory"


def test_requirements_file_readable():
    """Test that requirements.txt is readable and not empty."""
    requirements_path = Path("requirements.txt")
    
    # File should be readable
    assert os.access(requirements_path, os.R_OK), "requirements.txt must be readable"
    
    # File should not be empty
    content = requirements_path.read_text().strip()
    assert content, "requirements.txt must not be empty"


def test_required_dependencies_present():
    """Test that all minimal required dependencies are present."""
    requirements_path = Path("requirements.txt")
    content = requirements_path.read_text().lower()
    
    required_packages = [
        "openai",
        "click", 
        "pyyaml",
        "python-dotenv"
    ]
    
    for package in required_packages:
        assert package in content, f"Required package '{package}' must be in requirements.txt"


def test_dependency_format():
    """Test that dependencies follow proper format."""
    requirements_path = Path("requirements.txt")
    lines = requirements_path.read_text().strip().split('\n')
    
    # Filter out empty lines and comments
    dependency_lines = [line.strip() for line in lines 
                       if line.strip() and not line.strip().startswith('#')]
    
    assert len(dependency_lines) > 0, "requirements.txt must contain at least one dependency"
    
    for line in dependency_lines:
        # Each line should contain a package name
        assert len(line.split()) >= 1, f"Invalid dependency format: '{line}'"
        
        # Should not contain spaces in package names (basic validation)
        package_name = line.split('>=')[0].split('==')[0].split('~=')[0].strip()
        assert ' ' not in package_name, f"Package name should not contain spaces: '{package_name}'"


def test_no_conflicting_dependencies():
    """Test that there are no obvious conflicting dependencies."""
    requirements_path = Path("requirements.txt")
    lines = requirements_path.read_text().strip().split('\n')
    
    # Filter out empty lines and comments, get package names
    dependency_lines = [line.strip() for line in lines 
                       if line.strip() and not line.strip().startswith('#')]
    
    package_names = []
    for line in dependency_lines:
        # Extract package name (before version specifier)
        package_name = line.split('>=')[0].split('==')[0].split('~=')[0].strip().lower()
        package_names.append(package_name)
    
    # Check for common conflicting patterns
    conflicting_pairs = [
        ("pyyaml", "ruamel.yaml"),  # Different YAML parsers
        ("python-dotenv", "dotenv"),  # Different env loaders (but not python-dotenv vs dotenv substring)
    ]
    
    for pkg1, pkg2 in conflicting_pairs:
        if pkg1 in package_names and pkg2 in package_names:
            pytest.fail(f"Conflicting dependencies detected: {pkg1} and {pkg2}")


def test_minimal_dependency_count():
    """Test that we maintain minimal dependencies as specified."""
    requirements_path = Path("requirements.txt")
    lines = requirements_path.read_text().strip().split('\n')
    
    # Filter out empty lines and comments
    dependency_lines = [line.strip() for line in lines 
                       if line.strip() and not line.strip().startswith('#')]
    
    # Should have exactly 13 dependencies (4 original + 4 for file processing + 5 for testing)
    expected_count = 13
    assert len(dependency_lines) == expected_count, \
        f"Expected {expected_count} dependencies, found {len(dependency_lines)}: {dependency_lines}"


def test_version_pinning_strategy():
    """Test that dependencies use appropriate version pinning."""
    requirements_path = Path("requirements.txt")
    content = requirements_path.read_text()
    
    # Each dependency should have some version specification
    lines = [line.strip() for line in content.split('\n') 
             if line.strip() and not line.strip().startswith('#')]
    
    for line in lines:
        # Should contain version specifier (>=, ==, ~=, etc.)
        has_version = any(op in line for op in ['>=', '==', '~=', '>', '<'])
        assert has_version, f"Dependency should specify version: '{line}'" 