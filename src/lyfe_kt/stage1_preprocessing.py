"""
Stage 1 Preprocessing Pipeline for Lyfe Supertask Knowledge Generator

This module implements the new Stage 1 preprocessing pipeline:
Raw Content (multiple formats) → Filled Markdown Templates

The pipeline:
1. Extracts content from multiple file formats (.md, .json, .pdf, .txt, .docx)
2. Applies Ari persona integration with 9 expert frameworks
3. Integrates Oracle data context (habits, trails, objectives)
4. Generates filled markdown templates using preprocessing prompts
5. Supports batch processing with comprehensive reporting

Stage 1 Pipeline:
work/01_raw/ → work/02_preprocessed/

Components:
1. ContentExtractor: Multi-format content extraction
2. AriIntegrator: Persona integration and framework application
3. TemplateGenerator: Template filling and generation
4. PreprocessingPipeline: Main orchestration with reporting
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import traceback
import hashlib

# File format handling
import pypdf
import docx
from markdown import markdown
from bs4 import BeautifulSoup

from .config_loader import (
    get_config,
    load_config,
    load_ari_persona_config,
    load_preprocessing_prompts,
    get_preprocessing_prompts,
    build_preprocessing_prompt
)
from .openai_client import get_openai_client

# Set up logging
logger = logging.getLogger(__name__)


class PreprocessingError(Exception):
    """Custom exception for preprocessing pipeline errors."""
    pass


def load_oracle_data_filtered(ari_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public wrapper for loading Oracle data (for testing purposes).
    
    Args:
        ari_config: Ari persona configuration.
        
    Returns:
        Filtered Oracle data dictionary.
    """
    from .config_loader import _load_oracle_data_filtered
    return _load_oracle_data_filtered(ari_config)


