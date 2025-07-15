"""
Defensive tests for package structure validation.
Tests that the basic package structure is correctly set up.
"""
import os
import sys
import importlib.util
from pathlib import Path


def test_package_directory_exists():
    """Test that the main package directory exists."""
    package_dir = Path("src/lyfe_kt")
    assert package_dir.exists(), f"Package directory {package_dir} does not exist"
    assert package_dir.is_dir(), f"Package path {package_dir} is not a directory"


def test_package_init_file_exists():
    """Test that the package __init__.py file exists."""
    init_file = Path("src/lyfe_kt/__init__.py")
    assert init_file.exists(), f"Package __init__.py file {init_file} does not exist"
    assert init_file.is_file(), f"Package __init__.py {init_file} is not a file"


def test_package_can_be_imported():
    """Test that the package can be imported without errors."""
    # Add src to Python path for testing
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        import lyfe_kt
        assert hasattr(lyfe_kt, '__version__'), "Package should have __version__ attribute"
    except ImportError as e:
        assert False, f"Failed to import lyfe_kt package: {e}"


def test_package_structure_is_valid():
    """Test that the package structure follows Python conventions."""
    package_dir = Path("src/lyfe_kt")
    
    # Check that it's a valid Python package
    init_file = package_dir / "__init__.py"
    assert init_file.exists(), "Package must have __init__.py file"
    
    # Check that the package directory is readable
    assert os.access(package_dir, os.R_OK), f"Package directory {package_dir} is not readable"
    
    # Check that __init__.py is readable
    assert os.access(init_file, os.R_OK), f"Package __init__.py {init_file} is not readable"


def test_package_has_version():
    """Test that the package defines a version."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        import lyfe_kt
        version = getattr(lyfe_kt, '__version__', None)
        assert version is not None, "Package should define __version__"
        assert isinstance(version, str), "__version__ should be a string"
        assert len(version) > 0, "__version__ should not be empty"
    except ImportError:
        # If import fails, we'll catch it in the import test
        pass


def test_src_directory_exists():
    """Test that the src directory exists."""
    src_dir = Path("src")
    assert src_dir.exists(), f"Source directory {src_dir} does not exist"
    assert src_dir.is_dir(), f"Source path {src_dir} is not a directory"


def test_tests_directory_exists():
    """Test that the tests directory exists."""
    tests_dir = Path("tests")
    assert tests_dir.exists(), f"Tests directory {tests_dir} does not exist"
    assert tests_dir.is_dir(), f"Tests path {tests_dir} is not a directory"


if __name__ == "__main__":
    # Run tests manually if script is executed directly
    import pytest
    pytest.main([__file__, "-v"]) 