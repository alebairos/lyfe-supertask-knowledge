"""
CLI module for Lyfe Supertask Knowledge Generator.

This module provides the main command-line interface using Click.
It serves as the entry point for all CLI operations.
"""

import click
from pathlib import Path
import json
import sys
from . import __version__
from .logging_config import setup_logging, get_logger


@click.group()
@click.version_option(version=__version__, prog_name='lyfe-kt')
@click.help_option('--help', '-h')
@click.option('--log-file', type=click.Path(), help='Path to log file (default: logs/lyfe-kt.log)')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False), 
              default='INFO', help='Set the logging level (default: INFO)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output (DEBUG level)')
@click.pass_context
def main(ctx, log_file, log_level, verbose):
    """
    Lyfe Supertask Knowledge Generator CLI.
    
    A tool for generating knowledge tasks from markdown content using AI.
    Process content through multiple stages to create interactive learning materials.
    """
    # Set up logging
    if verbose:
        log_level = 'DEBUG'
    
    if log_file is None:
        log_file = Path('logs/lyfe-kt.log')
    else:
        log_file = Path(log_file)
    
    setup_logging(log_file=str(log_file), log_level=log_level)
    
    # Store logger in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['logger'] = get_logger('lyfe-kt')


@main.command()
@click.pass_context
def version(ctx):
    """Show version information."""
    logger = ctx.obj['logger']
    logger.info(f"Version command called")
    click.echo(f"Lyfe Supertask Knowledge Generator v{__version__}")


@main.command()
@click.pass_context
def status(ctx):
    """Show current system status."""
    logger = ctx.obj['logger']
    logger.info("Status command called")
    click.echo("Lyfe Supertask Knowledge Generator")
    click.echo(f"Version: {__version__}")
    click.echo("Status: Ready")


# Stage 1 Commands Group
@main.group(name='stage1')
@click.pass_context
def stage1(ctx):
    """
    Stage 1 commands for processing raw content into preprocessed JSON.
    
    Stage 1 transforms raw content (01_raw) into structured, template-compliant
    JSON files (02_preprocessed) with AI-powered content analysis and validation.
    """
    logger = ctx.obj['logger']
    logger.info("Stage 1 command group accessed")


@stage1.command(name='process-file')
@click.argument('input_file', type=click.Path(exists=True, readable=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--no-ai-analysis', is_flag=True, help='Skip AI-powered content analysis')
@click.option('--no-validation', is_flag=True, help='Skip output validation')
@click.option('--config', type=click.Path(exists=True, readable=True, path_type=Path), 
              help='Path to configuration file')
@click.option('--progress', is_flag=True, help='Show progress information')
@click.option('--output-format', type=click.Choice(['json', 'pretty'], case_sensitive=False), 
              default='json', help='Output format (default: json)')
@click.pass_context
def process_file(ctx, input_file, output_file, no_ai_analysis, no_validation, config, progress, output_format):
    """
    Process a single raw content file through Stage 1 pipeline.
    
    INPUT_FILE: Path to the raw content file (JSON, PDF, etc.)
    OUTPUT_FILE: Path where the preprocessed JSON will be saved
    
    Example:
        lyfe-kt stage1 process-file work/01_raw/sample.json work/02_preprocessed/sample.json
    """
    logger = ctx.obj['logger']
    logger.info(f"Processing single file: {input_file} -> {output_file}")
    
    try:
        # Import Stage 1 integration
        from .stage1_integration import process_single_file_stage1
        
        # Progress callback if requested
        def progress_callback(stage, progress_pct, message):
            if progress:
                click.echo(f"[{stage}] {progress_pct:.1f}% - {message}")
        
        # Load configuration if provided
        config_dict = None
        if config:
            logger.info(f"Loading configuration from: {config}")
            try:
                with open(config, 'r') as f:
                    if config.suffix.lower() == '.json':
                        config_dict = json.load(f)
                    elif config.suffix.lower() in ['.yaml', '.yml']:
                        import yaml
                        config_dict = yaml.safe_load(f)
                    else:
                        raise ValueError(f"Unsupported config format: {config.suffix}")
            except Exception as e:
                click.echo(f"Error loading configuration: {e}", err=True)
                sys.exit(1)
        
        # Process the file
        result = process_single_file_stage1(
            input_file=str(input_file),
            output_file=str(output_file),
            include_ai_analysis=not no_ai_analysis,
            include_validation=not no_validation,
            progress_callback=progress_callback if progress else None
        )
        
        # Display results
        if result.get('status') == 'success':
            click.echo(f"✅ Successfully processed: {input_file}")
            click.echo(f"📁 Output saved to: {output_file}")
            
            # Show processing statistics
            if 'processing_time_seconds' in result:
                click.echo(f"⏱️  Processing time: {result['processing_time_seconds']:.2f} seconds")
            
            if 'validation_result' in result and result['validation_result']:
                validation = result['validation_result']
                if validation.get('is_valid', False):
                    click.echo(f"✅ Validation passed (Quality score: {validation.get('quality_score', 0):.1f}/10)")
                else:
                    click.echo(f"⚠️  Validation warnings: {len(validation.get('warnings', []))}")
                    click.echo(f"❌ Validation errors: {len(validation.get('errors', []))}")
            
            # Show output in pretty format if requested
            if output_format == 'pretty' and output_file.exists():
                click.echo("\n📄 Generated content preview:")
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    click.echo(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "...")
        else:
            click.echo(f"❌ Processing failed: {result.get('error_message', result.get('error', 'Unknown error'))}", err=True)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@stage1.command(name='process-directory')
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path))
@click.argument('output_dir', type=click.Path(path_type=Path))
@click.option('--no-ai-analysis', is_flag=True, help='Skip AI-powered content analysis')
@click.option('--no-validation', is_flag=True, help='Skip output validation')
@click.option('--config', type=click.Path(exists=True, readable=True, path_type=Path), 
              help='Path to configuration file')
