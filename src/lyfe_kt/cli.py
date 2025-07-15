"""
CLI module for Lyfe Supertask Knowledge Generator.

This module provides the main command-line interface using Click.
It serves as the entry point for all CLI operations.
"""

import click
from pathlib import Path
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


if __name__ == '__main__':
    main() 