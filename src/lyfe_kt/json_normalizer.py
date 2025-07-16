"""
JSON normalizer module for Lyfe Supertask Knowledge Generator.

This module takes the output from the content analyzer and converts it to
template-compliant structure for the next stage of the pipeline. It enhances
the basic Stage 1 normalization with content analyzer insights and Ari persona
preparation.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .config_loader import get_config, load_config
from .content_analyzer import get_content_analyzer, ContentAnalyzerError


# Set up logging
logger = logging.getLogger(__name__)


class JSONNormalizerError(Exception):
    """Custom exception for JSON normalizer errors."""
    pass


class JSONNormalizer:
    """
    JSON normalizer that converts content analyzer output to template-compliant structure.
    
    This class provides comprehensive JSON normalization by:
    - Converting content analyzer output to template-compliant format
    - Enhancing basic normalization with AI insights and Ari persona preparation
    - Generating proper metadata and learning objectives
    - Creating structured content ready for markdown generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the JSON normalizer.
        
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
            
            # Initialize content analyzer
            self.content_analyzer = get_content_analyzer(config)
            
            # Set up normalization parameters
            self.normalization_config = config.get('validation', {})
            self.content_config = self.normalization_config.get('content', {})
            self.min_content_length = self.content_config.get('min_length', 50)
            self.max_content_length = self.content_config.get('max_length', 50000)
            
            logger.info("JSON normalizer initialized successfully")
            
        except Exception as e:
            raise JSONNormalizerError(f"Failed to initialize JSON normalizer: {e}")
    
    def normalize_single_file(self, file_path: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """
        Normalize a single file using content analyzer output.
        
        Args:
            file_path: Path to the JSON file to normalize.
            include_ai_analysis: Whether to include AI-powered analysis.
            
        Returns:
            Dictionary with normalized, template-compliant JSON structure.
            
        Raises:
            JSONNormalizerError: If normalization fails.
        """
        try:
            logger.info(f"Normalizing single file: {file_path}")
            
            # Step 1: Get comprehensive analysis from content analyzer
            analysis_result = self.content_analyzer.analyze_single_file(
                file_path, include_ai_analysis
            )
            
            # Step 2: Extract key components
            processed_data = analysis_result["processed_data"]
            ari_analysis = analysis_result["ari_analysis"]
            ai_analysis = analysis_result["ai_analysis"]
            integrated_analysis = analysis_result["integrated_analysis"]
            ari_preparation = analysis_result["ari_preparation"]
            
            # Step 3: Create template-compliant structure
            normalized_structure = self._create_template_compliant_structure(
                processed_data, ari_analysis, ai_analysis, integrated_analysis, ari_preparation
            )
            
            # Step 4: Validate and enhance the structure
            validated_structure = self._validate_and_enhance_structure(
                normalized_structure, analysis_result
            )
            
            # Step 5: Add normalization metadata
            final_structure = self._add_normalization_metadata(
                validated_structure, file_path, analysis_result
            )
            
            return final_structure
            
        except ContentAnalyzerError as e:
            raise JSONNormalizerError(f"Content analysis failed for {file_path}: {e}")
        except Exception as e:
            raise JSONNormalizerError(f"Unexpected error normalizing {file_path}: {e}")
    
    def normalize_from_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize using pre-computed analysis result.
        
        Args:
            analysis_result: Pre-computed analysis result from content analyzer.
            
        Returns:
            Dictionary with normalized, template-compliant JSON structure.
            
        Raises:
            JSONNormalizerError: If normalization fails.
        """
        try:
            file_path = analysis_result.get("file_path", "unknown")
            logger.info(f"Normalizing from analysis result: {file_path}")
            
            # Step 1: Extract key components
            processed_data = analysis_result["processed_data"]
            ari_analysis = analysis_result["ari_analysis"]
            ai_analysis = analysis_result["ai_analysis"]
            integrated_analysis = analysis_result["integrated_analysis"]
            ari_preparation = analysis_result["ari_preparation"]
            
            # Step 2: Create template-compliant structure
            normalized_structure = self._create_template_compliant_structure(
                processed_data, ari_analysis, ai_analysis, integrated_analysis, ari_preparation
            )
            
            # Step 3: Validate and enhance the structure
            validated_structure = self._validate_and_enhance_structure(
                normalized_structure, analysis_result
            )
            
            # Step 4: Add normalization metadata
            final_structure = self._add_normalization_metadata(
                validated_structure, file_path, analysis_result
            )
            
            return final_structure
            
        except Exception as e:
            file_path = analysis_result.get("file_path", "unknown")
            raise JSONNormalizerError(f"Unexpected error normalizing from analysis {file_path}: {e}")
    
    def normalize_directory(self, input_dir: str, output_dir: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """
        Normalize multiple JSON files in a directory.
        
        Args:
            input_dir: Directory containing raw JSON files.
            output_dir: Directory to save normalized JSON files.
            include_ai_analysis: Whether to include AI-powered analysis.
            
        Returns:
            Dictionary with normalization results for all files.
            
        Raises:
            JSONNormalizerError: If directory normalization fails.
        """
        try:
            logger.info(f"Normalizing directory: {input_dir}")
            
            # Step 1: Get comprehensive directory analysis
            directory_analysis = self.content_analyzer.analyze_directory(
                input_dir, output_dir, include_ai_analysis
            )
            
            # Step 2: Normalize each file
            normalized_files = []
            failed_files = []
            
            for file_info in directory_analysis["directory_results"].get("processed", []):
                try:
                    input_file = file_info["input_file"]
                    output_file = file_info["output_file"]
                    
                    # Normalize the file
                    normalized_result = self.normalize_single_file(
                        input_file, include_ai_analysis
                    )
                    
                    # Save normalized file
                    normalized_output_file = self._generate_normalized_output_path(
                        output_file, "normalized"
                    )
                    
                    self._save_normalized_file(normalized_result, normalized_output_file)
                    
                    normalized_files.append({
                        "input_file": input_file,
                        "output_file": normalized_output_file,
                        "title": normalized_result["title"],
                        "language": normalized_result["language"],
                        "normalization_status": "success"
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to normalize {input_file}: {e}")
                    failed_files.append({
                        "input_file": input_file,
                        "error": str(e)
                    })
            
            # Step 3: Create directory normalization summary
            directory_summary = self._create_directory_normalization_summary(
                directory_analysis, normalized_files, failed_files
            )
            
            return {
                "input_directory": input_dir,
                "output_directory": output_dir,
                "directory_analysis": directory_analysis,
                "normalized_files": normalized_files,
                "failed_files": failed_files,
                "directory_summary": directory_summary,
                "normalization_timestamp": datetime.now().isoformat(),
                "normalizer_version": "1.0.0"
            }
            
        except ContentAnalyzerError as e:
            raise JSONNormalizerError(f"Directory analysis failed: {e}")
        except Exception as e:
            raise JSONNormalizerError(f"Unexpected error normalizing directory {input_dir}: {e}")
    
    def _create_template_compliant_structure(
        self, 
        processed_data: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        ai_analysis: Dict[str, Any],
        integrated_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create template-compliant JSON structure that preserves input format.
        
        CRITICAL: This method now preserves the exact input structure while enhancing
        the flexibleItems content with AI analysis and Ari persona insights.
        
        Args:
            processed_data: Stage 1 processing results.
            ari_analysis: Ari persona analysis results.
            ai_analysis: AI analysis results.
            integrated_analysis: Integrated analysis results.
            ari_preparation: Ari preparation recommendations.
            
        Returns:
            Enhanced JSON structure that maintains input format.
        """
        try:
            # Start with the original structure from processed_data
            original_structure = processed_data.get("original_structure", {})
            
            # If no original structure, create basic structure
            if not original_structure:
                logger.warning("No original structure found, creating basic structure")
                original_structure = {
                    "title": processed_data.get("title", "Knowledge Task"),
                    "dimension": processed_data.get("dimension", "physicalHealth"),
                    "archetype": processed_data.get("archetype", "warrior"),
                    "relatedToType": processed_data.get("relatedToType", "HABITBP"),
                    "relatedToId": processed_data.get("relatedToId", "generic"),
                    "estimatedDuration": processed_data.get("estimatedDuration", 300),
                    "coinsReward": processed_data.get("coinsReward", 15),
                    "flexibleItems": []
                }
            
            # Create enhanced structure that preserves input format
            enhanced_structure = original_structure.copy()
            
            # Enhance flexibleItems with AI analysis and Ari persona insights
            if "flexibleItems" in enhanced_structure:
                enhanced_structure["flexibleItems"] = self._enhance_flexible_items(
                    enhanced_structure["flexibleItems"], 
                    ari_analysis, 
                    ai_analysis, 
                    ari_preparation
                )
            else:
                # If no flexibleItems, create from processed content
                enhanced_structure["flexibleItems"] = self._create_flexible_items_from_content(
                    processed_data.get("content", []),
                    processed_data.get("quiz", []),
                    ari_analysis,
                    ari_preparation
                )
            
            # Store enhancement metadata in existing metadata field to preserve format
            if "metadata" not in enhanced_structure:
                enhanced_structure["metadata"] = {}
            
            enhanced_structure["metadata"]["_enhancement_info"] = {
                "ai_analysis_applied": True,
                "ari_persona_applied": True,
                "enhancement_timestamp": datetime.now().isoformat(),
                "original_items_count": len(original_structure.get("flexibleItems", [])),
                "enhanced_items_count": len(enhanced_structure.get("flexibleItems", [])),
                "enhancement_version": "1.0.0"
            }
            
            return enhanced_structure
            
        except Exception as e:
            logger.error(f"Failed to create template-compliant structure: {e}")
            raise JSONNormalizerError(f"Template structure creation failed: {e}")
    
    def _enhance_flexible_items(
        self, 
        flexible_items: List[Dict[str, Any]], 
        ari_analysis: Dict[str, Any],
        ai_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance flexible items with AI analysis and Ari persona insights.
        
        Args:
            flexible_items: Original flexible items from input JSON.
            ari_analysis: Ari persona analysis results.
            ai_analysis: AI analysis results.
            ari_preparation: Ari preparation recommendations.
            
        Returns:
            Enhanced flexible items with AI and Ari insights.
        """
        try:
            enhanced_items = []
            
            for i, item in enumerate(flexible_items):
                enhanced_item = item.copy()
                
                # Add AI analysis enhancements
                enhanced_item["_ai_analysis"] = {
                    "themes": ai_analysis.get("themes", []),
                    "tone": ai_analysis.get("tone", "neutral"),
                    "complexity": ai_analysis.get("complexity", "intermediate"),
                    "language": ai_analysis.get("language", "portuguese")
                }
                
                # Add Ari persona enhancements
                enhanced_item["_ari_enhancement"] = {
                    "brevity_suggestions": ari_preparation.get("brevity_suggestions", []),
                    "question_opportunities": ari_preparation.get("question_opportunities", []),
                    "coaching_moments": ari_preparation.get("coaching_moments", []),
                    "framework_alignment": ari_preparation.get("framework_alignment", []),
                    "engagement_level": ari_analysis.get("engagement_level", "medium")
                }
                
                # Enhance content based on type
                if item.get("type") == "content":
                    enhanced_item = self._enhance_content_item(enhanced_item, ari_analysis, ai_analysis)
                elif item.get("type") == "quiz":
                    enhanced_item = self._enhance_quiz_item(enhanced_item, ari_analysis, ari_preparation)
                elif item.get("type") == "quote":
                    enhanced_item = self._enhance_quote_item(enhanced_item, ari_analysis, ai_analysis)
                
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
            
        except Exception as e:
            logger.error(f"Failed to enhance flexible items: {e}")
            # Return original items if enhancement fails
            return flexible_items
    
    def _create_flexible_items_from_content(
        self,
        content_items: List[Dict[str, Any]],
        quiz_items: List[Dict[str, Any]],
        ari_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create flexible items from processed content and quiz items.
        
        Args:
            content_items: Processed content items.
            quiz_items: Processed quiz items.
            ari_analysis: Ari persona analysis results.
            ari_preparation: Ari preparation recommendations.
            
        Returns:
            List of flexible items in original format.
        """
        try:
            flexible_items = []
            
            # Convert content items to flexible items
            for item in content_items:
                flexible_item = {
                    "type": item.get("type", "content"),
                    "content": item.get("content", ""),
                    "author": item.get("author", ""),
                    "_ai_analysis": item.get("_ai_analysis", {}),
                    "_ari_enhancement": item.get("ari_enhancement", {})
                }
                flexible_items.append(flexible_item)
            
            # Convert quiz items to flexible items
            for item in quiz_items:
                flexible_item = {
                    "type": "quiz",
                    "question": item.get("question", ""),
                    "options": item.get("options", []),
                    "correctAnswer": item.get("correctAnswer", ""),
                    "explanation": item.get("explanation", ""),
                    "_ari_enhancement": item.get("ari_coaching_style", {})
                }
                flexible_items.append(flexible_item)
            
            return flexible_items
            
        except Exception as e:
            logger.error(f"Failed to create flexible items from content: {e}")
            return []
    
    def _enhance_content_item(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any], 
        ai_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance a content item with AI and Ari insights."""
        try:
            enhanced_item = item.copy()
            
            # Add content-specific enhancements
            enhanced_item["_content_enhancement"] = {
                "readability_score": ai_analysis.get("readability_score", 0.7),
                "key_concepts": ai_analysis.get("key_concepts", []),
                "learning_value": ai_analysis.get("learning_value", "medium"),
                "ari_coaching_potential": ari_analysis.get("coaching_potential", "medium")
            }
            
            return enhanced_item
            
        except Exception as e:
            logger.warning(f"Failed to enhance content item: {e}")
            return item
    
    def _enhance_quiz_item(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any], 
        ari_preparation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance a quiz item with Ari coaching style."""
        try:
            enhanced_item = item.copy()
            
            # Add quiz-specific enhancements
            enhanced_item["_quiz_enhancement"] = {
                "coaching_style": ari_preparation.get("coaching_style", "supportive"),
                "question_type": "assessment",
                "learning_objective": ari_analysis.get("learning_objective", "knowledge_check"),
                "difficulty_level": ari_analysis.get("difficulty_level", "intermediate")
            }
            
            return enhanced_item
            
        except Exception as e:
            logger.warning(f"Failed to enhance quiz item: {e}")
            return item
    
    def _enhance_quote_item(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any], 
        ai_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance a quote item with motivational insights."""
        try:
            enhanced_item = item.copy()
            
            # Add quote-specific enhancements
            enhanced_item["_quote_enhancement"] = {
                "motivational_impact": ai_analysis.get("motivational_impact", "medium"),
                "relevance_score": ai_analysis.get("relevance_score", 0.7),
                "ari_integration_potential": ari_analysis.get("integration_potential", "medium"),
                "inspirational_value": ai_analysis.get("inspirational_value", "high")
            }
            
            return enhanced_item
            
        except Exception as e:
            logger.warning(f"Failed to enhance quote item: {e}")
            return item
    
    def _generate_enhanced_description(
        self, 
        processed_data: Dict[str, Any], 
        ai_analysis: Dict[str, Any],
        ari_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate enhanced description using AI insights and Ari persona.
        
        Args:
            processed_data: Stage 1 processing results.
            ai_analysis: AI analysis results.
            ari_analysis: Ari persona analysis results.
            
        Returns:
            Enhanced description string.
        """
        try:
            # Get basic description from processed data
            base_description = processed_data.get("description", "")
            
            # Extract AI insights
            ai_insights = ai_analysis.get("basic_analysis", {})
            themes = ai_insights.get("themes", [])
            tone = ai_insights.get("tone", "neutral")
            key_concepts = ai_insights.get("key_concepts", [])
            
            # Extract Ari insights
            coaching_opportunities = ari_analysis.get("coaching_opportunities", {})
            readiness_score = ari_analysis.get("ari_readiness_score", 0.5)
            
            # Generate enhanced description
            if base_description:
                enhanced_description = base_description
            else:
                # Generate from content
                content_items = processed_data.get("content", [])
                if content_items:
                    first_content = content_items[0].get("content", "")
                    # Take first sentence or first 150 characters
                    sentences = re.split(r'[.!?]', first_content)
                    if sentences:
                        enhanced_description = sentences[0].strip()
                        if len(enhanced_description) > 150:
                            enhanced_description = enhanced_description[:147] + "..."
                else:
                    enhanced_description = f"Knowledge task about {processed_data.get('title', 'the topic')}"
            
            # Add coaching context if high Ari readiness
            if readiness_score > 0.7:
                coaching_context = self._generate_coaching_context(coaching_opportunities)
                if coaching_context:
                    enhanced_description += f" {coaching_context}"
            
            # Add thematic context
            if themes:
                theme_context = self._generate_theme_context(themes)
                if theme_context:
                    enhanced_description += f" {theme_context}"
            
            return enhanced_description
            
        except Exception as e:
            logger.warning(f"Failed to generate enhanced description: {e}")
            if processed_data and isinstance(processed_data, dict):
                return processed_data.get("description", f"Knowledge task about {processed_data.get('title', 'the topic')}")
            else:
                return "Knowledge task about the topic"
    
    def _determine_target_audience(
        self, 
        processed_data: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        integrated_analysis: Dict[str, Any]
    ) -> str:
        """
        Determine target audience from analysis results.
        
        Args:
            processed_data: Stage 1 processing results.
            ari_analysis: Ari persona analysis results.
            integrated_analysis: Integrated analysis results.
            
        Returns:
            Target audience string.
        """
        try:
            # Check for explicit archetype in processed data
            archetype = processed_data.get("archetype", "")
            if archetype:
                return archetype
            
            # Determine from metadata
            metadata = processed_data.get("metadata", {})
            if "archetype" in metadata:
                return metadata["archetype"]
            
            # Determine from difficulty level and content characteristics
            difficulty = processed_data.get("difficulty_level", "intermediate")
            readiness_score = ari_analysis.get("ari_readiness_score", 0.5)
            
            # Map difficulty and readiness to audience
            if difficulty == "beginner":
                if readiness_score > 0.7:
                    return "nurturer"  # Supportive guidance needed
                else:
                    return "explorer"  # Discovery-oriented
            elif difficulty == "advanced":
                if readiness_score > 0.7:
                    return "achiever"  # Goal-oriented
                else:
                    return "builder"  # System-oriented
            else:  # intermediate
                if readiness_score > 0.6:
                    return "achiever"  # Balanced goal focus
                else:
                    return "explorer"  # Balanced discovery
                    
        except Exception as e:
            logger.warning(f"Failed to determine target audience: {e}")
            return "explorer"  # Default fallback
    
    def _generate_enhanced_learning_objectives(
        self, 
        processed_data: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        ai_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate enhanced learning objectives with Ari insights.
        
        Args:
            processed_data: Stage 1 processing results.
            ari_analysis: Ari persona analysis results.
            ai_analysis: AI analysis results.
            
        Returns:
            List of enhanced learning objectives.
        """
        try:
            # Get basic learning objectives
            base_objectives = processed_data.get("learning_objectives", [])
            
            # Extract insights
            ai_insights = ai_analysis.get("basic_analysis", {})
            themes = ai_insights.get("themes", [])
            key_concepts = ai_insights.get("key_concepts", [])
            
            coaching_opportunities = ari_analysis.get("coaching_opportunities", {})
            framework_integration = ari_analysis.get("framework_integration", {})
            
            # Start with base objectives or generate from themes
            objectives = base_objectives.copy() if base_objectives else []
            
            # Add objectives from themes if not already covered
            theme_objectives = self._generate_theme_based_objectives(themes)
            for objective in theme_objectives:
                if not any(self._objectives_similar(objective, existing) for existing in objectives):
                    objectives.append(objective)
            
            # Add coaching-focused objectives
            coaching_objectives = self._generate_coaching_objectives(coaching_opportunities)
            for objective in coaching_objectives:
                if not any(self._objectives_similar(objective, existing) for existing in objectives):
                    objectives.append(objective)
            
            # Add framework-based objectives
            framework_objectives = self._generate_framework_objectives(framework_integration)
            for objective in framework_objectives:
                if not any(self._objectives_similar(objective, existing) for existing in objectives):
                    objectives.append(objective)
            
            # Ensure we have at least 3 objectives
            if len(objectives) < 3:
                default_objectives = self._generate_default_objectives(processed_data)
                for objective in default_objectives:
                    if len(objectives) >= 3:
                        break
                    if not any(self._objectives_similar(objective, existing) for existing in objectives):
                        objectives.append(objective)
            
            # Limit to maximum 5 objectives
            return objectives[:5]
            
        except Exception as e:
            logger.warning(f"Failed to generate enhanced learning objectives: {e}")
            if processed_data and isinstance(processed_data, dict):
                return processed_data.get("learning_objectives", [
                    "Understand the key concepts",
                    "Apply the knowledge practically",
                    "Develop relevant skills"
                ])
            else:
                return [
                    "Understand the key concepts",
                    "Apply the knowledge practically",
                    "Develop relevant skills"
                ]
    
    def _enhance_content_items(
        self, 
        content_items: List[Dict[str, Any]], 
        ari_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance content items with Ari persona insights.
        
        Args:
            content_items: Original content items.
            ari_analysis: Ari persona analysis results.
            ari_preparation: Ari preparation recommendations.
            
        Returns:
            Enhanced content items.
        """
        try:
            enhanced_items = []
            
            for item in content_items:
                enhanced_item = item.copy()
                
                # Add Ari-specific enhancements
                enhanced_item["ari_enhancement"] = self._generate_content_ari_enhancement(
                    item, ari_analysis, ari_preparation
                )
                
                # Add coaching context if applicable
                coaching_context = self._generate_content_coaching_context(
                    item, ari_analysis
                )
                if coaching_context:
                    enhanced_item["coaching_context"] = coaching_context
                
                # Add framework alignment
                framework_alignment = self._identify_content_framework_alignment(
                    item, ari_analysis
                )
                if framework_alignment:
                    enhanced_item["framework_alignment"] = framework_alignment
                
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
            
        except Exception as e:
            logger.warning(f"Failed to enhance content items: {e}")
            return content_items
    
    def _enhance_quiz_items(
        self, 
        quiz_items: List[Dict[str, Any]], 
        ari_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance quiz items with Ari coaching style.
        
        Args:
            quiz_items: Original quiz items.
            ari_analysis: Ari persona analysis results.
            ari_preparation: Ari preparation recommendations.
            
        Returns:
            Enhanced quiz items.
        """
        try:
            enhanced_items = []
            
            for item in quiz_items:
                enhanced_item = item.copy()
                
                # Add Ari coaching style to questions
                enhanced_item["ari_coaching_style"] = self._generate_quiz_ari_enhancement(
                    item, ari_analysis, ari_preparation
                )
                
                # Add action-oriented context
                action_context = self._generate_quiz_action_context(
                    item, ari_analysis
                )
                if action_context:
                    enhanced_item["action_context"] = action_context
                
                # Add commitment questions if applicable
                commitment_questions = self._generate_commitment_questions(
                    item, ari_analysis
                )
                if commitment_questions:
                    enhanced_item["commitment_questions"] = commitment_questions
                
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
            
        except Exception as e:
            logger.warning(f"Failed to enhance quiz items: {e}")
            return quiz_items
    
    def _create_enhanced_metadata(
        self, 
        processed_data: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        ai_analysis: Dict[str, Any],
        integrated_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create enhanced metadata with comprehensive analysis results.
        
        Args:
            processed_data: Stage 1 processing results.
            ari_analysis: Ari persona analysis results.
            ai_analysis: AI analysis results.
            integrated_analysis: Integrated analysis results.
            ari_preparation: Ari preparation recommendations.
            
        Returns:
            Enhanced metadata dictionary.
        """
        try:
            # Base metadata
            base_metadata = processed_data.get("metadata", {})
            
            # Create comprehensive metadata
            enhanced_metadata = {
                # Original metadata
                **base_metadata,
                
                # Analysis results
                "content_analysis": {
                    "ai_analysis": ai_analysis,
                    "ari_analysis": ari_analysis,
                    "integrated_analysis": integrated_analysis,
                    "ari_preparation": ari_preparation
                },
                
                # Content statistics
                "content_statistics": {
                    "content_items_count": len(processed_data.get("content", [])),
                    "quiz_items_count": len(processed_data.get("quiz", [])),
                    "total_content_length": sum(len(item.get("content", "")) for item in processed_data.get("content", [])),
                    "ari_readiness_score": ari_analysis.get("ari_readiness_score", 0.5)
                },
                
                # Processing information
                "processing_info": {
                    "stage1_completed": True,
                    "content_analysis_completed": True,
                    "normalization_completed": True,
                    "processing_timestamp": datetime.now().isoformat()
                },
                
                # Quality metrics
                "quality_metrics": {
                    "content_quality_score": integrated_analysis.get("integrated_insights", {}).get("content_quality_score", 0.5),
                    "ari_integration_readiness": integrated_analysis.get("integrated_insights", {}).get("ari_integration_readiness", "medium"),
                    "coaching_transformation_potential": integrated_analysis.get("integrated_insights", {}).get("coaching_transformation_potential", "medium")
                }
            }
            
            return enhanced_metadata
            
        except Exception as e:
            logger.warning(f"Failed to create enhanced metadata: {e}")
            return processed_data.get("metadata", {})
    
    def _validate_and_enhance_structure(
        self, 
        structure: Dict[str, Any], 
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and enhance the normalized structure.
        
        CRITICAL: This method now validates the preserved input structure
        instead of adding new fields that break format compliance.
        
        Args:
            structure: Enhanced structure that preserves input format.
            analysis_result: Complete analysis result.
            
        Returns:
            Validated structure with minimal additional metadata.
        """
        try:
            validated_structure = structure.copy()
            
            # Validate that flexibleItems is present and enhanced
            if "flexibleItems" not in validated_structure:
                logger.warning("Missing flexibleItems, creating empty array")
                validated_structure["flexibleItems"] = []
            
            # Validate that required original fields are preserved
            required_original_fields = [
                "title", "dimension", "archetype", "relatedToType", 
                "relatedToId", "estimatedDuration", "coinsReward"
            ]
            
            for field in required_original_fields:
                if field not in validated_structure:
                    logger.warning(f"Missing required original field: {field}")
                    # Try to get from original structure
                    original_structure = analysis_result.get("processed_data", {}).get("original_structure", {})
                    if field in original_structure:
                        validated_structure[field] = original_structure[field]
                    else:
                        # Use default values that match original format
                        defaults = {
                            "title": "Knowledge Task",
                            "dimension": "physicalHealth",
                            "archetype": "warrior",
                            "relatedToType": "HABITBP",
                            "relatedToId": "generic",
                            "estimatedDuration": 300,
                            "coinsReward": 15
                        }
                        validated_structure[field] = defaults.get(field, "")
            
            return validated_structure
            
        except Exception as e:
            logger.error(f"Failed to validate and enhance structure: {e}")
            return structure
    
    def _add_normalization_metadata(
        self, 
        structure: Dict[str, Any], 
        file_path: str,
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add minimal normalization metadata to the final structure.
        
        CRITICAL: This method now only adds metadata that doesn't break
        format compliance. All metadata is stored in existing fields.
        
        Args:
            structure: Validated structure.
            file_path: Original file path.
            analysis_result: Complete analysis result.
            
        Returns:
            Final structure with minimal metadata additions.
        """
        try:
            final_structure = structure.copy()
            
            # Only add metadata to existing metadata field to preserve format
            if "metadata" not in final_structure:
                final_structure["metadata"] = {}
            
            # Add processing metadata to existing metadata field
            final_structure["metadata"]["_processing_info"] = {
                "source_file": file_path,
                "normalization_timestamp": datetime.now().isoformat(),
                "normalizer_version": "1.0.0",
                "analysis_version": analysis_result.get("analyzer_version", "1.0.0"),
                "processing_pipeline": [
                    "stage1_processing",
                    "content_analysis", 
                    "ari_persona_analysis",
                    "json_normalization"
                ],
                "format_compliance": "preserved",
                "enhancement_applied": True
            }
            
            return final_structure
            
        except Exception as e:
            logger.error(f"Failed to add normalization metadata: {e}")
            return structure
    
    # Helper methods for content generation and enhancement
    def _generate_coaching_context(self, coaching_opportunities: Dict[str, Any]) -> str:
        """Generate coaching context from opportunities."""
        try:
            contexts = []
            
            if coaching_opportunities.get("habit_formation"):
                contexts.append("Focus on building sustainable habits.")
            
            if coaching_opportunities.get("behavioral_change"):
                contexts.append("Explore behavioral change strategies.")
            
            if coaching_opportunities.get("motivation_points"):
                contexts.append("Discover motivation techniques.")
            
            return " ".join(contexts)
        except:
            return ""
    
    def _generate_theme_context(self, themes: List[str]) -> str:
        """Generate context from themes."""
        try:
            if not themes:
                return ""
            
            if len(themes) == 1:
                return f"Explore {themes[0]} concepts."
            elif len(themes) == 2:
                return f"Explore {themes[0]} and {themes[1]} concepts."
            else:
                return f"Explore {', '.join(themes[:-1])}, and {themes[-1]} concepts."
        except:
            return ""
    
    def _generate_theme_based_objectives(self, themes: List[str]) -> List[str]:
        """Generate learning objectives from themes."""
        objectives = []
        
        theme_mapping = {
            "morning": "Understand the benefits of morning routines",
            "routine": "Learn to establish consistent daily routines",
            "health": "Recognize the importance of healthy habits",
            "productivity": "Apply productivity techniques effectively",
            "habits": "Develop sustainable habit formation skills",
            "motivation": "Discover personal motivation strategies",
            "wellness": "Understand holistic wellness principles",
            "mindfulness": "Practice mindfulness techniques",
            "nutrition": "Learn about healthy nutrition choices",
            "exercise": "Understand the benefits of regular exercise",
            "sleep": "Learn about healthy sleep patterns",
            "stress": "Develop stress management techniques"
        }
        
        for theme in themes:
            if theme in theme_mapping:
                objectives.append(theme_mapping[theme])
        
        return objectives
    
    def _generate_coaching_objectives(self, coaching_opportunities: Dict[str, Any]) -> List[str]:
        """Generate coaching-focused objectives."""
        objectives = []
        
        if coaching_opportunities.get("habit_formation"):
            objectives.append("Master the art of habit formation")
        
        if coaching_opportunities.get("behavioral_change"):
            objectives.append("Implement effective behavioral change strategies")
        
        if coaching_opportunities.get("motivation_points"):
            objectives.append("Develop intrinsic motivation techniques")
        
        if coaching_opportunities.get("action_triggers"):
            objectives.append("Create actionable implementation plans")
        
        return objectives
    
    def _generate_framework_objectives(self, framework_integration: Dict[str, Any]) -> List[str]:
        """Generate framework-based objectives."""
        objectives = []
        
        if framework_integration.get("tiny_habits"):
            objectives.append("Apply Tiny Habits methodology for sustainable change")
        
        if framework_integration.get("behavioral_design"):
            objectives.append("Understand behavioral design principles")
        
        if framework_integration.get("huberman_protocols"):
            objectives.append("Implement science-based protocols for optimization")
        
        if framework_integration.get("perma_model"):
            objectives.append("Enhance wellbeing using PERMA model principles")
        
        return objectives
    
    def _generate_default_objectives(self, data: Dict[str, Any]) -> List[str]:
        """Generate default learning objectives."""
        title = data.get("title", "the topic") if isinstance(data, dict) else "the topic"
        
        return [
            f"Understand the key concepts of {title}",
            f"Apply {title} principles in daily life",
            f"Develop practical skills related to {title}"
        ]
    
    def _objectives_similar(self, obj1: str, obj2: str) -> bool:
        """Check if two objectives are similar."""
        return obj1.lower().strip() == obj2.lower().strip()
    
    def _calculate_estimated_duration(self, content_items: List[Dict[str, Any]], quiz_items: List[Dict[str, Any]]) -> int:
        """Calculate estimated duration in seconds."""
        try:
            # Base duration for content (average reading speed: 200 words per minute)
            content_duration = 0
            for item in content_items:
                content_text = item.get("content", "")
                word_count = len(content_text.split())
                content_duration += (word_count / 200) * 60  # Convert to seconds
            
            # Base duration for quiz (30 seconds per question)
            quiz_duration = len(quiz_items) * 30
            
            # Minimum duration of 60 seconds
            total_duration = max(int(content_duration + quiz_duration), 60)
            
            return total_duration
            
        except Exception as e:
            logger.warning(f"Failed to calculate estimated duration: {e}")
            return 300  # Default 5 minutes
    
    def _generate_tags(self, ai_analysis: Dict[str, Any], ari_analysis: Dict[str, Any]) -> List[str]:
        """Generate tags from analysis results."""
        try:
            tags = []
            
            # Add themes from AI analysis
            ai_insights = ai_analysis.get("basic_analysis", {})
            themes = ai_insights.get("themes", [])
            tags.extend(themes)
            
            # Add key concepts
            key_concepts = ai_insights.get("key_concepts", [])
            tags.extend(key_concepts)
            
            # Add framework tags
            framework_integration = ari_analysis.get("framework_integration", {})
            for framework, applicable in framework_integration.items():
                if applicable:
                    tags.append(framework.replace("_", "-"))
            
            # Remove duplicates and limit to 10 tags
            unique_tags = list(set(tags))
            return unique_tags[:10]
            
        except Exception as e:
            logger.warning(f"Failed to generate tags: {e}")
            return ["knowledge", "learning"]
    
    def _determine_dimension(self, processed_data: Dict[str, Any], ai_analysis: Dict[str, Any]) -> str:
        """Determine dimension from analysis."""
        try:
            # Check processed data first
            dimension = processed_data.get("dimension", "")
            if dimension:
                return dimension
            
            # Check metadata
            metadata = processed_data.get("metadata", {})
            if "dimension" in metadata:
                return metadata["dimension"]
            
            # Determine from themes
            ai_insights = ai_analysis.get("basic_analysis", {})
            themes = ai_insights.get("themes", [])
            
            # Map themes to dimensions
            if any(theme in ["health", "wellness", "exercise", "nutrition", "sleep"] for theme in themes):
                return "wellness"
            elif any(theme in ["productivity", "habits", "routine", "morning"] for theme in themes):
                return "productivity"
            elif any(theme in ["mindfulness", "meditation", "stress", "mental"] for theme in themes):
                return "mindfulness"
            elif any(theme in ["nutrition", "food", "diet", "eating"] for theme in themes):
                return "nutrition"
            else:
                return "wellness"  # Default
                
        except Exception as e:
            logger.warning(f"Failed to determine dimension: {e}")
            return "wellness"
    
    def _determine_archetype(self, processed_data: Dict[str, Any], ari_analysis: Dict[str, Any]) -> str:
        """Determine archetype from analysis."""
        try:
            # Check processed data first
            archetype = processed_data.get("archetype", "")
            if archetype:
                return archetype
            
            # Check metadata
            metadata = processed_data.get("metadata", {})
            if "archetype" in metadata:
                return metadata["archetype"]
            
            # Determine from Ari readiness and coaching opportunities
            readiness_score = ari_analysis.get("ari_readiness_score", 0.5)
            coaching_opportunities = ari_analysis.get("coaching_opportunities", {})
            
            # Map readiness and opportunities to archetypes
            if readiness_score > 0.8:
                return "achiever"  # High readiness for goal-oriented approach
            elif coaching_opportunities.get("habit_formation"):
                return "builder"  # System-building focus
            elif coaching_opportunities.get("motivation_points"):
                return "nurturer"  # Supportive guidance needed
            else:
                return "explorer"  # Discovery-oriented
                
        except Exception as e:
            logger.warning(f"Failed to determine archetype: {e}")
            return "explorer"
    
    def _generate_content_ari_enhancement(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Ari enhancement for content item."""
        try:
            enhancement = {
                "brevity_suggestions": [],
                "question_opportunities": [],
                "coaching_moments": []
            }
            
            # Add brevity suggestions
            engagement_patterns = ari_analysis.get("engagement_patterns", {})
            if engagement_patterns.get("brevity_potential") == "high":
                enhancement["brevity_suggestions"].append("Apply TARS-inspired conciseness")
            
            # Add question opportunities
            question_ops = engagement_patterns.get("question_opportunities", [])
            enhancement["question_opportunities"] = question_ops[:3]  # Limit to 3
            
            # Add coaching moments
            coaching_moments = engagement_patterns.get("coaching_moments", [])
            enhancement["coaching_moments"] = coaching_moments[:3]  # Limit to 3
            
            return enhancement
            
        except Exception as e:
            logger.warning(f"Failed to generate content Ari enhancement: {e}")
            return {}
    
    def _generate_content_coaching_context(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Generate coaching context for content item."""
        try:
            coaching_opportunities = ari_analysis.get("coaching_opportunities", {})
            
            contexts = []
            if coaching_opportunities.get("habit_formation"):
                contexts.append("habit-formation")
            if coaching_opportunities.get("behavioral_change"):
                contexts.append("behavioral-change")
            if coaching_opportunities.get("motivation_points"):
                contexts.append("motivation")
            
            return ", ".join(contexts) if contexts else None
            
        except Exception as e:
            logger.warning(f"Failed to generate coaching context: {e}")
            return None
    
    def _identify_content_framework_alignment(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify framework alignment for content item."""
        try:
            framework_integration = ari_analysis.get("framework_integration", {})
            
            aligned_frameworks = []
            for framework, applicable in framework_integration.items():
                if applicable:
                    aligned_frameworks.append(framework)
            
            return aligned_frameworks
            
        except Exception as e:
            logger.warning(f"Failed to identify framework alignment: {e}")
            return []
    
    def _generate_quiz_ari_enhancement(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        ari_preparation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Ari enhancement for quiz item."""
        try:
            enhancement = {
                "coaching_style": "question-heavy",
                "action_oriented": True,
                "brevity_applied": False
            }
            
            # Check for brevity potential
            engagement_patterns = ari_analysis.get("engagement_patterns", {})
            if engagement_patterns.get("brevity_potential") == "high":
                enhancement["brevity_applied"] = True
            
            # Add coaching recommendations
            recommendations = ari_preparation.get("recommendations", {})
            coaching_enhancement = recommendations.get("coaching_enhancement", [])
            if coaching_enhancement:
                enhancement["coaching_recommendations"] = coaching_enhancement[:2]
            
            return enhancement
            
        except Exception as e:
            logger.warning(f"Failed to generate quiz Ari enhancement: {e}")
            return {}
    
    def _generate_quiz_action_context(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Generate action context for quiz item."""
        try:
            coaching_opportunities = ari_analysis.get("coaching_opportunities", {})
            
            if coaching_opportunities.get("action_triggers"):
                return "action-trigger"
            elif coaching_opportunities.get("habit_formation"):
                return "habit-formation"
            elif coaching_opportunities.get("behavioral_change"):
                return "behavioral-change"
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Failed to generate action context: {e}")
            return None
    
    def _generate_commitment_questions(
        self, 
        item: Dict[str, Any], 
        ari_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate commitment questions for quiz item."""
        try:
            commitment_questions = []
            
            coaching_opportunities = ari_analysis.get("coaching_opportunities", {})
            
            if coaching_opportunities.get("action_triggers"):
                commitment_questions.append("When will you start implementing this?")
            
            if coaching_opportunities.get("habit_formation"):
                commitment_questions.append("How will you track your progress?")
            
            if coaching_opportunities.get("behavioral_change"):
                commitment_questions.append("What will you do differently tomorrow?")
            
            return commitment_questions
            
        except Exception as e:
            logger.warning(f"Failed to generate commitment questions: {e}")
            return []
    
    def _generate_default_value(self, field: str, analysis_result: Dict[str, Any]) -> Any:
        """Generate default value for missing field."""
        defaults = {
            "title": "Knowledge Task",
            "description": "Learn about important concepts",
            "target_audience": "explorer",
            "difficulty_level": "intermediate",
            "learning_objectives": ["Understand key concepts", "Apply knowledge", "Develop skills"],
            "language": "portuguese",
            "content": [{"type": "text", "content": "Content will be generated"}],
            "quiz": [{"question": "What did you learn?", "options": ["A lot", "Some", "Little"], "correct_answer": "A lot"}],
            "metadata": {}
        }
        
        return defaults.get(field, "")
    
    def _generate_default_content(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate default content items."""
        return [
            {
                "type": "text",
                "content": "This content will be enhanced with comprehensive analysis insights.",
                "ari_enhancement": {
                    "brevity_suggestions": ["Apply concise communication"],
                    "question_opportunities": ["Transform into coaching questions"],
                    "coaching_moments": ["Identify action points"]
                }
            }
        ]
    
    def _generate_default_quiz(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate default quiz items."""
        return [
            {
                "question": "What is the most important takeaway?",
                "options": ["Understanding", "Application", "Practice", "All of the above"],
                "correct_answer": "All of the above",
                "ari_coaching_style": {
                    "coaching_style": "question-heavy",
                    "action_oriented": True,
                    "brevity_applied": True
                }
            }
        ]
    
    def _generate_normalized_output_path(self, original_path: str, suffix: str) -> str:
        """Generate output path for normalized file."""
        try:
            path = Path(original_path)
            return str(path.with_name(f"{path.stem}_{suffix}{path.suffix}"))
        except Exception as e:
            logger.warning(f"Failed to generate normalized output path: {e}")
            return f"{original_path}_{suffix}"
    
    def _save_normalized_file(self, normalized_result: Dict[str, Any], output_file: str) -> None:
        """Save normalized result to file."""
        try:
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save normalized JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(normalized_result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Normalized file saved: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save normalized file {output_file}: {e}")
            raise JSONNormalizerError(f"Failed to save normalized file: {e}")
    
    def _create_directory_normalization_summary(
        self, 
        directory_analysis: Dict[str, Any],
        normalized_files: List[Dict[str, Any]],
        failed_files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create directory normalization summary."""
        try:
            total_files = len(normalized_files) + len(failed_files)
            success_rate = (len(normalized_files) / total_files * 100) if total_files > 0 else 0
            
            # Collect statistics
            languages = {}
            difficulties = {}
            
            for file_info in normalized_files:
                lang = file_info.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
            
            return {
                "total_files": total_files,
                "normalized_files": len(normalized_files),
                "failed_files": len(failed_files),
                "success_rate": success_rate,
                "language_distribution": languages,
                "processing_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to create directory normalization summary: {e}")
            return {
                "total_files": 0,
                "normalized_files": 0,
                "failed_files": 0,
                "success_rate": 0,
                "processing_timestamp": datetime.now().isoformat()
            }


# Global instance for easy access
_json_normalizer = None


def get_json_normalizer(config: Optional[Dict[str, Any]] = None) -> JSONNormalizer:
    """
    Get the global JSON normalizer instance.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        JSONNormalizer instance.
    """
    global _json_normalizer
    
    if _json_normalizer is None:
        _json_normalizer = JSONNormalizer(config)
    
    return _json_normalizer


def reset_json_normalizer():
    """Reset the global JSON normalizer instance."""
    global _json_normalizer
    _json_normalizer = None 