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


# Stage 1 Preprocessing Commands Group
@main.group(name='preprocess')
@click.pass_context
def preprocess(ctx):
    """
    Stage 1 preprocessing commands for raw content → filled templates.
    
    Transform raw content from multiple file formats into filled markdown templates
    using Ari persona integration and Oracle data context.
    """
    logger = ctx.obj['logger']
    logger.info("Preprocessing command group accessed")


@preprocess.command(name='file')
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--report', is_flag=True, help='Generate processing report')
@click.option('--progress', is_flag=True, help='Show progress information')
@click.pass_context
def preprocess_file(ctx, input_file, output_dir, report, progress):
    """
    Process a single file through Stage 1 preprocessing pipeline.
    
    INPUT_FILE: Path to the input file (.md, .json, .pdf, .txt, .docx)
    OUTPUT_DIR: Directory to save the filled template and analysis files
    """
    logger = ctx.obj['logger']
    
    try:
        from .stage1_preprocessing import preprocess_file as process_file_impl
        
        # Progress callback
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"🔄 [{current}/{total}] {message}")
        
        click.echo(f"🚀 Starting preprocessing of {input_file}")
        
        # Process the file
        result = process_file_impl(
            input_file=input_file,
            output_dir=output_dir,
            progress_callback=progress_callback if progress else None
        )
        
        # Store session ID for potential packaging
        if result.get('session_id'):
            ctx.obj['last_session_id'] = result['session_id']
        
        if result['status'] == 'success':
            click.echo(f"✅ Successfully processed {input_file}")
            click.echo(f"📁 Output directory: {result['output_directory']}")
            
            # Show generated files
            generated_files = result.get('generated_files', {})
            click.echo("\n📄 Generated files:")
            for file_type, file_path in generated_files.items():
                click.echo(f"  • {file_type}: {file_path}")
            
            # Show processing time
            processing_time = result.get('processing_time_seconds', 0)
            click.echo(f"⏱️  Processing time: {processing_time:.2f} seconds")
            
            # Generate report if requested
            if report:
                from .stage1_preprocessing import generate_preprocessing_report
                report_dir = Path(output_dir).parent / 'reports'
                generate_preprocessing_report({'individual_results': [result]}, str(report_dir))
                click.echo(f"📊 Report generated in: {report_dir}")
            
        else:
            click.echo(f"❌ Processing failed: {result.get('error_message', 'Unknown error')}")
            ctx.exit(1)
            
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@preprocess.command(name='directory')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--report', is_flag=True, help='Generate comprehensive processing report')
@click.option('--progress', is_flag=True, help='Show progress information')
@click.pass_context
def preprocess_directory(ctx, input_dir, output_dir, report, progress):
    """
    Process all supported files in a directory through Stage 1 preprocessing.
    
    INPUT_DIR: Directory containing raw content files
    OUTPUT_DIR: Directory to save processed templates (organized by topic)
    """
    logger = ctx.obj['logger']
    
    try:
        from .stage1_preprocessing import preprocess_directory as process_directory_impl
        
        # Progress callback
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"🔄 [{current}/{total}] {message}")
        
        click.echo(f"🚀 Starting batch preprocessing of {input_dir}")
        
        # Process the directory
        result = process_directory_impl(
            input_dir=input_dir,
            output_dir=output_dir,
            progress_callback=progress_callback if progress else None
        )
        
        if result['status'] == 'completed':
            summary = result.get('processing_summary', {})
            click.echo(f"✅ Batch processing completed")
            click.echo(f"📊 Results: {summary.get('successful', 0)}/{summary.get('total_files', 0)} files successful")
            click.echo(f"📈 Success rate: {summary.get('success_rate', 0):.1%}")
            click.echo(f"⏱️  Total time: {summary.get('total_processing_time', 0):.2f} seconds")
            
            # Show cross-file analysis
            cross_analysis = result.get('cross_file_analysis', {})
            if cross_analysis:
                common_themes = cross_analysis.get('common_themes', {})
                if common_themes:
                    click.echo(f"\n🎯 Common themes: {', '.join(list(common_themes.keys())[:5])}")
                
                framework_apps = cross_analysis.get('framework_applications', {})
                if framework_apps:
                    click.echo(f"🧠 Frameworks applied: {len(framework_apps)} different frameworks")
            
            # Generate report if requested or always for batch processing
            if report or True:  # Always generate report for batch processing
                from .stage1_preprocessing import generate_preprocessing_report
                report_dir = Path(output_dir).parent / 'reports'
                generate_preprocessing_report(result, str(report_dir))
                click.echo(f"📊 Comprehensive report generated in: {report_dir}")
            
        else:
            click.echo(f"❌ Batch processing failed")
            ctx.exit(1)
            
    except Exception as e:
        logger.error(f"Batch preprocessing failed: {e}")
        click.echo(f"❌ Error: {e}")
        ctx.exit(1)


