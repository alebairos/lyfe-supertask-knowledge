"""
Test CLI structure and basic functionality.

These tests ensure that:
1. CLI module exists and is importable
2. Main Click command is properly configured
3. Help functionality works correctly
4. CLI entry point can be invoked
5. Basic command structure follows Click conventions
"""

import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch
import pytest
from click.testing import CliRunner


def test_cli_module_exists():
    """Test that CLI module exists and is importable."""
    cli_path = Path("src/lyfe_kt/cli.py")
    assert cli_path.exists(), "CLI module src/lyfe_kt/cli.py must exist"
    assert cli_path.is_file(), "CLI module must be a file, not a directory"


def test_cli_module_importable():
    """Test that CLI module can be imported without errors."""
    # Add src to Python path for testing
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        from lyfe_kt import cli
        assert hasattr(cli, 'main'), "CLI module must have a 'main' function"
    except ImportError as e:
        pytest.fail(f"Failed to import CLI module: {e}")


def test_main_command_is_click_command():
    """Test that main command is a proper Click command."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt import cli
    import click
    
    # Main should be a Click command
    assert isinstance(cli.main, click.Command), "main must be a Click command"
    
    # Should have proper Click attributes
    assert hasattr(cli.main, 'name'), "Click command must have a name"
    assert hasattr(cli.main, 'help'), "Click command must have help text"


def test_cli_help_functionality():
    """Test that CLI help works correctly."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.cli import main
    
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    
    # Help should execute successfully
    assert result.exit_code == 0, f"Help command failed with exit code {result.exit_code}: {result.output}"
    
    # Help output should contain expected content
    assert 'Usage:' in result.output, "Help output must contain 'Usage:'"
    assert 'Options:' in result.output, "Help output must contain 'Options:'"


def test_cli_basic_invocation():
    """Test that CLI can be invoked without arguments."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.cli import main
    
    runner = CliRunner()
    result = runner.invoke(main, [])
    
    # Should not crash when invoked without arguments
    assert result.exit_code in [0, 2], f"CLI invocation failed unexpectedly: {result.output}"
    
    # Should show some output (help or main message)
    assert len(result.output.strip()) > 0, "CLI should produce some output when invoked"


def test_cli_command_structure():
    """Test that CLI has proper command structure."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.cli import main
    
    # Main command should have expected attributes
    assert main.name is not None, "Main command must have a name"
    assert main.help is not None, "Main command must have help text"
    
    # Should be a group or command
    import click
    assert isinstance(main, (click.Command, click.Group)), "main must be a Click Command or Group"


def test_cli_package_integration():
    """Test that CLI integrates properly with package structure."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Should be able to import from package
    from lyfe_kt import cli
    from lyfe_kt import __version__
    
    # CLI should be aware of package version
    assert __version__ is not None, "Package version should be available to CLI"


def test_cli_error_handling():
    """Test that CLI handles basic errors gracefully."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.cli import main
    
    runner = CliRunner()
    
    # Test with invalid option
    result = runner.invoke(main, ['--invalid-option'])
    
    # Should handle invalid options gracefully
    assert result.exit_code != 0, "Invalid options should result in non-zero exit code"
    assert 'Error:' in result.output or 'Usage:' in result.output, \
        "Invalid options should show error or usage message" 