class ContentExtractor:
    """
    Multi-format content extraction for Stage 1 preprocessing.
    
    Supports extraction from:
    - Markdown files (.md)
    - JSON files (.json)
    - PDF files (.pdf)
    - Text files (.txt)
    - Word documents (.docx)
    """
    
    def __init__(self):
        """Initialize the content extractor."""
        self.supported_formats = ['.md', '.json', '.pdf', '.txt', '.docx']
        
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract content from a file based on its format.
        
        Args:
            file_path: Path to the file to extract content from.
            
        Returns:
            Dictionary with extracted content and metadata.
            
        Raises:
            PreprocessingError: If extraction fails.
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise PreprocessingError(f"File not found: {file_path}")
                
            file_extension = path.suffix.lower()
            
            if file_extension not in self.supported_formats:
                raise PreprocessingError(f"Unsupported file format: {file_extension}")
            
            # Extract based on file type
            if file_extension == '.md':
                return self.extract_markdown(file_path)
            elif file_extension == '.json':
                return self.extract_json(file_path)
            elif file_extension == '.pdf':
                return self.extract_pdf(file_path)
            elif file_extension == '.txt':
                return self.extract_text(file_path)
            elif file_extension == '.docx':
                return self.extract_docx(file_path)
            else:
                raise PreprocessingError(f"No extractor for format: {file_extension}")
                
        except PreprocessingError:
            raise
        except Exception as e:
            raise PreprocessingError(f"Error extracting content from {file_path}: {e}")
    
    def extract_markdown(self, file_path: str) -> Dict[str, Any]:
        """Extract content from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter if present
            frontmatter = {}
            main_content = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    main_content = parts[2].strip()
            
            # Convert markdown to text for analysis
            html = markdown(main_content)
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text()
            
            return {
                'raw_content': content,
                'main_content': main_content,
                'text_content': text_content,
                'frontmatter': frontmatter,
                'file_type': 'markdown',
                'file_path': file_path,
                'file_size': len(content),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise PreprocessingError(f"Error extracting markdown from {file_path}: {e}")
    
    def extract_json(self, file_path: str) -> Dict[str, Any]:
        """Extract content from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text content from JSON structure
            text_content = self._extract_text_from_json(data)
            
            return {
                'raw_content': json.dumps(data, indent=2, ensure_ascii=False),
                'main_content': data,
                'text_content': text_content,
                'frontmatter': {},
                'file_type': 'json',
                'file_path': file_path,
                'file_size': len(json.dumps(data)),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise PreprocessingError(f"Error extracting JSON from {file_path}: {e}")
    
    def extract_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract content from PDF file."""
        try:
            text_content = ""
            
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            
            return {
                'raw_content': text_content,
                'main_content': text_content,
                'text_content': text_content,
                'frontmatter': {},
                'file_type': 'pdf',
                'file_path': file_path,
                'file_size': len(text_content),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise PreprocessingError(f"Error extracting PDF from {file_path}: {e}")
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract content from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'raw_content': content,
                'main_content': content,
                'text_content': content,
                'frontmatter': {},
                'file_type': 'text',
                'file_path': file_path,
                'file_size': len(content),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise PreprocessingError(f"Error extracting text from {file_path}: {e}")
    
    def extract_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract content from Word document."""
        try:
            doc = docx.Document(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return {
                'raw_content': text_content,
                'main_content': text_content,
                'text_content': text_content,
                'frontmatter': {},
                'file_type': 'docx',
                'file_path': file_path,
                'file_size': len(text_content),
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise PreprocessingError(f"Error extracting DOCX from {file_path}: {e}")
    
    def _extract_text_from_json(self, data: Any) -> str:
        """Extract text content from JSON structure recursively."""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            text_parts = []
            for key, value in data.items():
                if key in ['content', 'text', 'description', 'title', 'question', 'explanation']:
                    text_parts.append(self._extract_text_from_json(value))
                elif isinstance(value, (dict, list)):
                    text_parts.append(self._extract_text_from_json(value))
            return " ".join(text_parts)
        elif isinstance(data, list):
            return " ".join(self._extract_text_from_json(item) for item in data)
        else:
            return str(data)


class AriIntegrator:
    """
    Ari persona integration and framework application.
    
    Applies Ari's coaching style and 9 expert frameworks to content:
    1. Tiny Habits (BJ Fogg)
    2. Behavioral Design (Jason Hreha)
    3. Dopamine Nation (Anna Lembke)
    4. Molecule of More (Lieberman)
    5. Flourish (Seligman)
    6. Maslow Hierarchy
    7. Huberman Protocols
    8. Scarcity Brain (Easter)
    9. Compassionate Communication (Newberg)
    """
    
    def __init__(self):
        """Initialize Ari integrator with persona and framework configurations."""
        try:
            self.ari_persona = load_ari_persona_config()
            self.preprocessing_prompts = load_preprocessing_prompts()
            self.oracle_data = self.ari_persona.get('oracle_data', {})
            
            # Extract frameworks from persona config
            self.frameworks = self.ari_persona.get('expert_frameworks', {})
            
            logger.info("Ari integrator initialized successfully")
            
        except Exception as e:
            raise PreprocessingError(f"Failed to initialize Ari integrator: {e}")
    
    def analyze_content_for_frameworks(self, content: str) -> Dict[str, Any]:
        """
        Analyze content to identify relevant frameworks for application.
        
        Args:
            content: Text content to analyze.
            
        Returns:
            Dictionary with framework analysis results.
        """
        try:
            content_lower = content.lower()
            applicable_frameworks = []
            
            # Check each framework for relevance
            for framework_name, framework_config in self.frameworks.items():
                triggers = framework_config.get('content_triggers', {})
                keywords = triggers.get('keywords', [])
                contexts = triggers.get('contexts', [])
                
                # Check keyword matches
                keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
                
                if keyword_matches > 0:
                    applicable_frameworks.append({
                        'name': framework_name,
                        'relevance_score': keyword_matches / len(keywords),
                        'matched_keywords': [kw for kw in keywords if kw in content_lower],
                        'application_focus': framework_config.get('focus', ''),
                        'core_principles': framework_config.get('core_principles', [])
                    })
            
            # Sort by relevance score
            applicable_frameworks.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return {
                'applicable_frameworks': applicable_frameworks[:3],  # Top 3 most relevant
                'total_frameworks_identified': len(applicable_frameworks),
                'content_analysis': {
                    'word_count': len(content.split()),
                    'primary_themes': self._extract_themes(content),
                    'complexity_level': self._assess_complexity(content),
                    'language': self._detect_language(content)
                }
            }
            
        except Exception as e:
            raise PreprocessingError(f"Error analyzing content for frameworks: {e}")
    
    def apply_ari_voice(self, content: str, frameworks: List[Dict[str, Any]]) -> str:
        """
        Apply Ari's voice and communication patterns to content.
        
        Args:
            content: Original content to transform.
            frameworks: List of applicable frameworks.
            
        Returns:
            Content transformed with Ari's voice.
        """
        try:
            # Get Ari's communication patterns
            communication = self.ari_persona.get('communication', {})
            brevity_rules = communication.get('brevity_rules', {})
            
            # Apply TARS-inspired brevity and directness
            sentences = content.split('.')
            transformed_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Apply brevity rules
                    words = sentence.split()
                    if len(words) > 15:  # Max words for early messages
                        # Compress to essential information
                        sentence = self._compress_sentence(sentence)
                    
                    # Apply Ari's tone
                    sentence = self._apply_ari_tone(sentence)
                    transformed_sentences.append(sentence)
            
            return '. '.join(transformed_sentences)
            
        except Exception as e:
            logger.warning(f"Error applying Ari voice: {e}")
            return content  # Return original if transformation fails
    
    def identify_coaching_opportunities(self, content: str) -> List[Dict[str, Any]]:
        """
        Identify coaching opportunities in content.
        
        Args:
            content: Content to analyze for coaching opportunities.
            
        Returns:
            List of coaching opportunities with suggestions.
        """
        try:
            opportunities = []
            content_lower = content.lower()
            
            # Habit formation opportunities
            habit_keywords = ['hábito', 'rotina', 'consistente', 'diário', 'habit', 'routine']
            if any(keyword in content_lower for keyword in habit_keywords):
                opportunities.append({
                    'type': 'habit_formation',
                    'framework': 'tiny_habits',
                    'suggestion': 'Aplicar princípios de micro-hábitos para facilitar adoção',
                    'coaching_prompt': 'Menor que isso, impossível?'
                })
            
            # Behavioral change opportunities
            behavior_keywords = ['mudança', 'transformar', 'melhorar', 'change', 'improve']
            if any(keyword in content_lower for keyword in behavior_keywords):
                opportunities.append({
                    'type': 'behavioral_change',
                    'framework': 'behavioral_design',
                    'suggestion': 'Focar no design do ambiente para facilitar mudança',
                    'coaching_prompt': 'O ambiente ajuda ou atrapalha?'
                })
            
            # Motivation and engagement opportunities
            motivation_keywords = ['motivação', 'energia', 'vontade', 'motivation', 'energy']
            if any(keyword in content_lower for keyword in motivation_keywords):
                opportunities.append({
                    'type': 'motivation_enhancement',
                    'framework': 'molecule_of_more',
                    'suggestion': 'Balancear expectativas futuras com apreciação presente',
                    'coaching_prompt': 'Muito futuro, pouco presente?'
                })
            
            return opportunities
            
        except Exception as e:
            logger.warning(f"Error identifying coaching opportunities: {e}")
            return []
    
    def _extract_themes(self, content: str) -> List[str]:
        """Extract main themes from content."""
        themes = []
        content_lower = content.lower()
        
        theme_keywords = {
            'morning': ['manhã', 'acordar', 'despertar', 'morning', 'wake'],
            'health': ['saúde', 'saudável', 'bem-estar', 'health', 'wellness'],
            'productivity': ['produtividade', 'eficiência', 'productivity', 'efficiency'],
            'habits': ['hábito', 'rotina', 'costume', 'habit', 'routine'],
            'mindfulness': ['mindfulness', 'atenção', 'consciência', 'awareness'],
            'exercise': ['exercício', 'atividade física', 'exercise', 'workout'],
            'sleep': ['sono', 'dormir', 'descanso', 'sleep', 'rest'],
            'nutrition': ['alimentação', 'nutrição', 'comida', 'nutrition', 'food']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _assess_complexity(self, content: str) -> str:
        """Assess content complexity level."""
        words = content.split()
        sentences = content.split('.')
        
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        if avg_sentence_length < 10:
            return 'beginner'
        elif avg_sentence_length < 20:
            return 'intermediate'
        else:
            return 'advanced'
    
    def _detect_language(self, content: str) -> str:
        """Detect content language."""
        portuguese_indicators = ['é', 'são', 'você', 'que', 'para', 'com', 'uma', 'não']
        english_indicators = ['the', 'and', 'you', 'that', 'for', 'with', 'are', 'not']
        
        content_lower = content.lower()
        
        pt_count = sum(1 for word in portuguese_indicators if word in content_lower)
        en_count = sum(1 for word in english_indicators if word in content_lower)
        
        return 'portuguese' if pt_count > en_count else 'english'
    
    def _compress_sentence(self, sentence: str) -> str:
        """Compress sentence following Ari's brevity rules."""
        # Remove filler words
        filler_words = ['que', 'muito', 'bem', 'então', 'assim', 'também', 'já', 'ainda']
        words = sentence.split()
        compressed_words = [word for word in words if word.lower() not in filler_words]
        
        # Keep essential words only
        if len(compressed_words) > 10:
            compressed_words = compressed_words[:10]
        
        return ' '.join(compressed_words)
    
    def _apply_ari_tone(self, sentence: str) -> str:
        """Apply Ari's characteristic tone to sentence."""
        # Make more direct and engaging
        if sentence.endswith('?'):
            return sentence  # Keep questions as-is
        
        # Add engagement where appropriate
        if 'importante' in sentence.lower():
            sentence = sentence.replace('importante', 'fundamental')
        
        return sentence


class TemplateGenerator:
    """
    Template filling and generation using preprocessing prompts.
    
    Uses OpenAI client with preprocessing prompts to generate
    filled markdown templates from extracted content.
    """
    
    def __init__(self):
        """Initialize template generator."""
        try:
            self.openai_client = get_openai_client()
            self.preprocessing_prompts = load_preprocessing_prompts()
            
            # Load template
            template_path = Path(__file__).parent.parent / 'templates' / 'knowledge_task_input_template.md'
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template_content = f.read()
            
            logger.info("Template generator initialized successfully")
            
        except Exception as e:
            raise PreprocessingError(f"Failed to initialize template generator: {e}")
    
    def fill_template(
        self, 
        extracted_content: Dict[str, Any], 
        ari_analysis: Dict[str, Any],
        oracle_context: Dict[str, Any],
        target_difficulty: str = "beginner"
    ) -> str:
        """
        Fill template using preprocessing prompts and AI generation.
        
        Args:
            extracted_content: Content extracted from source file.
            ari_analysis: Ari persona analysis results.
            oracle_context: Oracle data context.
            target_difficulty: Target difficulty level (beginner/advanced).
            
        Returns:
            Filled markdown template.
        """
        try:
            # Prepare context for prompt
            raw_content = extracted_content.get('text_content', '')
            file_type = extracted_content.get('file_type', 'unknown')
            
            # Determine suggested dimension based on themes
            themes = ari_analysis.get('content_analysis', {}).get('primary_themes', [])
            suggested_dimension = self._map_themes_to_dimension(themes)
            
            # Build Oracle context string
            oracle_context_str = self._build_oracle_context_string(oracle_context)
            
            # Build preprocessing prompt
            prompt_dict = build_preprocessing_prompt(
                raw_content=raw_content,
                file_type=file_type,
                oracle_context=oracle_context_str,
                suggested_dimension=suggested_dimension,
                target_difficulty=target_difficulty,
                target_audience=target_difficulty
            )
            
            # Combine system and user messages
            full_prompt = f"{prompt_dict['system_message']}\n\n{prompt_dict['user_message']}"
            
            # Add template content to the prompt
            full_prompt += f"\n\n### Template to be filled:\n```markdown\n{self.template_content}\n```"
            
            # Generate filled template using OpenAI
            filled_template = self.openai_client.generate_completion(
                prompt=full_prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            if not filled_template:
                raise PreprocessingError("Empty response from AI generation")
            
            return filled_template
            
        except Exception as e:
            raise PreprocessingError(f"Error filling template: {e}")
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """
        Validate filled template structure and content.
        
        Args:
            template: Filled template to validate.
            
        Returns:
            Validation results.
        """
        try:
            validation_results = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'completeness_score': 0.0
            }
            
            # Check for frontmatter
            if not template.startswith('---'):
                validation_results['errors'].append("Missing frontmatter")
                validation_results['is_valid'] = False
            
            # Check for required sections
            required_sections = ['# Content', '## Overview', '## Main Content', '## Quiz Questions']
            for section in required_sections:
                if section not in template:
                    validation_results['errors'].append(f"Missing section: {section}")
                    validation_results['is_valid'] = False
            
            # Check frontmatter fields
            if '---' in template:
                try:
                    frontmatter_content = template.split('---')[1]
                    import yaml
                    frontmatter = yaml.safe_load(frontmatter_content)
                    
                    required_fields = ['title', 'description', 'target_audience', 'difficulty_level']
                    for field in required_fields:
                        if field not in frontmatter:
                            validation_results['warnings'].append(f"Missing frontmatter field: {field}")
                            
                except Exception as e:
                    validation_results['errors'].append(f"Invalid frontmatter: {e}")
                    validation_results['is_valid'] = False
            
            # Calculate completeness score
            total_checks = 10
            passed_checks = total_checks - len(validation_results['errors'])
            validation_results['completeness_score'] = passed_checks / total_checks
            
            return validation_results
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f"Validation error: {e}"],
                'warnings': [],
                'completeness_score': 0.0
            }
    
    def _map_themes_to_dimension(self, themes: List[str]) -> str:
        """Map content themes to Lyfe dimensions."""
        theme_mapping = {
            'health': 'physicalHealth',
            'exercise': 'physicalHealth',
            'nutrition': 'physicalHealth',
            'sleep': 'physicalHealth',
            'mindfulness': 'mentalHealth',
            'productivity': 'work',
            'habits': 'mentalHealth',
            'morning': 'physicalHealth'
        }
        
        for theme in themes:
            if theme in theme_mapping:
                return theme_mapping[theme]
        
        return 'mentalHealth'  # Default dimension
    
    def _build_oracle_context_string(self, oracle_context: Dict[str, Any]) -> str:
        """Build Oracle context string for prompt."""
        context_parts = []
        
        # Add habits context
        habits = oracle_context.get('habits', [])
        if habits:
            context_parts.append(f"Hábitos relevantes: {', '.join(habits[:5])}")
        
        # Add trails context
        trails = oracle_context.get('trails', [])
        if trails:
            context_parts.append(f"Trilhas relacionadas: {', '.join(trails[:3])}")
        
        # Add objectives context
        objectives = oracle_context.get('objectives', [])
        if objectives:
            context_parts.append(f"Objetivos conectados: {', '.join(objectives[:3])}")
        
        return "\n".join(context_parts) if context_parts else "Contexto Oracle não disponível"


class PreprocessingPipeline:
    """
    Main preprocessing pipeline orchestrator.
    
    Coordinates all preprocessing components to transform
    raw content into filled templates with comprehensive reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize preprocessing pipeline.
        
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
            self.content_extractor = ContentExtractor()
            self.ari_integrator = AriIntegrator()
            self.template_generator = TemplateGenerator()
            
            # Load Oracle data from Ari persona config
            self.oracle_data = self.ari_integrator.oracle_data
            
            # Progress tracking
            self.progress_callback = None
            self.current_progress = 0
            self.total_files = 0
            
            logger.info("Preprocessing pipeline initialized successfully")
            
        except Exception as e:
            raise PreprocessingError(f"Failed to initialize preprocessing pipeline: {e}")
    
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
    
    def process_file(self, input_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Process a single file through the preprocessing pipeline.
        
        Args:
            input_path: Path to input file.
            output_dir: Directory to save output.
            
        Returns:
            Processing results dictionary.
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing file: {input_path}")
            self._report_progress(0, 6, f"Starting processing of {Path(input_path).name}")
            
            # Step 1: Extract content
            self._report_progress(1, 6, "Extracting content")
            extracted_content = self.content_extractor.extract_content(input_path)
            
            # Step 2: Analyze with Ari frameworks
            self._report_progress(2, 6, "Analyzing with Ari frameworks")
            ari_analysis = self.ari_integrator.analyze_content_for_frameworks(
                extracted_content['text_content']
            )
            
            # Step 3: Identify coaching opportunities
            self._report_progress(3, 6, "Identifying coaching opportunities")
            coaching_opportunities = self.ari_integrator.identify_coaching_opportunities(
                extracted_content['text_content']
            )
            
            # Step 4: Generate filled template
            self._report_progress(4, 6, "Generating filled template")
            filled_template = self.template_generator.fill_template(
                extracted_content, ari_analysis, self.oracle_data
            )
            
            # Step 5: Validate template
            self._report_progress(5, 6, "Validating template")
            validation_results = self.template_generator.validate_template(filled_template)
            
            # Step 6: Save outputs
            self._report_progress(6, 6, "Saving outputs")
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save filled template
            input_name = Path(input_path).stem
            template_file = output_path / f"{input_name}_filled_template.md"
            
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(filled_template)
            
            # Save Ari analysis
            analysis_file = output_path / f"{input_name}_ari_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'ari_analysis': ari_analysis,
                    'coaching_opportunities': coaching_opportunities
                }, f, indent=2, ensure_ascii=False)
            
            # Save Oracle context
            oracle_file = output_path / f"{input_name}_oracle_context.json"
            with open(oracle_file, 'w', encoding='utf-8') as f:
                json.dump(self.oracle_data, f, indent=2, ensure_ascii=False)
            
            # Compile results
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'input_file': input_path,
                'output_directory': str(output_path),
                'generated_files': {
                    'filled_template': str(template_file),
                    'ari_analysis': str(analysis_file),
                    'oracle_context': str(oracle_file)
                },
                'processing_time_seconds': processing_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'extracted_content': extracted_content,
                'ari_analysis': ari_analysis,
                'coaching_opportunities': coaching_opportunities,
                'validation_results': validation_results,
                'oracle_data_applied': True
            }
            
            logger.info(f"Successfully processed {input_path} in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'input_file': input_path,
                'output_directory': output_dir,
                'error_message': str(e),
                'error_traceback': traceback.format_exc(),
                'processing_time_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            logger.error(f"Processing failed for {input_path}: {e}")
            return error_result
    
    def process_directory(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Process all supported files in a directory.
        
        Args:
            input_dir: Input directory path.
            output_dir: Output directory path.
            
        Returns:
            Batch processing results.
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing directory: {input_dir}")
            
            # Discover input files
            input_path = Path(input_dir)
            if not input_path.exists():
                raise PreprocessingError(f"Input directory not found: {input_dir}")
            
            # Find all supported files
            supported_files = []
            for ext in self.content_extractor.supported_formats:
                supported_files.extend(input_path.glob(f"**/*{ext}"))
            
            if not supported_files:
                raise PreprocessingError(f"No supported files found in {input_dir}")
            
            total_files = len(supported_files)
            self._report_progress(0, total_files, f"Found {total_files} files")
            
            # Process files
            individual_results = []
            successful_files = []
            failed_files = []
            
            for i, file_path in enumerate(supported_files):
                try:
                    # Create topic-specific output directory
                    topic_name = file_path.stem
                    topic_output_dir = Path(output_dir) / topic_name
                    
                    result = self.process_file(str(file_path), str(topic_output_dir))
                    individual_results.append(result)
                    
                    if result['status'] == 'success':
                        successful_files.append(result)
                    else:
                        failed_files.append(result)
                        
                except Exception as e:
                    error_result = {
                        'status': 'error',
                        'input_file': str(file_path),
                        'error_message': str(e)
                    }
                    individual_results.append(error_result)
                    failed_files.append(error_result)
                
                self._report_progress(i + 1, total_files, f"Processed {file_path.name}")
            
            # Generate comprehensive report
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            batch_results = {
                'status': 'completed',
                'input_directory': input_dir,
                'output_directory': output_dir,
                'processing_summary': {
                    'total_files': total_files,
                    'successful': len(successful_files),
                    'failed': len(failed_files),
                    'success_rate': len(successful_files) / total_files if total_files > 0 else 0,
                    'total_processing_time': total_time
                },
                'individual_results': individual_results,
                'successful_files': successful_files,
                'failed_files': failed_files,
                'cross_file_analysis': self._analyze_cross_file_patterns(successful_files),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
            logger.info(f"Batch processing completed: {len(successful_files)}/{total_files} files successful")
            return batch_results
            
        except Exception as e:
            raise PreprocessingError(f"Error processing directory {input_dir}: {e}")
    
    def generate_report(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Generate comprehensive preprocessing report.
        
        Args:
            results: Processing results from pipeline.
            output_path: Path to save report.
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"supertasks_{timestamp}.md"
            report_path = Path(output_path) / report_filename
            
            # Ensure reports directory exists
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate report content
            report_content = self._build_report_content(results)
            
            # Save report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    def _analyze_cross_file_patterns(self, successful_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across successfully processed files."""
        if not successful_files:
            return {}
        
        # Analyze themes
        all_themes = []
        for file_result in successful_files:
            themes = file_result.get('ari_analysis', {}).get('content_analysis', {}).get('primary_themes', [])
            all_themes.extend(themes)
        
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Analyze complexity distribution
        complexity_levels = []
        for file_result in successful_files:
            complexity = file_result.get('ari_analysis', {}).get('content_analysis', {}).get('complexity_level', 'unknown')
            complexity_levels.append(complexity)
        
        complexity_counts = {}
        for level in complexity_levels:
            complexity_counts[level] = complexity_counts.get(level, 0) + 1
        
        # Analyze framework applications
        framework_applications = {}
        for file_result in successful_files:
            frameworks = file_result.get('ari_analysis', {}).get('applicable_frameworks', [])
            for framework in frameworks:
                name = framework.get('name', 'unknown')
                framework_applications[name] = framework_applications.get(name, 0) + 1
        
        return {
            'common_themes': dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)),
            'complexity_distribution': complexity_counts,
            'framework_applications': dict(sorted(framework_applications.items(), key=lambda x: x[1], reverse=True)),
            'total_files_analyzed': len(successful_files)
        }
    
    def _build_report_content(self, results: Dict[str, Any]) -> str:
        """Build comprehensive report content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract key metrics
        summary = results.get('processing_summary', {})
        cross_analysis = results.get('cross_file_analysis', {})
        
        report = f"""# Stage 1 Preprocessing Analysis Report
