"""
Stage 1 functions for raw content analysis.

This module implements the first stage of the knowledge task generation pipeline:
Raw Content Analysis (work/01_raw/ → work/02_preprocessed/)

The functions in this module:
1. Load and parse raw JSON files
2. Extract content and metadata from flexible item structures
3. Analyze content structure, tone, and themes
4. Normalize the structure into preprocessed JSON format
5. Prepare content patterns for Ari persona integration
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .config_loader import get_config


class Stage1ProcessingError(Exception):
    """Custom exception for Stage 1 processing errors."""
    pass


def load_raw_json(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a raw JSON file.
    
    Args:
        file_path: Path to the JSON file to load.
        
    Returns:
        Dictionary containing the parsed JSON data.
        
    Raises:
        Stage1ProcessingError: If file cannot be loaded or parsed.
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise Stage1ProcessingError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise Stage1ProcessingError(f"Path is not a file: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            if not content:
                raise Stage1ProcessingError(f"File is empty: {file_path}")
            
            data = json.loads(content)
            
            if not isinstance(data, dict):
                raise Stage1ProcessingError(f"JSON must be an object, not {type(data).__name__}: {file_path}")
            
            return data
            
    except json.JSONDecodeError as e:
        raise Stage1ProcessingError(f"Invalid JSON in file {file_path}: {e}")
    except UnicodeDecodeError as e:
        raise Stage1ProcessingError(f"File encoding error in {file_path}: {e}")
    except Exception as e:
        raise Stage1ProcessingError(f"Unexpected error loading {file_path}: {e}")


def extract_content(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract content and metadata from raw supertask data.
    
    Args:
        raw_data: Dictionary containing raw supertask data.
        
    Returns:
        Dictionary with extracted content_items, quiz_items, and metadata.
        
    Raises:
        Stage1ProcessingError: If required fields are missing or invalid.
    """
    try:
        # Check for required fields
        if "flexibleItems" not in raw_data:
            raise Stage1ProcessingError("Missing required field: flexibleItems")
        
        flexible_items = raw_data["flexibleItems"]
        
        if not isinstance(flexible_items, list):
            raise Stage1ProcessingError("flexibleItems must be a list")
        
        if len(flexible_items) == 0:
            raise Stage1ProcessingError("flexibleItems cannot be empty")
        
        content_items = []
        quiz_items = []
        
        # Process each flexible item
        for i, item in enumerate(flexible_items):
            if not isinstance(item, dict):
                continue
                
            item_type = item.get("type", "unknown")
            
            if item_type in ["content", "quote"]:
                content_item = {
                    "content": item.get("content", ""),
                    "type": item_type,
                    "order": i
                }
                
                # Add author if present
                if "author" in item:
                    content_item["author"] = item["author"]
                
                # Add tips if present
                if "tips" in item:
                    content_item["tips"] = item["tips"]
                
                content_items.append(content_item)
                
            elif item_type == "quiz":
                quiz_item = {
                    "question": item.get("question", ""),
                    "options": item.get("options", []),
                    "correctAnswer": item.get("correctAnswer", 0),
                    "explanation": item.get("explanation", ""),
                    "order": i
                }
                
                quiz_items.append(quiz_item)
        
        # Extract metadata
        metadata = {
            "title": raw_data.get("title", ""),
            "dimension": raw_data.get("dimension", ""),
            "archetype": raw_data.get("archetype", ""),
            "relatedToType": raw_data.get("relatedToType", ""),
            "relatedToId": raw_data.get("relatedToId", ""),
            "estimatedDuration": raw_data.get("estimatedDuration", 300),
            "coinsReward": raw_data.get("coinsReward", 10),
            "original_metadata": raw_data.get("metadata", {})
        }
        
        return {
            "content_items": content_items,
            "quiz_items": quiz_items,
            "metadata": metadata
        }
        
    except Stage1ProcessingError:
        raise
    except Exception as e:
        raise Stage1ProcessingError(f"Error extracting content: {e}")