@preprocess.command(name='batch')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--comprehensive-reports', is_flag=True, help='Generate comprehensive analysis reports')
@click.option('--progress', is_flag=True, help='Show detailed progress information')
@click.pass_context
def preprocess_batch(ctx, input_dir, output_dir, comprehensive_reports, progress):
    """
    Advanced batch preprocessing with comprehensive reporting.
    
    INPUT_DIR: Directory containing raw content files
    OUTPUT_DIR: Directory to save processed templates with full analysis
    """
    logger = ctx.obj['logger']
    
    try:
        from .stage1_preprocessing import preprocess_directory as process_directory_impl
        
        # Enhanced progress callback
        def progress_callback(current, total, message):
            if progress:
                percentage = (current / total * 100) if total > 0 else 0
                click.echo(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message}")
        
        click.echo(f"🚀 Starting advanced batch preprocessing")
        click.echo(f"📁 Input: {input_dir}")
        click.echo(f"📁 Output: {output_dir}")
        
        # Process the directory
        result = process_directory_impl(
            input_dir=input_dir,
            output_dir=output_dir,
            progress_callback=progress_callback if progress else None
        )
        
        if result['status'] == 'completed':
            summary = result.get('processing_summary', {})
            
            # Detailed success reporting
            click.echo(f"\n✅ Advanced batch processing completed")
            click.echo(f"📊 Processing Summary:")
            click.echo(f"  • Total files: {summary.get('total_files', 0)}")
            click.echo(f"  • Successful: {summary.get('successful', 0)}")
            click.echo(f"  • Failed: {summary.get('failed', 0)}")
            click.echo(f"  • Success rate: {summary.get('success_rate', 0):.1%}")
            click.echo(f"  • Total time: {summary.get('total_processing_time', 0):.2f} seconds")
            
            # Cross-file analysis
            cross_analysis = result.get('cross_file_analysis', {})
            if cross_analysis:
                click.echo(f"\n🎯 Cross-File Analysis:")
                
                common_themes = cross_analysis.get('common_themes', {})
                if common_themes:
                    click.echo(f"  • Common themes: {', '.join(list(common_themes.keys())[:5])}")
                
                complexity_dist = cross_analysis.get('complexity_distribution', {})
                if complexity_dist:
                    click.echo(f"  • Complexity distribution: {complexity_dist}")
                
                framework_apps = cross_analysis.get('framework_applications', {})
                if framework_apps:
                    click.echo(f"  • Top frameworks: {', '.join(list(framework_apps.keys())[:3])}")
            
            # Always generate comprehensive reports for batch processing
            from .stage1_preprocessing import generate_preprocessing_report
            report_dir = Path(output_dir).parent / 'reports'
            generate_preprocessing_report(result, str(report_dir))
            
            click.echo(f"\n📊 Comprehensive reports generated:")
            click.echo(f"  • Report directory: {report_dir}")
            click.echo(f"  • Analysis includes: content patterns, Ari integration, Oracle utilization")
            
            if comprehensive_reports:
                click.echo(f"  • Enhanced analysis: framework applications, quality metrics, recommendations")
            
        else:
            click.echo(f"❌ Advanced batch processing failed")
            ctx.exit(1)
            
    except Exception as e:
        logger.error(f"Advanced batch preprocessing failed: {e}")
        sys.exit(1)


# Stage 3 Generation Commands Group
@main.group(name='generate')
@click.pass_context
def generate(ctx):
    """
    Stage 3 generation commands for filled templates → supertask JSON.
    
    Convert filled markdown templates into platform-ready supertask JSON files
    with exact test.json structure compliance and Ari persona consistency.
    """
    logger = ctx.obj['logger']
    logger.info("Generation command group accessed")


@generate.command(name='template')
@click.argument('template_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--difficulty', type=click.Choice(['beginner', 'advanced', 'both']), 
              default='both', help='Generate specific difficulty level or both (default: both)')