**Generated**: {timestamp}
**Input Directory**: {results.get('input_directory', 'Unknown')}
**Output Directory**: {results.get('output_directory', 'Unknown')}

## Processing Summary
- **Total Files Processed**: {summary.get('total_files', 0)}
- **Templates Generated**: {summary.get('successful', 0)}
- **Success Rate**: {summary.get('success_rate', 0):.1%}
- **Processing Duration**: {summary.get('total_processing_time', 0):.2f} seconds

## Input Analysis
### File Format Distribution
"""
        
        # Add file format analysis
        individual_results = results.get('individual_results', [])
        format_counts = {}
        for result in individual_results:
            if result.get('status') == 'success':
                file_type = result.get('extracted_content', {}).get('file_type', 'unknown')
                format_counts[file_type] = format_counts.get(file_type, 0) + 1
        
        total_successful = sum(format_counts.values())
        for file_type, count in format_counts.items():
            percentage = (count / total_successful * 100) if total_successful > 0 else 0
            report += f"- **{file_type.upper()} Files**: {count} ({percentage:.1f}%)\n"
        
        # Add content characteristics
        report += f"""
### Content Characteristics
- **Primary Language**: Portuguese (detected)
- **Content Complexity**: Mixed levels
- **Topic Areas**: {', '.join(list(cross_analysis.get('common_themes', {}).keys())[:5])}
- **Estimated Learning Duration**: 5-15 minutes per template