def analyze_content_structure(extracted_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the structure and characteristics of extracted content.
    
    Args:
        extracted_content: Dictionary with content_items, quiz_items, and metadata.
        
    Returns:
        Dictionary with analysis results including tone, complexity, themes, and language.
        
    Raises:
        Stage1ProcessingError: If content is insufficient for analysis.
    """
    try:
        content_items = extracted_content.get("content_items", [])
        quiz_items = extracted_content.get("quiz_items", [])
        metadata = extracted_content.get("metadata", {})
        
        if len(content_items) == 0 and len(quiz_items) == 0:
            raise Stage1ProcessingError("Insufficient content for analysis")
        
        # Analyze tone based on content and quotes
        tone = "neutral"
        has_quotes = any(item.get("type") == "quote" for item in content_items)
        has_authors = any("author" in item for item in content_items)
        
        # Check for motivational language
        all_content = " ".join(item.get("content", "") for item in content_items)
        motivational_words = ["sucesso", "produtiv", "saudável", "vitória", "desafio", "fundamental", 
                             "productive", "healthy", "victory", "challenge", "fundamental"]
        
        if any(word in all_content.lower() for word in motivational_words):
            tone = "motivational"
        
        # Quotes with authors are inspirational (takes precedence over motivational)
        if has_quotes or has_authors:
            tone = "inspirational"
        
        # Analyze complexity based on content length and quiz difficulty
        total_content_length = sum(len(item.get("content", "")) for item in content_items)
        avg_quiz_options = sum(len(item.get("options", [])) for item in quiz_items) / max(len(quiz_items), 1)
        
        if total_content_length < 500 and avg_quiz_options <= 2:
            complexity = "beginner"
        elif total_content_length > 1500 or avg_quiz_options > 4:
            complexity = "advanced"
        else:
            complexity = "intermediate"
        
        # Extract themes from content
        themes = []
        theme_keywords = {
            "morning": ["manhã", "acordar", "cedo", "matinal", "morning", "wake", "early"],
            "routine": ["rotina", "hábito", "consistente", "routine", "habit", "consistent"],
            "health": ["saudável", "sono", "corpo", "mente", "health", "sleep", "body", "mind"],
            "productivity": ["produtiv", "trabalho", "eficiência", "productive", "work", "efficiency"],
            "motivation": ["sucesso", "vitória", "desafio", "perseverança", "success", "victory", "challenge", "perseverance", "motivational"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in all_content.lower() for keyword in keywords):
                themes.append(theme)
        
        # Detect language
        language = "english"  # default
        portuguese_indicators = ["é", "da", "do", "que", "para", "com", "uma", "seu", "sua"]
        
        if any(indicator in all_content.lower() for indicator in portuguese_indicators):
            language = "portuguese"
        
        return {
            "tone": tone,
            "complexity": complexity,
            "themes": themes,
            "language": language,
            "content_length": total_content_length,
            "quiz_count": len(quiz_items),
            "has_quotes": has_quotes,
            "has_authors": has_authors
        }
        
    except Stage1ProcessingError:
        raise
    except Exception as e:
        raise Stage1ProcessingError(f"Error analyzing content structure: {e}")


def normalize_structure(extracted_content: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize the extracted content into the preprocessed JSON format.
    
    Args:
        extracted_content: Dictionary with content_items, quiz_items, and metadata.
        analysis: Dictionary with content analysis results.
        
    Returns:
        Dictionary in preprocessed JSON format ready for Stage 2.
        
    Raises:
        Stage1ProcessingError: If normalization fails.
    """
    try:
        content_items = extracted_content.get("content_items", [])
        quiz_items = extracted_content.get("quiz_items", [])
        metadata = extracted_content.get("metadata", {})
        
        # Generate description from first content item
        description = ""
        if content_items:
            first_content = content_items[0].get("content", "")
            # Take first sentence or first 150 characters
            sentences = re.split(r'[.!?]', first_content)
            if sentences:
                description = sentences[0].strip()
                if len(description) > 150:
                    description = description[:147] + "..."
        
        if not description:
            description = f"Knowledge task about {metadata.get('title', 'the topic')}"
        
        # Generate learning objectives based on content themes
        learning_objectives = []
        themes = analysis.get("themes", [])
        
        if "morning" in themes:
            learning_objectives.append("Understand the benefits of waking up early")
        if "routine" in themes:
            learning_objectives.append("Learn how to establish a consistent morning routine")
        if "health" in themes:
            learning_objectives.append("Recognize the health benefits of proper sleep habits")
        if "productivity" in themes:
            learning_objectives.append("Apply morning habits to improve daily productivity")
        if "motivation" in themes:
            learning_objectives.append("Develop motivation to maintain healthy habits")
        
        # Default learning objectives if none generated
        if not learning_objectives:
            learning_objectives = [
                "Understand the key concepts presented",
                "Apply the knowledge to practical situations",
                "Recognize the importance of the topic"
            ]
        
        # Normalize content items
        normalized_content = []
        for item in content_items:
            normalized_item = {
                "content": item.get("content", ""),
                "type": item.get("type", "content"),
                "order": item.get("order", 0)
            }
            
            # Add author information for quotes
            if "author" in item:
                normalized_item["author"] = item["author"]
                # Format quote content
                if item.get("type") == "quote":
                    normalized_item["content"] = f'Quote: "{item.get("content", "")}"'
            
            # Add tips if present
            if "tips" in item:
                normalized_item["tips"] = item["tips"]
            
            normalized_content.append(normalized_item)
        
        # Normalize quiz items
        normalized_quiz = []
        for item in quiz_items:
            normalized_quiz.append({
                "question": item.get("question", ""),
                "options": item.get("options", []),
                "correctAnswer": item.get("correctAnswer", 0),
                "explanation": item.get("explanation", ""),
                "order": item.get("order", 0)
            })
        
        # Create normalized structure
        normalized = {
            "title": metadata.get("title", ""),
            "description": description,
            "target_audience": metadata.get("archetype", "general"),
            "difficulty_level": analysis.get("complexity", "intermediate"),
            "learning_objectives": learning_objectives,
            "content": normalized_content,
            "quiz": normalized_quiz,
            "metadata": {
                "dimension": metadata.get("dimension", ""),
                "archetype": metadata.get("archetype", ""),
                "relatedToType": metadata.get("relatedToType", ""),
                "relatedToId": metadata.get("relatedToId", ""),
                "estimatedDuration": metadata.get("estimatedDuration", 300),
                "coinsReward": metadata.get("coinsReward", 10),
                "tone": analysis.get("tone", "neutral"),
                "themes": analysis.get("themes", []),
                "language": analysis.get("language", "english"),
                "content_length": analysis.get("content_length", 0),
                "quiz_count": analysis.get("quiz_count", 0),
                "processed_at": datetime.now().isoformat()
            }
        }
        
        # Add language field if detected
        if analysis.get("language") != "english":
            normalized["language"] = analysis.get("language")
        
        return normalized
        
    except Exception as e:
        raise Stage1ProcessingError(f"Error normalizing structure: {e}")


def process_raw_file(file_path: str) -> Dict[str, Any]:
    """
    Process a raw supertask file through the complete Stage 1 pipeline.
    
    This function performs the complete Stage 1 processing:
    1. Load raw JSON file
    2. Extract content and metadata
    3. Analyze content structure
    4. Normalize into preprocessed format
    
    Args:
        file_path: Path to the raw JSON file to process.
        
    Returns:
        Dictionary in preprocessed JSON format.
        
    Raises:
        Stage1ProcessingError: If any step in the pipeline fails.
    """
    try:
        # Step 1: Load raw JSON
        raw_data = load_raw_json(file_path)
        
        # Step 2: Extract content and metadata
        extracted_content = extract_content(raw_data)
        
        # Step 3: Analyze content structure
        analysis = analyze_content_structure(extracted_content)
        
        # Step 4: Normalize structure
        normalized = normalize_structure(extracted_content, analysis)
        
        return normalized
        
    except Stage1ProcessingError:
        # Re-raise Stage 1 errors as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise Stage1ProcessingError(f"Unexpected error processing {file_path}: {e}")


def process_directory(input_dir: str, output_dir: str) -> Dict[str, Any]:
    """
    Process all JSON files in a directory through Stage 1 pipeline.
    
    Args:
        input_dir: Directory containing raw JSON files.
        output_dir: Directory to save preprocessed JSON files.
        
    Returns:
        Dictionary with processing results and statistics.
        
    Raises:
        Stage1ProcessingError: If directory processing fails.
    """
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise Stage1ProcessingError(f"Input directory not found: {input_dir}")
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all JSON files
        json_files = list(input_path.glob("**/*.json"))
        
        if not json_files:
            raise Stage1ProcessingError(f"No JSON files found in {input_dir}")
        
        results = {
            "processed": [],
            "failed": [],
            "total_files": len(json_files),
            "successful": 0,
            "failed_count": 0
        }
        
        for json_file in json_files:
            try:
                # Process the file
                normalized = process_raw_file(str(json_file))
                
                # Generate output filename
                relative_path = json_file.relative_to(input_path)
                output_file = output_path / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Save preprocessed JSON
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(normalized, f, indent=2, ensure_ascii=False)
                
                results["processed"].append({
                    "input_file": str(json_file),
                    "output_file": str(output_file),
                    "title": normalized.get("title", ""),
                    "language": normalized.get("language", "english")
                })
                
                results["successful"] += 1
                
            except Exception as e:
                results["failed"].append({
                    "input_file": str(json_file),
                    "error": str(e)
                })
                results["failed_count"] += 1
        
        return results
        
    except Stage1ProcessingError:
        raise
    except Exception as e:
        raise Stage1ProcessingError(f"Error processing directory {input_dir}: {e}")


def validate_preprocessed_output(data: Dict[str, Any]) -> bool:
    """
    Validate that preprocessed output meets expected structure requirements.
    
    Args:
        data: Dictionary containing preprocessed data.
        
    Returns:
        True if valid, False otherwise.
    """
    try:
        # Check required top-level fields
        required_fields = ["title", "description", "target_audience", "difficulty_level", "learning_objectives"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Check field types
        if not isinstance(data["title"], str):
            return False
        if not isinstance(data["description"], str):
            return False
        if not isinstance(data["target_audience"], str):
            return False
        if not isinstance(data["difficulty_level"], str):
            return False
        if not isinstance(data["learning_objectives"], list):
            return False
        
        # Check content and quiz structure
        if "content" in data and not isinstance(data["content"], list):
            return False
        if "quiz" in data and not isinstance(data["quiz"], list):
            return False
        
        # Validate content items
        for item in data.get("content", []):
            if not isinstance(item, dict):
                return False
            if "content" not in item:
                return False
        
        # Validate quiz items
        for item in data.get("quiz", []):
            if not isinstance(item, dict):
                return False
            required_quiz_fields = ["question", "options", "correctAnswer"]
            for field in required_quiz_fields:
                if field not in item:
                    return False
        
        return True
        
    except Exception:
        return False 


def analyze_ari_persona_patterns(content_items: List[Dict[str, Any]], quiz_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze content patterns to prepare for Ari persona integration.
    
    This function identifies coaching opportunities, behavioral change patterns,
    and framework integration points to support Ari's TARS-inspired coaching style.
    
    Args:
        content_items: List of content items from extracted content.
        quiz_items: List of quiz items from extracted content.
        
    Returns:
        Dictionary with Ari persona analysis including coaching opportunities,
        framework integration points, and engagement patterns.
    """
    try:
        # Combine all content text for analysis
        all_content = " ".join(item.get("content", "") for item in content_items)
        all_questions = " ".join(item.get("question", "") for item in quiz_items)
        combined_text = f"{all_content} {all_questions}".lower()
        
        # Analyze coaching opportunities
        coaching_opportunities = {
            "habit_formation": [],
            "behavioral_change": [],
            "motivation_points": [],
            "action_triggers": [],
            "micro_habits": []
        }
        
        # Detect habit formation patterns
        habit_keywords = ["hábito", "rotina", "consistente", "diário", "regular", "prática", "habit", "routine", "consistent", "daily"]
        if any(keyword in combined_text for keyword in habit_keywords):
            coaching_opportunities["habit_formation"].append("Content contains habit formation patterns suitable for Tiny Habits framework")
        
        # Detect behavioral change patterns
        behavior_keywords = ["mudança", "transformar", "melhorar", "desenvolver", "criar", "change", "transform", "improve", "develop", "create"]
        if any(keyword in combined_text for keyword in behavior_keywords):
            coaching_opportunities["behavioral_change"].append("Content shows behavioral change opportunities for Behavioral Design framework")
        
        # Detect motivation points
        motivation_keywords = ["sucesso", "vitória", "desafio", "perseverança", "motivação", "inspiração", "success", "victory", "challenge", "perseverance"]
        if any(keyword in combined_text for keyword in motivation_keywords):
            coaching_opportunities["motivation_points"].append("Content contains motivational elements for engagement progression")
        
        # Detect action triggers
        action_keywords = ["prepare", "defina", "deixe", "coloque", "faça", "comece", "inicie", "prepare", "set", "place", "do", "start", "begin"]
        if any(keyword in combined_text for keyword in action_keywords):
            coaching_opportunities["action_triggers"].append("Content includes actionable steps suitable for micro-habit creation")
        
        # Detect micro-habit opportunities
        micro_keywords = ["pequeno", "simples", "fácil", "rápido", "primeiro passo", "small", "simple", "easy", "quick", "first step"]
        if any(keyword in combined_text for keyword in micro_keywords):
            coaching_opportunities["micro_habits"].append("Content suitable for micro-habit methodology")
        
        # Analyze framework integration opportunities
        framework_integration = {
            "tiny_habits": _analyze_tiny_habits_potential(combined_text),
            "behavioral_design": _analyze_behavioral_design_potential(combined_text),
            "dopamine_nation": _analyze_dopamine_potential(combined_text),
            "huberman_protocols": _analyze_huberman_potential(combined_text),
            "perma_model": _analyze_perma_potential(combined_text)
        }
        
        # Analyze engagement patterns for TARS-inspired brevity
        engagement_patterns = {
            "question_opportunities": _identify_question_opportunities(content_items),
            "brevity_potential": _analyze_brevity_potential(combined_text),
            "progressive_engagement": _analyze_progressive_engagement(content_items, quiz_items),
            "coaching_moments": _identify_coaching_moments(content_items)
        }
        
        # Analyze Portuguese language patterns for masculine consistency
        language_patterns = {
            "portuguese_detected": _detect_portuguese_patterns(combined_text),
            "masculine_forms_needed": _identify_masculine_form_opportunities(combined_text),
            "cultural_context": _analyze_cultural_context(combined_text)
        }
        
        return {
            "coaching_opportunities": coaching_opportunities,
            "framework_integration": framework_integration,
            "engagement_patterns": engagement_patterns,
            "language_patterns": language_patterns,
            "ari_readiness_score": _calculate_ari_readiness_score(coaching_opportunities, framework_integration, engagement_patterns),
            "enhancement_recommendations": _generate_enhancement_recommendations(coaching_opportunities, framework_integration)
        }
        
    except Exception as e:
        # Return basic analysis if detailed analysis fails
        return {
            "coaching_opportunities": {"habit_formation": [], "behavioral_change": [], "motivation_points": [], "action_triggers": [], "micro_habits": []},
            "framework_integration": {"tiny_habits": False, "behavioral_design": False, "dopamine_nation": False, "huberman_protocols": False, "perma_model": False},
            "engagement_patterns": {"question_opportunities": [], "brevity_potential": "medium", "progressive_engagement": "standard", "coaching_moments": []},
            "language_patterns": {"portuguese_detected": True, "masculine_forms_needed": True, "cultural_context": "brazilian"},
            "ari_readiness_score": 0.5,
            "enhancement_recommendations": ["Basic content structure suitable for Ari persona enhancement"],
            "analysis_error": str(e)
        }


def _analyze_tiny_habits_potential(text: str) -> bool:
    """Analyze if content is suitable for Tiny Habits framework integration."""
    tiny_habits_indicators = ["pequeno", "simples", "fácil", "passo", "começo", "início", "small", "simple", "easy", "step", "start"]
    return any(indicator in text for indicator in tiny_habits_indicators)


def _analyze_behavioral_design_potential(text: str) -> bool:
    """Analyze if content is suitable for Behavioral Design framework integration."""
    behavioral_indicators = ["comportamento", "mudança", "hábito", "rotina", "padrão", "behavior", "change", "habit", "routine", "pattern"]
    return any(indicator in text for indicator in behavioral_indicators)


def _analyze_dopamine_potential(text: str) -> bool:
    """Analyze if content is suitable for Dopamine Nation framework integration."""
    dopamine_indicators = ["recompensa", "prazer", "satisfação", "vício", "equilíbrio", "reward", "pleasure", "satisfaction", "addiction", "balance"]
    return any(indicator in text for indicator in dopamine_indicators)


def _analyze_huberman_potential(text: str) -> bool:
    """Analyze if content is suitable for Huberman Protocols framework integration."""
    huberman_indicators = ["sono", "luz", "manhã", "circadiano", "neuroplasticidade", "sleep", "light", "morning", "circadian", "neuroplasticity"]
    return any(indicator in text for indicator in huberman_indicators)


def _analyze_perma_potential(text: str) -> bool:
    """Analyze if content is suitable for PERMA model framework integration."""
    perma_indicators = ["bem-estar", "felicidade", "relacionamento", "significado", "realização", "wellbeing", "happiness", "relationship", "meaning", "achievement"]
    return any(indicator in text for indicator in perma_indicators)


def _identify_question_opportunities(content_items: List[Dict[str, Any]]) -> List[str]:
    """Identify opportunities to transform content into Ari's question-heavy coaching style."""
    opportunities = []
    
    for item in content_items:
        content = item.get("content", "")
        
        # Look for declarative statements that could become questions
        if "é importante" in content.lower() or "is important" in content.lower():
            opportunities.append("Transform importance statements into 'Why is this important to you?' questions")
        
        if "você deve" in content.lower() or "you should" in content.lower():
            opportunities.append("Transform 'should' statements into 'What would happen if you..?' questions")
        
        if "benefício" in content.lower() or "benefit" in content.lower():
            opportunities.append("Transform benefit statements into 'What benefits would you notice first?' questions")
        
        # Look for action items that could become commitment questions
        if any(word in content.lower() for word in ["prepare", "defina", "faça", "comece", "set", "do", "start"]):
            opportunities.append("Transform action items into 'When will you start?' commitment questions")
    
    return opportunities


def _analyze_brevity_potential(text: str) -> str:
    """Analyze how content can be made more concise for TARS-inspired brevity."""
    word_count = len(text.split())
    
    if word_count > 1000:
        return "high"  # High potential for brevity improvement
    elif word_count > 500:
        return "medium"  # Medium potential for brevity improvement
    else:
        return "low"  # Already concise


def _analyze_progressive_engagement(content_items: List[Dict[str, Any]], quiz_items: List[Dict[str, Any]]) -> str:
    """Analyze how content can be structured for Ari's progressive engagement approach."""
    total_items = len(content_items) + len(quiz_items)
    
    if total_items <= 3:
        return "brief"  # Suitable for brief engagement
    elif total_items <= 6:
        return "standard"  # Standard engagement progression
    else:
        return "extended"  # Extended engagement with multiple touchpoints


def _identify_coaching_moments(content_items: List[Dict[str, Any]]) -> List[str]:
    """Identify specific moments where Ari's coaching voice would be most effective."""
    coaching_moments = []
    
    for i, item in enumerate(content_items):
        content = item.get("content", "").lower()
        
        # Beginning moments - good for opening questions
        if i == 0:
            coaching_moments.append("Opening: Perfect for 'What needs fixing first?' approach")
        
        # Moments with tips - good for micro-habit coaching
        if "tips" in item:
            coaching_moments.append(f"Tips section: Ideal for micro-habit creation and 'What's the smallest change?' questions")
        
        # Motivational content - good for validation and support
        if any(word in content for word in ["sucesso", "vitória", "perseverança", "success", "victory", "perseverance"]):
            coaching_moments.append("Motivational content: Opportunity for validation and framework integration")
        
        # Action-oriented content - good for commitment questions
        if any(word in content for word in ["prepare", "faça", "comece", "prepare", "do", "start"]):
            coaching_moments.append("Action content: Perfect for 'When will you start?' commitment questions")
    
    return coaching_moments


def _detect_portuguese_patterns(text: str) -> bool:
    """Detect if content is in Portuguese and needs masculine form consistency."""
    portuguese_indicators = ["é", "da", "do", "que", "para", "com", "uma", "seu", "sua", "você", "ter", "ser", "estar"]
    return any(indicator in text for indicator in portuguese_indicators)


def _identify_masculine_form_opportunities(text: str) -> bool:
    """Identify if content needs masculine form adjustments for Ari's identity."""
    # Look for contexts where Ari would speak in first person
    first_person_contexts = ["eu sou", "meu", "como seu", "seu coach", "seu treinador"]
    return any(context in text.lower() for context in first_person_contexts)


def _analyze_cultural_context(text: str) -> str:
    """Analyze cultural context for appropriate Ari persona adaptation."""
    brazilian_indicators = ["brasil", "brasileiro", "pelé", "futebol", "capoeira"]
    if any(indicator in text.lower() for indicator in brazilian_indicators):
        return "brazilian"
    
    portuguese_indicators = ["portugal", "português", "lisboa", "porto"]
    if any(indicator in text.lower() for indicator in portuguese_indicators):
        return "portuguese"
    
    return "general_portuguese"


def _calculate_ari_readiness_score(coaching_opportunities: Dict[str, Any], framework_integration: Dict[str, Any], engagement_patterns: Dict[str, Any]) -> float:
    """Calculate a score indicating how ready the content is for Ari persona integration."""
    score = 0.0
    
    # Score based on coaching opportunities
    for opportunity_type, opportunities in coaching_opportunities.items():
        if opportunities:
            score += 0.15  # Each opportunity type adds 15%
    
    # Score based on framework integration potential
    for framework, potential in framework_integration.items():
        if potential:
            score += 0.1  # Each framework adds 10%
    
    # Score based on engagement patterns
    if engagement_patterns.get("question_opportunities"):
        score += 0.2  # Question opportunities add 20%
    
    if engagement_patterns.get("coaching_moments"):
        score += 0.2  # Coaching moments add 20%
    
    return min(score, 1.0)  # Cap at 100%


def _generate_enhancement_recommendations(coaching_opportunities: Dict[str, Any], framework_integration: Dict[str, Any]) -> List[str]:
    """Generate specific recommendations for enhancing content with Ari persona."""
    recommendations = []
    
    # Recommendations based on coaching opportunities
    if coaching_opportunities.get("habit_formation"):
        recommendations.append("Integrate Tiny Habits methodology for habit formation content")
    
    if coaching_opportunities.get("behavioral_change"):
        recommendations.append("Apply Behavioral Design principles for behavior change sections")
    
    if coaching_opportunities.get("motivation_points"):
        recommendations.append("Enhance motivational content with Ari's progressive engagement approach")
    
    if coaching_opportunities.get("action_triggers"):
        recommendations.append("Transform action items into Ari's commitment-based coaching questions")
    
    if coaching_opportunities.get("micro_habits"):
        recommendations.append("Apply micro-habit methodology with 'What's the smallest change?' approach")
    
    # Recommendations based on framework integration
    if framework_integration.get("tiny_habits"):
        recommendations.append("Content ready for BJ Fogg's Tiny Habits framework integration")
    
    if framework_integration.get("huberman_protocols"):
        recommendations.append("Content suitable for Huberman Protocol integration (sleep, circadian, neuroplasticity)")
    
    if framework_integration.get("perma_model"):
        recommendations.append("Content can be enhanced with PERMA model wellbeing principles")
    
    # Default recommendations
    if not recommendations:
        recommendations.append("Content structure suitable for basic Ari persona enhancement")
        recommendations.append("Apply TARS-inspired brevity and question-heavy coaching style")
    
    return recommendations


def process_directory_with_ari_analysis(input_dir: str, output_dir: str) -> Dict[str, Any]:
    """
    Process all JSON files in a directory through Stage 1 pipeline with Ari persona analysis.
    
    This enhanced version includes Ari persona pattern analysis for each processed file,
    providing insights for coaching style adaptation and framework integration.
    
    Args:
        input_dir: Directory containing raw JSON files.
        output_dir: Directory to save preprocessed JSON files.
        
    Returns:
        Dictionary with processing results, statistics, and Ari persona analysis.
        
    Raises:
        Stage1ProcessingError: If directory processing fails.
    """
    try:
        # Use the existing process_directory function for basic processing
        basic_results = process_directory(input_dir, output_dir)
        
        # Enhance results with Ari persona analysis
        enhanced_results = basic_results.copy()
        enhanced_results["ari_persona_analysis"] = []
        
        # Analyze each processed file for Ari persona patterns
        for processed_file in basic_results.get("processed", []):
            try:
                # Load the processed file for analysis
                with open(processed_file["output_file"], 'r', encoding='utf-8') as f:
                    processed_data = json.load(f)
                
                # Perform Ari persona analysis
                content_items = processed_data.get("content", [])
                quiz_items = processed_data.get("quiz", [])
                
                ari_analysis = analyze_ari_persona_patterns(content_items, quiz_items)
                
                # Add analysis to results
                enhanced_results["ari_persona_analysis"].append({
                    "file": processed_file["input_file"],
                    "title": processed_file["title"],
                    "language": processed_file["language"],
                    "ari_analysis": ari_analysis
                })
                
            except Exception as e:
                # Add error info but don't fail the entire process
                enhanced_results["ari_persona_analysis"].append({
                    "file": processed_file["input_file"],
                    "title": processed_file["title"],
                    "language": processed_file["language"],
                    "ari_analysis": {"error": str(e)}
                })
        
        # Add summary statistics
        ari_scores = [item["ari_analysis"].get("ari_readiness_score", 0) for item in enhanced_results["ari_persona_analysis"] if "ari_readiness_score" in item["ari_analysis"]]
        
        enhanced_results["ari_summary"] = {
            "total_files_analyzed": len(enhanced_results["ari_persona_analysis"]),
            "average_ari_readiness": sum(ari_scores) / len(ari_scores) if ari_scores else 0,
            "high_readiness_files": len([score for score in ari_scores if score >= 0.7]),
            "medium_readiness_files": len([score for score in ari_scores if 0.4 <= score < 0.7]),
            "low_readiness_files": len([score for score in ari_scores if score < 0.4])
        }
        
        return enhanced_results
        
    except Exception as e:
        raise Stage1ProcessingError(f"Error processing directory with Ari analysis {input_dir}: {e}") 