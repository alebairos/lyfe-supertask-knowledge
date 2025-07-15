"""
Lyfe Supertask Knowledge Generator

An intelligent system that transforms raw content into structured, 
interactive knowledge tasks for the Lyfe platform.
"""

__version__ = "0.1.0"
__author__ = "Lyfe Team"
__email__ = "dev@lyfe.com"

# Package metadata
__title__ = "lyfe-supertask-knowledge"
__description__ = "Intelligent system for generating knowledge tasks from raw content"
__url__ = "https://github.com/lyfe/supertask-knowledge"

# Import CLI module to make it available
from . import cli

# Import logging configuration module
from . import logging_config

# Import configuration loader module
from . import config_loader

# Import input validation module
from . import input_validation

# Import Stage 1 functions module
from . import stage1_functions
from .stage1_functions import analyze_ari_persona_patterns, process_directory_with_ari_analysis

# Import OpenAI client module
from . import openai_client

# Import content analyzer module
from . import content_analyzer
from .content_analyzer import ContentAnalyzer, get_content_analyzer

# Import JSON normalizer module
from . import json_normalizer
from .json_normalizer import JSONNormalizer, get_json_normalizer 

# Import output validation module
from . import output_validation
from .output_validation import OutputValidator, ValidationResult, validate_output_file, validate_output_directory, generate_validation_report 

# Import Stage 1 integration module
from . import stage1_integration
from .stage1_integration import Stage1Pipeline, create_stage1_pipeline, process_single_file_stage1, process_directory_stage1, generate_stage1_report 