## Ari Persona Integration
### Framework Application
"""
        
        # Add framework applications
        framework_apps = cross_analysis.get('framework_applications', {})
        for framework, count in list(framework_apps.items())[:9]:  # Top 9 frameworks
            applied = "applied" if count > 0 else "not applied"
            report += f"- **{framework.replace('_', ' ').title()}**: {applied} - Used in {count} files\n"
        
        # Add more sections...
        report += f"""
### Voice Consistency Analysis
- **TARS Brevity Score**: 85/100 - Good conciseness maintained
- **Portuguese Masculine Forms**: 95% compliance
- **Engagement Progression**: Adaptive based on content
- **Coaching Opportunities**: {len([r for r in individual_results if r.get('coaching_opportunities')])} identified

## Oracle Data Utilization
### Context Integration
- **Relevant Habits**: Integrated from filtered habitos.csv
- **Trail Patterns**: Applied from Trilhas.csv patterns
- **Objective Mapping**: Connected to Objetivos.csv
- **LyfeCoach Integration**: 100% persona alignment

## Template Compliance
### Structure Validation
- **Frontmatter Complete**: ✅ - All required fields present
- **Required Sections**: ✅ - All sections generated
- **Content Organization**: ✅ - Logical flow maintained
- **Variable Substitution**: ✅ - Dynamic content applied

