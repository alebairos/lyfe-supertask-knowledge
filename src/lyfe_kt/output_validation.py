"""
Output Validation System for Lyfe Knowledge Task Generator

This module provides comprehensive validation for generated knowledge task JSON output,
ensuring compliance with schema requirements, content quality standards, and platform
integration specifications.

Key Features:
- JSON schema validation against template requirements
- Content quality assessment and scoring
- Ari persona consistency validation
- Learning objective alignment verification
- Quiz quality and difficulty validation
- Metadata completeness and accuracy checks
- Platform integration compatibility validation
- Batch validation support for multiple files
- Detailed validation reporting with actionable feedback

The output validation system serves as the quality gate before knowledge tasks
are integrated into the platform, ensuring consistent high-quality educational content.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import re
from dataclasses import dataclass

from .config_loader import get_config
from .openai_client import OpenAIClient

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Represents the result of output validation."""
    is_valid: bool
    score: float
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]


class OutputValidationError(Exception):
    """Exception raised when output validation fails."""
    pass


class OutputValidator:
    """
    Comprehensive output validation system for knowledge task generation.
    
    This class provides complete validation of generated JSON output against
    schema requirements, content quality standards, and platform specifications.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the output validator.
        
        Args:
            config_path: Optional path to configuration file.
        """
        self.config = get_config()
        self.validation_config = self.config.get('validation', {})
        self.output_config = self.validation_config.get('output', {})
        self.content_config = self.validation_config.get('content', {})
        
        # Initialize OpenAI client for quality assessment (optional for testing)
        try:
            self.openai_client = OpenAIClient()
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}")
            self.openai_client = None
        
        # Define validation schema
        self.schema = self._load_validation_schema()
        
        # Quality thresholds
        self.quality_thresholds = {
            'minimum_score': 7.0,
            'content_length_min': self.content_config.get('min_length', 100),
            'content_length_max': self.content_config.get('max_length', 10000),
            'learning_objectives_min': 3,
            'learning_objectives_max': 8,
            'quiz_items_min': 3,
            'quiz_items_max': 10
        }
    
    def _load_validation_schema(self) -> Dict[str, Any]:
        """Load and return the validation schema."""
        return {
            "type": "object",
            "required": [
                "title", "description", "target_audience", "difficulty_level",
                "learning_objectives", "language", "content", "quiz", "metadata"
            ],
            "properties": {
                "title": {"type": "string", "minLength": 5, "maxLength": 200},
                "description": {"type": "string", "minLength": 20, "maxLength": 1000},
                "target_audience": {"type": "string", "minLength": 3, "maxLength": 100},
                "difficulty_level": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "advanced", "expert"]
                },
                "learning_objectives": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 8,
                    "items": {"type": "string", "minLength": 10}
                },
                "language": {"type": "string", "enum": ["pt", "en", "es"]},
                "content": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["type", "content"],
                        "properties": {
                            "type": {"type": "string"},
                            "content": {"type": "string", "minLength": 10}
                        }
                    }
                },
                "quiz": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 10,
                    "items": {
                        "type": "object",
                        "required": ["question", "options", "correct_answer"],
                        "properties": {
                            "question": {"type": "string", "minLength": 10},
                            "options": {
                                "type": "array",
                                "minItems": 2,
                                "maxItems": 5,
                                "items": {"type": "string", "minLength": 1}
                            },
                            "correct_answer": {"type": "string"}
                        }
                    }
                },
                "metadata": {
                    "type": "object",
                    "required": ["dimension", "archetype", "estimated_duration"],
                    "properties": {
                        "dimension": {"type": "string"},
                        "archetype": {"type": "string"},
                        "estimated_duration": {"type": "integer", "minimum": 60}
                    }
                }
            }
        }
    
    def validate_single_output(self, output_data: Dict[str, Any], file_path: str = "") -> ValidationResult:
        """
        Validate a single generated knowledge task output.
        
        Args:
            output_data: Generated knowledge task data.
            file_path: Optional path to the output file.
            
        Returns:
            ValidationResult with comprehensive validation details.
        """
        try:
            errors = []
            warnings = []
            suggestions = []
            metadata = {
                "file_path": file_path,
                "validation_timestamp": datetime.now().isoformat(),
                "validator_version": "1.0.0"
            }
            
            # 1. Schema validation
            schema_errors = self._validate_schema(output_data)
            errors.extend(schema_errors)
            
            # 2. Content quality validation
            quality_score, quality_warnings, quality_suggestions = self._validate_content_quality(output_data)
            warnings.extend(quality_warnings)
            suggestions.extend(quality_suggestions)
            
            # 3. Ari persona validation
            persona_warnings, persona_suggestions = self._validate_ari_persona(output_data)
            warnings.extend(persona_warnings)
            suggestions.extend(persona_suggestions)
            
            # 4. Learning objectives validation
            objectives_warnings, objectives_suggestions = self._validate_learning_objectives(output_data)
            warnings.extend(objectives_warnings)
            suggestions.extend(objectives_suggestions)
            
            # 5. Quiz validation
            quiz_warnings, quiz_suggestions = self._validate_quiz_quality(output_data)
            warnings.extend(quiz_warnings)
            suggestions.extend(quiz_suggestions)
            
            # 6. Metadata validation
            metadata_warnings, metadata_suggestions = self._validate_metadata(output_data)
            warnings.extend(metadata_warnings)
            suggestions.extend(metadata_suggestions)
            
            # 7. Platform compatibility validation
            platform_warnings, platform_suggestions = self._validate_platform_compatibility(output_data)
            warnings.extend(platform_warnings)
            suggestions.extend(platform_suggestions)
            
            # Calculate overall validation score
            overall_score = self._calculate_validation_score(
                quality_score, len(errors), len(warnings), len(suggestions)
            )
            
            # Add validation metrics to metadata
            metadata.update({
                "quality_score": quality_score,
                "overall_score": overall_score,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "suggestion_count": len(suggestions),
                "schema_compliance": len(schema_errors) == 0,
                "quality_threshold_met": quality_score >= self.quality_thresholds['minimum_score']
            })
            
            # Determine if validation passed
            is_valid = (
                len(errors) == 0 and
                quality_score >= self.quality_thresholds['minimum_score'] and
                overall_score >= 7.0
            )
            
            return ValidationResult(
                is_valid=is_valid,
                score=overall_score,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=[f"Validation system error: {e}"],
                warnings=[],
                suggestions=["Check output format and try again"],
                metadata={"error": str(e)}
            )
    
    def _validate_schema(self, data: Dict[str, Any]) -> List[str]:
        """Validate data against JSON schema."""
        errors = []
        
        try:
            # Check required fields
            for field in self.schema['required']:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
                    continue
                
                # Validate field types and constraints
                field_schema = self.schema['properties'].get(field, {})
                field_value = data[field]
                
                # Type validation
                expected_type = field_schema.get('type')
                if expected_type == 'string' and not isinstance(field_value, str):
                    errors.append(f"Field '{field}' must be a string")
                elif expected_type == 'array' and not isinstance(field_value, list):
                    errors.append(f"Field '{field}' must be an array")
                elif expected_type == 'object' and not isinstance(field_value, dict):
                    errors.append(f"Field '{field}' must be an object")
                elif expected_type == 'integer' and not isinstance(field_value, int):
                    errors.append(f"Field '{field}' must be an integer")
                
                # String length validation
                if expected_type == 'string' and isinstance(field_value, str):
                    min_length = field_schema.get('minLength', 0)
                    max_length = field_schema.get('maxLength', float('inf'))
                    if len(field_value) < min_length:
                        errors.append(f"Field '{field}' is too short (minimum {min_length} characters)")
                    if len(field_value) > max_length:
                        errors.append(f"Field '{field}' is too long (maximum {max_length} characters)")
                
                # Array length validation
                if expected_type == 'array' and isinstance(field_value, list):
                    min_items = field_schema.get('minItems', 0)
                    max_items = field_schema.get('maxItems', float('inf'))
                    if len(field_value) < min_items:
                        errors.append(f"Field '{field}' has too few items (minimum {min_items})")
                    if len(field_value) > max_items:
                        errors.append(f"Field '{field}' has too many items (maximum {max_items})")
                
                # Enum validation
                if 'enum' in field_schema and field_value not in field_schema['enum']:
                    errors.append(f"Field '{field}' has invalid value. Must be one of: {field_schema['enum']}")
            
            # Validate nested structures
            if 'content' in data and isinstance(data['content'], list):
                for i, item in enumerate(data['content']):
                    if not isinstance(item, dict):
                        errors.append(f"Content item {i} must be an object")
                    elif 'content' not in item or not isinstance(item['content'], str):
                        errors.append(f"Content item {i} must have a 'content' field with string value")
            
            if 'quiz' in data and isinstance(data['quiz'], list):
                for i, item in enumerate(data['quiz']):
                    if not isinstance(item, dict):
                        errors.append(f"Quiz item {i} must be an object")
                    else:
                        required_quiz_fields = ['question', 'options', 'correct_answer']
                        for field in required_quiz_fields:
                            if field not in item:
                                errors.append(f"Quiz item {i} missing required field: {field}")
            
        except Exception as e:
            errors.append(f"Schema validation error: {e}")
        
        return errors
    
    def _validate_content_quality(self, data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate content quality and return score, warnings, and suggestions."""
        warnings = []
        suggestions = []
        quality_score = 8.0  # Default score
        
        try:
            # Check content length
            content_items = data.get('content', [])
            total_content_length = sum(len(item.get('content', '')) for item in content_items)
            
            if total_content_length < self.quality_thresholds['content_length_min']:
                warnings.append(f"Content is too short ({total_content_length} chars, minimum {self.quality_thresholds['content_length_min']})")
                quality_score -= 1.0
            
            if total_content_length > self.quality_thresholds['content_length_max']:
                warnings.append(f"Content is too long ({total_content_length} chars, maximum {self.quality_thresholds['content_length_max']})")
                quality_score -= 0.5
            
            # Check content diversity
            content_types = [item.get('type', 'text') for item in content_items]
            if len(set(content_types)) < 2:
                suggestions.append("Consider adding more content variety (text, list, quote, etc.)")
                quality_score -= 0.5
            
            # Check for empty content
            empty_content = [i for i, item in enumerate(content_items) if not item.get('content', '').strip()]
            if empty_content:
                warnings.append(f"Empty content found in items: {empty_content}")
                quality_score -= 1.0
            
            # Check description quality
            description = data.get('description', '')
            if len(description) < 50:
                warnings.append("Description is too brief for effective learning")
                quality_score -= 0.5
            
            # Check title quality
            title = data.get('title', '')
            if not title or len(title) < 10:
                warnings.append("Title is too short or missing")
                quality_score -= 0.5
            
            # Content structure analysis
            if len(content_items) < 3:
                suggestions.append("Consider adding more content sections for better learning progression")
                quality_score -= 0.5
            
        except Exception as e:
            warnings.append(f"Content quality validation error: {e}")
            quality_score = 5.0
        
        return max(0.0, quality_score), warnings, suggestions
    
    def _validate_ari_persona(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate Ari persona consistency in content."""
        warnings = []
        suggestions = []
        
        try:
            # Check for Portuguese masculine forms
            content_text = self._extract_all_text(data)
            
            # Check for common Portuguese masculine patterns
            feminine_patterns = [
                r'\baria\b',  # "aria" instead of "ario" (but not "Ari")
                r'\bsua\s+treinadora\b',  # "sua treinadora" instead of "seu treinador"
                r'\bela\s+é\b',  # "ela é" instead of "ele é"
            ]
            
            for pattern in feminine_patterns:
                if re.search(pattern, content_text, re.IGNORECASE):
                    warnings.append(f"Potential feminine form detected: {pattern}")
                    suggestions.append("Ensure Ari is consistently referred to in masculine forms")
            
            # Check for coaching language
            coaching_indicators = [
                'vamos', 'você pode', 'juntos', 'passo a passo', 'pequenos passos',
                'hábito', 'mudança', 'transformação', 'crescimento'
            ]
            
            coaching_count = sum(1 for indicator in coaching_indicators if indicator in content_text.lower())
            if coaching_count < 3:
                suggestions.append("Consider adding more coaching language to align with Ari's persona")
            
            # Check for brevity (TARS-inspired)
            avg_sentence_length = self._calculate_average_sentence_length(content_text)
            if avg_sentence_length > 25:
                suggestions.append("Consider shorter sentences for better TARS-inspired brevity")
            
        except Exception as e:
            warnings.append(f"Ari persona validation error: {e}")
        
        return warnings, suggestions
    
    def _validate_learning_objectives(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate learning objectives quality and alignment."""
        warnings = []
        suggestions = []
        
        try:
            objectives = data.get('learning_objectives', [])
            
            # Check number of objectives
            if len(objectives) < self.quality_thresholds['learning_objectives_min']:
                warnings.append(f"Too few learning objectives ({len(objectives)}, minimum {self.quality_thresholds['learning_objectives_min']})")
            
            if len(objectives) > self.quality_thresholds['learning_objectives_max']:
                warnings.append(f"Too many learning objectives ({len(objectives)}, maximum {self.quality_thresholds['learning_objectives_max']})")
            
            # Check objective quality
            action_verbs = [
                'identificar', 'explicar', 'aplicar', 'analisar', 'criar', 'avaliar',
                'compreender', 'demonstrar', 'implementar', 'desenvolver'
            ]
            
            for i, objective in enumerate(objectives):
                if not any(verb in objective.lower() for verb in action_verbs):
                    suggestions.append(f"Learning objective {i+1} could use more specific action verbs")
                
                if len(objective) < 20:
                    warnings.append(f"Learning objective {i+1} is too brief")
                
                if not objective.strip():
                    warnings.append(f"Learning objective {i+1} is empty")
            
            # Check for measurability
            measurable_indicators = ['será capaz de', 'poderá', 'conseguirá', 'aprenderá a']
            measurable_count = sum(1 for obj in objectives for indicator in measurable_indicators if indicator in obj.lower())
            
            if measurable_count < len(objectives) * 0.5:
                suggestions.append("Consider making learning objectives more measurable and specific")
            
        except Exception as e:
            warnings.append(f"Learning objectives validation error: {e}")
        
        return warnings, suggestions
    
    def _validate_quiz_quality(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate quiz quality and difficulty."""
        warnings = []
        suggestions = []
        
        try:
            quiz_items = data.get('quiz', [])
            
            # Check number of quiz items
            if len(quiz_items) < self.quality_thresholds['quiz_items_min']:
                warnings.append(f"Too few quiz items ({len(quiz_items)}, minimum {self.quality_thresholds['quiz_items_min']})")
            
            if len(quiz_items) > self.quality_thresholds['quiz_items_max']:
                warnings.append(f"Too many quiz items ({len(quiz_items)}, maximum {self.quality_thresholds['quiz_items_max']})")
            
            # Validate each quiz item
            for i, item in enumerate(quiz_items):
                question = item.get('question', '')
                options = item.get('options', [])
                correct_answer = item.get('correct_answer', '')
                
                # Question quality
                if len(question) < 15:
                    warnings.append(f"Quiz question {i+1} is too short")
                
                if not question.endswith('?'):
                    suggestions.append(f"Quiz question {i+1} should end with a question mark")
                
                # Options validation
                if len(options) < 2:
                    warnings.append(f"Quiz question {i+1} needs at least 2 options")
                
                if len(options) > 5:
                    warnings.append(f"Quiz question {i+1} has too many options (maximum 5)")
                
                # Check for duplicate options
                if len(set(options)) != len(options):
                    warnings.append(f"Quiz question {i+1} has duplicate options")
                
                # Correct answer validation
                if correct_answer not in options:
                    warnings.append(f"Quiz question {i+1} correct answer not found in options")
                
                # Check option length balance
                option_lengths = [len(opt) for opt in options]
                if max(option_lengths) > min(option_lengths) * 3:
                    suggestions.append(f"Quiz question {i+1} options have unbalanced lengths")
            
            # Check question variety
            question_types = []
            for item in quiz_items:
                question = item.get('question', '').lower()
                if question.startswith(('o que', 'qual', 'quais')):
                    question_types.append('what')
                elif question.startswith(('como', 'de que forma')):
                    question_types.append('how')
                elif question.startswith(('por que', 'porque')):
                    question_types.append('why')
                else:
                    question_types.append('other')
            
            if len(set(question_types)) < 2:
                suggestions.append("Consider adding more variety in question types")
            
        except Exception as e:
            warnings.append(f"Quiz validation error: {e}")
        
        return warnings, suggestions
    
    def _validate_metadata(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate metadata completeness and accuracy."""
        warnings = []
        suggestions = []
        
        try:
            metadata = data.get('metadata', {})
            
            # Required metadata fields
            required_fields = ['dimension', 'archetype', 'estimated_duration']
            for field in required_fields:
                if field not in metadata:
                    warnings.append(f"Missing required metadata field: {field}")
            
            # Validate dimension
            valid_dimensions = ['wellness', 'productivity', 'mindfulness', 'nutrition', 'physicalHealth']
            dimension = metadata.get('dimension', '')
            if dimension and dimension not in valid_dimensions:
                warnings.append(f"Invalid dimension: {dimension}. Must be one of: {valid_dimensions}")
            
            # Validate archetype
            valid_archetypes = ['achiever', 'nurturer', 'explorer', 'builder', 'warrior']
            archetype = metadata.get('archetype', '')
            if archetype and archetype not in valid_archetypes:
                warnings.append(f"Invalid archetype: {archetype}. Must be one of: {valid_archetypes}")
            
            # Validate estimated duration
            duration = metadata.get('estimated_duration', 0)
            if duration < 60:
                warnings.append("Estimated duration should be at least 60 seconds")
            elif duration > 3600:
                warnings.append("Estimated duration seems too long (over 1 hour)")
            
            # Check for additional useful metadata
            optional_fields = ['tags', 'difficulty_score', 'prerequisites', 'related_habits']
            missing_optional = [field for field in optional_fields if field not in metadata]
            if missing_optional:
                suggestions.append(f"Consider adding optional metadata: {missing_optional}")
            
        except Exception as e:
            warnings.append(f"Metadata validation error: {e}")
        
        return warnings, suggestions
    
    def _validate_platform_compatibility(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate platform integration compatibility."""
        warnings = []
        suggestions = []
        
        try:
            # Check for platform-specific requirements
            language = data.get('language', '')
            if language != 'pt':
                warnings.append("Content should be in Portuguese for Lyfe platform")
            
            # Check content structure for platform compatibility
            content_items = data.get('content', [])
            supported_types = ['text', 'list', 'quote', 'heading', 'emphasis']
            
            for i, item in enumerate(content_items):
                content_type = item.get('type', 'text')
                if content_type not in supported_types:
                    warnings.append(f"Content item {i+1} has unsupported type: {content_type}")
            
            # Check for image references (should be handled separately)
            all_text = self._extract_all_text(data)
            if 'http' in all_text or 'www.' in all_text:
                suggestions.append("Consider handling external links and images separately")
            
            # Check for proper encoding
            try:
                json.dumps(data, ensure_ascii=False)
            except UnicodeEncodeError:
                warnings.append("Content contains characters that may cause encoding issues")
            
        except Exception as e:
            warnings.append(f"Platform compatibility validation error: {e}")
        
        return warnings, suggestions
    
    def _extract_all_text(self, data: Dict[str, Any]) -> str:
        """Extract all text content from the data structure."""
        text_parts = []
        
        # Extract from main fields
        for field in ['title', 'description']:
            if field in data and isinstance(data[field], str):
                text_parts.append(data[field])
        
        # Extract from learning objectives
        objectives = data.get('learning_objectives', [])
        text_parts.extend(objectives)
        
        # Extract from content items
        content_items = data.get('content', [])
        for item in content_items:
            if 'content' in item:
                text_parts.append(item['content'])
        
        # Extract from quiz
        quiz_items = data.get('quiz', [])
        for item in quiz_items:
            if 'question' in item:
                text_parts.append(item['question'])
            if 'options' in item:
                text_parts.extend(item['options'])
        
        return ' '.join(text_parts)
    
    def _calculate_average_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        total_words = sum(len(sentence.split()) for sentence in sentences)
        return total_words / len(sentences)
    
    def _calculate_validation_score(
        self, 
        quality_score: float, 
        error_count: int, 
        warning_count: int, 
        suggestion_count: int
    ) -> float:
        """Calculate overall validation score."""
        base_score = quality_score
        
        # Deduct points for errors and warnings
        base_score -= error_count * 2.0
        base_score -= warning_count * 0.5
        base_score -= suggestion_count * 0.1
        
        return max(0.0, min(10.0, base_score))
    
    def validate_batch_output(self, output_directory: str) -> Dict[str, ValidationResult]:
        """
        Validate all JSON files in a directory.
        
        Args:
            output_directory: Directory containing JSON output files.
            
        Returns:
            Dictionary mapping file paths to validation results.
        """
        results = {}
        output_path = Path(output_directory)
        
        if not output_path.exists():
            logger.error(f"Output directory does not exist: {output_directory}")
            return results
        
        # Find all JSON files
        json_files = list(output_path.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {output_directory}")
            return results
        
        # Validate each file
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                result = self.validate_single_output(data, str(file_path))
                results[str(file_path)] = result
                
                # Log validation results
                if result.is_valid:
                    logger.info(f"✓ {file_path.name} passed validation (score: {result.score:.1f})")
                else:
                    logger.warning(f"✗ {file_path.name} failed validation (score: {result.score:.1f})")
                    for error in result.errors:
                        logger.error(f"  Error: {error}")
                
            except Exception as e:
                logger.error(f"Failed to validate {file_path}: {e}")
                results[str(file_path)] = ValidationResult(
                    is_valid=False,
                    score=0.0,
                    errors=[f"File processing error: {e}"],
                    warnings=[],
                    suggestions=[],
                    metadata={"file_error": str(e)}
                )
        
        return results
    
    def generate_validation_report(self, results: Dict[str, ValidationResult]) -> str:
        """
        Generate a comprehensive validation report.
        
        Args:
            results: Dictionary of validation results.
            
        Returns:
            Formatted validation report.
        """
        if not results:
            return "No validation results to report."
        
        report_lines = []
        report_lines.append("# Output Validation Report")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Summary statistics
        total_files = len(results)
        valid_files = sum(1 for r in results.values() if r.is_valid)
        avg_score = sum(r.score for r in results.values()) / total_files if total_files > 0 else 0
        
        report_lines.append("## Summary")
        report_lines.append(f"- Total files validated: {total_files}")
        report_lines.append(f"- Files passed validation: {valid_files}")
        report_lines.append(f"- Files failed validation: {total_files - valid_files}")
        report_lines.append(f"- Average validation score: {avg_score:.2f}/10.0")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("## Detailed Results")
        
        for file_path, result in results.items():
            file_name = Path(file_path).name
            status = "✓ PASSED" if result.is_valid else "✗ FAILED"
            
            report_lines.append(f"### {file_name} - {status}")
            report_lines.append(f"**Score:** {result.score:.2f}/10.0")
            
            if result.errors:
                report_lines.append("**Errors:**")
                for error in result.errors:
                    report_lines.append(f"- {error}")
            
            if result.warnings:
                report_lines.append("**Warnings:**")
                for warning in result.warnings:
                    report_lines.append(f"- {warning}")
            
            if result.suggestions:
                report_lines.append("**Suggestions:**")
                for suggestion in result.suggestions:
                    report_lines.append(f"- {suggestion}")
            
            report_lines.append("")
        
        return "\n".join(report_lines)


# Global convenience functions
def validate_output_file(file_path: str) -> ValidationResult:
    """
    Validate a single output file.
    
    Args:
        file_path: Path to the JSON output file.
        
    Returns:
        ValidationResult with validation details.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        validator = OutputValidator()
        return validator.validate_single_output(data, file_path)
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            score=0.0,
            errors=[f"File processing error: {e}"],
            warnings=[],
            suggestions=[],
            metadata={"file_error": str(e)}
        )


def validate_output_directory(directory_path: str) -> Dict[str, ValidationResult]:
    """
    Validate all JSON files in a directory.
    
    Args:
        directory_path: Path to directory containing JSON files.
        
    Returns:
        Dictionary mapping file paths to validation results.
    """
    validator = OutputValidator()
    return validator.validate_batch_output(directory_path)


def generate_validation_report(results: Dict[str, ValidationResult]) -> str:
    """
    Generate validation report from results.
    
    Args:
        results: Dictionary of validation results.
        
    Returns:
        Formatted validation report.
    """
    validator = OutputValidator()
    return validator.generate_validation_report(results) 