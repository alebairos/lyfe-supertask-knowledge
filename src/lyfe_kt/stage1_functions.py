"""
Stage 1 functions for raw content analysis.

This module implements the first stage of the knowledge task generation pipeline:
Raw Content Analysis (work/01_raw/ → work/02_preprocessed/)

The functions in this module:
1. Load and parse raw JSON files
2. Extract content and metadata from flexible item structures
3. Analyze content structure, tone, and themes
4. Normalize the structure into preprocessed JSON format
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