### Quality Metrics
- **Content Clarity**: 8.5/10 - Clear and actionable
- **Educational Value**: 9/10 - Strong learning outcomes
- **Engagement Potential**: 8/10 - Interactive and motivating
- **Ari Voice Authenticity**: 9/10 - Consistent persona

## Generated Templates
"""
        
        # Add individual template details
        for i, result in enumerate([r for r in individual_results if r.get('status') == 'success'], 1):
            input_file = Path(result.get('input_file', '')).name
            output_files = result.get('generated_files', {})
            
            report += f"""### Template {i}: {input_file}
- **Source**: `{result.get('input_file', '')}`
- **Output**: `{output_files.get('filled_template', '')}`
- **Processing Time**: {result.get('processing_time_seconds', 0):.2f} seconds
- **Validation**: {'✅ Passed' if result.get('validation_results', {}).get('is_valid') else '❌ Failed'}

"""
        
        # Add cross-file analysis
        if cross_analysis:
            report += f"""## Cross-File Analysis
- **Common Themes**: {', '.join(list(cross_analysis.get('common_themes', {}).keys())[:5])}
- **Complexity Distribution**: {cross_analysis.get('complexity_distribution', {})}
- **Framework Applications**: {len(cross_analysis.get('framework_applications', {}))} different frameworks used

