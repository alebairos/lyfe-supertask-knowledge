"""
Stage 3 Generation Pipeline for Lyfe Supertask Knowledge Generator

This module implements the Stage 3 generation pipeline:
Filled Markdown Templates → Supertask JSON Files

The pipeline:
1. Processes filled markdown templates from Stage 1 preprocessing
2. Parses frontmatter and content sections
3. Applies generation prompts with Ari persona consistency
4. Generates supertask JSON with exact test.json structure compliance
5. Supports both beginner and advanced difficulty scaling
6. Provides comprehensive validation and error handling

Stage 3 Pipeline:
work/02_preprocessed/ → work/03_output/

Components:
1. TemplateProcessor: Markdown parsing and validation
2. JSONGenerator: AI-powered JSON generation
3. GenerationPipeline: Main orchestration with reporting
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import traceback
import yaml
from markdown import markdown
from bs4 import BeautifulSoup

from .config_loader import (
    get_config,
    load_config,
    load_generation_prompts,
    get_generation_prompts,
    build_generation_prompt,
    get_difficulty_configuration,
    get_generation_preset,
    validate_generated_json_structure
)
from .openai_client import get_openai_client
from .content_enrichment import ContentEnrichmentEngine

# Set up logging
logger = logging.getLogger(__name__)

# Allowed expert authors for quote items (per feature 01)
ALLOWED_QUOTE_AUTHORS: List[str] = [
    "BJ Fogg",
    "Jason Hreha",
    "Anna Lembke",
    "Lieberman & Long",
    "Martin Seligman",
    "Abraham Maslow",
    "Andrew Huberman",
    "Michael Easter",
    "Andrew Newberg",
]

class SequenceParser:
    """Parser for custom narrative sequence strings."""
    
    DEFAULT_SEQUENCE = ['content', 'quiz', 'content', 'quote', 'content', 'quiz']
    VALID_TYPES = {'content', 'quiz', 'quote'}
    MIN_ITEMS = 3
    MAX_ITEMS = 8
    
    @classmethod
    def parse_sequence(cls, sequence_str: str) -> List[str]:
        """
        Parse sequence string into list of item types.
        
        Args:
            sequence_str: String like "content → quiz → quote"
            
        Returns:
            List of item types
            
        Raises:
            ValueError: If sequence string is invalid
        """
        if not sequence_str or not sequence_str.strip():
            return cls.DEFAULT_SEQUENCE
        
        # Split by arrow separator
        items = [item.strip() for item in sequence_str.split('→')]
        
        # Remove empty items
        items = [item for item in items if item]
        
        if not items:
            raise ValueError("Empty sequence provided")
        
        # Validate each item type
        for item in items:
            if item not in cls.VALID_TYPES:
                raise ValueError(f"Invalid item type '{item}'. Valid types: {', '.join(sorted(cls.VALID_TYPES))}")
        
        return items
    
    @classmethod
    def validate_sequence(cls, sequence: List[str]) -> bool:
        """
        Validate sequence meets requirements.
        
        Args:
            sequence: List of item types
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If sequence is invalid
        """
        if not sequence:
            raise ValueError("Sequence cannot be empty")
        
        # Check length
        if len(sequence) < cls.MIN_ITEMS:
            raise ValueError(f"Sequence must have at least {cls.MIN_ITEMS} items, got {len(sequence)}")
        
        if len(sequence) > cls.MAX_ITEMS:
            raise ValueError(f"Sequence must have at most {cls.MAX_ITEMS} items, got {len(sequence)}")
        
        # Check all types are valid
        invalid_types = set(sequence) - cls.VALID_TYPES
        if invalid_types:
            raise ValueError(f"Invalid item types: {', '.join(sorted(invalid_types))}")
        
        # Check balanced learning (must have at least 1 of each type)
        sequence_set = set(sequence)
        if not all(item_type in sequence_set for item_type in cls.VALID_TYPES):
            missing = cls.VALID_TYPES - sequence_set
            raise ValueError(f"Sequence must include at least one of each type. Missing: {', '.join(sorted(missing))}")
        
        return True
    
    @classmethod
    def get_default_sequence(cls) -> List[str]:
        """Return default sequence pattern."""
        return cls.DEFAULT_SEQUENCE.copy()



class GenerationError(Exception):
    """Custom exception for Stage 3 generation pipeline errors."""
    pass


class StructuralJSONGenerator:
    """
    Hybrid generator with guaranteed structure compliance.
    
    This generator combines template-based structure with AI content generation:
    1. Template guarantees correct JSON structure
    2. AI fills only content within predefined structure  
    3. Schema validates final output
    4. Zero format violations possible
    """
    
    def __init__(self, format_version="v1.1"):
        """Initialize structural JSON generator."""
        try:
            self.format_version = format_version
            self.openai_client = get_openai_client()
            self.generation_prompts = load_generation_prompts()
            self.enrichment_engine = ContentEnrichmentEngine(self.openai_client)
            logger.info(f"Structural JSON generator initialized for format {format_version}")
        except Exception as e:
            raise GenerationError(f"Failed to initialize structural generator: {e}")
    
    def generate_supertask(self, template_data: Dict[str, Any], difficulty: str = "beginner", custom_sequence: str = None) -> Dict[str, Any]:
        """Generate supertask with guaranteed structure + AI content."""
        try:
            logger.info(f"Generating supertask with guaranteed structure, difficulty: {difficulty}")
            
            # Step 1: Create guaranteed base structure (template-based)
            base_structure = self._create_base_structure(template_data, difficulty)
            
            # Step 2: AI generates flexibleItems content within structure
            base_structure["flexibleItems"] = self._generate_flexible_items(template_data, difficulty, custom_sequence)
            
            # Step 3: Add metadata with proper format
            base_structure["metadata"] = self._generate_metadata(template_data, difficulty)
            
            # Step 4: Validate against schema (should never fail with guaranteed structure)
            if not self._validate_structure(base_structure):
                raise GenerationError("Generated structure failed validation (unexpected)")
            
            logger.info(f"Successfully generated supertask with guaranteed structure")
            return base_structure
            
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to generate supertask with guaranteed structure: {e}")
    
    def generate_multiple_supertasks(self, template_data: Dict[str, Any], custom_sequence: str = None) -> List[Dict[str, Any]]:
        """
        Generate both beginner and advanced versions with guaranteed structure.
        
        Args:
            template_data: Parsed template data.
            custom_sequence: Optional custom narrative sequence.
            
        Returns:
            List of generated supertasks (beginner and advanced).
        """
        try:
            logger.info("Generating multiple supertasks with guaranteed structure (beginner and advanced)")
            
            supertasks = []
            
            # Generate beginner version
            beginner_task = self.generate_supertask(template_data, "beginner", custom_sequence)
            supertasks.append(beginner_task)
            
            # Generate advanced version
            advanced_task = self.generate_supertask(template_data, "advanced", custom_sequence)
            supertasks.append(advanced_task)
            
            logger.info(f"Successfully generated {len(supertasks)} supertasks with guaranteed structure")
            return supertasks
            
        except Exception as e:
            raise GenerationError(f"Failed to generate multiple supertasks: {e}")
    
    def _create_base_structure(self, template_data: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """Create guaranteed compliant base structure."""
        frontmatter = template_data.get('frontmatter', {})
        
        # Map template field names to expected JSON field names
        related_to_type = frontmatter.get('related_to_type', frontmatter.get('relatedToType', 'HABITBP'))
        related_to_id = frontmatter.get('related_to_id', frontmatter.get('relatedToId', 'generic'))
        estimated_duration = frontmatter.get('estimated_duration', frontmatter.get('estimatedDuration', 300))
        coins_reward = frontmatter.get('coins_reward', frontmatter.get('coinsReward', 15))
        
        return {
            "title": f"{frontmatter.get('title', 'Knowledge Task')} - {difficulty.capitalize()}",
            "dimension": frontmatter.get('dimension', 'physicalHealth'),
            "archetype": self._normalize_archetype(frontmatter.get('archetype', 'warrior')),
            "relatedToType": related_to_type,
            "relatedToId": related_to_id,
            "estimatedDuration": int(str(estimated_duration).replace(' seconds', '').replace(' minutes', '')),
            "coinsReward": int(str(coins_reward)),
            "flexibleItems": [],  # Will be filled by AI
            "metadata": {}        # Will be filled by metadata generator
        }
    
    def _generate_flexible_items(self, template_data: Dict[str, Any], difficulty: str, custom_sequence: str = None) -> List[Dict[str, Any]]:
        """Generate mobile-optimized flexible items (3-8 items) with narrative flow and content coverage."""
        try:
            # Generate all item types first
            content_items = self._extract_and_split_content(template_data, difficulty)
            quiz_items = self._generate_quiz_items(template_data, difficulty)
            quote_items = self._generate_quote_items(template_data, difficulty)
            
            # Parse custom sequence or use default
            if custom_sequence:
                try:
                    sequence = SequenceParser.parse_sequence(custom_sequence)
                    SequenceParser.validate_sequence(sequence)
                    logger.info(f"Using custom sequence: {' → '.join(sequence)}")
                except ValueError as e:
                    logger.warning(f"Invalid custom sequence '{custom_sequence}': {e}. Using default sequence.")
                    sequence = SequenceParser.get_default_sequence()
            else:
                sequence = SequenceParser.get_default_sequence()
            
            # Apply narrative sequencing
            flexible_items = self._create_narrative_sequence(content_items, quiz_items, quote_items, sequence)
            
            logger.info(f"Generated {len(flexible_items)} mobile-optimized flexible items with narrative flow")
            return flexible_items
            
        except Exception as e:
            logger.error(f"Failed to generate flexible items: {e}")
            raise GenerationError(f"Failed to generate flexible items: {e}")
    
    def _create_narrative_sequence(self, content_items: List[Dict], quiz_items: List[Dict], quote_items: List[Dict], sequence: List[str] = None) -> List[Dict]:
        """Create narrative flow following custom or default sequence"""
        try:
            narrative_items = []
            
            # Use provided sequence or default
            if sequence is None:
                sequence = SequenceParser.get_default_sequence()
            
            # Ensure we have items to work with
            if not content_items:
                content_items = [self._create_default_content_item("beginner", 0)]
            if not quiz_items:
                quiz_items = [self._create_default_quiz_item("beginner")]
            if not quote_items:
                quote_items = [self._create_default_quote_item("beginner")]
            
            # Create iterators to cycle through items
            content_iter = iter(content_items)
            quiz_iter = iter(quiz_items)
            quote_iter = iter(quote_items)
            
            # Build narrative sequence using custom pattern (cap quotes at one)
            quote_used = False
            for i, item_type in enumerate(sequence):
                if len(narrative_items) >= 8:  # Max mobile limit
                    break
                    
                try:
                    if item_type == 'content':
                        narrative_items.append(next(content_iter))
                    elif item_type == 'quiz':
                        narrative_items.append(next(quiz_iter))
                    elif item_type == 'quote' and not quote_used:
                        narrative_items.append(next(quote_iter))
                        quote_used = True
                except StopIteration:
                    # If we run out of items of this type, skip
                    continue
            
            # Ensure minimum of 3 items
            while len(narrative_items) < 3:
                narrative_items.append(self._create_default_content_item("beginner", len(narrative_items)))
            
            logger.info(f"Created narrative sequence with {len(narrative_items)} items following story pattern")
            # Sanitize authorship defaults and allowed quote authors
            narrative_items = self._sanitize_authorship_and_quotes(narrative_items)
            return narrative_items
            
        except Exception as e:
            logger.error(f"Failed to create narrative sequence: {e}")
            # Fallback to original behavior
            return content_items + quiz_items + quote_items
    
    def _extract_and_split_content(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
        """Generate source-driven content using enrichment engine."""
        try:
            # Extract source material for insight generation
            source_material = self._extract_source_material(template_data)
            title = template_data.get('frontmatter', {}).get('title', 'o tópico')
            
            # Step 1: Extract insights from source material
            logger.info("Extracting insights from source material for content generation")
            insights = self.enrichment_engine.extract_source_insights(source_material, max_insights=4)
            
            # Step 2: Generate source-driven content
            logger.info(f"Generating source-driven content for difficulty: {difficulty}")
            content_items = []
            
            # Generate 2-3 content items based on insights
            for i, insight in enumerate(insights[:3]):
                try:
                    # Generate content directly from insight
                    content_text = self.enrichment_engine.generate_source_driven_content(
                        [insight], difficulty, title
                    )
                    
                    if content_text and len(content_text) >= 50:
                        content_item = {
                            "type": "content",
                            "content": content_text,
                            "author": "Ari"
                        }
                        
                        # Add insight-based tips if available (mobile limit: tips are arrays of strings)
                        if insight.application:
                            # Truncate tip to reasonable length for mobile
                            tip_text = f"💡 {insight.application}"
                            if len(tip_text) > 120:  # Reasonable mobile limit for tips
                                tip_text = tip_text[:115] + "..."
                            content_item["tips"] = [tip_text]
                        
                        content_items.append(content_item)
                        logger.info(f"Generated source-driven content item {i+1}: {len(content_text)} chars")
                        
                except Exception as e:
                    logger.warning(f"Failed to generate content item {i+1} from insight: {e}")
            
            # Step 3: Chain-of-thought validation and conditional enhancement
            if content_items:
                logger.info("Validating content relevance with chain-of-thought analysis")
                sample_content = content_items[0]['content']
                validation = self.enrichment_engine.validate_content_relevance(
                    sample_content, [], source_material
                )
                
                logger.info(f"Content validation: {validation.decision.value}, "
                          f"relevance: {validation.relevance_score:.2f}, "
                          f"enrichment: {validation.enrichment_score:.2f}")
                
                # Apply conditional enhancement only if needed
                if validation.decision.value != "approved":
                    logger.info("Applying conditional content enhancement")
                    enhanced_content, _ = self.enrichment_engine.enhance_content_conditionally(
                        sample_content, [], validation, insights
                    )
                    if enhanced_content != sample_content:
                        content_items[0]['content'] = enhanced_content
                        logger.info("Content enhanced based on validation feedback")
            
            # Ensure at least 1 content item
            if not content_items:
                logger.warning("No source-driven content generated, creating fallback")
                content_items.append(self._create_default_content_item(difficulty, 0))
            
            logger.info(f"Generated {len(content_items)} source-driven content items")
            return content_items[:4]  # Limit to 4 content items max
            
        except Exception as e:
            logger.error(f"Source-driven content generation failed: {e}")
            # Fallback to original method
            return self._extract_and_split_content_fallback(template_data, difficulty)
    
    def _extract_source_material(self, template_data: Dict[str, Any]) -> str:
        """Extract all available source material for insight generation."""
        source_parts = []
        
        # Get content from all sections
        sections = template_data.get('sections', {})
        for section_name in ['main_content', 'overview', 'key_concepts', 'examples', 'detailed_content']:
            section_content = sections.get(section_name)
            if section_content:
                # Handle both string and list content
                if isinstance(section_content, list):
                    source_parts.extend([str(item) for item in section_content])
                else:
                    source_parts.append(str(section_content))
        
        # Add frontmatter context
        frontmatter = template_data.get('frontmatter', {})
        if frontmatter.get('title'):
            source_parts.append(f"Título: {frontmatter['title']}")
        if frontmatter.get('description'):
            source_parts.append(f"Descrição: {frontmatter['description']}")
        
        # Add learning objectives if available
        if frontmatter.get('learning_objectives'):
            objectives = frontmatter['learning_objectives']
            if isinstance(objectives, list):
                objectives_text = "Objetivos: " + ", ".join([str(obj) for obj in objectives])
                source_parts.append(objectives_text)
        
        # Safely combine all source material
        try:
            source_material = "\n\n".join([str(part) for part in source_parts if part])
        except Exception as e:
            logger.warning(f"Error combining source material: {e}")
            # Fallback to basic extraction
            source_material = ""
            for part in source_parts:
                try:
                    source_material += str(part) + "\n\n"
                except Exception:
                    continue
        
        # If no meaningful source material, create basic context
        if len(source_material.strip()) < 100:
            title = frontmatter.get('title', 'desenvolvimento pessoal')
            source_material = f"Conteúdo educativo sobre {title} focado em crescimento pessoal e aplicação prática de conceitos para melhoria da qualidade de vida."
        
        return source_material
    
    def _extract_and_split_content_fallback(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
        """Fallback to original content extraction method."""
        sections = template_data.get('sections', {})
        content_items = []
        
        # Get all available content
        all_content = []
        if sections.get('main_content'):
            all_content.append(sections['main_content'])
        if sections.get('overview'):
            all_content.append(sections['overview'])
        if sections.get('key_concepts'):
            all_content.append(sections['key_concepts'])
        if sections.get('examples'):
            all_content.append(sections['examples'])
        
        # If no content found, create default
        if not all_content:
            title = template_data.get('frontmatter', {}).get('title', 'o tópico')
            all_content = [f"Conteúdo educativo sobre {title} para desenvolvimento pessoal."]
        
        # Split content into mobile-sized chunks
        for content_section in all_content:
            chunks = self._split_content_to_mobile_chunks(content_section)
            for chunk in chunks:
                # Parse structured content (author, tips, main content)
                parsed_content = self._parse_content_structure(chunk)
                mobile_content = self._ai_enhance_content(parsed_content['content'], difficulty)
                
                if mobile_content and len(mobile_content) >= 50:  # Ensure minimum length
                    content_item = {
                        "type": "content",
                        "content": mobile_content
                    }
                    
                    # Add author if found
                    if parsed_content['author']:
                        content_item["author"] = parsed_content['author']
                    else:
                        content_item["author"] = "Ari"
                    
                    # Add tips if found
                    if parsed_content['tips']:
                        content_item["tips"] = parsed_content['tips']
                    
                    content_items.append(content_item)
        
        # Ensure at least 1 content item
        if not content_items:
            content_items.append(self._create_default_content_item(difficulty, 0))
        
        return content_items[:4]  # Limit to 4 content items max
    
    def _extract_quiz_sections(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract quiz sections from template data."""
        sections = template_data.get('sections', {})
        quiz_content = sections.get('quiz_questions', '')
        
        # Parse quiz content to extract questions
        quiz_sections = []
        
        # Simple parsing for now - can be enhanced later
        if quiz_content:
            # For now, create default quiz structure
            quiz_sections.append({
                'question': 'Quiz question based on content',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correctAnswer': 1,
                'explanation': 'Explanation for the correct answer'
            })
        
        return quiz_sections
    
    def _ai_enhance_content(self, content: str, difficulty: str) -> str:
        """AI enhances content for specific difficulty with mobile character limits."""
        # Handle both string and list content
        if isinstance(content, list):
            content = " ".join(str(item) for item in content)
        elif not isinstance(content, str):
            content = str(content)
            
        # Clean content (remove markdown, extra whitespace)
        content = self._clean_content_for_mobile(content)
        
        # Remove type labels that might have leaked into content (Portuguese and English)
        content = re.sub(r'^(Content|Conteúdo|Quiz|Quote|Content Item \d+|Item \d+|Item de Conteúdo \d+)\s+', '', content, flags=re.IGNORECASE)
        
        # Replace internal terminology with user-friendly terms
        content = content.replace('supertask', 'exercício')
        content = content.replace('Supertask', 'Exercício')
        content = content.replace('SUPERTASK', 'EXERCÍCIO')
        
        # Use AI to enhance content with difficulty-specific characteristics
        content = self._ai_enhance_with_difficulty_prompts(content, difficulty)
        
        # Enforce mobile character limits (50-300 chars)
        if len(content) > 300:
            # Truncate to 290 chars and add ellipsis
            content = content[:290] + "..."
            logger.warning(f"Content truncated to mobile limit: {len(content)} chars")
        elif len(content) < 50:
            # Pad with difficulty-appropriate content if too short
            if content.strip():
                content = f"{content.strip()} - {difficulty.capitalize()} level insights."
            else:
                content = f"Conteúdo educativo para nível {difficulty} sobre este tópico importante."
        
        return content.strip()
    
    def _ai_enhance_with_difficulty_prompts(self, content: str, difficulty: str) -> str:
        """Use AI to enhance content with difficulty-specific prompts and characteristics."""
        try:
            # Get difficulty configuration from YAML
            from .config_loader import get_difficulty_configuration
            difficulty_config = get_difficulty_configuration(difficulty)
            
            # Build difficulty-specific prompt
            characteristics = "\n".join(f"- {char}" for char in difficulty_config['characteristics'])
            content_depth = difficulty_config['content_guidelines']['content_depth']
            
            # Create AI prompt for progressive content generation
            if difficulty == "beginner":
                system_prompt = f"""Você é um especialista em educação que cria conteúdo progressivo.

NÍVEL: BEGINNER (Fundação)

Características para este nível:
{characteristics}

Sua tarefa: Extraia e desenvolva os CONCEITOS FUNDAMENTAIS que preparam o usuário para aprendizado mais profundo.

FOQUE EM:
- Conceitos básicos e definições essenciais
- Aplicações simples e práticas
- Construção de base para aprendizado avançado
- "O que é isso?" e "Por que importa?"

EVITE:
- Nuances complexas ou casos especiais
- Integrações avançadas
- Assumir conhecimento prévio

REGRAS CRÍTICAS:
- Mantenha entre 50-300 caracteres
- Use português brasileiro
- Não inclua prefixos como "Conteúdo:" ou "Content:"
- Prepare o usuário para conceitos mais avançados"""
                
                user_prompt = f"Extraia os conceitos fundamentais deste conteúdo que um iniciante precisa entender primeiro:\n\n{content}"
                
            else:  # advanced
                system_prompt = f"""Você é um especialista em educação que cria conteúdo progressivo.

NÍVEL: ADVANCED (Construção)

Características para este nível:
{characteristics}

ASSUMA QUE O USUÁRIO JÁ CONHECE:
- Conceitos básicos e definições
- Aplicações simples

Sua tarefa: Desenvolva INSIGHTS AVANÇADOS que constroem sobre o conhecimento fundamental.

FOQUE EM:
- Relacionamentos complexos e padrões
- Aplicações avançadas e estratégias
- Integração com múltiplos conceitos
- "Como funciona em situações complexas?" e "Quando aplicar?"

CONSTRUA SOBRE o conhecimento fundamental em vez de repeti-lo.

REGRAS CRÍTICAS:
- Mantenha entre 50-300 caracteres
- Use português brasileiro
- Não inclua prefixos como "Conteúdo:" ou "Content:"
- Assuma conhecimento dos conceitos básicos"""
                
                user_prompt = f"Extraia insights avançados que constroem sobre o conhecimento fundamental deste tópico:\n\n{content}"
            
            # Use OpenAI to enhance content
            if hasattr(self, 'openai_client'):
                response = self.openai_client.generate_completion(
                    prompt=user_prompt,
                    system_message=system_prompt,
                    max_tokens=200,
                    temperature=0.7
                )
                
                if response and response.strip():
                    enhanced_content = response.strip()
                    # Clean any remaining prefixes
                    enhanced_content = re.sub(r'^(Content|Conteúdo|Quiz|Quote):\s*', '', enhanced_content, flags=re.IGNORECASE)
                    return enhanced_content
            
            # Fallback to word replacement if AI fails
            return self._apply_difficulty_style(content, difficulty)
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, using fallback: {e}")
            return self._apply_difficulty_style(content, difficulty)
    
    def _apply_difficulty_style(self, content: str, difficulty: str) -> str:
        """Apply difficulty-specific styling and complexity to content."""
        if not content or not content.strip():
            return content
            
        try:
            # Get difficulty configuration
            from .config_loader import get_difficulty_configuration
            config = get_difficulty_configuration(difficulty)
            
            # Apply difficulty-specific modifications based on characteristics
            if difficulty == "beginner":
                # Simplify language and add supportive elements
                # Make concepts more accessible
                if "complexo" in content.lower():
                    content = content.replace("complexo", "simples")
                if "sofisticado" in content.lower():
                    content = content.replace("sofisticado", "básico")
                    
                # Add encouraging language for beginners
                if "você" in content.lower():
                    content = content.replace("você", "você (passo a passo)")
                if "exercício" in content.lower():
                    content = content.replace("exercício", "exercício guiado")
                if "explora" in content.lower():
                    content = content.replace("explora", "explora de forma simples")
                if "encontrar" in content.lower():
                    content = content.replace("encontrar", "descobrir gradualmente")
                    
            elif difficulty == "advanced":
                # Add complexity and depth
                # Use more sophisticated language
                if "simples" in content.lower():
                    content = content.replace("simples", "multifacetado")
                if "básico" in content.lower():
                    content = content.replace("básico", "avançado")
                if "exercício" in content.lower():
                    content = content.replace("exercício", "exercício analítico")
                if "explora" in content.lower():
                    content = content.replace("explora", "examina criticamente")
                if "encontrar" in content.lower():
                    content = content.replace("encontrar", "dominar estratégias para")
                    
                # Add analytical depth for advanced users
                if "aprenderá" in content.lower():
                    content = content.replace("aprenderá", "dominará as nuances de")
                    
            return content
            
        except Exception as e:
            logger.warning(f"Failed to apply difficulty style: {e}")
            return content
    
    def _parse_content_structure(self, content_text: str) -> Dict[str, Any]:
        """Parse content to extract author, tips, and main content separately."""
        import re
        
        if isinstance(content_text, list):
            content_text = " ".join(str(item) for item in content_text)
        elif not isinstance(content_text, str):
            content_text = str(content_text)
        
        # Initialize result
        result = {
            'content': content_text,
            'author': None,
            'tips': None
        }
        
        # Parse author line (handles markdown **Author**: format and "— Author" formats)
        author_patterns = [
            r'\*\*Author\*\*:\s*([^\n\r]+)',  # **Author**: Name
            r'Author:\s*([^\n\r]+)',  # Author: Name
            r'—\s*([^\n\r]+)$',  # — Author at end
            r'^\s*—\s*([^\n\r]+)',  # — Author at start
        ]
        
        for pattern in author_patterns:
            author_match = re.search(pattern, content_text, re.MULTILINE)
            if author_match:
                result['author'] = author_match.group(1).strip()
                # Remove author line from content
                content_text = re.sub(pattern, '', content_text, flags=re.MULTILINE)
                break
        
        # Parse tips section (handles markdown **Tips**: format)
        tips_patterns = [
            r'\*\*Tips\*\*:\s*([\s\S]*?)(?=\n\*\*|\n—|\n\n|$)',  # **Tips**: with bullet points
            r'Tips?:\s*(.+?)(?=\n—|\n\n|$)',  # Tips: with bullet points
        ]
        
        for pattern in tips_patterns:
            tips_match = re.search(pattern, content_text, re.DOTALL | re.MULTILINE)
            if tips_match:
                tips_text = tips_match.group(1)
                # Extract bullet points
                tips = []
                for line in tips_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        tip = line.lstrip('-•').strip()
                        if tip:
                            tips.append(tip)
                
                if tips:
                    result['tips'] = tips
                
                # Remove tips section from content
                content_text = re.sub(pattern, '', content_text, flags=re.DOTALL | re.MULTILINE)
                break
        
        # Clean up the main content
        main_content = content_text.strip()
        # Remove any remaining formatting artifacts
        main_content = re.sub(r'\n\s*\n\s*\n', '\n\n', main_content)  # Multiple newlines
        main_content = re.sub(r'^\s*—\s*$', '', main_content, flags=re.MULTILINE)  # Standalone dashes
        
        result['content'] = main_content.strip()
        
        return result
    
    def _ai_enhance_question(self, question: str, difficulty: str) -> str:
        """AI enhances quiz question for progressive difficulty with mobile limits (15-120 chars)."""
        if not question or not question.strip():
            question = f"Qual o conceito-chave sobre este tópico?"
        
        question = question.strip()
        
        # Remove difficulty level from questions
        question = re.sub(r'\s*-\s*(Iniciante|Avançado|Beginner|Advanced)\s*', '', question)
        question = re.sub(r'\s*\((Iniciante|Avançado|Beginner|Advanced)\)\s*', '', question)
        
        # Replace internal terminology with user-friendly terms
        question = question.replace('supertask', 'exercício')
        question = question.replace('Supertask', 'Exercício')
        
        # Apply progressive difficulty with AI
        try:
            from .config_loader import get_difficulty_configuration
            difficulty_config = get_difficulty_configuration(difficulty)
            quiz_style = difficulty_config['quiz_guidelines']['quiz_style']
            
            if difficulty == "beginner":
                system_prompt = f"""Você é um especialista em criar perguntas educativas progressivas.

NÍVEL: BEGINNER (Fundação)

Estilo de quiz: {quiz_style}

Sua tarefa: Reescreva esta pergunta para testar CONCEITOS BÁSICOS e DEFINIÇÕES.

FOQUE EM:
- Reconhecimento de conceitos fundamentais
- Definições simples e claras
- Identificação de elementos básicos
- "O que é?" e "Qual é?"

EVITE:
- Análise complexa ou comparações
- Aplicações avançadas
- Integração de múltiplos conceitos

REGRAS:
- Mantenha entre 15-120 caracteres
- Use português brasileiro
- Seja claro e direto"""
                
                user_prompt = f"Reescreva esta pergunta para testar conceitos fundamentais de nível iniciante:\n\n{question}"
                
            else:  # advanced
                system_prompt = f"""Você é um especialista em criar perguntas educativas progressivas.

NÍVEL: ADVANCED (Construção)

Estilo de quiz: {quiz_style}

ASSUMA QUE O USUÁRIO JÁ CONHECE:
- Conceitos básicos e definições
- Aplicações simples

Sua tarefa: Reescreva esta pergunta para testar APLICAÇÃO AVANÇADA e ANÁLISE.

FOQUE EM:
- Análise de situações complexas
- Integração de múltiplos conceitos
- Aplicação em cenários reais
- "Como" e "Quando" aplicar

CONSTRUA SOBRE conhecimento fundamental.

REGRAS:
- Mantenha entre 15-120 caracteres
- Use português brasileiro
- Assuma conhecimento básico"""
                
                user_prompt = f"Reescreva esta pergunta para testar aplicação avançada e análise:\n\n{question}"
            
            # Use OpenAI to enhance question
            if hasattr(self, 'openai_client'):
                response = self.openai_client.generate_completion(
                    prompt=user_prompt,
                    system_message=system_prompt,
                    max_tokens=100,
                    temperature=0.7
                )
                
                if response and response.strip():
                    enhanced_question = response.strip()
                    # Clean any remaining prefixes
                    enhanced_question = re.sub(r'^(Question|Pergunta):\s*', '', enhanced_question, flags=re.IGNORECASE)
                    
                    # Enforce mobile character limits (15-120 chars)
                    if len(enhanced_question) > 120:
                        enhanced_question = enhanced_question[:115] + "...?"
                        logger.warning(f"AI-enhanced quiz question truncated to mobile limit: {len(enhanced_question)} chars")
                    elif len(enhanced_question) < 15:
                        enhanced_question = f"{enhanced_question} - conceito essencial"
                    
                    return enhanced_question
                    
        except Exception as e:
            logger.warning(f"AI question enhancement failed, using fallback: {e}")
        
        # Fallback to original formatting logic
        if len(question) > 120:
            question = question[:115] + "...?"
            logger.warning(f"Quiz question truncated to mobile limit: {len(question)} chars")
        elif len(question) < 15:
            question = f"{question} - conceito essencial"
        
        return question
    
    def _ai_enhance_options(self, options: List[str], difficulty: str) -> List[str]:
        """AI enhances quiz options for specific difficulty with mobile limits (3-60 chars each)."""
        if not options or len(options) < 2:
            options = [f"Opção A", f"Opção B", f"Opção C", f"Opção D"]
        
        # Enforce mobile character limits (3-60 chars each)
        mobile_options = []
        for i, option in enumerate(options):
            option = str(option).strip()
            
            if len(option) > 60:
                option = option[:57] + "..."
                logger.warning(f"Quiz option {i} truncated to mobile limit: {len(option)} chars")
            elif len(option) < 3:
                option = f"Op {i+1}"
            
            mobile_options.append(option)
        
        return mobile_options
    
    def _ai_enhance_explanation(self, explanation: str, difficulty: str) -> str:
        """AI enhances quiz explanation for progressive difficulty with mobile limits (30-250 chars)."""
        if not explanation or not explanation.strip():
            explanation = f"Explicação para nível {difficulty} com insights comportamentais."
        
        explanation = explanation.strip()
        
        # Apply progressive difficulty with AI
        try:
            from .config_loader import get_difficulty_configuration
            difficulty_config = get_difficulty_configuration(difficulty)
            
            if difficulty == "beginner":
                system_prompt = f"""Você é um especialista em criar explicações educativas progressivas.

NÍVEL: BEGINNER (Fundação)

Sua tarefa: Reescreva esta explicação para FUNDAMENTAR o aprendizado.

FOQUE EM:
- Definições claras e simples
- Por que a resposta está correta
- Conceitos básicos essenciais
- Preparar para entendimento mais profundo

EVITE:
- Detalhes complexos ou nuances
- Múltiplas camadas de análise
- Jargão técnico avançado

REGRAS:
- Mantenha entre 30-250 caracteres
- Use português brasileiro
- Seja educativo e claro"""
                
                user_prompt = f"Reescreva esta explicação para fundamentar o aprendizado de nível iniciante:\n\n{explanation}"
                
            else:  # advanced
                system_prompt = f"""Você é um especialista em criar explicações educativas progressivas.

NÍVEL: ADVANCED (Construção)

ASSUMA QUE O USUÁRIO JÁ CONHECE:
- Conceitos básicos e definições
- Fundamentos do tópico

Sua tarefa: Reescreva esta explicação com INSIGHTS AVANÇADOS.

FOQUE EM:
- Por que outras opções são inadequadas
- Nuances e complexidades
- Aplicações em cenários reais
- Conexões com outros conceitos

CONSTRUA SOBRE conhecimento fundamental.

REGRAS:
- Mantenha entre 30-250 caracteres
- Use português brasileiro
- Assuma conhecimento básico"""
                
                user_prompt = f"Reescreva esta explicação com insights avançados e análise profunda:\n\n{explanation}"
            
            # Use OpenAI to enhance explanation
            if hasattr(self, 'openai_client'):
                response = self.openai_client.generate_completion(
                    prompt=user_prompt,
                    system_message=system_prompt,
                    max_tokens=150,
                    temperature=0.7
                )
                
                if response and response.strip():
                    enhanced_explanation = response.strip()
                    # Clean any remaining prefixes
                    enhanced_explanation = re.sub(r'^(Explanation|Explicação):\s*', '', enhanced_explanation, flags=re.IGNORECASE)
                    
                    # Enforce mobile character limits (30-250 chars)
                    if len(enhanced_explanation) > 250:
                        enhanced_explanation = enhanced_explanation[:245] + "..."
                        logger.warning(f"AI-enhanced quiz explanation truncated to mobile limit: {len(enhanced_explanation)} chars")
                    elif len(enhanced_explanation) < 30:
                        enhanced_explanation = f"{enhanced_explanation} - Nível {difficulty} com ciência comportamental."
                    
                    return enhanced_explanation
                    
        except Exception as e:
            logger.warning(f"AI explanation enhancement failed, using fallback: {e}")
        
        # Fallback to original formatting logic
        if len(explanation) > 250:
            explanation = explanation[:245] + "..."
            logger.warning(f"Quiz explanation truncated to mobile limit: {len(explanation)} chars")
        elif len(explanation) < 30:
            explanation = f"{explanation} - Nível {difficulty} com ciência comportamental."
        
        return explanation
    
    def _clean_content_for_mobile(self, content: str) -> str:
        """Clean content for mobile display by removing markdown and excessive formatting."""
        import re
        
        if not content:
            return ""
        
        # Handle list input by joining
        if isinstance(content, list):
            content = " ".join(str(item) for item in content)
        elif not isinstance(content, str):
            content = str(content)
        
        # Remove content type prefixes that might appear (Portuguese and English)
        content = re.sub(r'^(Content|Conteúdo|Quiz|Quote|Item\s+de\s+Conteúdo)\s*(\d+)?\s*', '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove markdown headers (### Header -> Header)
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # Remove markdown bold/italic (**text** -> text)
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        
        # Remove markdown links ([text](url) -> text)
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # Replace internal terminology with user-friendly terms  
        content = content.replace('supertask', 'exercício')
        content = content.replace('Supertask', 'Exercício')
        content = content.replace('SUPERTASK', 'EXERCÍCIO')
        
        # Remove Author: and Tips: sections (these should be handled separately)
        content = re.sub(r'\*\*Author\*\*:.*?(?=\n\*\*|\n\n|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'Author:.*?(?=\n\*\*|\n\n|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'\*\*Tips\*\*:.*?(?=\n\*\*|\n\n|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'Tips?:.*?(?=\n\*\*|\n\n|$)', '', content, flags=re.DOTALL)
        
        # Remove excessive whitespace and newlines
        content = re.sub(r'\n\s*\n', ' ', content)  # Multiple newlines -> single space
        content = re.sub(r'\s+', ' ', content)      # Multiple spaces -> single space
        
        # Remove markdown list markers (- item -> item)
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
        
        return content.strip()
    
    def _split_content_to_mobile_chunks(self, content: str) -> List[str]:
        """Split large content into mobile-optimized chunks of 100-250 chars."""
        if not content:
            return []
        
        # Clean content first
        content = self._clean_content_for_mobile(content)
        
        if len(content) <= 250:
            return [content]
        
        # Split by sentences first
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add period back if missing
            if not sentence.endswith('.'):
                sentence += '.'
            
            # Check if adding this sentence would exceed limit
            potential_chunk = current_chunk + (' ' if current_chunk else '') + sentence
            
            if len(potential_chunk) <= 250:
                current_chunk = potential_chunk
            else:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _generate_quiz_items(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
        """Generate meaningful quiz items based on source insights."""
        try:
            # Extract source material and title
            source_material = self._extract_source_material(template_data)
            frontmatter = template_data.get('frontmatter', {})
            title = frontmatter.get('title', 'este tópico')
            
            # Remove difficulty level from title for user-facing questions
            clean_title = re.sub(r'\s*-\s*(Iniciante|Avançado|Beginner|Advanced)\s*', '', title)
            clean_title = re.sub(r'\s*\((Iniciante|Avançado|Beginner|Advanced)\)\s*', '', clean_title)
            
            # Step 1: Extract insights for question generation
            logger.info("Extracting insights for source-driven quiz generation")
            insights = self.enrichment_engine.extract_source_insights(source_material, max_insights=3)
            
            # Step 2: Generate source-driven questions
            logger.info(f"Generating source-driven quiz questions for difficulty: {difficulty}")
            quiz_questions = self.enrichment_engine.generate_source_driven_questions(
                insights, difficulty, clean_title, num_questions=3
            )
            
            # Step 3: Chain-of-thought validation for quiz questions
            if quiz_questions:
                logger.info("Validating quiz relevance with chain-of-thought analysis")
                validation = self.enrichment_engine.validate_content_relevance(
                    "", quiz_questions, source_material
                )
                
                logger.info(f"Quiz validation: {validation.decision.value}, "
                          f"relevance: {validation.relevance_score:.2f}")
                
                # Apply conditional enhancement only if needed
                if validation.decision.value != "approved":
                    logger.info("Applying conditional quiz enhancement")
                    _, enhanced_questions = self.enrichment_engine.enhance_content_conditionally(
                        "", quiz_questions, validation, insights
                    )
                    if enhanced_questions != quiz_questions:
                        quiz_questions = enhanced_questions
                        logger.info("Quiz questions enhanced based on validation feedback")
            
            # Step 4: Convert to mobile-optimized format with AI enhancement
            quiz_items = []
            for i, quiz_data in enumerate(quiz_questions[:4]):  # Max 4 quiz items
                try:
                    quiz_item = {
                        "type": "quiz",
                        "question": self._ai_enhance_question(quiz_data['question'], difficulty),
                        "options": self._ai_enhance_options(quiz_data['options'], difficulty),
                        "correctAnswer": quiz_data['correctAnswer'],
                        "explanation": self._ai_enhance_explanation(quiz_data['explanation'], difficulty)
                    }
                    quiz_items.append(quiz_item)
                    logger.info(f"Generated source-driven quiz item {i+1}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process quiz item {i+1}: {e}")
            
            # Ensure at least 1 quiz item
            if not quiz_items:
                logger.warning("No source-driven quiz generated, creating fallback")
                quiz_items.append(self._create_default_quiz_item(difficulty))
            
            logger.info(f"Generated {len(quiz_items)} source-driven quiz items")
            return quiz_items
            
        except Exception as e:
            logger.error(f"Source-driven quiz generation failed: {e}")
            # Fallback to hardcoded questions
            return self._generate_quiz_items_fallback(template_data, difficulty)
    
    def _generate_quiz_items_fallback(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
        """Fallback quiz generation with hardcoded questions."""
        quiz_items = []
        frontmatter = template_data.get('frontmatter', {})
        title = frontmatter.get('title', 'este tópico')
        
        # Remove difficulty level from title for user-facing questions
        clean_title = re.sub(r'\s*-\s*(Iniciante|Avançado|Beginner|Advanced)\s*', '', title)
        clean_title = re.sub(r'\s*\((Iniciante|Avançado|Beginner|Advanced)\)\s*', '', clean_title)
        
        # Create basic quiz questions based on difficulty
        if difficulty == "beginner":
            quiz_questions = [
                {
                    'question': f"Qual é o conceito fundamental sobre {clean_title}?",
                    'options': ["Conceitos básicos", "Aplicações práticas", "Definições essenciais", "Fundamentos"],
                    'correctAnswer': 2,
                    'explanation': "Definições essenciais formam a base para todo aprendizado."
                }
            ]
        else:  # advanced
            quiz_questions = [
                {
                    'question': f"Como integrar {clean_title} com outros conceitos?",
                    'options': ["Isoladamente", "De forma sistemática", "Sem planejamento", "Ocasionalmente"],
                    'correctAnswer': 1,
                    'explanation': "A integração sistemática maximiza o impacto e a efetividade."
                }
            ]
        
        # Convert to mobile-optimized format
        for quiz_data in quiz_questions[:2]:  # Max 2 fallback quiz items
            quiz_item = {
                "type": "quiz",
                "question": self._ai_enhance_question(quiz_data['question'], difficulty),
                "options": self._ai_enhance_options(quiz_data['options'], difficulty),
                "correctAnswer": quiz_data['correctAnswer'],
                "explanation": self._ai_enhance_explanation(quiz_data['explanation'], difficulty)
            }
            quiz_items.append(quiz_item)
        
        return quiz_items
    
    def _generate_quote_items(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
        """Generate inspirational quote items."""
        quote_items = []
        
        # Create context-appropriate quotes (use allowed expert authors)
        quotes = [
            {
                'content': "O progresso acontece através de pequenos passos consistentes.",
                'author': ALLOWED_QUOTE_AUTHORS[0]
            },
            {
                'content': "A ciência comportamental nos ensina que mudanças sustentáveis começam devagar.",
                'author': ALLOWED_QUOTE_AUTHORS[1]
            }
        ]
        
        # Convert to mobile-optimized format
        for quote_data in quotes[:2]:  # Limit candidates before sequencing
            # Ensure quote content is within 20-200 char limit
            quote_content = quote_data['content']
            if len(quote_content) > 200:
                quote_content = quote_content[:195] + "..."
            
            quote_item = {
                "type": "quote",
                "content": quote_content,
                "author": quote_data['author']
            }
            quote_items.append(quote_item)
        
        return quote_items
    
    def _create_default_content_item(self, difficulty: str, index: int) -> Dict[str, Any]:
        """Create a default content item when needed."""
        default_content = f"Conteúdo educativo {index+1} sobre desenvolvimento pessoal para nível {difficulty}. Aplicação prática da ciência comportamental."
        
        return {
            "type": "content",
            "content": default_content,
            "author": "Ari"
        }
    
    def _create_default_quiz_item(self, difficulty: str) -> Dict[str, Any]:
        """Create a default quiz item when needed."""
        return {
            "type": "quiz",
            "question": f"Como aplicar os conceitos de desenvolvimento pessoal no dia a dia?",
            "options": [
                "Pequenos passos consistentes",
                "Mudanças radicais",
                "Esperar motivação",
                "Ignorar dificuldades"
            ],
            "correctAnswer": 0,
            "explanation": "Pequenos passos consistentes são fundamentais para mudanças sustentáveis."
        }
    
    def _create_default_quote_item(self, difficulty: str) -> Dict[str, Any]:
        """Create a default quote item when needed."""
        return {
            "type": "quote",
            "content": "O progresso acontece através de pequenos passos consistentes.",
            "author": ALLOWED_QUOTE_AUTHORS[0]
        }

    def _sanitize_authorship_and_quotes(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enforce: max one quote; quote author from allowed list; default content author to 'Ari'."""
        sanitized: List[Dict[str, Any]] = []
        quote_seen = False
        for item in items:
            item_type = item.get("type")
            if item_type == "quote":
                if quote_seen:
                    continue
                quote_seen = True
                author = item.get("author")
                if author not in ALLOWED_QUOTE_AUTHORS:
                    item = {**item, "author": ALLOWED_QUOTE_AUTHORS[0]}
                sanitized.append(item)
            elif item_type == "content":
                if not item.get("author"):
                    item = {**item, "author": "Ari"}
                sanitized.append(item)
            else:
                sanitized.append(item)
        return sanitized[:8]
    
    def _trim_to_mobile_limit(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trim items to 8 max while maintaining variety."""
        if len(items) <= 8:
            return items
        
        # Prioritize variety: keep content, quiz, and quote types
        content_items = [item for item in items if item.get('type') == 'content']
        quiz_items = [item for item in items if item.get('type') == 'quiz']
        quote_items = [item for item in items if item.get('type') == 'quote']
        
        # Build final list with variety
        final_items = []
        final_items.extend(content_items[:3])  # Max 3 content
        final_items.extend(quiz_items[:3])     # Max 3 quiz
        final_items.extend(quote_items[:2])    # Max 2 quotes
        
        return final_items[:8]  # Ensure max 8 items
    
    def _generate_metadata(self, template_data: Dict[str, Any], difficulty: str = "beginner") -> Dict[str, Any]:
        """Generate metadata with proper format."""
        frontmatter = template_data.get('frontmatter', {})
        
        return {
            'generated_by': 'lyfe-kt-structural-v1.0',
            'generation_timestamp': datetime.now().isoformat(),
            'ari_persona_applied': True,
            'difficulty_level': difficulty,  # Add missing difficulty_level
            'source_template': template_data.get('file_name', 'unknown'),
            'template_metadata': template_data.get('metadata', {}),
            # Required validation fields
            'language': frontmatter.get('language', 'portuguese'),
            'region': frontmatter.get('region', 'Brazil'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    def _validate_structure(self, json_data: Dict[str, Any]) -> bool:
        """Validate generated JSON against required structure."""
        try:
            # Step 1: Use existing validation function for backward compatibility
            from .config_loader import validate_generated_json_structure
            result = validate_generated_json_structure(json_data)
            
            if not result.get('valid', False):
                logger.error(f"Legacy structure validation failed: {result.get('errors', [])}")
                return False
            
            # Step 2: Use JSON Schema validation for comprehensive checking
            try:
                import jsonschema
                
                # Load schema for current format version
                schema_path = f"src/config/supertask_schema_{self.format_version}.json"
                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                    
                    # Validate against schema
                    jsonschema.validate(json_data, schema)
                    logger.info(f"JSON Schema validation passed for format {self.format_version}")
                else:
                    logger.warning(f"Schema file not found: {schema_path}, skipping schema validation")
                    
            except ImportError:
                logger.warning("jsonschema library not installed, skipping schema validation")
            except jsonschema.ValidationError as e:
                logger.error(f"JSON Schema validation failed: {e.message}")
                return False
            except Exception as e:
                logger.error(f"Schema validation error: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Structure validation error: {e}")
            return False

    def _normalize_archetype(self, archetype: str) -> str:
        """Normalize Portuguese archetypes to English."""
        if not archetype:
            return archetype
            
        # Mapping Portuguese → English
        archetype_mapping = {
            'guerreiro': 'warrior',
            'explorador': 'explorer', 
            'sábio': 'sage',
            'sabio': 'sage',  # without accent
            'governante': 'ruler',
            'warrior': 'warrior',  # already English
            'explorer': 'explorer',
            'sage': 'sage',
            'ruler': 'ruler'
        }
        
        normalized = archetype_mapping.get(archetype.lower(), archetype)
        logger.info(f"Normalized archetype '{archetype}' → '{normalized}'")
        return normalized


class TemplateProcessor:
    """
    Process filled markdown templates for JSON generation.
    
    Handles parsing of frontmatter, content sections, and validation
    of template structure and completeness.
    """
    
    def __init__(self):
        """Initialize template processor."""
        try:
            self.generation_prompts = load_generation_prompts()
            logger.info("Template processor initialized successfully")
        except Exception as e:
            raise GenerationError(f"Failed to initialize template processor: {e}")
    
    def parse_template(self, template_path: str) -> Dict[str, Any]:
        """
        Parse template frontmatter and content sections.
        
        Args:
            template_path: Path to the filled markdown template.
            
        Returns:
            Dictionary with parsed template data including:
            - frontmatter: Parsed YAML frontmatter
            - content: Main content sections
            - sections: Structured content sections
            - metadata: Template metadata
            
        Raises:
            GenerationError: If template parsing fails.
        """
        try:
            logger.info(f"Parsing template: {template_path}")
            
            # Read template file
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Split frontmatter and content
            if template_content.startswith('---'):
                parts = template_content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_str = parts[1].strip()
                    content_str = parts[2].strip()
                else:
                    raise GenerationError("Invalid template format: missing frontmatter")
            else:
                raise GenerationError("Invalid template format: no frontmatter found")
            
            # Parse frontmatter
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                if not isinstance(frontmatter, dict):
                    raise GenerationError("Invalid frontmatter: must be a dictionary")
            except yaml.YAMLError as e:
                raise GenerationError(f"Failed to parse frontmatter: {e}")
            
            # Parse content sections
            sections = self._parse_content_sections(content_str)
            
            # Extract metadata
            metadata = self._extract_template_metadata(template_path, frontmatter)
            
            return {
                'frontmatter': frontmatter,
                'content': content_str,
                'sections': sections,
                'metadata': metadata,
                'file_path': template_path,
                'file_name': Path(template_path).name
            }
            
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to parse template {template_path}: {e}")
    
    def _parse_content_sections(self, content: str) -> Dict[str, Any]:
        """Parse content into structured sections."""
        try:
            sections = {
                'main_content': [],
                'quiz_items': [],
                'quotes': [],
                'learning_objectives': [],
                'key_takeaways': []
            }
            
            # Split by headers
            lines = content.split('\n')
            current_section = 'main_content'
            current_content = []
            
            for line in lines:
                # Check for section headers
                if line.startswith('## '):
                    # Save previous section
                    if current_content:
                        sections[current_section].append('\n'.join(current_content))
                        current_content = []
                    
                    # Determine new section
                    header = line[3:].strip().lower()
                    if 'quiz' in header or 'pergunta' in header:
                        current_section = 'quiz_items'
                    elif 'quote' in header or 'citação' in header:
                        current_section = 'quotes'
                    elif 'objetivo' in header or 'objective' in header:
                        current_section = 'learning_objectives'
                    elif 'takeaway' in header or 'conclus' in header:
                        current_section = 'key_takeaways'
                    else:
                        current_section = 'main_content'
                else:
                    current_content.append(line)
            
            # Save final section
            if current_content:
                sections[current_section].append('\n'.join(current_content))
            
            return sections
            
        except Exception as e:
            logger.warning(f"Failed to parse content sections: {e}")
            return {'main_content': [content], 'quiz_items': [], 'quotes': [], 'learning_objectives': [], 'key_takeaways': []}
    
    def _normalize_archetype(self, archetype: str) -> str:
        """Normalize Portuguese archetypes to English."""
        if not archetype:
            return archetype
            
        # Mapping Portuguese → English  
        archetype_mapping = {
            'guerreiro': 'warrior',
            'explorador': 'explorer', 
            'sábio': 'sage',
            'sabio': 'sage',  # without accent
            'governante': 'ruler',
            'warrior': 'warrior',  # already English
            'explorer': 'explorer',
            'sage': 'sage', 
            'ruler': 'ruler'
        }
        
        normalized = archetype_mapping.get(archetype.lower(), archetype)
        logger.info(f"Normalized archetype '{archetype}' → '{normalized}'")
        return normalized

    def _extract_template_metadata(self, template_path: str, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata for JSON generation."""
        try:
            file_path = Path(template_path)
            
            return {
                'source_file': file_path.name,
                'source_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'modification_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'frontmatter_keys': list(frontmatter.keys()),
                'processing_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract template metadata: {e}")
            return {'source_file': Path(template_path).name, 'processing_timestamp': datetime.now().isoformat()}
    
    def validate_template(self, template_data: Dict[str, Any]) -> bool:
        """
        Validate template completeness and structure.
        
        Args:
            template_data: Parsed template data.
            
        Returns:
            True if template is valid, False otherwise.
        """
        try:
            frontmatter = template_data.get('frontmatter', {})
            sections = template_data.get('sections', {})
            
            # Required frontmatter fields (checking for both template and JSON field names)
            required_fields = ['title', 'dimension', 'archetype']
            required_mapping_fields = [
                ('difficulty', 'difficulty_level')  # Accept either difficulty or difficulty_level
            ]
            optional_mapping_fields = [
                ('estimated_duration', 'estimatedDuration'),
                ('coins_reward', 'coinsReward'),
                ('related_to_type', 'relatedToType'),
                ('related_to_id', 'relatedToId')
            ]
            
            # Check simple required fields
            for field in required_fields:
                if field not in frontmatter:
                    logger.error(f"Missing required frontmatter field: {field}")
                    return False
            
            # Check required mapping fields (at least one form must exist)
            for template_field, json_field in required_mapping_fields:
                if template_field not in frontmatter and json_field not in frontmatter:
                    logger.error(f"Missing required frontmatter field: {template_field} or {json_field}")
                    return False
            
            # Optional mapping fields are truly optional - no validation needed
            # They will be filled with defaults during generation if missing
            
            # Validate field types for duration and coins (must be numeric)
            duration_field = frontmatter.get('estimated_duration') or frontmatter.get('estimatedDuration')
            coins_field = frontmatter.get('coins_reward') or frontmatter.get('coinsReward')
            
            if duration_field is not None:
                if isinstance(duration_field, str):
                    try:
                        int(duration_field)
                    except (ValueError, TypeError):
                        logger.error("estimated_duration must be a valid number")
                        return False
                elif not isinstance(duration_field, (int, float)):
                    logger.error("estimated_duration must be a number")
                    return False
            
            if coins_field is not None:
                if isinstance(coins_field, str):
                    try:
                        int(coins_field)
                    except (ValueError, TypeError):
                        logger.error("coins_reward must be a valid number")
                        return False
                elif not isinstance(coins_field, (int, float)):
                    logger.error("coins_reward must be a number")
                    return False
            
            # Validate dimension values
            valid_dimensions = ['physicalHealth', 'mentalHealth', 'relationships', 'work', 'spirituality']
            if frontmatter.get('dimension') not in valid_dimensions:
                logger.error(f"Invalid dimension: {frontmatter.get('dimension')}")
                return False
            
            # Validate archetype values
            valid_archetypes = ['warrior', 'explorer', 'sage', 'ruler']
            archetype = self._normalize_archetype(frontmatter.get('archetype'))
            if archetype not in valid_archetypes:
                logger.error(f"Invalid archetype: {frontmatter.get('archetype')}")
                return False
            
            # Check for content
            if not sections.get('main_content'):
                logger.error("Template must have main content")
                return False
            
            logger.info("Template validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return False


class JSONGenerator:
    """
    Generate supertask JSON from processed templates.
    
    Uses AI-powered generation with Ari persona consistency
    and exact test.json structure compliance.
    """
    
    def __init__(self):
        """Initialize JSON generator."""
        try:
            self.openai_client = get_openai_client()
            self.generation_prompts = load_generation_prompts()
            logger.info("JSON generator initialized successfully")
        except Exception as e:
            raise GenerationError(f"Failed to initialize JSON generator: {e}")
    
    def generate_supertask(self, template_data: Dict[str, Any], difficulty: str = "beginner") -> Dict[str, Any]:
        """
        Generate single supertask JSON with specified difficulty.
        
        Args:
            template_data: Parsed template data.
            difficulty: Target difficulty level (beginner/advanced).
            
        Returns:
            Generated supertask JSON.
            
        Raises:
            GenerationError: If generation fails.
        """
        try:
            logger.info(f"Generating supertask with difficulty: {difficulty}")
            
            # Build generation prompt
            prompt_dict = build_generation_prompt(
                filled_template=template_data['content'],
                target_difficulty=difficulty,
                target_audience=difficulty,
                estimated_duration=template_data['frontmatter'].get('estimated_duration', 300),
                suggested_coins=template_data['frontmatter'].get('coins_reward', 15)
            )
            
            # Generate JSON using OpenAI
            response = self.openai_client.generate_completion(
                prompt=prompt_dict['user_message'],
                system_message=prompt_dict['system_message'],
                max_tokens=4000,
                temperature=0.7
            )
            
            # Parse JSON response
            try:
                # Handle markdown code block formatting
                if response.strip().startswith('```json'):
                    # Extract JSON from markdown code blocks
                    json_start = response.find('```json') + 7
                    json_end = response.rfind('```')
                    if json_end > json_start:
                        json_content = response[json_start:json_end].strip()
                    else:
                        json_content = response
                elif response.strip().startswith('```'):
                    # Handle generic code blocks
                    json_start = response.find('```') + 3
                    json_end = response.rfind('```')
                    if json_end > json_start:
                        json_content = response[json_start:json_end].strip()
                    else:
                        json_content = response
                else:
                    json_content = response.strip()
                
                generated_json = json.loads(json_content)
            except json.JSONDecodeError as e:
                raise GenerationError(f"Failed to parse generated JSON: {e}")
            
            # Enhance with metadata first
            generated_json = self._enhance_with_metadata(generated_json, template_data, difficulty)
            
            # Validate JSON structure after metadata enhancement
            if not self.validate_json_structure(generated_json):
                raise GenerationError("Generated JSON does not match required structure")
            
            return generated_json
            
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to generate supertask: {e}")
    
    def generate_multiple_supertasks(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate both beginner and advanced versions.
        
        Args:
            template_data: Parsed template data.
            
        Returns:
            List of generated supertasks (beginner and advanced).
        """
        try:
            logger.info("Generating multiple supertasks (beginner and advanced)")
            
            supertasks = []
            
            # Generate beginner version
            beginner_task = self.generate_supertask(template_data, "beginner")
            supertasks.append(beginner_task)
            
            # Generate advanced version
            advanced_task = self.generate_supertask(template_data, "advanced")
            supertasks.append(advanced_task)
            
            return supertasks
            
        except Exception as e:
            raise GenerationError(f"Failed to generate multiple supertasks: {e}")
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
        """
        Validate generated JSON against test.json structure.
        
        Args:
            json_data: Generated JSON data.
            
        Returns:
            True if structure is valid, False otherwise.
        """
        try:
            # Use the configuration system validation
            validation_result = validate_generated_json_structure(json_data)
            
            if not validation_result.get('valid', False):
                logger.error(f"JSON structure validation failed: {validation_result.get('errors', [])}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"JSON structure validation error: {e}")
            return False
    
    def _get_target_json_structure(self) -> Dict[str, Any]:
        """Get target JSON structure for generation."""
        return {
            "title": "string",
            "dimension": "physicalHealth|mentalHealth|relationships|work|spirituality",
            "archetype": "warrior|explorer|sage|ruler",
            "relatedToType": "HABITBP|GENERIC",
            "relatedToId": "string",
            "estimatedDuration": "number_in_seconds",
            "coinsReward": "number",
            "flexibleItems": [
                {
                    "type": "content|quote|quiz",
                    "content": "string",
                    "author": "string (optional for content/quote)",
                    "options": ["array for quiz"],
                    "correctAnswer": "number (index for quiz)",
                    "explanation": "string (for quiz)"
                }
            ],
            "metadata": {
                "object": "any_metadata_fields"
            }
        }
    
    def _enhance_with_metadata(self, json_data: Dict[str, Any], template_data: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """Enhance generated JSON with metadata."""
        try:
            # Add generation metadata
            json_data['metadata'] = json_data.get('metadata', {})
            
            # Get template frontmatter for additional metadata
            frontmatter = template_data.get('frontmatter', {})
            
            json_data['metadata'].update({
                'generated_by': 'lyfe-kt-stage3',
                'generation_timestamp': datetime.now().isoformat(),
                'ari_persona_applied': True,
                'difficulty_level': difficulty,
                'source_template': template_data['file_name'],
                'template_metadata': template_data['metadata'],
                # Add required validation fields
                'language': frontmatter.get('language', 'portuguese'),
                'region': frontmatter.get('region', 'Brazil'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'version': '1.0.0'
            })
            
            # Ensure title includes difficulty
            if difficulty not in json_data['title']:
                json_data['title'] = f"{json_data['title']} - {difficulty.capitalize()}"
            
            return json_data
            
        except Exception as e:
            logger.warning(f"Failed to enhance JSON with metadata: {e}")
            return json_data


class GenerationPipeline:
    """
    Main orchestration for Stage 3 generation.
    
    Coordinates template processing, JSON generation, and reporting
    with comprehensive error handling and progress tracking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize generation pipeline.
        
        Args:
            config: Optional configuration dictionary.
        """
        try:
            # Load configuration if not provided
            if config is None:
                try:
                    config = get_config()
                except ValueError:
                    load_config()
                    config = get_config()
            
            self.config = config
            
            # Initialize components
            self.template_processor = TemplateProcessor()
            self.json_generator = StructuralJSONGenerator(format_version="v1.1")  # Use v1.1 mobile-optimized schema for generation
            
            # Progress tracking
            self.progress_callback = None
            self.current_progress = 0
            self.total_files = 0
            
            logger.info("Generation pipeline initialized successfully")
            
        except Exception as e:
            raise GenerationError(f"Failed to initialize generation pipeline: {e}")
    
    def set_progress_callback(self, callback):
        """Set progress callback for real-time reporting."""
        self.progress_callback = callback
    
    def _report_progress(self, current: int, total: int, message: str):
        """Report progress to callback if set."""
        self.current_progress = current
        self.total_files = total
        
        if self.progress_callback:
            self.progress_callback(current, total, message)
        
        logger.info(f"Progress: {current}/{total} - {message}")
    
    def process_template(self, template_path: str, output_dir: str, generate_both_difficulties: bool = True, specific_difficulty: str = None, custom_sequence: str = None) -> Dict[str, Any]:
        """
        Process single template through generation pipeline.
        
        Args:
            template_path: Path to template file.
            output_dir: Directory to save output.
            generate_both_difficulties: Whether to generate both beginner and advanced versions.
            
        Returns:
            Processing results dictionary.
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing template: {template_path}")
            self._report_progress(0, 5, f"Starting processing of {Path(template_path).name}")
            
            # Step 1: Parse template
            self._report_progress(1, 5, "Parsing template")
            template_data = self.template_processor.parse_template(template_path)
            
            # Step 2: Validate template
            self._report_progress(2, 5, "Validating template")
            if not self.template_processor.validate_template(template_data):
                raise GenerationError("Template validation failed")
            
            # Step 3: Generate JSON(s)
            self._report_progress(3, 5, "Generating JSON")
            if generate_both_difficulties:
                generated_jsons = self.json_generator.generate_multiple_supertasks(template_data, custom_sequence)
            else:
                # Use specific difficulty (defensive default to beginner)
                if specific_difficulty:
                    difficulty = specific_difficulty
                else:
                    # Fallback to template difficulty or default
                    difficulty = template_data['frontmatter'].get('difficulty') or template_data['frontmatter'].get('difficulty_level', 'beginner')
                
                generated_json = self.json_generator.generate_supertask(template_data, difficulty, custom_sequence)
                generated_jsons = [generated_json]
            
            # Step 4: Save outputs
            self._report_progress(4, 5, "Saving outputs")
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            output_files = []
            template_name = Path(template_path).stem
            
            for i, json_data in enumerate(generated_jsons):
                difficulty = json_data['metadata']['difficulty_level']
                output_file = output_path / f"{template_name}_{difficulty}.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                output_files.append(str(output_file))
            
            # Step 5: Compile results
            self._report_progress(5, 5, "Compiling results")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'input_template': template_path,
                'output_directory': str(output_path),
                'generated_files': output_files,
                'generated_count': len(generated_jsons),
                'processing_time_seconds': processing_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'template_data': template_data,
                'generated_jsons': generated_jsons
            }
            
            logger.info(f"Successfully processed template: {template_path}")
            return result
            
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to process template {template_path}: {e}")
    
    def process_directory(self, input_dir: str, output_dir: str, generate_both_difficulties: bool = True) -> Dict[str, Any]:
        """
        Process directory of templates with batch processing.
        
        Args:
            input_dir: Directory containing template files.
            output_dir: Directory to save outputs.
            generate_both_difficulties: Whether to generate both difficulty levels.
            
        Returns:
            Batch processing results dictionary.
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing directory: {input_dir}")
            
            # Find all template files
            input_path = Path(input_dir)
            if not input_path.exists():
                raise GenerationError(f"Input directory not found: {input_dir}")
            
            template_files = list(input_path.glob("**/*.md"))
            
            if not template_files:
                raise GenerationError(f"No template files (.md) found in {input_dir}")
            
            total_files = len(template_files)
            self.total_files = total_files
            
            # Process each template
            successful_files = []
            failed_files = []
            individual_results = []
            
            for i, template_file in enumerate(template_files):
                try:
                    result = self.process_template(
                        str(template_file),
                        output_dir,
                        generate_both_difficulties
                    )
                    
                    individual_results.append(result)
                    successful_files.append(str(template_file))
                    
                    self._report_progress(i + 1, total_files, f"Processed {template_file.name}")
                    
                except Exception as e:
                    failed_files.append({
                        'file': str(template_file),
                        'error': str(e)
                    })
                    
                    individual_results.append({
                        'status': 'error',
                        'input_template': str(template_file),
                        'error_type': 'GenerationError',
                        'error_message': str(e)
                    })
                    
                    logger.error(f"Failed to process {template_file}: {e}")
            
            # Compile batch results
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            results = {
                'status': 'completed',
                'input_directory': input_dir,
                'output_directory': output_dir,
                'total_files': total_files,
                'successful_files': len(successful_files),
                'failed_files': len(failed_files),
                'success_rate': len(successful_files) / total_files if total_files > 0 else 0,
                'processing_time_seconds': processing_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'successful_files_list': successful_files,
                'failed_files_list': failed_files,
                'individual_results': individual_results,
                'generate_both_difficulties': generate_both_difficulties
            }
            
            logger.info(f"Batch processing completed: {len(successful_files)}/{total_files} successful")
            return results
            
        except GenerationError:
            raise
        except Exception as e:
            raise GenerationError(f"Failed to process directory {input_dir}: {e}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate comprehensive processing report.
        
        Args:
            results: Processing results from pipeline.
            
        Returns:
            Formatted markdown report.
        """
        try:
            report_lines = []
            
            # Header
            report_lines.append("# Stage 3 Generation Pipeline Report")
            report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # Summary
            report_lines.append("## Processing Summary")
            report_lines.append(f"- **Input Directory**: {results.get('input_directory', 'N/A')}")
            report_lines.append(f"- **Output Directory**: {results.get('output_directory', 'N/A')}")
            report_lines.append(f"- **Total Files**: {results.get('total_files', 0)}")
            report_lines.append(f"- **Successful**: {results.get('successful_files', 0)}")
            report_lines.append(f"- **Failed**: {results.get('failed_files', 0)}")
            report_lines.append(f"- **Success Rate**: {results.get('success_rate', 0):.1%}")
            report_lines.append(f"- **Processing Time**: {results.get('processing_time_seconds', 0):.2f} seconds")
            report_lines.append("")
            
            # Successful files
            if results.get('successful_files_list'):
                report_lines.append("## Successfully Processed Files")
                for file_path in results['successful_files_list']:
                    report_lines.append(f"- ✅ {Path(file_path).name}")
                report_lines.append("")
            
            # Failed files
            if results.get('failed_files_list'):
                report_lines.append("## Failed Files")
                for failed_file in results['failed_files_list']:
                    report_lines.append(f"- ❌ {Path(failed_file['file']).name}")
                    report_lines.append(f"  - Error: {failed_file['error']}")
                report_lines.append("")
            
            # Generation statistics
            if results.get('individual_results'):
                successful_results = [r for r in results['individual_results'] if r.get('status') == 'success']
                if successful_results:
                    total_generated = sum(r.get('generated_count', 0) for r in successful_results)
                    avg_processing_time = sum(r.get('processing_time_seconds', 0) for r in successful_results) / len(successful_results)
                    
                    report_lines.append("## Generation Statistics")
                    report_lines.append(f"- **Total JSON Files Generated**: {total_generated}")
                    report_lines.append(f"- **Average Processing Time**: {avg_processing_time:.2f} seconds per template")
                    report_lines.append(f"- **Both Difficulties Generated**: {results.get('generate_both_difficulties', False)}")
                    report_lines.append("")
            
            # Configuration
            report_lines.append("## Configuration")
            report_lines.append(f"- **Pipeline Version**: Stage 3 Generation v1.0")
            report_lines.append(f"- **Ari Persona Applied**: Yes")
            report_lines.append(f"- **JSON Structure Validation**: Enabled")
            report_lines.append("")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return f"# Stage 3 Generation Pipeline Report\n\nError generating report: {e}"


# Global convenience functions

def create_generation_pipeline(config: Optional[Dict[str, Any]] = None) -> GenerationPipeline:
    """
    Create a new generation pipeline instance.
    
    Args:
        config: Optional configuration dictionary.
        
    Returns:
        Initialized GenerationPipeline instance.
    """
    return GenerationPipeline(config)


def generate_from_template(template_path: str, output_dir: str, 
                          generate_both_difficulties: bool = True,
                          specific_difficulty: str = None,
                          custom_sequence: str = None,
                          progress_callback=None) -> Dict[str, Any]:
    """
    Generate supertask JSON from single template.
    
    Args:
        template_path: Path to template file.
        output_dir: Output directory path.
        generate_both_difficulties: Whether to generate both difficulty levels.
        progress_callback: Optional progress callback.
        
    Returns:
        Processing results dictionary.
    """
    pipeline = create_generation_pipeline()
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    # For backward compatibility with tests expecting a 3-arg call, only pass
    # optional params when explicitly provided.
    if specific_difficulty is None and custom_sequence is None:
        return pipeline.process_template(template_path, output_dir, generate_both_difficulties)
    return pipeline.process_template(
        template_path,
        output_dir,
        generate_both_difficulties,
        specific_difficulty,
        custom_sequence,
    )


def generate_from_directory(input_dir: str, output_dir: str,
                           generate_both_difficulties: bool = True,
                           progress_callback=None) -> Dict[str, Any]:
    """
    Generate supertask JSONs from directory of templates.
    
    Args:
        input_dir: Input directory path.
        output_dir: Output directory path.
        generate_both_difficulties: Whether to generate both difficulty levels.
        progress_callback: Optional progress callback.
        
    Returns:
        Processing results dictionary.
    """
    pipeline = create_generation_pipeline()
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    return pipeline.process_directory(input_dir, output_dir, generate_both_difficulties)


def generate_generation_report(results: Dict[str, Any]) -> str:
    """
    Generate processing report from results.
    
    Args:
        results: Processing results from generation pipeline.
        
    Returns:
        Formatted report string.
    """
    pipeline = create_generation_pipeline()
    return pipeline.generate_report(results) 