@click.option('--sequence', type=str, help='Custom narrative sequence (e.g., "content → quiz → quote")')
@click.option('--report', type=click.Path(), help='Save processing report to file')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_template(ctx, template_file, output_dir, difficulty, sequence, report, progress):
    """
    Generate supertask JSON from a single filled template.
    
    TEMPLATE_FILE: Path to the filled markdown template
    OUTPUT_DIR: Directory where generated JSON files will be saved
    
    Example:
        lyfe-kt generate template work/02_preprocessed/sample.md work/03_output
    """
    logger = ctx.obj['logger']
    
    try:
        from .stage3_generation import generate_from_template
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🚀 Starting generation from template: {template_file}")
        
        # Determine difficulty settings
        if difficulty == 'both':
            generate_both = True
            specific_difficulty = None
        else:
            generate_both = False
            specific_difficulty = difficulty
        
        result = generate_from_template(
            template_file,
            output_dir,
            generate_both_difficulties=generate_both,
            specific_difficulty=specific_difficulty,
            custom_sequence=sequence,
            progress_callback=progress_callback if progress else None
        )
        
        if result['status'] == 'success':
            click.echo(f"✅ Generation completed successfully!")
            click.echo(f"📁 Output directory: {result['output_directory']}")
            click.echo(f"📄 Generated files: {len(result['generated_files'])}")
            
            for file_path in result['generated_files']:
                click.echo(f"   - {Path(file_path).name}")
            
            click.echo(f"⏱️  Processing time: {result['processing_time_seconds']:.2f} seconds")
            
            # Generate report if requested
            if report:
                from .stage3_generation import generate_generation_report
                report_dir = Path(report).parent
                report_dir.mkdir(parents=True, exist_ok=True)
                
                report_content = generate_generation_report(result)
                with open(report, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                click.echo(f"📊 Report saved to: {report}")
        else:
            click.echo(f"❌ Generation failed: {result.get('error_message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Template generation failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@generate.command(name='directory')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--difficulty', type=click.Choice(['beginner', 'advanced', 'both']), 
              default='both', help='Generate specific difficulty level or both (default: both)')
@click.option('--report', type=click.Path(), help='Save processing report to file')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_directory(ctx, input_dir, output_dir, difficulty, report, progress):
    """
    Generate supertask JSONs from all templates in a directory.
    
    INPUT_DIR: Directory containing filled markdown templates
    OUTPUT_DIR: Directory where generated JSON files will be saved
    
    Example:
        lyfe-kt generate directory work/02_preprocessed work/03_output
    """
    logger = ctx.obj['logger']
    
    try:
        from .stage3_generation import generate_from_directory
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🚀 Starting batch generation from directory: {input_dir}")
        
        # Determine difficulty settings
        generate_both = difficulty == 'both'
        
        result = generate_from_directory(
            input_dir,
            output_dir,
            generate_both_difficulties=generate_both,
            progress_callback=progress_callback if progress else None
        )
        
        if result['status'] == 'completed':
            click.echo(f"✅ Batch generation completed!")
            click.echo(f"📁 Output directory: {result['output_directory']}")
            click.echo(f"📊 Processing summary:")
            click.echo(f"   - Total templates: {result['total_files']}")
            click.echo(f"   - Successful: {result['successful_files']}")
            click.echo(f"   - Failed: {result['failed_files']}")
            click.echo(f"   - Success rate: {result['success_rate']:.1%}")
            click.echo(f"⏱️  Total processing time: {result['processing_time_seconds']:.2f} seconds")
            
            # Show failed files if any
            if result['failed_files_list']:
                click.echo(f"\n❌ Failed files:")
                for failed_file in result['failed_files_list']:
                    click.echo(f"   - {Path(failed_file['file']).name}: {failed_file['error']}")
            
            # Generate report if requested
            if report:
                from .stage3_generation import generate_generation_report
                report_dir = Path(report).parent
                report_dir.mkdir(parents=True, exist_ok=True)
                
                report_content = generate_generation_report(result)
                with open(report, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                click.echo(f"📊 Report saved to: {report}")
        else:
            click.echo(f"❌ Batch generation failed: {result.get('error_message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Directory generation failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@generate.command(name='pipeline')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--difficulty', type=click.Choice(['beginner', 'advanced', 'both']), 
              default='both', help='Generate specific difficulty level or both (default: both)')
@click.option('--report', type=click.Path(), help='Save processing report to file')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_pipeline(ctx, input_dir, output_dir, difficulty, report, progress):
    """
    Run complete Stage 3 generation pipeline with validation.
    
    INPUT_DIR: Directory containing filled markdown templates
    OUTPUT_DIR: Directory where generated JSON files will be saved
    
    This command includes comprehensive validation and quality checks.
    
    Example:
        lyfe-kt generate pipeline work/02_preprocessed work/03_output --report report.md
    """
    logger = ctx.obj['logger']
    
    try:
        from .stage3_generation import generate_from_directory, generate_generation_report
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🚀 Starting complete Stage 3 generation pipeline")
        click.echo(f"📁 Input: {input_dir}")
        click.echo(f"📁 Output: {output_dir}")
        click.echo(f"🎯 Difficulty: {difficulty}")
        
        # Determine difficulty settings
        generate_both = difficulty == 'both'
        
        result = generate_from_directory(
            input_dir,
            output_dir,
            generate_both_difficulties=generate_both,
            progress_callback=progress_callback if progress else None
        )
        
        if result['status'] == 'completed':
            click.echo(f"\n✅ Stage 3 generation pipeline completed successfully!")
            click.echo(f"📊 Final summary:")
            click.echo(f"   - Templates processed: {result['total_files']}")
            click.echo(f"   - JSON files generated: {sum(r.get('generated_count', 0) for r in result['individual_results'] if r.get('status') == 'success')}")
            click.echo(f"   - Success rate: {result['success_rate']:.1%}")
            click.echo(f"   - Total time: {result['processing_time_seconds']:.2f} seconds")
            
            # Quality metrics
            successful_results = [r for r in result['individual_results'] if r.get('status') == 'success']
            if successful_results:
                avg_time = sum(r.get('processing_time_seconds', 0) for r in successful_results) / len(successful_results)
                click.echo(f"   - Average time per template: {avg_time:.2f} seconds")
            
            # Generate comprehensive report
            report_path = report or Path(output_dir) / 'generation_report.md'
            report_dir = Path(report_path).parent
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_content = generate_generation_report(result)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            click.echo(f"📊 Comprehensive report saved to: {report_path}")
            
            if result['failed_files_list']:
                click.echo(f"\n⚠️  {len(result['failed_files_list'])} files failed processing - check report for details")
                sys.exit(1)
        else:
            click.echo(f"❌ Pipeline failed: {result.get('error_message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Generation pipeline failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@main.command()
@click.argument('title', required=False)
@click.option('--output-dir', default='packages', help='Output directory for packages (default: packages)')
@click.option('--keep-work', is_flag=True, help='Keep work directory content after packaging')
@click.option('--session-id', help='Session ID for log correlation (auto-detect if not provided)')
@click.pass_context
def package(ctx, title, output_dir, keep_work, session_id):
    """
    Package pipeline content into organized folders.
    
    Moves all content from work directories to a timestamped package folder
    and cleans up the work directory for the next project.
    
    TITLE: Optional custom package name. If not provided, auto-detects from supertask files.
    
    Examples:
    \b
    # Auto-detect title and package content
    python -m src.lyfe_kt.cli package
    
    # Custom title
    python -m src.lyfe_kt.cli package "naval_wealth_concepts"
    
    # Custom output directory
    python -m src.lyfe_kt.cli package --output-dir "archived_projects"
    
    # Keep work directory content
    python -m src.lyfe_kt.cli package --keep-work
    """
    logger = ctx.obj['logger']
    logger.info("Packaging command accessed")
    
    try:
        from .content_packager import ContentPackager
        
        click.echo("📦 Starting content packaging...")
        
        # Initialize packager
        packager = ContentPackager(work_dir="work", packages_dir=output_dir)
        
        # Auto-detect title if not provided
        if not title:
            detected_title = packager.detect_title()
            click.echo(f"🔍 Auto-detected title: {detected_title}")
            title = detected_title
        
        # Use last session ID if not provided
        if not session_id:
            session_id = ctx.obj.get('last_session_id')
            if session_id:
                click.echo(f"🔗 Using session from last pipeline run: {session_id}")
        
        # Package content
        result = packager.package_content(title=title, keep_work=keep_work, session_id=session_id)
        
        if result["success"]:
            click.echo(f"📁 Created package: {result['package_path']}")
            
            # Show summary
            package_path = Path(result['package_path'])
            if package_path.exists():
                # Count total files in package
                total_files = len(list(package_path.rglob("*")))
                click.echo(f"📋 Packaged {total_files} items")
            
            if not keep_work:
                click.echo("🧹 Cleaned work directory (kept structural folders)")
            else:
                click.echo("📂 Work directory preserved (--keep-work flag)")
                
            click.echo("✅ Content packaged successfully!")
            
        else:
            click.echo(f"❌ Packaging failed: {result['message']}")
            sys.exit(1)
            
    except ImportError as e:
        logger.error(f"Missing dependency for packaging: {e}")
        click.echo(f"❌ Error: Missing dependency - {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Packaging failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@generate.command(name='narrative')
@click.argument('template_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--levels', type=int, default=3, help='Number of learning levels (default: 3)')
@click.option('--progression', type=str, default='foundation → application → mastery',
              help='Learning progression pattern (default: foundation → application → mastery)')
@click.option('--theme', type=str, help='Journey theme (auto-detected from content if not provided)')
@click.option('--continuity', type=click.Choice(['low', 'medium', 'high']), default='medium',
              help='Narrative continuity level (default: medium)')
@click.option('--report', type=click.Path(), help='Save journey report to file')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_narrative(ctx, template_file, output_dir, levels, progression, theme, continuity, report, progress):
    """
    Generate progressive learning narrative from a single template.
    
    Creates multiple interconnected supertasks (beginner → intermediate → advanced)
    forming a complete learning journey with narrative continuity.
    
    TEMPLATE_FILE: Path to the filled markdown template
    OUTPUT_DIR: Directory where generated narrative files will be saved
    
    Example:
        lyfe-kt generate narrative work/02_preprocessed/sample.md work/03_output
        lyfe-kt generate narrative content.md output/ --levels 2 --theme "Mastering Mindfulness"
    """
    logger = ctx.obj['logger']
    
    try:
        from .progressive_narrative import NarrativeSequenceOrchestrator
        from .content_enrichment import ContentEnrichmentEngine
        from .openai_client import OpenAIClient
        import json
        from datetime import datetime
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🎭 Starting progressive narrative generation: {template_file}")
        progress_callback(0, 5, "Initializing narrative generation system")
        
        # Parse progression levels
        level_names = [level.strip() for level in progression.split(' → ')]
        if len(level_names) != levels:
            click.echo(f"⚠️  Warning: Progression has {len(level_names)} levels but --levels is {levels}")
            level_names = level_names[:levels] if len(level_names) > levels else level_names + ['advanced'] * (levels - len(level_names))
        
        progress_callback(1, 5, f"Parsing template and extracting content")
        
        # Read and parse template
        template_path = Path(template_file)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Extract title from template or filename
        title = theme or template_path.stem.replace('_filled_template', '').replace('_', ' ').title()
        
        progress_callback(2, 5, f"Initializing AI systems for {len(level_names)} levels")
        
        # Initialize AI systems with configuration
        from .config_loader import load_config
        config = load_config()
        
        openai_client = OpenAIClient()
        enrichment_engine = ContentEnrichmentEngine(openai_client)
        orchestrator = NarrativeSequenceOrchestrator(enrichment_engine)
        
        progress_callback(3, 5, f"Generating progressive learning journey")
        
        # Generate progressive narrative
        journey = orchestrator.create_progressive_journey(
            source_material=template_content,
            title=title,
            levels=level_names,
            theme=theme
        )
        
        progress_callback(4, 5, "Saving narrative files and generating report")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual supertasks
        saved_files = []
        for level_name, supertask in journey['supertasks'].items():
            filename = f"level_{level_names.index(level_name)+1}_{level_name}.json"
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(supertask, f, indent=2, ensure_ascii=False)
            
            saved_files.append(filename)
            logger.info(f"Saved {level_name} supertask: {filename}")
        
        # Save journey metadata
        metadata_file = output_path / "narrative_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            # Prepare serializable metadata
            serializable_metadata = {
                'levels': journey['metadata']['levels'],
                'theme': journey['metadata']['theme'],
                'total_supertasks': journey['metadata']['total_supertasks'],
                'generated_at': datetime.now().isoformat(),
                'progression': progression,
                'continuity_level': continuity,
                'source_template': str(template_path)
            }
            json.dump(serializable_metadata, f, indent=2, ensure_ascii=False)
        
        # Generate journey report
        report_content = _generate_journey_report(journey, level_names, title, progression)
        report_file = output_path / "narrative_journey_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Save report to custom location if specified
        if report:
            custom_report_path = Path(report)
            custom_report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(custom_report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        progress_callback(5, 5, "Narrative generation completed")
        
        # Success summary
        click.echo("✅ Progressive narrative generation completed!")
        click.echo(f"📁 Output directory: {output_dir}")
        click.echo(f"📄 Generated files: {len(saved_files) + 2}")
        for filename in saved_files:
            click.echo(f"   - {filename}")
        click.echo(f"   - narrative_metadata.json")
        click.echo(f"   - narrative_journey_report.md")
        click.echo(f"🎭 Learning journey: {len(level_names)} levels with narrative continuity")
        
    except ImportError as e:
        logger.error(f"Missing dependency for narrative generation: {e}")
        click.echo(f"❌ Error: Missing dependency - {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Narrative generation failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


def _generate_journey_report(journey: dict, level_names: list, title: str, progression: str) -> str:
    """Generate a comprehensive journey report."""
    try:
        from datetime import datetime
        metadata = journey['metadata']
        supertasks = journey['supertasks']
        
        report_lines = [
            f"# Learning Journey: {title}",
            "",
            "## 🎯 Journey Overview",
            f"**Total Levels**: {len(level_names)}",
            f"**Progression**: {progression}",
            f"**Theme**: {metadata.get('theme', 'N/A')}",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Add level details
        total_duration = 0
        for i, level_name in enumerate(level_names):
            if level_name in supertasks:
                supertask = supertasks[level_name]
                duration = supertask.get('estimatedDuration', 300)
                total_duration += duration
                
                level_emoji = {"foundation": "📚", "application": "🛠️", "mastery": "🎓"}.get(level_name, "⭐")
                
                report_lines.extend([
                    f"## {level_emoji} Level {i+1}: {level_name.capitalize()} ({duration//60}-{(duration+120)//60} min)",
                    f"**Objective**: {_get_level_objective(level_name)}",
                    f"**Items**: {len(supertask.get('flexibleItems', []))}",
                    f"**Reward**: {supertask.get('coinsReward', 100)} coins",
                    ""
                ])
        
        # Add summary
        report_lines.extend([
            "## 📊 Journey Summary",
            f"**Total Estimated Time**: {total_duration//60}-{(total_duration+240)//60} minutes",
            f"**Total Reward**: {sum(st.get('coinsReward', 100) for st in supertasks.values())} coins",
            f"**Learning Path**: Progressive difficulty from basic concepts to mastery",
            "",
            "## 🚀 Getting Started",
            "1. Begin with Level 1 (Foundation) to build core understanding",
            "2. Progress sequentially through each level",
            "3. Each level builds upon previous knowledge",
            "4. Complete all levels for comprehensive mastery",
            "",
            "---",
            "*Generated by Lyfe Supertask Knowledge Generator - Progressive Narrative System*"
        ])
        
        return "\n".join(report_lines)
        
    except Exception as e:
        # Use print since logger may not be available in this context
        print(f"Failed to generate journey report: {e}")
        return f"# Learning Journey Report\n\nError generating detailed report: {e}"


def _get_level_objective(level_name: str) -> str:
    """Get the learning objective for a level."""
    objectives = {
        'foundation': "Understand core concepts and build solid knowledge base",
        'application': "Apply knowledge in practical, real-world scenarios", 
        'mastery': "Integrate concepts and handle complex, nuanced situations"
    }
    return objectives.get(level_name, f"Master {level_name} level concepts")


@generate.command(name='simple')
@click.argument('template_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--difficulty', type=click.Choice(['beginner', 'intermediate', 'advanced']), 
              default='beginner', help='Difficulty level (default: beginner)')
@click.option('--sequence', type=str, default='content → quiz → content → quote → content → quiz',
              help='Content sequence pattern')
@click.option('--theme', type=str, help='Optional theme override')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_simple(ctx, template_file, output_dir, difficulty, sequence, theme, progress):
    """
    Generate single supertask using simplified v2.0 system.
    
    Fast, high-quality generation with minimal processing.
    Uses single AI call for complete supertask creation.
    
    TEMPLATE_FILE: Path to the filled markdown template
    OUTPUT_DIR: Directory where generated JSON will be saved
    
    Example:
        lyfe-kt generate simple content.md output/ --difficulty beginner
        lyfe-kt generate simple content.md output/ --sequence "quote → content → quiz"
    """
    logger = ctx.obj['logger']
    
    try:
        from .simplified_generator import SimplifiedGenerator, GenerationRequest
        from .openai_client import OpenAIClient
        from .config_loader import load_config
        import json
        from pathlib import Path
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🚀 Starting simplified generation: {template_file}")
        progress_callback(0, 4, "Initializing simplified v2.0 system")
        
        # Load configuration
        config = load_config()
        
        # Read template content
        template_path = Path(template_file)
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title = theme or template_path.stem.replace('_filled_template', '').replace('_', ' ').title()
        
        progress_callback(1, 4, "Creating comprehensive AI prompt")
        
        # Initialize simplified generator
        openai_client = OpenAIClient()
        generator = SimplifiedGenerator(openai_client)
        
        # Create generation request
        request = GenerationRequest(
            source_content=content,
            difficulty=difficulty,
            sequence=sequence,
            title=title,
            theme=theme
        )
        
        progress_callback(2, 4, f"Generating {difficulty} supertask with single AI call")
        
        # Generate supertask (single AI call!)
        supertask = generator.generate_supertask(request)
        
        progress_callback(3, 4, "Saving output")
        
        # Save output
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{template_path.stem}_{difficulty}.json"
        output_file = output_path / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(supertask, f, indent=2, ensure_ascii=False)
        
        progress_callback(4, 4, "Generation completed")
        
        # Success summary
        items_count = len(supertask.get('flexibleItems', []))
        duration = supertask.get('estimatedDuration', 0)
        reward = supertask.get('coinsReward', 0)
        
        click.echo("✅ Simplified generation completed!")
        click.echo(f"📁 Output: {output_file}")
        click.echo(f"📊 Content: {items_count} items, {duration//60} min, {reward} coins")
        click.echo(f"⚡ Speed: ~30 seconds (vs 2+ minutes with complex system)")
        
    except ImportError as e:
        logger.error(f"Missing dependency for simplified generation: {e}")
        click.echo(f"❌ Error: Missing dependency - {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Simplified generation failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@generate.command(name='journey')
@click.argument('template_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--levels', type=int, default=3, help='Number of levels (default: 3)')
@click.option('--progression', type=str, default='foundation → application → mastery',
              help='Level progression pattern')
@click.option('--sequence', type=str, default='content → quiz → content → quote → content → quiz',
              help='Content sequence pattern for each level')
@click.option('--theme', type=str, help='Journey theme')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_journey(ctx, template_file, output_dir, levels, progression, sequence, theme, progress):
    """
    Generate progressive learning journey using simplified v2.0 system.
    
    Creates multiple levels in parallel for maximum speed.
    Each level generated with single AI call.
    
    TEMPLATE_FILE: Path to the filled markdown template
    OUTPUT_DIR: Directory where journey files will be saved
    
    Example:
        lyfe-kt generate journey content.md output/
        lyfe-kt generate journey content.md output/ --levels 2 --theme "Mindfulness Mastery"
    """
    logger = ctx.obj['logger']
    
    try:
        from .simplified_generator import SimplifiedNarrativeGenerator, GenerationRequest
        from .openai_client import OpenAIClient
        from .config_loader import load_config
        import json
        from pathlib import Path
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🎭 Starting simplified journey generation: {template_file}")
        progress_callback(0, 5, "Initializing simplified v2.0 journey system")
        
        # Parse progression levels
        level_names = [level.strip() for level in progression.split(' → ')][:levels]
        
        # Load configuration
        config = load_config()
        
        # Read template content
        template_path = Path(template_file)
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title = theme or template_path.stem.replace('_filled_template', '').replace('_', ' ').title()
        
        progress_callback(1, 5, f"Preparing {len(level_names)} levels for parallel generation")
        
        # Initialize simplified narrative generator
        openai_client = OpenAIClient()
        generator = SimplifiedNarrativeGenerator(openai_client)
        
        # Create generation request
        request = GenerationRequest(
            source_content=content,
            difficulty='beginner',  # Will be overridden per level
            sequence=sequence,
            title=title,
            theme=theme
        )
        
        progress_callback(2, 5, f"Generating {len(level_names)} levels in parallel")
        
        # Generate journey (parallel generation!)
        journey = generator.generate_progressive_journey(request, level_names)
        
        progress_callback(3, 5, "Saving journey files")
        
        # Save outputs
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        supertasks = journey['supertasks']
        
        # Save individual level files
        for i, (level_name, supertask) in enumerate(supertasks.items()):
            filename = f"level_{i+1}_{level_name}.json"
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(supertask, f, indent=2, ensure_ascii=False)
            
            saved_files.append(filename)
        
        # Save journey metadata
        metadata_file = output_path / "journey_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(journey['metadata'], f, indent=2, ensure_ascii=False)
        
        # Save journey report
        report_file = output_path / "journey_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(journey['journey_report'])
        
        progress_callback(4, 5, "Journey generation completed")
        
        # Success summary
        total_items = sum(len(st.get('flexibleItems', [])) for st in supertasks.values())
        total_duration = sum(st.get('estimatedDuration', 0) for st in supertasks.values())
        total_reward = sum(st.get('coinsReward', 0) for st in supertasks.values())
        
        click.echo("✅ Simplified journey generation completed!")
        click.echo(f"📁 Output directory: {output_dir}")
        click.echo(f"📄 Generated files: {len(saved_files) + 2}")
        for filename in saved_files:
            click.echo(f"   - {filename}")
        click.echo(f"   - journey_metadata.json")
        click.echo(f"   - journey_report.md")
        click.echo(f"📊 Journey: {len(level_names)} levels, {total_items} items, {total_duration//60} min, {total_reward} coins")
        click.echo(f"⚡ Speed: ~60 seconds (vs 5+ minutes with complex system)")
        
    except ImportError as e:
        logger.error(f"Missing dependency for simplified journey: {e}")
        click.echo(f"❌ Error: Missing dependency - {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Simplified journey generation failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@generate.command(name='comprehensive')
@click.argument('template_file', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('--levels', type=int, default=5, help='Number of levels (default: 5 for full coverage)')
@click.option('--sequence', type=str, default='content → quiz → content → quote → content → quiz',
              help='Content sequence pattern for each level')
@click.option('--theme', type=str, help='Journey theme (auto-detected if not provided)')
@click.option('--validate-coverage', is_flag=True, default=True, help='Validate comprehensive concept coverage')
@click.option('--progress', is_flag=True, help='Show detailed progress')
@click.pass_context
def generate_comprehensive(ctx, template_file, output_dir, levels, sequence, theme, validate_coverage, progress):
    """
    Generate comprehensive journey with full concept coverage validation.
    
    Uses AI-powered concept extraction to ensure ALL source material concepts
    are systematically covered across multiple learning levels. Includes
    coverage validation and improvement suggestions.
    
    TEMPLATE_FILE: Path to the filled markdown template
    OUTPUT_DIR: Directory where comprehensive journey files will be saved
    
    Example:
        lyfe-kt generate comprehensive content.md output/
        lyfe-kt generate comprehensive content.md output/ --levels 5 --validate-coverage
        lyfe-kt generate comprehensive content.md output/ --theme "Arthur Brooks Pillars"
    """
    logger = ctx.obj['logger']
    
    try:
        from .simplified_generator import ComprehensiveNarrativeGenerator, GenerationRequest
        from .openai_client import OpenAIClient
        from .config_loader import load_config
        import json
        from pathlib import Path
        from datetime import datetime
        
        def progress_callback(current, total, message):
            if progress:
                click.echo(f"[{current}/{total}] {message}")
        
        click.echo(f"🎯 Starting comprehensive coverage generation: {template_file}")
        progress_callback(0, 6, "Initializing comprehensive coverage system")
        
        # Load configuration
        config = load_config()
        
        # Read template content
        template_path = Path(template_file)
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title
        title = theme or template_path.stem.replace('_filled_template', '').replace('_', ' ').title()
        
        progress_callback(1, 6, f"Extracting concepts for {levels}-level comprehensive coverage")
        
        # Initialize comprehensive generator
        openai_client = OpenAIClient()
        generator = ComprehensiveNarrativeGenerator(openai_client)
        
        # Create generation request
        request = GenerationRequest(
            source_content=content,
            difficulty='comprehensive',  # Special mode for comprehensive coverage
            sequence=sequence,
            title=title,
            theme=theme
        )
        
        progress_callback(2, 6, "Generating comprehensive journey with concept mapping")
        
        # Generate comprehensive journey
        result = generator.generate_comprehensive_journey(
            request=request,
            num_levels=levels,
            validate_coverage=validate_coverage
        )
        
        progress_callback(3, 6, "Validating concept coverage and generating reports")
        
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save all generated levels
        supertasks = result.get('supertasks', {})
        saved_files = []
        
        for i, (level_name, supertask) in enumerate(supertasks.items(), 1):
            filename = f"level_{i}_{level_name}.json"
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(supertask, f, ensure_ascii=False, indent=2)
            
            saved_files.append(filename)
            logger.info(f"Saved {level_name} level: {file_path}")
        
        progress_callback(4, 6, "Saving comprehensive metadata and reports")
        
        # Save comprehensive metadata
        metadata = result.get('metadata', {})
        metadata_file = output_path / 'comprehensive_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Save comprehensive report
        journey_report = result.get('journey_report', 'No report generated')
        report_file = output_path / 'comprehensive_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(journey_report)
        
        progress_callback(5, 6, "Comprehensive generation completed")
        
        # Display results
        click.echo("✅ Comprehensive coverage generation completed!")
        click.echo(f"📁 Output directory: {output_dir}")
        click.echo(f"📄 Generated files: {len(saved_files) + 2}")
        
        for filename in saved_files:
            click.echo(f"   - {filename}")
        click.echo(f"   - comprehensive_metadata.json")
        click.echo(f"   - comprehensive_report.md")
        
        # Display coverage summary
        coverage_report = metadata.get('coverage_validation', {})
        if coverage_report:
            coverage_score = coverage_report.get('coverage_score', 'N/A')
            click.echo(f"📊 Coverage Score: {coverage_score}{'%' if isinstance(coverage_score, (int, float)) else ''}")
            
            improvements = coverage_report.get('improvement_suggestions', [])
            if improvements and len(improvements) > 0:
                click.echo(f"💡 Improvement suggestions available in report")
        
        total_concepts = metadata.get('total_concepts', 0)
        total_items = sum(len(st.get('flexibleItems', [])) for st in supertasks.values())
        total_duration = sum(st.get('estimatedDuration', 300) for st in supertasks.values())
        total_reward = sum(st.get('coinsReward', 50) for st in supertasks.values())
        
        click.echo(f"📚 Source Concepts: {total_concepts}, Items: {total_items}, Duration: {total_duration//60} min, Reward: {total_reward} coins")
        click.echo(f"⚡ Comprehensive Coverage System: Systematic concept extraction and validation")
        
        progress_callback(6, 6, "All files saved successfully")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        click.echo(f"❌ File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Comprehensive generation failed: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 