@click.option('--progress', is_flag=True, help='Show progress information')
@click.option('--pattern', default='*.json', help='File pattern to match (default: *.json)')
@click.option('--report', type=click.Path(path_type=Path), help='Save processing report to file')
@click.option('--save-results', type=click.Path(path_type=Path), help='Save raw JSON results to file for later report generation')
@click.option('--continue-on-error', is_flag=True, help='Continue processing other files if one fails')
@click.pass_context
def process_directory(ctx, input_dir, output_dir, no_ai_analysis, no_validation, config, progress, pattern, report, save_results, continue_on_error):
    """
    Process all files in a directory through Stage 1 pipeline.
    
    INPUT_DIR: Directory containing raw content files
    OUTPUT_DIR: Directory where preprocessed JSON files will be saved
    
    Example:
        lyfe-kt stage1 process-directory work/01_raw work/02_preprocessed
    """
    logger = ctx.obj['logger']
    logger.info(f"Processing directory: {input_dir} -> {output_dir}")
    
    try:
        # Import Stage 1 integration
        from .stage1_integration import process_directory_stage1
        
        # Progress callback if requested
        def progress_callback(stage, progress_pct, message):
            if progress:
                click.echo(f"[{stage}] {progress_pct:.1f}% - {message}")
        
        # Load configuration if provided
        config_dict = None
        if config:
            logger.info(f"Loading configuration from: {config}")
            try:
                with open(config, 'r') as f:
                    if config.suffix.lower() == '.json':
                        config_dict = json.load(f)
                    elif config.suffix.lower() in ['.yaml', '.yml']:
                        import yaml
                        config_dict = yaml.safe_load(f)
                    else:
                        raise ValueError(f"Unsupported config format: {config.suffix}")
            except Exception as e:
                click.echo(f"Error loading configuration: {e}", err=True)
                sys.exit(1)
        
        # Process the directory
        result = process_directory_stage1(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            include_ai_analysis=not no_ai_analysis,
            include_validation=not no_validation,
            progress_callback=progress_callback if progress else None
        )
        
        # Display results
        stats = result.get('statistics', {})
        click.echo(f"\n📊 Processing Results:")
        click.echo(f"📁 Input Directory: {input_dir}")
        click.echo(f"📁 Output Directory: {output_dir}")
        click.echo(f"📄 Total Files: {stats.get('total_files', 0)}")
        click.echo(f"✅ Successful: {stats.get('successful_files', 0)}")
        click.echo(f"❌ Failed: {stats.get('failed_files', 0)}")
        click.echo(f"📈 Success Rate: {stats.get('success_rate', 0):.1%}")
        click.echo(f"⏱️  Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
        
        # Show cross-file analysis if available
        cross_analysis = result.get('cross_file_analysis', {})
        if cross_analysis.get('status') == 'completed':
            dominant = cross_analysis.get('dominant_patterns', {})
            click.echo(f"\n🔍 Cross-File Analysis:")
            click.echo(f"🗣️  Dominant Language: {dominant.get('language', 'N/A')}")
            click.echo(f"📊 Dominant Difficulty: {dominant.get('difficulty', 'N/A')}")
            click.echo(f"🎯 Dominant Archetype: {dominant.get('archetype', 'N/A')}")
            
            themes = dominant.get('themes', [])
            if themes:
                click.echo(f"💡 Top Themes:")
                for theme, count in themes[:3]:
                    click.echo(f"   - {theme}: {count} files")
        
        # Show validation summary if available
        validation = result.get('validation_summary', {})
        if validation.get('status') == 'completed':
            click.echo(f"\n✅ Validation Summary:")
            click.echo(f"📄 Files Validated: {validation.get('total_files_validated', 0)}")
            click.echo(f"📈 Success Rate: {validation.get('validation_success_rate', 0):.1%}")
            click.echo(f"⭐ Avg Quality Score: {validation.get('average_quality_score', 0):.1f}/10")
            
            # Show improvement recommendations
            recommendations = validation.get('improvement_recommendations', [])
            if recommendations:
                click.echo(f"\n💡 Improvement Recommendations:")
                for rec in recommendations[:3]:
                    click.echo(f"   - {rec}")
        
        # Show failed files if any
        failed_files = result.get('failed_files', [])
        if failed_files:
            click.echo(f"\n❌ Failed Files:")
            for failed in failed_files[:5]:  # Show first 5 failures
                click.echo(f"   - {failed.get('file', 'Unknown')}: {failed.get('error', 'Unknown error')}")
            if len(failed_files) > 5:
                click.echo(f"   ... and {len(failed_files) - 5} more")
        
        # Generate and save report if requested
        if report:
            from .stage1_integration import generate_stage1_report
            report_content = generate_stage1_report(result)
            report.parent.mkdir(parents=True, exist_ok=True)
            with open(report, 'w') as f:
                f.write(report_content)
            click.echo(f"\n📄 Processing report saved to: {report}")
        
        # Save raw JSON results if requested
        if save_results:
            save_results.parent.mkdir(parents=True, exist_ok=True)
            with open(save_results, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"\n💾 Raw results saved to: {save_results}")
        
        # Exit with error code if there were failures and continue-on-error is not set
        if stats.get('failed_files', 0) > 0 and not continue_on_error:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error processing directory: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@stage1.command(name='generate-report')
@click.argument('results_file', type=click.Path(exists=True, readable=True, path_type=Path))
@click.option('--output', type=click.Path(path_type=Path), help='Output file for the report (default: stdout)')
@click.option('--format', 'report_format', type=click.Choice(['markdown', 'json', 'text'], case_sensitive=False), 
              default='markdown', help='Report format (default: markdown)')
@click.option('--type', 'report_type', type=click.Choice(['technical', 'content'], case_sensitive=False), 
              default='technical', help='Report type: technical (processing metrics) or content (educational value)')
@click.pass_context
def generate_report(ctx, results_file, output, report_format, report_type):
    """
    Generate a processing report from Stage 1 results.
    
    RESULTS_FILE: Path to the JSON results file from a previous processing run
    
    Report Types:
    - technical: Processing metrics, validation, and technical statistics
    - content: Educational value, learning outcomes, and content analysis
    
    Example:
        lyfe-kt stage1 generate-report results.json --output report.md --type content
    """
    logger = ctx.obj['logger']
    logger.info(f"Generating {report_type} report from: {results_file}")
    
    try:
        # Load results
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Generate appropriate report
        if report_type == 'content':
            from .stage1_integration import generate_content_analysis_report
            report_content = generate_content_analysis_report(results)
        else:
            from .stage1_integration import generate_stage1_report
            report_content = generate_stage1_report(results)
        
        # Output report
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, 'w') as f:
                f.write(report_content)
            click.echo(f"📄 {report_type.title()} report saved to: {output}")
        else:
            click.echo(report_content)
            
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 