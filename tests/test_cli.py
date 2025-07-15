"""
Test CLI structure and basic functionality.

These tests ensure that:
1. CLI module exists and is importable
2. Main Click command is properly configured
3. Help functionality works correctly
4. CLI entry point can be invoked
5. Basic command structure follows Click conventions
6. Stage 1 commands are properly integrated
"""

import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner
import json
import tempfile
import os


def test_cli_module_exists():
    """Test that CLI module exists and is importable."""
    cli_path = Path("src/lyfe_kt/cli.py")
    assert cli_path.exists(), "CLI module src/lyfe_kt/cli.py must exist"
    assert cli_path.is_file(), "CLI module must be a file, not a directory"


def test_cli_module_importable():
    """Test that CLI module can be imported."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        from lyfe_kt import cli
        assert hasattr(cli, 'main'), "CLI module must have a 'main' function"
    except ImportError as e:
        pytest.fail(f"CLI module could not be imported: {e}")


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
    """Test that CLI is properly integrated with package structure."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Should be able to import CLI from package
    from lyfe_kt import cli
    assert hasattr(cli, 'main'), "Package must expose main CLI function"
    
    # CLI should be importable from package __init__
    import lyfe_kt
    assert hasattr(lyfe_kt, 'cli'), "Package __init__ must import cli module"


def test_cli_error_handling():
    """Test that CLI handles errors gracefully."""
    src_path = Path("src").resolve()
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from lyfe_kt.cli import main
    
    runner = CliRunner()
    # Test with invalid option
    result = runner.invoke(main, ['--invalid-option'])
    
    # Should handle invalid options gracefully
    assert result.exit_code != 0, "Invalid options should result in non-zero exit code"
    assert len(result.output) > 0, "Error output should provide feedback"


