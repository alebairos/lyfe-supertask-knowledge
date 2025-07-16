"""
Stage 1 Integration Module for Lyfe Supertask Knowledge Generator

This module integrates all Stage 1 components into a cohesive pipeline:
- Stage 1 functions (raw content analysis)
- Content analyzer (AI-powered analysis with Ari persona preparation)
- JSON normalizer (template-compliant structure generation)
- Output validation (quality assurance and compliance checking)

The integration provides:
- Complete Stage 1 pipeline execution
- Error handling and recovery
- Progress reporting and logging
- Batch processing capabilities
- Quality assurance at each step
- Comprehensive reporting and analytics

Stage 1 Pipeline:
work/01_raw/*.json → work/02_preprocessed/*.json

Components:
1. Raw content loading and validation
2. Content extraction and analysis
3. Ari persona pattern analysis
4. AI-powered content insights
5. JSON normalization to template compliance
6. Output validation and quality assurance
7. Progress reporting and error handling
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import traceback

from .config_loader import get_config, load_config
from .stage1_functions import (
    process_raw_file,
    process_directory_with_ari_analysis,
    analyze_ari_persona_patterns,
    Stage1ProcessingError
)
from .content_analyzer import ContentAnalyzer, ContentAnalyzerError
from .json_normalizer import JSONNormalizer, get_json_normalizer
from .output_validation import OutputValidator, ValidationResult, validate_output_file

# Set up logging
logger = logging.getLogger(__name__)


class Stage1IntegrationError(Exception):
    """Custom exception for Stage 1 integration errors."""
    pass


class Stage1Pipeline:
    """
    Comprehensive Stage 1 pipeline integrating all components.
    
    This class orchestrates the complete Stage 1 processing pipeline:
    1. Raw content analysis and extraction
    2. Ari persona pattern analysis
    3. AI-powered content insights
    4. JSON normalization to template compliance
    5. Output validation and quality assurance
    6. Progress reporting and error handling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Stage 1 pipeline.
        
        Args:
            config: Optional configuration dictionary. If None, loads from config files.
        """
        try:
            # Load configuration if not provided
            if config is None:
                try:
                    config = get_config()
                except ValueError:
                    # Configuration not loaded, load it
                    load_config()
                    config = get_config()
            
            self.config = config
            
            # Initialize components
            self.content_analyzer = ContentAnalyzer(config)
            self.json_normalizer = get_json_normalizer()
            self.output_validator = OutputValidator()
            
            # Pipeline configuration
            self.pipeline_config = config.get('processing', {})
            self.enable_ai_analysis = self.pipeline_config.get('enable_ai_analysis', True)
            self.enable_validation = self.pipeline_config.get('enable_validation', True)
            self.batch_size = self.pipeline_config.get('batch_size', 10)
            
            # Progress tracking
            self.progress_callback = None
            self.current_progress = 0
            self.total_files = 0
            
            logger.info("Stage 1 pipeline initialized successfully")
            
        except Exception as e:
            raise Stage1IntegrationError(f"Failed to initialize Stage 1 pipeline: {e}")
    
    def set_progress_callback(self, callback):
        """
        Set a progress callback function for real-time progress reporting.
        
        Args:
            callback: Function that takes (current, total, message) parameters.
        """
        self.progress_callback = callback
    
    def _report_progress(self, current: int, total: int, message: str):
        """Report progress to callback if set."""
        self.current_progress = current
        self.total_files = total
        
        if self.progress_callback:
            self.progress_callback(current, total, message)
        
        logger.info(f"Progress: {current}/{total} - {message}")
    
    def process_single_file(
        self, 
        input_file: str, 
        output_file: str, 
        include_ai_analysis: bool = True,
        include_validation: bool = True
    ) -> Dict[str, Any]:
        """
        Process a single file through the complete Stage 1 pipeline.
        
        Args:
            input_file: Path to the input JSON file.
            output_file: Path to save the processed output.
            include_ai_analysis: Whether to include AI-powered analysis.
            include_validation: Whether to include output validation.
            
        Returns:
            Dictionary with comprehensive processing results including:
            - Processing status and timing
            - Content analysis results
            - Ari persona analysis
            - JSON normalization results
            - Validation results (if enabled)
            - Error information (if any)
            
        Raises:
            Stage1IntegrationError: If processing fails.
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing single file: {input_file}")
            self._report_progress(0, 5, f"Starting processing of {Path(input_file).name}")
            
            # Step 1: Content analysis with Ari persona preparation
            self._report_progress(1, 5, "Performing content analysis")
            analysis_result = self.content_analyzer.analyze_single_file(
                input_file, include_ai_analysis=include_ai_analysis
            )
            
            # Step 2: JSON normalization to template compliance
            self._report_progress(2, 5, "Normalizing JSON structure")
            normalized_result = self.json_normalizer.normalize_from_analysis(
                analysis_result
            )
            
            # Step 3: Save normalized output
            self._report_progress(3, 5, "Saving normalized output")
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(normalized_result, f, indent=2, ensure_ascii=False)
            
            # Step 4: Output validation (if enabled)
            validation_result = None
            if include_validation and self.enable_validation:
                self._report_progress(4, 5, "Validating output")
                validation_result = validate_output_file(str(output_path))
            
            # Step 5: Compile results
            self._report_progress(5, 5, "Compiling results")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                "status": "success",
                "input_file": input_file,
                "output_file": str(output_path),
                "processing_time_seconds": processing_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "pipeline_version": "1.0.0",
                "components_used": {
                    "content_analyzer": True,
                    "json_normalizer": True,
                    "output_validator": include_validation,
                    "ai_analysis": include_ai_analysis
                },
                "analysis_result": analysis_result,
                "normalized_result": normalized_result,
                "validation_result": validation_result.metadata if validation_result else None,
                "validation_passed": validation_result.is_valid if validation_result else None,
                "quality_score": validation_result.score if validation_result else None
            }
            
            logger.info(f"Successfully processed {input_file} in {processing_time:.2f} seconds")
            return result
            
        except (Stage1ProcessingError, ContentAnalyzerError) as e:
            error_result = {
                "status": "error",
                "input_file": input_file,
                "output_file": output_file,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "pipeline_version": "1.0.0"
            }
            
            logger.error(f"Processing failed for {input_file}: {e}")
            return error_result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "input_file": input_file,
                "output_file": output_file,
                "error_type": "UnexpectedError",
                "error_message": str(e),
                "error_traceback": traceback.format_exc(),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "pipeline_version": "1.0.0"
            }
            
            logger.error(f"Unexpected error processing {input_file}: {e}")
            return error_result
    
    def process_directory(
        self, 
        input_dir: str, 
        output_dir: str,
        include_ai_analysis: bool = True,
        include_validation: bool = True
    ) -> Dict[str, Any]:
        """
        Process all JSON files in a directory through the complete Stage 1 pipeline.
        
        Args:
            input_dir: Directory containing raw JSON files.
            output_dir: Directory to save processed outputs.
            include_ai_analysis: Whether to include AI-powered analysis.
            include_validation: Whether to include output validation.
            
        Returns:
            Dictionary with comprehensive processing results including:
            - Overall processing statistics
            - Individual file results
            - Cross-file analysis patterns
            - Comprehensive Ari persona preparation
            - Validation summary
            - Error summary and recovery information
            
        Raises:
            Stage1IntegrationError: If directory processing fails.
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing directory: {input_dir}")
            
            # Step 1: Discover input files
            input_path = Path(input_dir)
            if not input_path.exists():
                raise Stage1IntegrationError(f"Input directory not found: {input_dir}")
            
            json_files = list(input_path.glob("**/*.json"))
            if not json_files:
                raise Stage1IntegrationError(f"No JSON files found in {input_dir}")
            
            total_files = len(json_files)
            self._report_progress(0, total_files, f"Found {total_files} JSON files")
            
            # Step 2: Process files individually
            individual_results = []
            successful_files = []
            failed_files = []
            
            for i, json_file in enumerate(json_files):
                try:
                    # Generate output file path
                    relative_path = json_file.relative_to(input_path)
                    output_file = Path(output_dir) / relative_path
                    
                    # Process the file
                    result = self.process_single_file(
                        str(json_file),
                        str(output_file),
                        include_ai_analysis=include_ai_analysis,
                        include_validation=include_validation
                    )
                    
                    individual_results.append(result)
                    
                    if result["status"] == "success":
                        successful_files.append(str(json_file))
                    else:
                        failed_files.append({
                            "file": str(json_file),
                            "error": result.get("error_message", "Unknown error")
                        })
                    
                    self._report_progress(i + 1, total_files, f"Processed {json_file.name}")
                    
                except Exception as e:
                    failed_files.append({
                        "file": str(json_file),
                        "error": str(e)
                    })
                    
                    individual_results.append({
                        "status": "error",
                        "input_file": str(json_file),
                        "error_type": "ProcessingError",
                        "error_message": str(e)
                    })
                    
                    logger.error(f"Failed to process {json_file}: {e}")
            
            # Step 3: Cross-file analysis (if we have successful results)
            cross_file_analysis = {}
            if successful_files:
                self._report_progress(total_files, total_files, "Performing cross-file analysis")
                cross_file_analysis = self._perform_cross_file_analysis(individual_results)
            
            # Step 4: Validation summary
            validation_summary = {}
            if include_validation:
                validation_summary = self._create_validation_summary(individual_results)
            
            # Step 5: Compile comprehensive results
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                "status": "completed",
                "input_directory": input_dir,
                "output_directory": output_dir,
                "processing_time_seconds": processing_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "pipeline_version": "1.0.0",
                "statistics": {
                    "total_files": total_files,
                    "successful_files": len(successful_files),
                    "failed_files": len(failed_files),
                    "success_rate": len(successful_files) / total_files if total_files > 0 else 0,
                    "average_processing_time": processing_time / total_files if total_files > 0 else 0
                },
                "individual_results": individual_results,
                "successful_files": successful_files,
                "failed_files": failed_files,
                "cross_file_analysis": cross_file_analysis,
                "validation_summary": validation_summary,
                "components_used": {
                    "content_analyzer": True,
                    "json_normalizer": True,
                    "output_validator": include_validation,
                    "ai_analysis": include_ai_analysis
                }
            }
            
            logger.info(f"Directory processing completed: {len(successful_files)}/{total_files} files successful")
            return result
            
        except Stage1IntegrationError:
            raise
        except Exception as e:
            raise Stage1IntegrationError(f"Directory processing failed: {e}")
    
    def _perform_cross_file_analysis(self, individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform cross-file analysis to identify patterns across multiple files.
        
        Args:
            individual_results: List of individual file processing results.
            
        Returns:
            Dictionary with cross-file analysis patterns.
        """
        try:
            successful_results = [r for r in individual_results if r["status"] == "success"]
            
            if not successful_results:
                return {"status": "no_successful_files"}
            
            # Analyze common themes across files
            all_themes = []
            all_languages = []
            all_difficulty_levels = []
            all_archetypes = []
            
            for result in successful_results:
                analysis = result.get("analysis_result", {})
                if "analysis_summary" in analysis:
                    summary = analysis["analysis_summary"]
                    all_themes.extend(summary.get("common_themes", []))
                    all_languages.append(summary.get("primary_language", "portuguese"))
                    all_difficulty_levels.append(summary.get("average_difficulty", "intermediate"))
                    all_archetypes.append(summary.get("primary_archetype", "achiever"))
            
            # Calculate patterns
            theme_frequency = {}
            for theme in all_themes:
                theme_frequency[theme] = theme_frequency.get(theme, 0) + 1
            
            language_frequency = {}
            for lang in all_languages:
                language_frequency[lang] = language_frequency.get(lang, 0) + 1
            
            difficulty_frequency = {}
            for diff in all_difficulty_levels:
                difficulty_frequency[diff] = difficulty_frequency.get(diff, 0) + 1
            
            archetype_frequency = {}
            for arch in all_archetypes:
                archetype_frequency[arch] = archetype_frequency.get(arch, 0) + 1
            
            # Identify dominant patterns
            dominant_themes = sorted(theme_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            dominant_language = max(language_frequency.items(), key=lambda x: x[1])[0] if language_frequency else "portuguese"
            dominant_difficulty = max(difficulty_frequency.items(), key=lambda x: x[1])[0] if difficulty_frequency else "intermediate"
            dominant_archetype = max(archetype_frequency.items(), key=lambda x: x[1])[0] if archetype_frequency else "achiever"
            
            return {
                "status": "completed",
                "files_analyzed": len(successful_results),
                "dominant_patterns": {
                    "themes": dominant_themes,
                    "language": dominant_language,
                    "difficulty": dominant_difficulty,
                    "archetype": dominant_archetype
                },
                "pattern_frequencies": {
                    "themes": theme_frequency,
                    "languages": language_frequency,
                    "difficulties": difficulty_frequency,
                    "archetypes": archetype_frequency
                },
                "ari_persona_insights": {
                    "content_readiness": "high" if len(successful_results) > 3 else "medium",
                    "framework_integration_potential": "high" if len(dominant_themes) > 2 else "medium",
                    "coaching_opportunities": len([t for t in dominant_themes if t[0] in ["habit", "routine", "motivation"]]),
                    "cultural_context": "portuguese" if dominant_language == "portuguese" else "international"
                }
            }
            
        except Exception as e:
            logger.error(f"Cross-file analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _create_validation_summary(self, individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a validation summary from individual file results.
        
        Args:
            individual_results: List of individual file processing results.
            
        Returns:
            Dictionary with validation summary.
        """
        try:
            validated_results = [r for r in individual_results if r.get("validation_result")]
            
            if not validated_results:
                return {"status": "no_validation_data"}
            
            # Calculate validation statistics
            total_validated = len(validated_results)
            passed_validation = len([r for r in validated_results if r.get("validation_passed")])
            failed_validation = total_validated - passed_validation
            
            # Calculate quality scores
            quality_scores = [r.get("quality_score", 0) for r in validated_results if r.get("quality_score")]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Collect common validation issues
            all_errors = []
            all_warnings = []
            all_suggestions = []
            
            for result in validated_results:
                validation_result = result.get("validation_result", {})
                if isinstance(validation_result, dict):
                    all_errors.extend(validation_result.get("errors", []))
                    all_warnings.extend(validation_result.get("warnings", []))
                    all_suggestions.extend(validation_result.get("suggestions", []))
            
            # Count issue frequencies
            error_frequency = {}
            for error in all_errors:
                error_frequency[error] = error_frequency.get(error, 0) + 1
            
            warning_frequency = {}
            for warning in all_warnings:
                warning_frequency[warning] = warning_frequency.get(warning, 0) + 1
            
            return {
                "status": "completed",
                "total_files_validated": total_validated,
                "passed_validation": passed_validation,
                "failed_validation": failed_validation,
                "validation_success_rate": passed_validation / total_validated if total_validated > 0 else 0,
                "average_quality_score": avg_quality_score,
                "quality_distribution": {
                    "excellent": len([s for s in quality_scores if s >= 9]),
                    "good": len([s for s in quality_scores if 7 <= s < 9]),
                    "fair": len([s for s in quality_scores if 5 <= s < 7]),
                    "poor": len([s for s in quality_scores if s < 5])
                },
                "common_issues": {
                    "errors": sorted(error_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
                    "warnings": sorted(warning_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
                },
                "improvement_recommendations": self._generate_improvement_recommendations(
                    error_frequency, warning_frequency
                )
            }
            
        except Exception as e:
            logger.error(f"Validation summary creation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_improvement_recommendations(
        self, 
        error_frequency: Dict[str, int], 
        warning_frequency: Dict[str, int]
    ) -> List[str]:
        """Generate improvement recommendations based on validation issues."""
        recommendations = []
        
        # Recommendations based on common errors
        for error, count in sorted(error_frequency.items(), key=lambda x: x[1], reverse=True)[:3]:
            if "content" in error.lower():
                recommendations.append("Focus on improving content quality and length")
            elif "quiz" in error.lower():
                recommendations.append("Enhance quiz questions with better variety and clarity")
            elif "metadata" in error.lower():
                recommendations.append("Ensure complete and accurate metadata")
            elif "schema" in error.lower():
                recommendations.append("Verify JSON structure compliance with template")
        
        # Recommendations based on common warnings
        for warning, count in sorted(warning_frequency.items(), key=lambda x: x[1], reverse=True)[:3]:
            if "ari" in warning.lower():
                recommendations.append("Improve Ari persona consistency and coaching language")
            elif "objective" in warning.lower():
                recommendations.append("Enhance learning objectives with more specific action verbs")
            elif "brief" in warning.lower():
                recommendations.append("Expand content sections for better learning progression")
        
        # Default recommendations if none specific
        if not recommendations:
            recommendations.append("Review content structure and quality standards")
            recommendations.append("Ensure template compliance and validation requirements")
        
        return recommendations
    
    def generate_content_analysis_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a content-focused analysis report that highlights the educational value
        and learning content created from raw data.
        
        Args:
            results: Processing results from Stage 1 pipeline.
            
        Returns:
            Formatted content analysis report.
        """
        try:
            report_lines = []
            
            # Header
            report_lines.append("# Supertask Content Analysis Report")
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Executive Summary
            stats = results.get("statistics", {})
            successful_files = stats.get("successful_files", 0)
            
            report_lines.append("## Executive Summary")
            report_lines.append(f"From the raw input data, we successfully created **{successful_files} comprehensive supertask{'s' if successful_files != 1 else ''}** ")
            report_lines.append("designed to help users learn through structured, interactive experiences.")
            report_lines.append("")
            
            # Content Analysis
            if results.get("individual_results"):
                report_lines.append("## Content Analysis: What Was Created")
                report_lines.append("")
                
                for i, result in enumerate(results.get("individual_results", [])):
                    if result.get("status") == "success":
                        report_lines.extend(self._analyze_individual_content(result, i + 1))
            
            # Learning Outcomes Summary
            cross_analysis = results.get("cross_file_analysis", {})
            if cross_analysis.get("status") == "completed":
                report_lines.append("## Learning Outcomes and Educational Value")
                report_lines.append("")
                
                dominant = cross_analysis.get("dominant_patterns", {})
                themes = dominant.get("themes", [])
                
                if themes:
                    report_lines.append("### Primary Learning Topics Identified:")
                    for theme, count in themes[:5]:
                        report_lines.append(f"- **{theme.title()}**: {count} supertask{'s' if count != 1 else ''}")
                    report_lines.append("")
                
                # Ari persona insights
                ari_insights = cross_analysis.get("ari_persona_insights", {})
                if ari_insights:
                    report_lines.append("### Coaching and Behavioral Change Potential:")
                    report_lines.append(f"- **Content Readiness**: {ari_insights.get('content_readiness', 'N/A').title()}")
                    report_lines.append(f"- **Framework Integration**: {ari_insights.get('framework_integration_potential', 'N/A').title()}")
                    report_lines.append(f"- **Coaching Opportunities**: {ari_insights.get('coaching_opportunities', 0)} identified")
                    report_lines.append(f"- **Cultural Context**: {ari_insights.get('cultural_context', 'N/A').title()}")
                    report_lines.append("")
            
            # Content Quality and Impact
            validation = results.get("validation_summary", {})
            if validation.get("status") == "completed":
                report_lines.append("## Content Quality and Impact")
                report_lines.append("")
                
                avg_quality = validation.get("average_quality_score", 0)
                quality_dist = validation.get("quality_distribution", {})
                
                report_lines.append(f"### Overall Quality Assessment:")
                report_lines.append(f"- **Average Quality Score**: {avg_quality:.1f}/10.0")
                report_lines.append(f"- **Excellent Content**: {quality_dist.get('excellent', 0)} supertasks")
                report_lines.append(f"- **Good Content**: {quality_dist.get('good', 0)} supertasks")
                report_lines.append(f"- **Fair Content**: {quality_dist.get('fair', 0)} supertasks")
                report_lines.append("")
                
                # Improvement recommendations
                recommendations = validation.get("improvement_recommendations", [])
                if recommendations:
                    report_lines.append("### Content Enhancement Recommendations:")
                    for rec in recommendations:
                        report_lines.append(f"- {rec}")
                    report_lines.append("")
            
            # Future Content Generation Vision
            report_lines.append("## Future Content Generation Vision")
            report_lines.append("")
            report_lines.append("### Current Capability Demonstrated:")
            report_lines.append("- **Automatic Topic Inference**: System successfully identified learning topics from raw content")
            report_lines.append("- **Content Structuring**: Transformed raw content into progressive learning sequences")
            report_lines.append("- **Interactive Elements**: Generated relevant quiz questions with coaching integration")
            report_lines.append("- **Framework Alignment**: Prepared content for behavioral change methodologies")
            report_lines.append("")
            
            report_lines.append("### Next Phase Capabilities (Planned):")
            report_lines.append("- **User-Requested Topics**: \"I want to learn about habit formation based on BJ Fogg\"")
            report_lines.append("- **Specific Challenges**: \"How to reduce social media usage\"")
            report_lines.append("- **Custom Learning Paths**: Personalized content based on user goals and archetype")
            report_lines.append("- **Multi-Supertask Series**: Connected learning experiences across related topics")
            report_lines.append("")
            
            # Processing Statistics
            report_lines.append("## Processing Statistics")
            report_lines.append(f"- **Total Files Processed**: {stats.get('total_files', 0)}")
            report_lines.append(f"- **Successful Supertasks Created**: {stats.get('successful_files', 0)}")
            report_lines.append(f"- **Success Rate**: {stats.get('success_rate', 0):.1%}")
            report_lines.append(f"- **Average Processing Time**: {stats.get('average_processing_time', 0):.2f} seconds per file")
            report_lines.append("")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Content analysis report generation failed: {e}")
            return f"Content analysis report generation failed: {e}"
    
    def _analyze_individual_content(self, result: Dict[str, Any], index: int) -> List[str]:
        """
        Analyze individual content result for the report.
        
        Args:
            result: Individual processing result.
            index: File index number.
            
        Returns:
            List of report lines for this content.
        """
        lines = []
        
        try:
            normalized_result = result.get("normalized_result", {})
            if not normalized_result:
                return lines
            
            title = normalized_result.get("title", "Unknown Title")
            description = normalized_result.get("description", "")
            
            lines.append(f"### {index}. {title}")
            lines.append("")
            
            # Topic and learning focus
            if description:
                lines.append(f"**Learning Focus**: {description[:200]}{'...' if len(description) > 200 else ''}")
                lines.append("")
            
            # Content structure analysis
            content_items = normalized_result.get("content", [])
            quiz_items = normalized_result.get("quiz", [])
            
            lines.append("**Content Structure:**")
            lines.append(f"- **Educational Content**: {len(content_items)} sections")
            lines.append(f"- **Interactive Elements**: {len(quiz_items)} quiz questions")
            
            # Learning objectives
            objectives = normalized_result.get("learning_objectives", [])
            if objectives:
                lines.append(f"- **Learning Objectives**: {len(objectives)} defined goals")
            
            # Target audience and difficulty
            audience = normalized_result.get("target_audience", "")
            difficulty = normalized_result.get("difficulty_level", "")
            if audience or difficulty:
                lines.append(f"- **Target Audience**: {audience.title()} archetype")
                lines.append(f"- **Difficulty Level**: {difficulty.title()}")
            
            lines.append("")
            
            # Key learning points (from content analysis)
            if content_items:
                lines.append("**Key Learning Points:**")
                for i, item in enumerate(content_items[:3]):  # Show first 3 items
                    content_text = item.get("content", "")
                    if content_text:
                        # Extract first sentence or up to 100 characters
                        summary = content_text.split('.')[0][:100] + "..."
                        lines.append(f"- {summary}")
                
                if len(content_items) > 3:
                    lines.append(f"- ... and {len(content_items) - 3} more content sections")
                lines.append("")
            
            # Coaching and framework integration
            metadata = normalized_result.get("metadata", {})
            if metadata:
                themes = metadata.get("themes", [])
                if themes:
                    lines.append("**Coaching Integration:**")
                    lines.append(f"- **Key Themes**: {', '.join(themes[:5])}")
                    
                    # Check for framework alignment in content
                    framework_count = 0
                    for item in content_items:
                        if item.get("framework_alignment"):
                            framework_count += len(item.get("framework_alignment", []))
                    
                    if framework_count > 0:
                        lines.append(f"- **Framework Alignments**: {framework_count} identified")
                    
                    lines.append("")
            
            # Quality metrics
            quality_score = result.get("quality_score")
            if quality_score:
                lines.append(f"**Quality Score**: {quality_score:.1f}/10.0")
                lines.append("")
            
        except Exception as e:
            logger.error(f"Error analyzing individual content: {e}")
            lines.append(f"Error analyzing content: {e}")
            lines.append("")
        
        return lines

    def generate_processing_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive processing report.
        
        Args:
            results: Processing results from process_directory.
            
        Returns:
            Formatted processing report.
        """
        try:
            report_lines = []
            
            # Header
            report_lines.append("# Stage 1 Processing Report")
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Summary
            stats = results.get("statistics", {})
            report_lines.append("## Processing Summary")
            report_lines.append(f"- Input Directory: {results.get('input_directory', 'N/A')}")
            report_lines.append(f"- Output Directory: {results.get('output_directory', 'N/A')}")
            report_lines.append(f"- Total Files: {stats.get('total_files', 0)}")
            report_lines.append(f"- Successful: {stats.get('successful_files', 0)}")
            report_lines.append(f"- Failed: {stats.get('failed_files', 0)}")
            report_lines.append(f"- Success Rate: {stats.get('success_rate', 0):.1%}")
            report_lines.append(f"- Processing Time: {results.get('processing_time_seconds', 0):.2f} seconds")
            report_lines.append("")
            
            # Cross-file analysis
            cross_analysis = results.get("cross_file_analysis", {})
            if cross_analysis.get("status") == "completed":
                report_lines.append("## Cross-File Analysis")
                dominant = cross_analysis.get("dominant_patterns", {})
                report_lines.append(f"- Dominant Language: {dominant.get('language', 'N/A')}")
                report_lines.append(f"- Dominant Difficulty: {dominant.get('difficulty', 'N/A')}")
                report_lines.append(f"- Dominant Archetype: {dominant.get('archetype', 'N/A')}")
                
                themes = dominant.get("themes", [])
                if themes:
                    report_lines.append("- Top Themes:")
                    for theme, count in themes[:3]:
                        report_lines.append(f"  - {theme}: {count} files")
                report_lines.append("")
            
            # Validation summary
            validation = results.get("validation_summary", {})
            if validation.get("status") == "completed":
                report_lines.append("## Validation Summary")
                report_lines.append(f"- Files Validated: {validation.get('total_files_validated', 0)}")
                report_lines.append(f"- Validation Success Rate: {validation.get('validation_success_rate', 0):.1%}")
                report_lines.append(f"- Average Quality Score: {validation.get('average_quality_score', 0):.1f}/10.0")
                
                quality_dist = validation.get("quality_distribution", {})
                report_lines.append("- Quality Distribution:")
                report_lines.append(f"  - Excellent (9+): {quality_dist.get('excellent', 0)}")
                report_lines.append(f"  - Good (7-9): {quality_dist.get('good', 0)}")
                report_lines.append(f"  - Fair (5-7): {quality_dist.get('fair', 0)}")
                report_lines.append(f"  - Poor (<5): {quality_dist.get('poor', 0)}")
                report_lines.append("")
            
            # Failed files
            failed_files = results.get("failed_files", [])
            if failed_files:
                report_lines.append("## Failed Files")
                for failed in failed_files:
                    report_lines.append(f"- {failed.get('file', 'Unknown')}: {failed.get('error', 'Unknown error')}")
                report_lines.append("")
            
            # Recommendations
            recommendations = validation.get("improvement_recommendations", [])
            if recommendations:
                report_lines.append("## Improvement Recommendations")
                for rec in recommendations:
                    report_lines.append(f"- {rec}")
                report_lines.append("")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"Report generation failed: {e}"


# Global convenience functions
def create_stage1_pipeline(config: Optional[Dict[str, Any]] = None) -> Stage1Pipeline:
    """
    Create a Stage 1 pipeline instance.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        Stage1Pipeline instance.
    """
    return Stage1Pipeline(config)


def process_single_file_stage1(
    input_file: str,
    output_file: str,
    include_ai_analysis: bool = True,
    include_validation: bool = True,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Process a single file through Stage 1 pipeline.
    
    Args:
        input_file: Path to input JSON file.
        output_file: Path to save output.
        include_ai_analysis: Whether to include AI analysis.
        include_validation: Whether to include validation.
        progress_callback: Optional progress callback function.
        
    Returns:
        Processing results dictionary.
    """
    pipeline = create_stage1_pipeline()
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    return pipeline.process_single_file(
        input_file, output_file, include_ai_analysis, include_validation
    )


def process_directory_stage1(
    input_dir: str,
    output_dir: str,
    include_ai_analysis: bool = True,
    include_validation: bool = True,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Process a directory through Stage 1 pipeline.
    
    Args:
        input_dir: Input directory path.
        output_dir: Output directory path.
        include_ai_analysis: Whether to include AI analysis.
        include_validation: Whether to include validation.
        progress_callback: Optional progress callback function.
        
    Returns:
        Processing results dictionary.
    """
    pipeline = create_stage1_pipeline()
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    return pipeline.process_directory(
        input_dir, output_dir, include_ai_analysis, include_validation
    )


def generate_stage1_report(results: Dict[str, Any]) -> str:
    """
    Generate a Stage 1 processing report.
    
    Args:
        results: Processing results from Stage 1 pipeline.
        
    Returns:
        Formatted report string.
    """
    pipeline = create_stage1_pipeline()
    return pipeline.generate_processing_report(results)


def generate_content_analysis_report(results: Dict[str, Any]) -> str:
    """
    Generate a content-focused analysis report highlighting educational value.
    
    Args:
        results: Processing results from Stage 1 pipeline.
        
    Returns:
        Formatted content analysis report string.
    """
    pipeline = create_stage1_pipeline()
    return pipeline.generate_content_analysis_report(results) 