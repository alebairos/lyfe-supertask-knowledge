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
from .config_loader import (
    load_config,
    get_config, 
    validate_config,
    load_ari_persona_config,
    validate_ari_config,
    get_ari_persona_config,
    reload_ari_persona_config,
    clear_ari_persona_cache,
    load_preprocessing_prompts,
    validate_preprocessing_prompts_config,
    get_preprocessing_prompts,
    build_preprocessing_prompt,
    get_framework_integration_for_content,
    clear_preprocessing_prompts_cache,
    load_generation_prompts,
    validate_generation_prompts_config,
    get_generation_prompts,
    build_generation_prompt,
    get_difficulty_configuration,
    get_generation_preset,
    validate_generated_json_structure,
    clear_generation_prompts_cache
)

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

# Import Stage 1 preprocessing module
from . import stage1_preprocessing
from .stage1_preprocessing import (
    PreprocessingPipeline,
    ContentExtractor,
    AriIntegrator,
    TemplateGenerator,
    create_preprocessing_pipeline,
    preprocess_file,
    preprocess_directory,
    generate_preprocessing_report,
    PreprocessingError
)

# Import Stage 3 generation module
from . import stage3_generation
from .stage3_generation import (
    GenerationPipeline,
    TemplateProcessor,
    JSONGenerator,
    create_generation_pipeline,
    generate_from_template,
    generate_from_directory,
    generate_generation_report,
    GenerationError
) 