# Stage 1 CLI Command Tests
class TestStage1CLI:
    """Test Stage 1 CLI commands."""
    
    def setup_method(self):
        """Set up test environment."""
        src_path = Path("src").resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from lyfe_kt.cli import main
        self.runner = CliRunner()
        self.main = main
    
    def test_stage1_command_group_exists(self):
        """Test that stage1 command group exists."""
        result = self.runner.invoke(self.main, ['stage1', '--help'])
        assert result.exit_code == 0, f"stage1 help failed: {result.output}"
        assert 'Stage 1 commands' in result.output, "stage1 help should describe Stage 1 commands"
        assert 'process-file' in result.output, "stage1 help should list process-file command"
        assert 'process-directory' in result.output, "stage1 help should list process-directory command"
        assert 'generate-report' in result.output, "stage1 help should list generate-report command"
    
    def test_stage1_process_file_help(self):
        """Test that process-file command help works."""
        result = self.runner.invoke(self.main, ['stage1', 'process-file', '--help'])
        assert result.exit_code == 0, f"process-file help failed: {result.output}"
        assert 'Process a single raw content file' in result.output, "process-file help should describe functionality"
        assert 'INPUT_FILE' in result.output, "process-file help should describe INPUT_FILE argument"
        assert 'OUTPUT_FILE' in result.output, "process-file help should describe OUTPUT_FILE argument"
    
    def test_stage1_process_directory_help(self):
        """Test that process-directory command help works."""
        result = self.runner.invoke(self.main, ['stage1', 'process-directory', '--help'])
        assert result.exit_code == 0, f"process-directory help failed: {result.output}"
        assert 'Process all files in a directory' in result.output, "process-directory help should describe functionality"
        assert 'INPUT_DIR' in result.output, "process-directory help should describe INPUT_DIR argument"
        assert 'OUTPUT_DIR' in result.output, "process-directory help should describe OUTPUT_DIR argument"
    
    def test_stage1_generate_report_help(self):
        """Test that generate-report command help works."""
        result = self.runner.invoke(self.main, ['stage1', 'generate-report', '--help'])
        assert result.exit_code == 0, f"generate-report help failed: {result.output}"
        assert 'Generate a processing report' in result.output, "generate-report help should describe functionality"
        assert 'RESULTS_FILE' in result.output, "generate-report help should describe RESULTS_FILE argument"
    
    @patch('lyfe_kt.stage1_integration.process_single_file_stage1')
    def test_stage1_process_file_success(self, mock_process):
        """Test successful single file processing."""
        # Mock successful processing
        mock_process.return_value = {
            'success': True,
            'processing_time_seconds': 1.5,
            'validation_result': {
                'is_valid': True,
                'quality_score': 8.5
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test input file
            input_file = Path(temp_dir) / 'input.json'
            input_file.write_text('{"test": "data"}')
            
            output_file = Path(temp_dir) / 'output.json'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-file', 
                str(input_file), str(output_file)
            ])
            
            assert result.exit_code == 0, f"process-file failed: {result.output}"
            assert '✅ Successfully processed' in result.output, "Should show success message"
            assert 'Processing time:' in result.output, "Should show processing time"
            assert 'Validation passed' in result.output, "Should show validation status"
            
            # Verify mock was called correctly
            mock_process.assert_called_once()
            args, kwargs = mock_process.call_args
            assert kwargs['input_file'] == str(input_file), "Should pass correct input file"
            assert kwargs['output_file'] == str(output_file), "Should pass correct output file"
    
    @patch('lyfe_kt.stage1_integration.process_single_file_stage1')
    def test_stage1_process_file_failure(self, mock_process):
        """Test failed single file processing."""
        # Mock failed processing
        mock_process.return_value = {
            'success': False,
            'error': 'Test error message'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / 'input.json'
            input_file.write_text('{"test": "data"}')
            
            output_file = Path(temp_dir) / 'output.json'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-file', 
                str(input_file), str(output_file)
            ])
            
            assert result.exit_code == 1, "Failed processing should return exit code 1"
            assert '❌ Processing failed' in result.output, "Should show failure message"
            assert 'Test error message' in result.output, "Should show error details"
    
    @patch('lyfe_kt.stage1_integration.process_directory_stage1')
    def test_stage1_process_directory_success(self, mock_process):
        """Test successful directory processing."""
        # Mock successful processing
        mock_process.return_value = {
            'statistics': {
                'total_files': 3,
                'successful_files': 2,
                'failed_files': 1,
                'success_rate': 0.667
            },
            'processing_time_seconds': 5.2,
            'cross_file_analysis': {
                'status': 'completed',
                'dominant_patterns': {
                    'language': 'portuguese',
                    'difficulty': 'intermediate',
                    'archetype': 'habit_formation',
                    'themes': [('motivation', 2), ('routine', 1)]
                }
            },
            'validation_summary': {
                'status': 'completed',
                'total_files_validated': 2,
                'validation_success_rate': 1.0,
                'average_quality_score': 7.8,
                'improvement_recommendations': [
                    'Focus on improving content quality',
                    'Enhance quiz questions'
                ]
            },
            'failed_files': [
                {'file': 'test.json', 'error': 'Test error'}
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / 'input'
            input_dir.mkdir()
            output_dir = Path(temp_dir) / 'output'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-directory', 
                str(input_dir), str(output_dir)
            ])
            
            assert result.exit_code == 1, "Should exit with error code due to failed files"
            assert '📊 Processing Results:' in result.output, "Should show processing results"
            assert 'Total Files: 3' in result.output, "Should show total files"
            assert 'Successful: 2' in result.output, "Should show successful files"
            assert 'Failed: 1' in result.output, "Should show failed files"
            assert '🔍 Cross-File Analysis:' in result.output, "Should show cross-file analysis"
            assert 'Dominant Language: portuguese' in result.output, "Should show dominant language"
            assert '✅ Validation Summary:' in result.output, "Should show validation summary"
            assert 'Avg Quality Score: 7.8' in result.output, "Should show quality score"
            assert '💡 Improvement Recommendations:' in result.output, "Should show recommendations"
            assert '❌ Failed Files:' in result.output, "Should show failed files"
    
    @patch('lyfe_kt.stage1_integration.process_directory_stage1')
    def test_stage1_process_directory_with_continue_on_error(self, mock_process):
        """Test directory processing with continue-on-error flag."""
        # Mock processing with failures
        mock_process.return_value = {
            'statistics': {
                'total_files': 2,
                'successful_files': 1,
                'failed_files': 1,
                'success_rate': 0.5
            },
            'processing_time_seconds': 2.1,
            'failed_files': [
                {'file': 'test.json', 'error': 'Test error'}
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / 'input'
            input_dir.mkdir()
            output_dir = Path(temp_dir) / 'output'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-directory', 
                str(input_dir), str(output_dir),
                '--continue-on-error'
            ])
            
            assert result.exit_code == 0, "Should exit with success when continue-on-error is used"
            assert 'Failed: 1' in result.output, "Should show failed files"
    
    @patch('lyfe_kt.stage1_integration.process_directory_stage1')
    @patch('lyfe_kt.stage1_integration.generate_stage1_report')
    def test_stage1_process_directory_with_report(self, mock_generate_report, mock_process):
        """Test directory processing with report generation."""
        # Mock processing results
        mock_process.return_value = {
            'statistics': {
                'total_files': 1,
                'successful_files': 1,
                'failed_files': 0,
                'success_rate': 1.0
            },
            'processing_time_seconds': 1.0
        }
        
        mock_generate_report.return_value = "# Test Report\nProcessing completed successfully."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / 'input'
            input_dir.mkdir()
            output_dir = Path(temp_dir) / 'output'
            report_file = Path(temp_dir) / 'report.md'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-directory', 
                str(input_dir), str(output_dir),
                '--report', str(report_file)
            ])
            
            assert result.exit_code == 0, f"process-directory with report failed: {result.output}"
            assert f'Processing report saved to: {report_file}' in result.output, "Should show report saved message"
            assert report_file.exists(), "Report file should be created"
            
            # Verify report content
            report_content = report_file.read_text()
            assert "# Test Report" in report_content, "Report should contain expected content"
    
    @patch('lyfe_kt.stage1_integration.generate_stage1_report')
    def test_stage1_generate_report_success(self, mock_generate_report):
        """Test successful report generation."""
        mock_generate_report.return_value = "# Test Report\nProcessing completed successfully."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test results file
            results_file = Path(temp_dir) / 'results.json'
            results_data = {
                'statistics': {
                    'total_files': 1,
                    'successful_files': 1
                }
            }
            results_file.write_text(json.dumps(results_data))
            
            output_file = Path(temp_dir) / 'report.md'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'generate-report', 
                str(results_file),
                '--output', str(output_file)
            ])
            
            assert result.exit_code == 0, f"generate-report failed: {result.output}"
            assert f'Report saved to: {output_file}' in result.output, "Should show report saved message"
            assert output_file.exists(), "Report file should be created"
            
            # Verify report content
            report_content = output_file.read_text()
            assert "# Test Report" in report_content, "Report should contain expected content"
    
    @patch('lyfe_kt.stage1_integration.generate_stage1_report')
    def test_stage1_generate_report_to_stdout(self, mock_generate_report):
        """Test report generation to stdout."""
        mock_generate_report.return_value = "# Test Report\nProcessing completed successfully."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test results file
            results_file = Path(temp_dir) / 'results.json'
            results_data = {
                'statistics': {
                    'total_files': 1,
                    'successful_files': 1
                }
            }
            results_file.write_text(json.dumps(results_data))
            
            result = self.runner.invoke(self.main, [
                'stage1', 'generate-report', 
                str(results_file)
            ])
            
            assert result.exit_code == 0, f"generate-report to stdout failed: {result.output}"
            assert "# Test Report" in result.output, "Should output report to stdout"
            assert "Processing completed successfully." in result.output, "Should show report content"
    
    def test_stage1_process_file_missing_input(self):
        """Test process-file with missing input file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / 'nonexistent.json'
            output_file = Path(temp_dir) / 'output.json'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-file', 
                str(input_file), str(output_file)
            ])
            
            assert result.exit_code == 2, "Should return error code for missing input file"
            assert "does not exist" in result.output, "Should show file not found error"
    
    def test_stage1_process_directory_missing_input(self):
        """Test process-directory with missing input directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / 'nonexistent'
            output_dir = Path(temp_dir) / 'output'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'process-directory', 
                str(input_dir), str(output_dir)
            ])
            
            assert result.exit_code == 2, "Should return error code for missing input directory"
            assert "does not exist" in result.output, "Should show directory not found error"
    
    def test_stage1_generate_report_missing_results(self):
        """Test generate-report with missing results file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_file = Path(temp_dir) / 'nonexistent.json'
            
            result = self.runner.invoke(self.main, [
                'stage1', 'generate-report', 
                str(results_file)
            ])
            
            assert result.exit_code == 2, "Should return error code for missing results file"
            assert "does not exist" in result.output, "Should show file not found error"


class TestCLIIntegration:
    """Test CLI integration with logging and configuration."""
    
    def setup_method(self):
        """Set up test environment."""
        src_path = Path("src").resolve()
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        from lyfe_kt.cli import main
        self.runner = CliRunner()
        self.main = main
    
    def test_cli_logging_integration(self):
        """Test that CLI integrates properly with logging."""
        result = self.runner.invoke(self.main, ['--verbose', 'status'])
        
        assert result.exit_code == 0, f"CLI with verbose logging failed: {result.output}"
        assert "Status: Ready" in result.output, "Should show status output"
    
    def test_cli_log_level_option(self):
        """Test that log level option works."""
        result = self.runner.invoke(self.main, ['--log-level', 'ERROR', 'status'])
        
        assert result.exit_code == 0, f"CLI with log level failed: {result.output}"
        assert "Status: Ready" in result.output, "Should show status output"
    
    def test_cli_log_file_option(self):
        """Test that log file option works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / 'test.log'
            
            result = self.runner.invoke(self.main, [
                '--log-file', str(log_file), 
                'status'
            ])
            
            assert result.exit_code == 0, f"CLI with log file failed: {result.output}"
            assert "Status: Ready" in result.output, "Should show status output" 