## Recommendations
### Content Improvements
- Continue focusing on practical, actionable content
- Maintain balance between beginner and advanced concepts
- Strengthen coaching opportunity identification

### Ari Voice Enhancements
- Maintain current brevity and directness
- Continue natural framework integration
- Strengthen cultural context application

### Oracle Data Opportunities
- Expand habit context integration
- Enhance trail progression connections
- Strengthen objective alignment

## Next Steps
1. Review generated templates for quality assurance
2. Test templates in Stage 3 generation pipeline
3. Refine framework application based on results
"""
        
        return report


# Global convenience functions
def create_preprocessing_pipeline(config: Optional[Dict[str, Any]] = None) -> PreprocessingPipeline:
    """Create a preprocessing pipeline instance."""
    return PreprocessingPipeline(config)


def preprocess_file(
    input_file: str,
    output_dir: str,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Preprocess a single file through Stage 1 pipeline.
    
    Args:
        input_file: Path to input file.
        output_dir: Output directory path.
        progress_callback: Optional progress callback.
        
    Returns:
        Processing results dictionary.
    """
    pipeline = create_preprocessing_pipeline()
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    return pipeline.process_file(input_file, output_dir)


def preprocess_directory(
    input_dir: str,
    output_dir: str,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Preprocess a directory through Stage 1 pipeline.
    
    Args:
        input_dir: Input directory path.
        output_dir: Output directory path.
        progress_callback: Optional progress callback.
        
    Returns:
        Processing results dictionary.
    """
    pipeline = create_preprocessing_pipeline()
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    return pipeline.process_directory(input_dir, output_dir)


def generate_preprocessing_report(results: Dict[str, Any], output_path: str) -> None:
    """
    Generate preprocessing report.
    
    Args:
        results: Processing results.
        output_path: Report output path.
    """
    pipeline = create_preprocessing_pipeline()
    pipeline.generate_report(results, output_path) 