"""
Content analyzer module for Lyfe Supertask Knowledge Generator.

This module integrates the OpenAI client with Stage 1 functions to provide
comprehensive content analysis with Ari persona preparation. It enhances
multi-sample processing with AI-powered insights and coaching opportunities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .config_loader import get_config, load_config
from .openai_client import get_openai_client, OpenAIClientError
from .stage1_functions import (
    analyze_ari_persona_patterns,
    process_directory_with_ari_analysis,
    process_raw_file,
    Stage1ProcessingError
)


# Set up logging
logger = logging.getLogger(__name__)


class ContentAnalyzerError(Exception):
    """Custom exception for content analyzer errors."""
    pass


class ContentAnalyzer:
    """
    Content analyzer that integrates OpenAI client with Stage 1 functions.
    
    This class provides comprehensive content analysis by combining:
    - OpenAI-powered content analysis for tone, themes, and complexity
    - Ari persona pattern analysis for coaching opportunities
    - Multi-sample processing with batch analysis capabilities
    - Enhanced content insights for Ari persona preparation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the content analyzer.
        
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
            
            # Initialize OpenAI client
            self.openai_client = get_openai_client()
            
            # Set up analysis parameters
            self.analysis_config = config.get('processing', {})
            self.enable_ai_analysis = self.analysis_config.get('enable_ai_analysis', True)
            self.batch_size = self.analysis_config.get('batch_size', 10)
            
            logger.info("Content analyzer initialized successfully")
            
        except Exception as e:
            raise ContentAnalyzerError(f"Failed to initialize content analyzer: {e}")
    
    def analyze_single_file(self, file_path: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """
        Analyze a single JSON file with comprehensive content analysis.
        
        Args:
            file_path: Path to the JSON file to analyze.
            include_ai_analysis: Whether to include AI-powered analysis.
            
        Returns:
            Dictionary with comprehensive analysis results including:
            - Basic Stage 1 processing results
            - Ari persona pattern analysis
            - AI-powered content insights (if enabled)
            - Enhanced recommendations for Ari persona integration
            
        Raises:
            ContentAnalyzerError: If analysis fails.
        """
        try:
            logger.info(f"Analyzing single file: {file_path}")
            
            # Step 1: Process file through Stage 1 pipeline
            processed_data = process_raw_file(file_path)
            
            # Step 2: Perform Ari persona analysis
            content_items = processed_data.get("content", [])
            quiz_items = processed_data.get("quiz", [])
            
            ari_analysis = analyze_ari_persona_patterns(content_items, quiz_items)
            
            # Step 3: AI-powered content analysis (if enabled)
            ai_analysis = {}
            if include_ai_analysis and self.enable_ai_analysis:
                ai_analysis = self._perform_ai_analysis(content_items, quiz_items)
            
            # Step 4: Integrate analyses and generate enhanced insights
            integrated_analysis = self._integrate_analyses(
                processed_data, ari_analysis, ai_analysis
            )
            
            # Step 5: Generate Ari persona preparation recommendations
            ari_preparation = self._generate_ari_preparation_recommendations(
                integrated_analysis
            )
            
            return {
                "file_path": file_path,
                "processed_data": processed_data,
                "ari_analysis": ari_analysis,
                "ai_analysis": ai_analysis,
                "integrated_analysis": integrated_analysis,
                "ari_preparation": ari_preparation,
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzer_version": "1.0.0"
            }
            
        except (Stage1ProcessingError, OpenAIClientError) as e:
            raise ContentAnalyzerError(f"Analysis failed for {file_path}: {e}")
        except Exception as e:
            raise ContentAnalyzerError(f"Unexpected error analyzing {file_path}: {e}")
    
    def analyze_directory(self, input_dir: str, output_dir: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
        """
        Analyze multiple JSON files in a directory with comprehensive content analysis.
        
        Args:
            input_dir: Directory containing raw JSON files.
            output_dir: Directory to save processed JSON files.
            include_ai_analysis: Whether to include AI-powered analysis.
            
        Returns:
            Dictionary with comprehensive analysis results for all files including:
            - Basic directory processing results
            - Per-file Ari persona analysis
            - Batch AI analysis insights
            - Cross-file pattern recognition
            - Enhanced Ari persona preparation recommendations
            
        Raises:
            ContentAnalyzerError: If directory analysis fails.
        """
        try:
            logger.info(f"Analyzing directory: {input_dir}")
            
            # Step 1: Process directory through enhanced Stage 1 pipeline
            directory_results = process_directory_with_ari_analysis(input_dir, output_dir)
            
            # Step 2: Enhance with AI analysis (if enabled)
            enhanced_results = directory_results.copy()
            
            if include_ai_analysis and self.enable_ai_analysis:
                enhanced_results = self._enhance_directory_with_ai_analysis(
                    directory_results, output_dir
                )
            
            # Step 3: Perform cross-file pattern analysis
            cross_file_analysis = self._analyze_cross_file_patterns(enhanced_results)
            
            # Step 4: Generate comprehensive Ari persona preparation
            comprehensive_ari_preparation = self._generate_comprehensive_ari_preparation(
                enhanced_results, cross_file_analysis
            )
            
            # Step 5: Create analysis summary
            analysis_summary = self._create_analysis_summary(
                enhanced_results, cross_file_analysis, comprehensive_ari_preparation
            )
            
            return {
                "input_directory": input_dir,
                "output_directory": output_dir,
                "directory_results": enhanced_results,
                "cross_file_analysis": cross_file_analysis,
                "comprehensive_ari_preparation": comprehensive_ari_preparation,
                "analysis_summary": analysis_summary,
                "analysis_timestamp": datetime.now().isoformat(),
                "analyzer_version": "1.0.0"
            }
            
        except Stage1ProcessingError as e:
            raise ContentAnalyzerError(f"Directory analysis failed: {e}")
        except Exception as e:
            raise ContentAnalyzerError(f"Unexpected error analyzing directory {input_dir}: {e}")
    
    def _perform_ai_analysis(self, content_items: List[Dict[str, Any]], quiz_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform AI-powered content analysis using OpenAI client.
        
        Args:
            content_items: List of content items to analyze.
            quiz_items: List of quiz items to analyze.
            
        Returns:
            Dictionary with AI analysis results.
        """
        try:
            # Combine content for analysis
            combined_content = []
            
            # Add content items
            for item in content_items:
                content_text = item.get("content", "")
                if content_text:
                    combined_content.append(content_text)
            
            # Add quiz questions
            for item in quiz_items:
                question_text = item.get("question", "")
                if question_text:
                    combined_content.append(question_text)
            
            # Perform AI analysis if we have content
            if combined_content:
                full_content = " ".join(combined_content)
                
                # Use OpenAI client for analysis
                ai_analysis = self.openai_client.analyze_content(
                    content=full_content,
                    analysis_type="comprehensive"
                )
                
                # Enhance with Ari-specific analysis
                ari_specific_analysis = self._enhance_with_ari_specific_analysis(
                    full_content, ai_analysis
                )
                
                return {
                    "basic_analysis": ai_analysis,
                    "ari_specific_analysis": ari_specific_analysis,
                    "content_length": len(full_content),
                    "content_items_count": len(content_items),
                    "quiz_items_count": len(quiz_items)
                }
            
            return {
                "basic_analysis": {},
                "ari_specific_analysis": {},
                "content_length": 0,
                "content_items_count": 0,
                "quiz_items_count": 0,
                "note": "No content available for AI analysis"
            }
            
        except OpenAIClientError as e:
            logger.warning(f"AI analysis failed, using fallback: {e}")
            return {
                "basic_analysis": {
                    "tone": "neutral",
                    "themes": ["general"],
                    "complexity": "intermediate",
                    "language": "pt",
                    "key_concepts": ["content analysis"],
                    "estimated_reading_time": 5
                },
                "ari_specific_analysis": {
                    "coaching_potential": "medium",
                    "question_transformation_opportunities": [],
                    "brevity_recommendations": [],
                    "framework_alignment": []
                },
                "analysis_error": str(e)
            }
    
    def _enhance_with_ari_specific_analysis(self, content: str, basic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance AI analysis with Ari-specific coaching insights.
        
        Args:
            content: The content to analyze.
            basic_analysis: Basic AI analysis results.
            
        Returns:
            Dictionary with Ari-specific analysis enhancements.
        """
        try:
            # Create Ari-specific analysis prompt
            ari_prompt = f"""
            Analyze this content from the perspective of Ari, a male life coach with TARS-inspired personality.
            
            Content: {content[:1000]}...
            
            Basic Analysis: {json.dumps(basic_analysis, indent=2)}
            
            Provide Ari-specific coaching analysis:
            1. Coaching potential (high/medium/low)
            2. Question transformation opportunities (how to make content more question-heavy)
            3. Brevity recommendations (how to apply TARS-inspired conciseness)
            4. Framework alignment (which of Ari's 9 frameworks apply)
            5. Engagement progression opportunities
            
            Return as JSON with these fields:
            - coaching_potential
            - question_transformation_opportunities (array)
            - brevity_recommendations (array)
            - framework_alignment (array)
            - engagement_progression (string)
            """
            
            # Use OpenAI client for Ari-specific analysis
            ari_response = self.openai_client.generate_completion(
                prompt=ari_prompt,
                system_message="You are an expert in Ari's coaching methodology and TARS-inspired communication.",
                temperature=0.4
            )
            
            # Try to parse JSON response
            try:
                ari_analysis = json.loads(ari_response)
                return ari_analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "coaching_potential": "medium",
                    "question_transformation_opportunities": [
                        "Transform declarative statements into coaching questions",
                        "Add 'When will you start?' commitment questions"
                    ],
                    "brevity_recommendations": [
                        "Apply TARS-inspired conciseness",
                        "Use active voice and concrete language"
                    ],
                    "framework_alignment": [
                        "Tiny Habits methodology applicable",
                        "Behavioral Design principles relevant"
                    ],
                    "engagement_progression": "standard"
                }
                
        except Exception as e:
            logger.warning(f"Ari-specific analysis failed: {e}")
            return {
                "coaching_potential": "medium",
                "question_transformation_opportunities": [],
                "brevity_recommendations": [],
                "framework_alignment": [],
                "engagement_progression": "standard",
                "analysis_error": str(e)
            }
    
    def _integrate_analyses(self, processed_data: Dict[str, Any], ari_analysis: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate Stage 1 processing, Ari persona analysis, and AI analysis.
        
        Args:
            processed_data: Stage 1 processing results.
            ari_analysis: Ari persona analysis results.
            ai_analysis: AI analysis results.
            
        Returns:
            Dictionary with integrated analysis results.
        """
        try:
            # Extract key insights from each analysis
            stage1_insights = {
                "title": processed_data.get("title", ""),
                "language": processed_data.get("language", "portuguese"),
                "difficulty_level": processed_data.get("difficulty_level", "intermediate"),
                "content_count": len(processed_data.get("content", [])),
                "quiz_count": len(processed_data.get("quiz", []))
            }
            
            ari_insights = {
                "readiness_score": ari_analysis.get("ari_readiness_score", 0.5),
                "coaching_opportunities": ari_analysis.get("coaching_opportunities", {}),
                "framework_integration": ari_analysis.get("framework_integration", {}),
                "engagement_patterns": ari_analysis.get("engagement_patterns", {})
            }
            
            ai_insights = {
                "tone": ai_analysis.get("basic_analysis", {}).get("tone", "neutral"),
                "themes": ai_analysis.get("basic_analysis", {}).get("themes", []),
                "complexity": ai_analysis.get("basic_analysis", {}).get("complexity", "intermediate"),
                "key_concepts": ai_analysis.get("basic_analysis", {}).get("key_concepts", []),
                "ari_coaching_potential": ai_analysis.get("ari_specific_analysis", {}).get("coaching_potential", "medium")
            }
            
            # Create integrated insights
            integrated_insights = {
                "content_quality_score": self._calculate_content_quality_score(stage1_insights, ari_insights, ai_insights),
                "ari_integration_readiness": self._assess_ari_integration_readiness(ari_insights, ai_insights),
                "coaching_transformation_potential": self._assess_coaching_transformation_potential(ari_insights, ai_insights),
                "framework_applicability": self._assess_framework_applicability(ari_insights, ai_insights),
                "content_enhancement_priorities": self._identify_content_enhancement_priorities(stage1_insights, ari_insights, ai_insights)
            }
            
            return {
                "stage1_insights": stage1_insights,
                "ari_insights": ari_insights,
                "ai_insights": ai_insights,
                "integrated_insights": integrated_insights
            }
            
        except Exception as e:
            logger.warning(f"Analysis integration failed: {e}")
            return {
                "stage1_insights": stage1_insights if 'stage1_insights' in locals() else {},
                "ari_insights": ari_insights if 'ari_insights' in locals() else {},
                "ai_insights": ai_insights if 'ai_insights' in locals() else {},
                "integrated_insights": {},
                "integration_error": str(e)
            }
    
    def _generate_ari_preparation_recommendations(self, integrated_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate specific recommendations for Ari persona preparation.
        
        Args:
            integrated_analysis: Integrated analysis results.
            
        Returns:
            Dictionary with Ari preparation recommendations.
        """
        try:
            integrated_insights = integrated_analysis.get("integrated_insights", {})
            ari_insights = integrated_analysis.get("ari_insights", {})
            ai_insights = integrated_analysis.get("ai_insights", {})
            
            # Generate specific recommendations
            recommendations = {
                "voice_adaptation": self._generate_voice_adaptation_recommendations(ari_insights, ai_insights),
                "coaching_enhancement": self._generate_coaching_enhancement_recommendations(ari_insights),
                "framework_integration": self._generate_framework_integration_recommendations(ari_insights),
                "engagement_optimization": self._generate_engagement_optimization_recommendations(ari_insights, ai_insights),
                "content_transformation": self._generate_content_transformation_recommendations(integrated_insights),
                "priority_actions": self._generate_priority_actions(integrated_insights)
            }
            
            return {
                "recommendations": recommendations,
                "readiness_assessment": integrated_insights.get("ari_integration_readiness", "medium"),
                "transformation_potential": integrated_insights.get("coaching_transformation_potential", "medium"),
                "implementation_complexity": self._assess_implementation_complexity(recommendations)
            }
            
        except Exception as e:
            logger.warning(f"Ari preparation recommendations failed: {e}")
            return {
                "recommendations": {
                    "voice_adaptation": ["Apply TARS-inspired brevity"],
                    "coaching_enhancement": ["Transform statements into questions"],
                    "framework_integration": ["Consider Tiny Habits methodology"],
                    "engagement_optimization": ["Progressive engagement approach"],
                    "content_transformation": ["Enhance with coaching style"],
                    "priority_actions": ["Start with voice adaptation"]
                },
                "readiness_assessment": "medium",
                "transformation_potential": "medium",
                "implementation_complexity": "medium",
                "generation_error": str(e)
            }
    
    def _enhance_directory_with_ai_analysis(self, directory_results: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Enhance directory results with AI analysis for each file.
        
        Args:
            directory_results: Directory processing results.
            output_dir: Output directory path.
            
        Returns:
            Enhanced directory results with AI analysis.
        """
        try:
            enhanced_results = directory_results.copy()
            enhanced_results["ai_analysis"] = []
            
            # Process each file with AI analysis
            for file_info in directory_results.get("processed", []):
                try:
                    # Load processed file
                    output_file = file_info["output_file"]
                    with open(output_file, 'r', encoding='utf-8') as f:
                        processed_data = json.load(f)
                    
                    # Perform AI analysis
                    content_items = processed_data.get("content", [])
                    quiz_items = processed_data.get("quiz", [])
                    
                    ai_analysis = self._perform_ai_analysis(content_items, quiz_items)
                    
                    enhanced_results["ai_analysis"].append({
                        "file": file_info["input_file"],
                        "title": file_info["title"],
                        "language": file_info["language"],
                        "ai_analysis": ai_analysis
                    })
                    
                except Exception as e:
                    logger.warning(f"AI analysis failed for {file_info['input_file']}: {e}")
                    enhanced_results["ai_analysis"].append({
                        "file": file_info["input_file"],
                        "title": file_info["title"],
                        "language": file_info["language"],
                        "ai_analysis": {"error": str(e)}
                    })
            
            return enhanced_results
            
        except Exception as e:
            logger.warning(f"Directory AI enhancement failed: {e}")
            return directory_results
    
    def _analyze_cross_file_patterns(self, enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patterns across multiple files for insights.
        
        Args:
            enhanced_results: Enhanced directory results.
            
        Returns:
            Dictionary with cross-file pattern analysis.
        """
        try:
            # Analyze Ari persona patterns across files
            ari_analyses = enhanced_results.get("ari_persona_analysis", [])
            
            # Collect framework integration patterns
            framework_patterns = {}
            coaching_patterns = {}
            language_patterns = {}
            
            for analysis in ari_analyses:
                ari_data = analysis.get("ari_analysis", {})
                
                # Framework integration patterns
                frameworks = ari_data.get("framework_integration", {})
                for framework, applicable in frameworks.items():
                    if applicable:
                        framework_patterns[framework] = framework_patterns.get(framework, 0) + 1
                
                # Coaching opportunity patterns
                coaching_ops = ari_data.get("coaching_opportunities", {})
                for opportunity_type, opportunities in coaching_ops.items():
                    if opportunities:
                        coaching_patterns[opportunity_type] = coaching_patterns.get(opportunity_type, 0) + 1
                
                # Language patterns
                lang_patterns = ari_data.get("language_patterns", {})
                lang = lang_patterns.get("cultural_context", "general")
                language_patterns[lang] = language_patterns.get(lang, 0) + 1
            
            # Analyze AI patterns if available
            ai_patterns = {}
            ai_analyses = enhanced_results.get("ai_analysis", [])
            
            for analysis in ai_analyses:
                ai_data = analysis.get("ai_analysis", {})
                basic_analysis = ai_data.get("basic_analysis", {})
                
                # Collect tone patterns
                tone = basic_analysis.get("tone", "neutral")
                if "tone_patterns" not in ai_patterns:
                    ai_patterns["tone_patterns"] = {}
                ai_patterns["tone_patterns"][tone] = ai_patterns["tone_patterns"].get(tone, 0) + 1
                
                # Collect complexity patterns
                complexity = basic_analysis.get("complexity", "intermediate")
                if "complexity_patterns" not in ai_patterns:
                    ai_patterns["complexity_patterns"] = {}
                ai_patterns["complexity_patterns"][complexity] = ai_patterns["complexity_patterns"].get(complexity, 0) + 1
            
            return {
                "framework_patterns": framework_patterns,
                "coaching_patterns": coaching_patterns,
                "language_patterns": language_patterns,
                "ai_patterns": ai_patterns,
                "total_files_analyzed": len(ari_analyses),
                "pattern_strength": self._calculate_pattern_strength(framework_patterns, coaching_patterns)
            }
            
        except Exception as e:
            logger.warning(f"Cross-file pattern analysis failed: {e}")
            return {
                "framework_patterns": {},
                "coaching_patterns": {},
                "language_patterns": {},
                "ai_patterns": {},
                "total_files_analyzed": 0,
                "pattern_strength": "low",
                "analysis_error": str(e)
            }
    
    def _generate_comprehensive_ari_preparation(self, enhanced_results: Dict[str, Any], cross_file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive Ari persona preparation recommendations.
        
        Args:
            enhanced_results: Enhanced directory results.
            cross_file_analysis: Cross-file pattern analysis.
            
        Returns:
            Dictionary with comprehensive Ari preparation recommendations.
        """
        try:
            # Analyze overall readiness
            ari_summary = enhanced_results.get("ari_summary", {})
            average_readiness = ari_summary.get("average_ari_readiness", 0.5)
            
            # Generate comprehensive recommendations
            comprehensive_recommendations = {
                "overall_readiness": self._assess_overall_readiness(average_readiness, cross_file_analysis),
                "framework_integration_strategy": self._create_framework_integration_strategy(cross_file_analysis),
                "coaching_transformation_plan": self._create_coaching_transformation_plan(cross_file_analysis),
                "voice_adaptation_guidelines": self._create_voice_adaptation_guidelines(cross_file_analysis),
                "content_enhancement_roadmap": self._create_content_enhancement_roadmap(enhanced_results, cross_file_analysis),
                "implementation_phases": self._create_implementation_phases(cross_file_analysis)
            }
            
            return comprehensive_recommendations
            
        except Exception as e:
            logger.warning(f"Comprehensive Ari preparation failed: {e}")
            return {
                "overall_readiness": "medium",
                "framework_integration_strategy": ["Apply most common frameworks first"],
                "coaching_transformation_plan": ["Transform statements to questions"],
                "voice_adaptation_guidelines": ["Apply TARS-inspired brevity"],
                "content_enhancement_roadmap": ["Enhance content with coaching style"],
                "implementation_phases": ["Phase 1: Voice adaptation", "Phase 2: Framework integration"],
                "generation_error": str(e)
            }
    
    def _create_analysis_summary(self, enhanced_results: Dict[str, Any], cross_file_analysis: Dict[str, Any], comprehensive_ari_preparation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive analysis summary.
        
        Args:
            enhanced_results: Enhanced directory results.
            cross_file_analysis: Cross-file pattern analysis.
            comprehensive_ari_preparation: Comprehensive Ari preparation.
            
        Returns:
            Dictionary with analysis summary.
        """
        try:
            # Basic statistics
            total_files = enhanced_results.get("total_files", 0)
            successful_files = enhanced_results.get("successful", 0)
            failed_files = enhanced_results.get("failed_count", 0)
            
            # Ari analysis statistics
            ari_summary = enhanced_results.get("ari_summary", {})
            average_readiness = ari_summary.get("average_ari_readiness", 0.5)
            high_readiness_files = ari_summary.get("high_readiness_files", 0)
            
            # Cross-file patterns
            framework_patterns = cross_file_analysis.get("framework_patterns", {})
            coaching_patterns = cross_file_analysis.get("coaching_patterns", {})
            
            # Overall assessment
            overall_readiness = comprehensive_ari_preparation.get("overall_readiness", "medium")
            
            return {
                "processing_summary": {
                    "total_files": total_files,
                    "successful_files": successful_files,
                    "failed_files": failed_files,
                    "success_rate": (successful_files / total_files * 100) if total_files > 0 else 0
                },
                "ari_readiness_summary": {
                    "average_readiness_score": average_readiness,
                    "high_readiness_files": high_readiness_files,
                    "overall_assessment": overall_readiness
                },
                "pattern_summary": {
                    "most_applicable_frameworks": sorted(framework_patterns.items(), key=lambda x: x[1], reverse=True)[:3],
                    "most_common_coaching_opportunities": sorted(coaching_patterns.items(), key=lambda x: x[1], reverse=True)[:3],
                    "pattern_consistency": cross_file_analysis.get("pattern_strength", "medium")
                },
                "recommendations_summary": {
                    "priority_frameworks": self._extract_priority_frameworks(framework_patterns),
                    "key_coaching_enhancements": self._extract_key_coaching_enhancements(coaching_patterns),
                    "implementation_complexity": self._assess_overall_implementation_complexity(comprehensive_ari_preparation)
                }
            }
            
        except Exception as e:
            logger.warning(f"Analysis summary creation failed: {e}")
            return {
                "processing_summary": {"error": str(e)},
                "ari_readiness_summary": {"error": str(e)},
                "pattern_summary": {"error": str(e)},
                "recommendations_summary": {"error": str(e)}
            }
    
    # Helper methods for analysis calculations
    def _calculate_content_quality_score(self, stage1_insights: Dict[str, Any], ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> float:
        """Calculate overall content quality score."""
        try:
            # Base score from content structure
            base_score = 0.3
            
            # Ari readiness contribution
            ari_score = ari_insights.get("readiness_score", 0.5) * 0.4
            
            # AI analysis contribution
            complexity_bonus = 0.1 if ai_insights.get("complexity") == "intermediate" else 0.05
            tone_bonus = 0.1 if ai_insights.get("tone") in ["motivational", "inspirational"] else 0.05
            
            return min(base_score + ari_score + complexity_bonus + tone_bonus, 1.0)
        except:
            return 0.5
    
    def _assess_ari_integration_readiness(self, ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> str:
        """Assess readiness for Ari integration."""
        try:
            readiness_score = ari_insights.get("readiness_score", 0.5)
            coaching_potential = ai_insights.get("ari_coaching_potential", "medium")
            
            if readiness_score >= 0.7 and coaching_potential == "high":
                return "high"
            elif readiness_score >= 0.4 and coaching_potential in ["medium", "high"]:
                return "medium"
            else:
                return "low"
        except:
            return "medium"
    
    def _assess_coaching_transformation_potential(self, ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> str:
        """Assess potential for coaching transformation."""
        try:
            coaching_opportunities = ari_insights.get("coaching_opportunities", {})
            total_opportunities = sum(len(opportunities) for opportunities in coaching_opportunities.values())
            
            if total_opportunities >= 4:
                return "high"
            elif total_opportunities >= 2:
                return "medium"
            else:
                return "low"
        except:
            return "medium"
    
    def _assess_framework_applicability(self, ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> List[str]:
        """Assess which frameworks are most applicable."""
        try:
            framework_integration = ari_insights.get("framework_integration", {})
            applicable_frameworks = [framework for framework, applicable in framework_integration.items() if applicable]
            return applicable_frameworks[:3]  # Top 3 most applicable
        except:
            return ["tiny_habits", "behavioral_design"]
    
    def _identify_content_enhancement_priorities(self, stage1_insights: Dict[str, Any], ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> List[str]:
        """Identify content enhancement priorities."""
        try:
            priorities = []
            
            # Check for coaching opportunities
            coaching_opportunities = ari_insights.get("coaching_opportunities", {})
            if coaching_opportunities.get("habit_formation"):
                priorities.append("Enhance habit formation content")
            if coaching_opportunities.get("behavioral_change"):
                priorities.append("Apply behavioral change principles")
            if coaching_opportunities.get("motivation_points"):
                priorities.append("Strengthen motivational elements")
            
            # Check AI insights
            if ai_insights.get("tone") == "neutral":
                priorities.append("Enhance content tone")
            
            return priorities[:3]  # Top 3 priorities
        except:
            return ["Enhance coaching style", "Apply framework integration", "Improve engagement"]
    
    def _generate_voice_adaptation_recommendations(self, ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> List[str]:
        """Generate voice adaptation recommendations."""
        try:
            recommendations = []
            
            # TARS-inspired brevity
            recommendations.append("Apply TARS-inspired brevity and conciseness")
            
            # Question-heavy approach
            engagement_patterns = ari_insights.get("engagement_patterns", {})
            if engagement_patterns.get("question_opportunities"):
                recommendations.append("Transform declarative statements into coaching questions")
            
            # Masculine Portuguese forms
            language_patterns = ari_insights.get("language_patterns", {})
            if language_patterns.get("masculine_forms_needed"):
                recommendations.append("Ensure masculine Portuguese forms for Ari's identity")
            
            return recommendations
        except:
            return ["Apply TARS-inspired brevity", "Use question-heavy coaching approach"]
    
    def _generate_coaching_enhancement_recommendations(self, ari_insights: Dict[str, Any]) -> List[str]:
        """Generate coaching enhancement recommendations."""
        try:
            recommendations = []
            
            coaching_opportunities = ari_insights.get("coaching_opportunities", {})
            
            if coaching_opportunities.get("habit_formation"):
                recommendations.append("Integrate Tiny Habits methodology")
            if coaching_opportunities.get("behavioral_change"):
                recommendations.append("Apply Behavioral Design principles")
            if coaching_opportunities.get("motivation_points"):
                recommendations.append("Enhance motivational content with progressive engagement")
            if coaching_opportunities.get("action_triggers"):
                recommendations.append("Transform action items into commitment questions")
            
            return recommendations
        except:
            return ["Enhance coaching style", "Apply framework integration"]
    
    def _generate_framework_integration_recommendations(self, ari_insights: Dict[str, Any]) -> List[str]:
        """Generate framework integration recommendations."""
        try:
            recommendations = []
            
            framework_integration = ari_insights.get("framework_integration", {})
            
            if framework_integration.get("tiny_habits"):
                recommendations.append("Integrate BJ Fogg's Tiny Habits methodology")
            if framework_integration.get("behavioral_design"):
                recommendations.append("Apply Jason Hreha's Behavioral Design principles")
            if framework_integration.get("huberman_protocols"):
                recommendations.append("Integrate Huberman Protocols for sleep and circadian content")
            if framework_integration.get("perma_model"):
                recommendations.append("Apply PERMA model for wellbeing enhancement")
            
            return recommendations
        except:
            return ["Apply most relevant frameworks", "Start with Tiny Habits methodology"]
    
    def _generate_engagement_optimization_recommendations(self, ari_insights: Dict[str, Any], ai_insights: Dict[str, Any]) -> List[str]:
        """Generate engagement optimization recommendations."""
        try:
            recommendations = []
            
            engagement_patterns = ari_insights.get("engagement_patterns", {})
            
            brevity_potential = engagement_patterns.get("brevity_potential", "medium")
            if brevity_potential == "high":
                recommendations.append("Apply significant brevity improvements")
            
            progressive_engagement = engagement_patterns.get("progressive_engagement", "standard")
            if progressive_engagement == "extended":
                recommendations.append("Structure content for extended engagement with multiple touchpoints")
            
            coaching_moments = engagement_patterns.get("coaching_moments", [])
            if coaching_moments:
                recommendations.append("Leverage identified coaching moments for maximum impact")
            
            return recommendations
        except:
            return ["Optimize engagement progression", "Apply TARS-inspired brevity"]
    
    def _generate_content_transformation_recommendations(self, integrated_insights: Dict[str, Any]) -> List[str]:
        """Generate content transformation recommendations."""
        try:
            recommendations = []
            
            quality_score = integrated_insights.get("content_quality_score", 0.5)
            if quality_score < 0.7:
                recommendations.append("Enhance overall content quality")
            
            transformation_potential = integrated_insights.get("coaching_transformation_potential", "medium")
            if transformation_potential == "high":
                recommendations.append("Apply comprehensive coaching transformation")
            
            framework_applicability = integrated_insights.get("framework_applicability", [])
            if len(framework_applicability) >= 2:
                recommendations.append("Integrate multiple frameworks for comprehensive enhancement")
            
            return recommendations
        except:
            return ["Transform content with coaching style", "Apply framework integration"]
    
    def _generate_priority_actions(self, integrated_insights: Dict[str, Any]) -> List[str]:
        """Generate priority actions for implementation."""
        try:
            priorities = []
            
            # Check integration readiness
            readiness = integrated_insights.get("ari_integration_readiness", "medium")
            if readiness == "high":
                priorities.append("Begin immediate Ari persona integration")
            elif readiness == "medium":
                priorities.append("Enhance content before Ari integration")
            else:
                priorities.append("Focus on basic content improvement first")
            
            # Check enhancement priorities
            enhancement_priorities = integrated_insights.get("content_enhancement_priorities", [])
            if enhancement_priorities:
                priorities.extend(enhancement_priorities[:2])
            
            return priorities[:3]  # Top 3 priorities
        except:
            return ["Enhance content quality", "Apply coaching methodology", "Integrate frameworks"]
    
    def _assess_implementation_complexity(self, recommendations: Dict[str, Any]) -> str:
        """Assess implementation complexity."""
        try:
            total_recommendations = sum(len(rec_list) for rec_list in recommendations.values())
            
            if total_recommendations >= 15:
                return "high"
            elif total_recommendations >= 8:
                return "medium"
            else:
                return "low"
        except:
            return "medium"
    
    def _calculate_pattern_strength(self, framework_patterns: Dict[str, int], coaching_patterns: Dict[str, int]) -> str:
        """Calculate pattern strength across files."""
        try:
            total_patterns = sum(framework_patterns.values()) + sum(coaching_patterns.values())
            
            if total_patterns >= 10:
                return "high"
            elif total_patterns >= 5:
                return "medium"
            else:
                return "low"
        except:
            return "medium"
    
    def _assess_overall_readiness(self, average_readiness: float, cross_file_analysis: Dict[str, Any]) -> str:
        """Assess overall readiness across all files."""
        try:
            pattern_strength = cross_file_analysis.get("pattern_strength", "medium")
            
            if average_readiness >= 0.7 and pattern_strength == "high":
                return "high"
            elif average_readiness >= 0.4 and pattern_strength in ["medium", "high"]:
                return "medium"
            else:
                return "low"
        except:
            return "medium"
    
    def _create_framework_integration_strategy(self, cross_file_analysis: Dict[str, Any]) -> List[str]:
        """Create framework integration strategy."""
        try:
            framework_patterns = cross_file_analysis.get("framework_patterns", {})
            sorted_frameworks = sorted(framework_patterns.items(), key=lambda x: x[1], reverse=True)
            
            strategy = []
            for framework, count in sorted_frameworks[:3]:
                strategy.append(f"Integrate {framework} framework (applicable to {count} files)")
            
            return strategy
        except:
            return ["Apply most common frameworks", "Start with Tiny Habits", "Integrate Behavioral Design"]
    
    def _create_coaching_transformation_plan(self, cross_file_analysis: Dict[str, Any]) -> List[str]:
        """Create coaching transformation plan."""
        try:
            coaching_patterns = cross_file_analysis.get("coaching_patterns", {})
            sorted_patterns = sorted(coaching_patterns.items(), key=lambda x: x[1], reverse=True)
            
            plan = []
            for pattern, count in sorted_patterns[:3]:
                plan.append(f"Transform {pattern} content (found in {count} files)")
            
            return plan
        except:
            return ["Transform statements to questions", "Enhance motivational content", "Apply coaching methodology"]
    
    def _create_voice_adaptation_guidelines(self, cross_file_analysis: Dict[str, Any]) -> List[str]:
        """Create voice adaptation guidelines."""
        try:
            language_patterns = cross_file_analysis.get("language_patterns", {})
            
            guidelines = []
            guidelines.append("Apply TARS-inspired brevity and conciseness")
            
            if "portuguese" in language_patterns:
                guidelines.append("Maintain masculine Portuguese forms for Ari's identity")
            
            guidelines.append("Use question-heavy coaching approach")
            guidelines.append("Apply progressive engagement patterns")
            
            return guidelines
        except:
            return ["Apply TARS-inspired brevity", "Use coaching questions", "Maintain cultural authenticity"]
    
    def _create_content_enhancement_roadmap(self, enhanced_results: Dict[str, Any], cross_file_analysis: Dict[str, Any]) -> List[str]:
        """Create content enhancement roadmap."""
        try:
            roadmap = []
            
            # Check overall readiness
            ari_summary = enhanced_results.get("ari_summary", {})
            average_readiness = ari_summary.get("average_ari_readiness", 0.5)
            
            if average_readiness < 0.6:
                roadmap.append("Phase 1: Basic content quality improvement")
            
            roadmap.append("Phase 2: Framework integration implementation")
            roadmap.append("Phase 3: Coaching style transformation")
            roadmap.append("Phase 4: Voice adaptation and finalization")
            
            return roadmap
        except:
            return ["Phase 1: Content improvement", "Phase 2: Framework integration", "Phase 3: Voice adaptation"]
    
    def _create_implementation_phases(self, cross_file_analysis: Dict[str, Any]) -> List[str]:
        """Create implementation phases."""
        try:
            phases = []
            
            pattern_strength = cross_file_analysis.get("pattern_strength", "medium")
            
            if pattern_strength == "high":
                phases.append("Phase 1: Immediate framework integration")
                phases.append("Phase 2: Voice adaptation")
                phases.append("Phase 3: Content enhancement")
            elif pattern_strength == "medium":
                phases.append("Phase 1: Content analysis and preparation")
                phases.append("Phase 2: Framework integration")
                phases.append("Phase 3: Voice adaptation")
            else:
                phases.append("Phase 1: Basic content improvement")
                phases.append("Phase 2: Pattern identification")
                phases.append("Phase 3: Gradual framework integration")
            
            return phases
        except:
            return ["Phase 1: Preparation", "Phase 2: Implementation", "Phase 3: Optimization"]
    
    def _extract_priority_frameworks(self, framework_patterns: Dict[str, int]) -> List[str]:
        """Extract priority frameworks from patterns."""
        try:
            sorted_frameworks = sorted(framework_patterns.items(), key=lambda x: x[1], reverse=True)
            return [framework for framework, count in sorted_frameworks[:3]]
        except:
            return ["tiny_habits", "behavioral_design", "huberman_protocols"]
    
    def _extract_key_coaching_enhancements(self, coaching_patterns: Dict[str, int]) -> List[str]:
        """Extract key coaching enhancements from patterns."""
        try:
            sorted_patterns = sorted(coaching_patterns.items(), key=lambda x: x[1], reverse=True)
            return [pattern for pattern, count in sorted_patterns[:3]]
        except:
            return ["habit_formation", "behavioral_change", "motivation_points"]
    
    def _assess_overall_implementation_complexity(self, comprehensive_ari_preparation: Dict[str, Any]) -> str:
        """Assess overall implementation complexity."""
        try:
            phases = comprehensive_ari_preparation.get("implementation_phases", [])
            
            if len(phases) >= 4:
                return "high"
            elif len(phases) >= 3:
                return "medium"
            else:
                return "low"
        except:
            return "medium"


# Global instance for easy access
_content_analyzer = None


def get_content_analyzer(config: Optional[Dict[str, Any]] = None) -> ContentAnalyzer:
    """
    Get the global content analyzer instance.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        ContentAnalyzer instance.
    """
    global _content_analyzer
    
    if _content_analyzer is None:
        _content_analyzer = ContentAnalyzer(config)
    
    return _content_analyzer


def reset_content_analyzer():
    """Reset the global content analyzer instance."""
    global _content_analyzer
    _content_analyzer = None 