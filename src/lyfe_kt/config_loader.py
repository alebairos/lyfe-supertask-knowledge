"""
Configuration loader module for Lyfe Supertask Knowledge Generator.

This module provides functions to load, validate, and access configuration
from YAML files with support for environment variables and caching.
Enhanced with Ari persona configuration loading and Oracle data integration.
"""

import os
import yaml
import csv
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv


# Global configuration cache
_config_cache: Optional[Dict[str, Any]] = None
_ari_persona_cache: Optional[Dict[str, Any]] = None
_oracle_data_cache: Optional[Dict[str, Any]] = None
_default_config_path = "src/config/config.yaml"
_default_ari_persona_path = "src/config/ari_persona.yaml"
_oracle_directory = "/Users/alebairos/Projects/mahhp/oracle"

# Global preprocessing prompts cache
_preprocessing_prompts_cache: Optional[Dict[str, Any]] = None
_default_preprocessing_prompts_path = "src/config/preprocessing_prompts.yaml"

# Global generation prompts cache
_generation_prompts_cache: Optional[Dict[str, Any]] = None
_default_generation_prompts_path = "src/config/generation_prompts.yaml"


class AriPersonaConfigError(Exception):
    """Custom exception for Ari persona configuration errors."""
    pass


def load_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable support.
    
    Args:
        config_path: Path to configuration YAML file. If None, uses default path.
        env_file: Path to .env file to load. If None, looks for .env in current directory.
        
    Returns:
        Dictionary containing loaded configuration.
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist.
        yaml.YAMLError: If YAML file is invalid.
        ValueError: If configuration is invalid.
    """
    global _config_cache
    
    # Use default config path if none provided
    if config_path is None:
        config_path = _default_config_path
    
    # Load environment variables
    _load_environment_variables(env_file)
    
    # Load YAML configuration
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in configuration file: {e}")
    
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    
    # Apply environment variable overrides
    config = _apply_environment_overrides(config)
    
    # Validate configuration
    if not validate_config(config):
        raise ValueError("Configuration validation failed")
    
    # Cache the configuration
    _config_cache = config
    
    return config


def load_ari_persona_config(config_path: Optional[str] = None, 
                          include_oracle_data: bool = True,
                          force_reload: bool = False) -> Dict[str, Any]:
    """
    Load Ari persona configuration with Oracle data integration.
    
    Args:
        config_path: Path to Ari persona YAML file. If None, uses default path.
        include_oracle_data: Whether to include filtered Oracle data in configuration.
        force_reload: Whether to force reload even if cached.
        
    Returns:
        Dictionary containing Ari persona configuration with optional Oracle data.
        
    Raises:
        AriPersonaConfigError: If configuration loading or validation fails.
        FileNotFoundError: If configuration file doesn't exist.
    """
    global _ari_persona_cache
    
    # Return cached version if available and not forcing reload
    if not force_reload and _ari_persona_cache is not None:
        return _ari_persona_cache
    
    # Use default config path if none provided
    if config_path is None:
        config_path = _default_ari_persona_path
    
    try:
        # Load Ari persona YAML configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Ari persona configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            ari_config = yaml.safe_load(f)
        
        if not isinstance(ari_config, dict) or 'ari_persona' not in ari_config:
            raise AriPersonaConfigError("Invalid Ari persona configuration structure")
        
        # Validate Ari persona configuration
        validation_result = validate_ari_config(ari_config['ari_persona'])
        if not validation_result['valid']:
            raise AriPersonaConfigError(f"Ari persona validation failed: {validation_result['errors']}")
        
        # Include Oracle data if requested
        if include_oracle_data:
            oracle_data = _load_oracle_data_filtered(ari_config['ari_persona'])
            ari_config['oracle_data'] = oracle_data
        
        # Cache the configuration
        _ari_persona_cache = ari_config
        
        return ari_config
        
    except Exception as e:
        if isinstance(e, (AriPersonaConfigError, FileNotFoundError)):
            raise
        raise AriPersonaConfigError(f"Failed to load Ari persona configuration: {e}")


def validate_ari_config(ari_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate Ari persona configuration structure and content.
    
    Args:
        ari_config: Ari persona configuration dictionary to validate.
        
    Returns:
        Dictionary with validation results including 'valid' boolean and 'errors' list.
    """
    errors = []
    warnings = []
    
    try:
        # Check required top-level sections
        required_sections = [
            'identity', 'communication', 'expert_frameworks', 
            'oracle_integration', 'validation_rules', 'cultural_context'
        ]
        
        for section in required_sections:
            if section not in ari_config:
                errors.append(f"Missing required section: {section}")
        
        # Validate identity section
        if 'identity' in ari_config:
            identity = ari_config['identity']
            required_identity_fields = ['name', 'role', 'personality', 'coaching_philosophy', 'language_forms']
            
            for field in required_identity_fields:
                if field not in identity:
                    errors.append(f"Missing required identity field: {field}")
            
            # Check for correct masculine forms
            if 'identity_markers' in identity:
                markers = identity['identity_markers']
                if 'correct_references' not in markers or not markers['correct_references']:
                    warnings.append("No correct reference examples provided")
        
        # Validate communication section
        if 'communication' in ari_config:
            communication = ari_config['communication']
            required_comm_sections = ['brevity_rules', 'engagement_progression', 'forbidden_phrases']
            
            for section in required_comm_sections:
                if section not in communication:
                    errors.append(f"Missing communication section: {section}")
        
        # Validate expert frameworks (should have exactly 9)
        if 'expert_frameworks' in ari_config:
            frameworks = ari_config['expert_frameworks']
            expected_frameworks = [
                'tiny_habits', 'behavioral_design', 'dopamine_nation', 'molecule_of_more',
                'flourish', 'maslow_hierarchy', 'huberman_protocols', 'scarcity_brain',
                'compassionate_communication'
            ]
            
            for framework in expected_frameworks:
                if framework not in frameworks:
                    errors.append(f"Missing expert framework: {framework}")
                else:
                    # Check framework structure
                    fw = frameworks[framework]
                    required_fw_fields = ['focus', 'application', 'core_principles', 'content_triggers']
                    for field in required_fw_fields:
                        if field not in fw:
                            warnings.append(f"Framework {framework} missing field: {field}")
        
        # Validate Oracle integration section
        if 'oracle_integration' in ari_config:
            oracle = ari_config['oracle_integration']
            if 'data_sources' not in oracle:
                errors.append("Missing Oracle data_sources configuration")
            else:
                required_sources = ['lyfe_coach', 'habits_catalog', 'trails_structure', 'objectives_mapping']
                for source in required_sources:
                    if source not in oracle['data_sources']:
                        errors.append(f"Missing Oracle data source: {source}")
        
    except Exception as e:
        errors.append(f"Configuration validation error: {e}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def _load_oracle_data_filtered(ari_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load and filter Oracle data according to Ari persona configuration.
    
    Args:
        ari_config: Ari persona configuration with Oracle integration settings.
        
    Returns:
        Dictionary containing filtered Oracle data optimized for LLM context.
        
    Raises:
        AriPersonaConfigError: If Oracle data loading fails.
    """
    global _oracle_data_cache
    
    # Return cached data if available
    if _oracle_data_cache is not None:
        return _oracle_data_cache
    
    try:
        oracle_config = ari_config.get('oracle_integration', {})
        data_sources = oracle_config.get('data_sources', {})
        
        oracle_data = {}
        
        # Load LyfeCoach file (complete)
        lyfe_coach_config = data_sources.get('lyfe_coach', {})
        if lyfe_coach_config.get('inclusion') == 'complete':
            lyfe_coach_path = Path(_oracle_directory) / lyfe_coach_config.get('file', 'LyfeCoach')
            if lyfe_coach_path.exists():
                with open(lyfe_coach_path, 'r', encoding='utf-8') as f:
                    oracle_data['lyfe_coach'] = f.read()
        
        # Load and filter habits catalog
        habits_config = data_sources.get('habits_catalog', {})
        if habits_config.get('inclusion') == 'filtered_essential':
            habits_data = _filter_habits_catalog(habits_config)
            oracle_data['habits_catalog'] = habits_data
        
        # Load and filter trails structure
        trails_config = data_sources.get('trails_structure', {})
        if trails_config.get('inclusion') == 'pattern_exemplars':
            trails_data = _filter_trails_structure(trails_config)
            oracle_data['trails_structure'] = trails_data
        
        # Load objectives mapping (complete)
        objectives_config = data_sources.get('objectives_mapping', {})
        if objectives_config.get('inclusion') == 'complete':
            objectives_data = _load_objectives_complete(objectives_config)
            oracle_data['objectives_mapping'] = objectives_data
        
        # Cache the Oracle data
        _oracle_data_cache = oracle_data
        
        return oracle_data
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to load Oracle data: {e}")


def _filter_habits_catalog(habits_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter habits catalog according to configuration rules."""
    habits_file = Path(_oracle_directory) / habits_config.get('file', 'habitos.csv')
    
    if not habits_file.exists():
        return []
    
    filtered_habits = []
    
    try:
        with open(habits_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Calculate total dimension score
                try:
                    dimension_scores = {
                        'R': int(row.get('Relacionamento ', 0) or 0),
                        'TG': int(row.get('Trabalho', 0) or 0),
                        'SF': int(row.get('Saúde física', 0) or 0),
                        'E': int(row.get('Espiritualidade', 0) or 0),
                        'SM': int(row.get('Saúde mental', 0) or 0)
                    }
                    
                    total_score = sum(dimension_scores.values())
                    
                    # Apply filtering rules: include habits with total score >15
                    if total_score > 15:
                        habit_data = {
                            'id': row.get('ID', ''),
                            'habit': row.get('Hábito ', ''),
                            'intensity': row.get('Intensidade', ''),
                            'duration': row.get('Duração ', ''),
                            'dimensions': dimension_scores,
                            'total_score': total_score
                        }
                        filtered_habits.append(habit_data)
                        
                except (ValueError, TypeError):
                    # Skip rows with invalid dimension scores
                    continue
        
        # Sort by total score and limit to maintain size target
        filtered_habits.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Target around 50 high-quality habits for ~8KB
        return filtered_habits[:50]
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to filter habits catalog: {e}")


def _filter_trails_structure(trails_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter trails structure according to configuration rules."""
    trails_file = Path(_oracle_directory) / trails_config.get('file', 'Trilhas.csv')
    
    if not trails_file.exists():
        return []
    
    filtered_trails = []
    
    try:
        with open(trails_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            trails_data = list(reader)
        
        # Group by dimension and select representative examples
        dimension_trails = {}
        for row in trails_data:
            dimension = row.get('Dimensão', '')
            if dimension not in dimension_trails:
                dimension_trails[dimension] = []
            dimension_trails[dimension].append(row)
        
        # Select 2-3 complete trail examples per dimension
        for dimension, trails in dimension_trails.items():
            # Group by trail code to get complete trails
            trail_groups = {}
            for trail in trails:
                trail_code = trail.get('Código Trilha', '')
                if trail_code not in trail_groups:
                    trail_groups[trail_code] = []
                trail_groups[trail_code].append(trail)
            
            # Select up to 2 complete trails per dimension
            selected_trails = list(trail_groups.values())[:2]
            for trail_group in selected_trails:
                filtered_trails.extend(trail_group)
        
        return filtered_trails
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to filter trails structure: {e}")


def _load_objectives_complete(objectives_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Load complete objectives mapping."""
    objectives_file = Path(_oracle_directory) / objectives_config.get('file', 'Objetivos.csv')
    
    if not objectives_file.exists():
        return []
    
    try:
        objectives_data = []
        with open(objectives_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                objective_data = {
                    'dimension': row.get('Dimensão', ''),
                    'id': row.get('ID Objetivo', ''),
                    'description': row.get('Descrição', ''),
                    'trail': row.get('Trilha', '')
                }
                objectives_data.append(objective_data)
        
        return objectives_data
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to load objectives: {e}")


def get_ari_persona_config(key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
    """
    Get Ari persona configuration value(s) from cached configuration.
    
    Args:
        key: Configuration key to retrieve. If None, returns entire config.
             Supports dot notation for nested values (e.g., 'identity.name').
             
    Returns:
        Ari persona configuration value or entire configuration dictionary.
        
    Raises:
        AriPersonaConfigError: If configuration hasn't been loaded yet.
        KeyError: If requested key doesn't exist.
    """
    global _ari_persona_cache
    
    if _ari_persona_cache is None:
        raise AriPersonaConfigError("Ari persona configuration not loaded. Call load_ari_persona_config() first.")
    
    if key is None:
        return _ari_persona_cache
    
    # Handle dot notation for nested keys
    if '.' in key:
        keys = key.split('.')
        value = _ari_persona_cache.get('ari_persona', {})
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                raise KeyError(f"Configuration key not found: {key}")
            value = value[k]
        return value
    
    # Direct key access
    if key in _ari_persona_cache:
        return _ari_persona_cache[key]
    elif key in _ari_persona_cache.get('ari_persona', {}):
        return _ari_persona_cache['ari_persona'][key]
    else:
        raise KeyError(f"Configuration key not found: {key}")


def get_config(key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
    """
    Get configuration value(s) from cached configuration.
    
    Args:
        key: Configuration key to retrieve. If None, returns entire config.
             Supports dot notation for nested values (e.g., 'openai.model').
             
    Returns:
        Configuration value or entire configuration dictionary.
        
    Raises:
        ValueError: If configuration hasn't been loaded yet.
        KeyError: If requested key doesn't exist.
    """
    global _config_cache
    
    if _config_cache is None:
        raise ValueError("Configuration not loaded. Call load_config() first.")
    
    if key is None:
        return _config_cache
    
    # Handle dot notation for nested keys
    if '.' in key:
        keys = key.split('.')
        value = _config_cache
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                raise KeyError(f"Configuration key not found: {key}")
            value = value[k]
        return value
    
    # Direct key access
    if key not in _config_cache:
        raise KeyError(f"Configuration key not found: {key}")
    
    return _config_cache[key]


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary to validate.
        
    Returns:
        True if configuration is valid, False otherwise.
    """
    if not isinstance(config, dict):
        return False
    
    # Required sections
    required_sections = ['openai', 'processing', 'validation', 'logging', 'output']
    for section in required_sections:
        if section not in config:
            return False
        if not isinstance(config[section], dict):
            return False
    
    # Validate OpenAI section
    openai_config = config['openai']
    required_openai_fields = ['model', 'max_tokens', 'temperature', 'timeout']
    for field in required_openai_fields:
        if field not in openai_config:
            return False
    
    # Validate OpenAI field types and ranges
    if not isinstance(openai_config['model'], str):
        return False
    if not isinstance(openai_config['max_tokens'], int) or openai_config['max_tokens'] <= 0:
        return False
    if not isinstance(openai_config['temperature'], (int, float)):
        return False
    if not (0 <= openai_config['temperature'] <= 2):
        return False
    if not isinstance(openai_config['timeout'], int) or openai_config['timeout'] <= 0:
        return False
    
    # Validate processing section
    processing_config = config['processing']
    required_processing_fields = ['stages', 'retry_attempts', 'retry_delay', 'batch_size']
    for field in required_processing_fields:
        if field not in processing_config:
            return False
    
    # Validate processing field types and ranges
    if not isinstance(processing_config['stages'], list) or len(processing_config['stages']) == 0:
        return False
    if not isinstance(processing_config['retry_attempts'], int) or processing_config['retry_attempts'] < 0:
        return False
    if not isinstance(processing_config['retry_delay'], (int, float)) or processing_config['retry_delay'] < 0:
        return False
    if not isinstance(processing_config['batch_size'], int) or processing_config['batch_size'] <= 0:
        return False
    
    # Validate validation section
    validation_config = config['validation']
    required_validation_sections = ['input', 'output', 'content']
    for section in required_validation_sections:
        if section not in validation_config:
            return False
        if not isinstance(validation_config[section], dict):
            return False
    
    # Validate input validation section
    input_validation = validation_config['input']
    if 'required_fields' not in input_validation:
        return False
    if not isinstance(input_validation['required_fields'], list):
        return False
    
    # Validate output validation section
    output_validation = validation_config['output']
    if 'schema' not in output_validation:
        return False
    
    # Validate content validation section
    content_validation = validation_config['content']
    if 'min_length' not in content_validation:
        return False
    if not isinstance(content_validation['min_length'], int):
        return False
    
    # Validate logging section
    logging_config = config['logging']
    required_logging_fields = ['level', 'format', 'file_path']
    for field in required_logging_fields:
        if field not in logging_config:
            return False
    
    # Validate logging field types
    if not isinstance(logging_config['level'], str):
        return False
    if not isinstance(logging_config['format'], str):
        return False
    if not isinstance(logging_config['file_path'], str):
        return False
    
    # Validate logging level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if logging_config['level'] not in valid_levels:
        return False
    
    # Validate output section
    output_config = config['output']
    required_output_fields = ['format', 'directory', 'filename_pattern']
    for field in required_output_fields:
        if field not in output_config:
            return False
    
    # Validate output field types
    if not isinstance(output_config['format'], str):
        return False
    if not isinstance(output_config['directory'], str):
        return False
    if not isinstance(output_config['filename_pattern'], str):
        return False
    
    return True


def load_preprocessing_prompts(config_path: Optional[str] = None, 
                             force_reload: bool = False) -> Dict[str, Any]:
    """
    Load preprocessing prompts configuration for Stage 1 processing.
    
    Args:
        config_path: Path to preprocessing prompts YAML file. If None, uses default path.
        force_reload: Whether to force reload even if cached.
        
    Returns:
        Dictionary containing preprocessing prompts configuration.
        
    Raises:
        AriPersonaConfigError: If configuration loading or validation fails.
        FileNotFoundError: If configuration file doesn't exist.
    """
    global _preprocessing_prompts_cache
    
    # Return cached version if available and not forcing reload
    if not force_reload and _preprocessing_prompts_cache is not None:
        return _preprocessing_prompts_cache
    
    # Use default config path if none provided
    if config_path is None:
        config_path = _default_preprocessing_prompts_path
    
    try:
        # Load preprocessing prompts YAML configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Preprocessing prompts configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            prompts_config = yaml.safe_load(f)
        
        if not isinstance(prompts_config, dict):
            raise AriPersonaConfigError("Invalid preprocessing prompts configuration structure")
        
        # Validate configuration structure
        validation_result = validate_preprocessing_prompts_config(prompts_config)
        if not validation_result['valid']:
            raise AriPersonaConfigError(f"Preprocessing prompts validation failed: {validation_result['errors']}")
        
        # Cache the configuration
        _preprocessing_prompts_cache = prompts_config
        
        return prompts_config
        
    except Exception as e:
        if isinstance(e, (AriPersonaConfigError, FileNotFoundError)):
            raise
        raise AriPersonaConfigError(f"Failed to load preprocessing prompts configuration: {e}")


def validate_preprocessing_prompts_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate preprocessing prompts configuration structure and content.
    
    Args:
        config: Preprocessing prompts configuration dictionary to validate.
        
    Returns:
        Dictionary with validation results including 'valid' boolean and 'errors' list.
    """
    errors = []
    warnings = []
    
    try:
        # Check required top-level sections
        required_sections = [
            'preprocessing_prompts', 'difficulty_configurations', 'validation_rules'
        ]
        
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate preprocessing_prompts section
        if 'preprocessing_prompts' in config:
            preprocessing = config['preprocessing_prompts']
            required_subsections = [
                'main_prompt', 'content_analysis', 'framework_integration', 
                'oracle_integration', 'quality_standards', 'output_format'
            ]
            
            for subsection in required_subsections:
                if subsection not in preprocessing:
                    errors.append(f"Missing preprocessing subsection: {subsection}")
            
            # Validate main_prompt structure
            if 'main_prompt' in preprocessing:
                main_prompt = preprocessing['main_prompt']
                if 'system_message' not in main_prompt:
                    errors.append("Missing system_message in main_prompt")
                if 'user_prompt_template' not in main_prompt:
                    errors.append("Missing user_prompt_template in main_prompt")
            
            # Validate framework_integration (should have all 9 frameworks)
            if 'framework_integration' in preprocessing:
                frameworks = preprocessing['framework_integration']
                expected_frameworks = [
                    'tiny_habits', 'behavioral_design', 'dopamine_nation', 'molecule_of_more',
                    'flourish', 'maslow_hierarchy', 'huberman_protocols', 'scarcity_brain',
                    'compassionate_communication'
                ]
                
                for framework in expected_frameworks:
                    if framework not in frameworks:
                        errors.append(f"Missing framework integration: {framework}")
                    else:
                        fw = frameworks[framework]
                        if 'triggers' not in fw or 'application' not in fw:
                            warnings.append(f"Framework {framework} missing triggers or application")
        
        # Validate difficulty_configurations
        if 'difficulty_configurations' in config:
            difficulties = config['difficulty_configurations']
            required_difficulties = ['beginner', 'advanced']
            
            for difficulty in required_difficulties:
                if difficulty not in difficulties:
                    errors.append(f"Missing difficulty configuration: {difficulty}")
                else:
                    diff_config = difficulties[difficulty]
                    if 'characteristics' not in diff_config or 'content_guidelines' not in diff_config:
                        warnings.append(f"Difficulty {difficulty} missing characteristics or content_guidelines")
        
        # Validate validation_rules
        if 'validation_rules' in config:
            validation = config['validation_rules']
            required_validation_sections = ['required_fields', 'content_validation', 'quality_checks']
            
            for section in required_validation_sections:
                if section not in validation:
                    warnings.append(f"Missing validation section: {section}")
        
    except Exception as e:
        errors.append(f"Configuration validation error: {e}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def get_preprocessing_prompts(key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
    """
    Get preprocessing prompts configuration value(s) from cached configuration.
    
    Args:
        key: Configuration key to retrieve. If None, returns entire config.
             Supports dot notation for nested values (e.g., 'main_prompt.system_message').
             
    Returns:
        Preprocessing prompts configuration value or entire configuration dictionary.
        
    Raises:
        AriPersonaConfigError: If configuration hasn't been loaded yet.
        KeyError: If requested key doesn't exist.
    """
    global _preprocessing_prompts_cache
    
    if _preprocessing_prompts_cache is None:
        raise AriPersonaConfigError("Preprocessing prompts configuration not loaded. Call load_preprocessing_prompts() first.")
    
    if key is None:
        return _preprocessing_prompts_cache
    
    # Handle dot notation for nested keys
    if '.' in key:
        keys = key.split('.')
        value = _preprocessing_prompts_cache
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                raise KeyError(f"Preprocessing prompts key not found: {key}")
            value = value[k]
        return value
    
    # Direct key access
    if key not in _preprocessing_prompts_cache:
        raise KeyError(f"Preprocessing prompts key not found: {key}")
    
    return _preprocessing_prompts_cache[key]


def build_preprocessing_prompt(raw_content: str, 
                             file_type: str,
                             oracle_context: Optional[str] = None,
                             suggested_dimension: Optional[str] = None,
                             target_difficulty: str = "beginner",
                             target_audience: str = "beginner") -> Dict[str, str]:
    """
    Build complete preprocessing prompt for given content and context.
    
    Args:
        raw_content: The raw content to be processed.
        file_type: Type of the input file (md, json, pdf, txt, etc.).
        oracle_context: Filtered Oracle data context (optional).
        suggested_dimension: Suggested dimension for the content (optional).
        target_difficulty: Target difficulty level (beginner/advanced).
        target_audience: Target audience (beginner/advanced).
        
    Returns:
        Dictionary with 'system_message' and 'user_message' for the LLM.
        
    Raises:
        AriPersonaConfigError: If preprocessing prompts configuration not loaded.
    """
    try:
        prompts_config = get_preprocessing_prompts()
        main_prompt = prompts_config['preprocessing_prompts']['main_prompt']
        
        # Get template content
        template_file = Path("src/templates/knowledge_task_input_template.md")
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            template_content = "[Template not found - please provide manually]"
        
        # Build system message
        system_message = main_prompt['system_message']
        
        # Build user message with content substitution
        user_message = main_prompt['user_prompt_template'].format(
            raw_content=raw_content,
            file_type=file_type,
            suggested_dimension=suggested_dimension or "auto-detect",
            target_difficulty=target_difficulty,
            target_audience=target_audience,
            oracle_context=oracle_context or "No specific Oracle context available",
            template_content=template_content
        )
        
        return {
            'system_message': system_message,
            'user_message': user_message
        }
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to build preprocessing prompt: {e}")


def get_framework_integration_for_content(content: str) -> List[Dict[str, Any]]:
    """
    Analyze content and return relevant framework integrations.
    
    Args:
        content: Content to analyze for framework relevance.
        
    Returns:
        List of relevant frameworks with their integration guidelines.
        
    Raises:
        AriPersonaConfigError: If preprocessing prompts configuration not loaded.
    """
    try:
        prompts_config = get_preprocessing_prompts()
        framework_integration = prompts_config['preprocessing_prompts']['framework_integration']
        
        relevant_frameworks = []
        content_lower = content.lower()
        
        for framework_name, framework_config in framework_integration.items():
            # Check if any triggers are found in content
            triggers = framework_config.get('triggers', [])
            for trigger in triggers:
                if trigger.lower() in content_lower:
                    relevant_frameworks.append({
                        'framework': framework_name,
                        'triggers_found': [t for t in triggers if t.lower() in content_lower],
                        'application': framework_config.get('application', ''),
                        'relevance_score': len([t for t in triggers if t.lower() in content_lower])
                    })
                    break
        
        # Sort by relevance score (number of triggers found)
        relevant_frameworks.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return relevant_frameworks
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to get framework integration: {e}")


def load_generation_prompts(config_path: Optional[str] = None, 
                          force_reload: bool = False) -> Dict[str, Any]:
    """
    Load generation prompts configuration for Stage 3 processing.
    
    Args:
        config_path: Path to generation prompts YAML file. If None, uses default path.
        force_reload: Whether to force reload even if cached.
        
    Returns:
        Dictionary containing generation prompts configuration.
        
    Raises:
        AriPersonaConfigError: If configuration loading or validation fails.
        FileNotFoundError: If configuration file doesn't exist.
    """
    global _generation_prompts_cache
    
    # Return cached version if available and not forcing reload
    if not force_reload and _generation_prompts_cache is not None:
        return _generation_prompts_cache
    
    # Use default config path if none provided
    if config_path is None:
        config_path = _default_generation_prompts_path
    
    try:
        # Load generation prompts YAML configuration
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Generation prompts configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            prompts_config = yaml.safe_load(f)
        
        if not isinstance(prompts_config, dict):
            raise AriPersonaConfigError("Invalid generation prompts configuration structure")
        
        # Validate configuration structure
        validation_result = validate_generation_prompts_config(prompts_config)
        if not validation_result['valid']:
            raise AriPersonaConfigError(f"Generation prompts validation failed: {validation_result['errors']}")
        
        # Cache the configuration
        _generation_prompts_cache = prompts_config
        
        return prompts_config
        
    except Exception as e:
        if isinstance(e, (AriPersonaConfigError, FileNotFoundError)):
            raise
        raise AriPersonaConfigError(f"Failed to load generation prompts configuration: {e}")


def validate_generation_prompts_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate generation prompts configuration structure and content.
    
    Args:
        config: Generation prompts configuration dictionary to validate.
        
    Returns:
        Dictionary with validation results including 'valid' boolean and 'errors' list.
    """
    errors = []
    warnings = []
    
    try:
        # Check required top-level sections
        required_sections = [
            'generation_prompts', 'generation_presets', 'output_formatting'
        ]
        
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate generation_prompts section
        if 'generation_prompts' in config:
            generation = config['generation_prompts']
            required_subsections = [
                'main_prompt', 'content_conversion', 'difficulty_generation', 
                'ari_voice_integration', 'json_structure_validation', 'quality_standards'
            ]
            
            for subsection in required_subsections:
                if subsection not in generation:
                    errors.append(f"Missing generation subsection: {subsection}")
            
            # Validate main_prompt structure
            if 'main_prompt' in generation:
                main_prompt = generation['main_prompt']
                if 'system_message' not in main_prompt:
                    errors.append("Missing system_message in main_prompt")
                if 'user_prompt_template' not in main_prompt:
                    errors.append("Missing user_prompt_template in main_prompt")
            
            # Validate difficulty_generation (should have beginner and advanced)
            if 'difficulty_generation' in generation:
                difficulty = generation['difficulty_generation']
                required_difficulties = ['beginner', 'advanced']
                
                for diff in required_difficulties:
                    if diff not in difficulty:
                        errors.append(f"Missing difficulty configuration: {diff}")
                    else:
                        diff_config = difficulty[diff]
                        required_fields = ['title_suffix', 'characteristics', 'content_guidelines']
                        for field in required_fields:
                            if field not in diff_config:
                                warnings.append(f"Difficulty {diff} missing field: {field}")
            
            # Validate json_structure_validation
            if 'json_structure_validation' in generation:
                validation = generation['json_structure_validation']
                required_validation_fields = ['required_fields', 'metadata_required', 'flexibleitems_validation']
                
                for field in required_validation_fields:
                    if field not in validation:
                        warnings.append(f"Missing JSON validation field: {field}")
        
        # Validate generation_presets
        if 'generation_presets' in config:
            presets = config['generation_presets']
            expected_presets = ['default_beginner', 'default_advanced', 'habit_specific', 'generic_learning']
            
            for preset in expected_presets:
                if preset not in presets:
                    warnings.append(f"Missing generation preset: {preset}")
        
        # Validate output_formatting
        if 'output_formatting' in config:
            formatting = config['output_formatting']
            required_formatting_sections = ['json_formatting', 'metadata_generation', 'final_validation']
            
            for section in required_formatting_sections:
                if section not in formatting:
                    warnings.append(f"Missing output formatting section: {section}")
        
    except Exception as e:
        errors.append(f"Configuration validation error: {e}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def get_generation_prompts(key: Optional[str] = None) -> Union[Dict[str, Any], Any]:
    """
    Get generation prompts configuration value(s) from cached configuration.
    
    Args:
        key: Configuration key to retrieve. If None, returns entire config.
             Supports dot notation for nested values (e.g., 'main_prompt.system_message').
             
    Returns:
        Generation prompts configuration value or entire configuration dictionary.
        
    Raises:
        AriPersonaConfigError: If configuration hasn't been loaded yet.
        KeyError: If requested key doesn't exist.
    """
    global _generation_prompts_cache
    
    if _generation_prompts_cache is None:
        raise AriPersonaConfigError("Generation prompts configuration not loaded. Call load_generation_prompts() first.")
    
    if key is None:
        return _generation_prompts_cache
    
    # Handle dot notation for nested keys
    if '.' in key:
        keys = key.split('.')
        value = _generation_prompts_cache
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                raise KeyError(f"Generation prompts key not found: {key}")
            value = value[k]
        return value
    
    # Direct key access
    if key not in _generation_prompts_cache:
        raise KeyError(f"Generation prompts key not found: {key}")
    
    return _generation_prompts_cache[key]


def build_generation_prompt(filled_template: str,
                          target_difficulty: str = "beginner",
                          target_audience: str = "beginner",
                          estimated_duration: int = 300,
                          suggested_coins: int = 15) -> Dict[str, str]:
    """
    Build complete generation prompt for converting filled template to JSON.
    
    Args:
        filled_template: The filled markdown template to be converted.
        target_difficulty: Target difficulty level (beginner/advanced).
        target_audience: Target audience (beginner/advanced).
        estimated_duration: Estimated duration in seconds.
        suggested_coins: Suggested coin reward.
        
    Returns:
        Dictionary with 'system_message' and 'user_message' for the LLM.
        
    Raises:
        AriPersonaConfigError: If generation prompts configuration not loaded.
    """
    try:
        prompts_config = get_generation_prompts()
        main_prompt = prompts_config['generation_prompts']['main_prompt']
        
        # Load target JSON structure from test.json
        target_json_file = Path("work/01_raw/levantar_da_cama/test.json")
        if target_json_file.exists():
            with open(target_json_file, 'r', encoding='utf-8') as f:
                import json
                target_json_structure = json.dumps(json.load(f), indent=2, ensure_ascii=False)
        else:
            target_json_structure = """
{
  "title": "string",
  "dimension": "string",
  "archetype": "string", 
  "relatedToType": "string",
  "relatedToId": "string",
  "estimatedDuration": 0,
  "coinsReward": 0,
  "flexibleItems": [],
  "metadata": {}
}"""
        
        # Build system message
        system_message = main_prompt['system_message']
        
        # Build user message with content substitution
        user_message = main_prompt['user_prompt_template'].format(
            filled_template=filled_template,
            target_json_structure=target_json_structure,
            target_difficulty=target_difficulty,
            target_audience=target_audience,
            estimated_duration=estimated_duration,
            suggested_coins=suggested_coins
        )
        
        return {
            'system_message': system_message,
            'user_message': user_message
        }
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to build generation prompt: {e}")


def get_difficulty_configuration(difficulty: str) -> Dict[str, Any]:
    """
    Get difficulty-specific configuration for content generation.
    
    Args:
        difficulty: Difficulty level ('beginner' or 'advanced').
        
    Returns:
        Dictionary with difficulty-specific configuration.
        
    Raises:
        AriPersonaConfigError: If configuration not loaded or difficulty not found.
    """
    try:
        prompts_config = get_generation_prompts()
        difficulty_configs = prompts_config['generation_prompts']['difficulty_generation']
        
        if difficulty not in difficulty_configs:
            raise KeyError(f"Difficulty configuration not found: {difficulty}")
        
        return difficulty_configs[difficulty]
        
    except Exception as e:
        if isinstance(e, KeyError):
            raise
        raise AriPersonaConfigError(f"Failed to get difficulty configuration: {e}")


def get_generation_preset(preset_name: str) -> Dict[str, Any]:
    """
    Get generation preset configuration.
    
    Args:
        preset_name: Name of the preset (e.g., 'default_beginner', 'habit_specific').
        
    Returns:
        Dictionary with preset configuration.
        
    Raises:
        AriPersonaConfigError: If configuration not loaded or preset not found.
    """
    try:
        prompts_config = get_generation_prompts()
        presets = prompts_config['generation_presets']
        
        if preset_name not in presets:
            raise KeyError(f"Generation preset not found: {preset_name}")
        
        return presets[preset_name]
        
    except Exception as e:
        if isinstance(e, KeyError):
            raise
        raise AriPersonaConfigError(f"Failed to get generation preset: {e}")


def validate_generated_json_structure(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate generated JSON against required structure.
    
    Args:
        json_data: Generated JSON data to validate.
        
    Returns:
        Dictionary with validation results including 'valid' boolean and 'errors' list.
        
    Raises:
        AriPersonaConfigError: If generation prompts configuration not loaded.
    """
    try:
        prompts_config = get_generation_prompts()
        validation_config = prompts_config['generation_prompts']['json_structure_validation']
        
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = validation_config.get('required_fields', [])
        for field in required_fields:
            if field not in json_data:
                errors.append(f"Missing required field: {field}")
        
        # Check metadata required fields
        if 'metadata' in json_data:
            metadata_required = validation_config.get('metadata_required', [])
            metadata = json_data['metadata']
            for field in metadata_required:
                if field not in metadata:
                    errors.append(f"Missing required metadata field: {field}")
        
        # Check flexibleItems structure
        if 'flexibleItems' in json_data:
            flexible_items = json_data['flexibleItems']
            if not isinstance(flexible_items, list):
                errors.append("flexibleItems must be an array")
            else:
                flexible_validation = validation_config.get('flexibleitems_validation', {})
                allowed_types = flexible_validation.get('allowed_types', [])
                
                for i, item in enumerate(flexible_items):
                    if not isinstance(item, dict):
                        errors.append(f"flexibleItems[{i}] must be an object")
                        continue
                    
                    item_type = item.get('type')
                    if item_type not in allowed_types:
                        errors.append(f"flexibleItems[{i}] has invalid type: {item_type}")
                    
                    # Validate based on type
                    if item_type == 'content':
                        content_required = flexible_validation.get('content_required', [])
                        for field in content_required:
                            if field not in item:
                                errors.append(f"flexibleItems[{i}] missing required field: {field}")
                    
                    elif item_type == 'quote':
                        quote_required = flexible_validation.get('quote_required', [])
                        for field in quote_required:
                            if field not in item:
                                errors.append(f"flexibleItems[{i}] missing required field: {field}")
                    
                    elif item_type == 'quiz':
                        quiz_required = flexible_validation.get('quiz_required', [])
                        for field in quiz_required:
                            if field not in item:
                                errors.append(f"flexibleItems[{i}] missing required field: {field}")
        
        # Check data types
        data_types = validation_config.get('data_types', {})
        for field, expected_type in data_types.items():
            if field in json_data:
                value = json_data[field]
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field {field} must be a string")
                elif expected_type == 'integer' and not isinstance(value, int):
                    errors.append(f"Field {field} must be an integer")
                elif expected_type == 'array' and not isinstance(value, list):
                    errors.append(f"Field {field} must be an array")
                elif expected_type == 'object' and not isinstance(value, dict):
                    errors.append(f"Field {field} must be an object")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
    except Exception as e:
        raise AriPersonaConfigError(f"Failed to validate JSON structure: {e}")


def _load_environment_variables(env_file: Optional[str] = None) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file. If None, looks for .env in current directory.
    """
    if env_file:
        # Load specific env file
        load_dotenv(env_file)
    else:
        # Load default .env file if it exists
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)


def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.
    
    Args:
        config: Configuration dictionary to modify.
        
    Returns:
        Modified configuration dictionary.
    """
    # Create a copy to avoid modifying the original
    config = config.copy()
    
    # Check for environment variable overrides
    # Format: LYFE_KT_SECTION_KEY (e.g., LYFE_KT_OPENAI_MODEL)
    for env_key, env_value in os.environ.items():
        if env_key.startswith('LYFE_KT_'):
            # Parse the key
            key_parts = env_key[8:].lower().split('_')  # Remove LYFE_KT_ prefix
            if len(key_parts) >= 2:
                section = key_parts[0]
                field = '_'.join(key_parts[1:])
                
                # Apply override if section exists
                if section in config and isinstance(config[section], dict):
                    # Try to convert value to appropriate type
                    converted_value = _convert_env_value(env_value)
                    config[section][field] = converted_value
    
    return config


def _convert_env_value(value: str) -> Union[str, int, float, bool]:
    """
    Convert environment variable string value to appropriate type.
    
    Args:
        value: String value from environment variable.
        
    Returns:
        Converted value with appropriate type.
    """
    # Try boolean conversion
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # Try integer conversion
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float conversion
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def reload_config(config_path: Optional[str] = None, env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Reload configuration, clearing cache first.
    
    Args:
        config_path: Path to configuration YAML file.
        env_file: Path to .env file to load.
        
    Returns:
        Reloaded configuration dictionary.
    """
    global _config_cache
    _config_cache = None
    return load_config(config_path, env_file)


def clear_config_cache() -> None:
    """Clear the configuration cache."""
    global _config_cache
    _config_cache = None 


def reload_ari_persona_config(config_path: Optional[str] = None, 
                            include_oracle_data: bool = True) -> Dict[str, Any]:
    """
    Reload Ari persona configuration, clearing cache first.
    
    Args:
        config_path: Path to Ari persona YAML file. If None, uses default path.
        include_oracle_data: Whether to include filtered Oracle data.
        
    Returns:
        Reloaded Ari persona configuration dictionary.
    """
    global _ari_persona_cache, _oracle_data_cache
    _ari_persona_cache = None
    _oracle_data_cache = None
    return load_ari_persona_config(config_path, include_oracle_data, force_reload=True)


def clear_ari_persona_cache() -> None:
    """Clear the Ari persona configuration cache."""
    global _ari_persona_cache, _oracle_data_cache
    _ari_persona_cache = None
    _oracle_data_cache = None 


def clear_preprocessing_prompts_cache() -> None:
    """Clear the preprocessing prompts configuration cache."""
    global _preprocessing_prompts_cache
    _preprocessing_prompts_cache = None 


def clear_generation_prompts_cache() -> None:
    """Clear the generation prompts configuration cache."""
    global _generation_prompts_cache
    _generation_prompts_cache = None 