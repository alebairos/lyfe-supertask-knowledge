"""
Progressive Learning Narrative System

This module implements a system for generating multiple interconnected supertasks
that form a complete learning journey from foundation to mastery.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from .content_enrichment import ContentEnrichmentEngine, SourceInsight

logger = logging.getLogger(__name__)


class LearningLevel(Enum):
    """Learning progression levels."""
    FOUNDATION = "foundation"
    APPLICATION = "application" 
    MASTERY = "mastery"


@dataclass
class NarrativeThread:
    """Represents the connecting story elements across learning levels."""
    journey_theme: str
    opening_hook: str
    level_transitions: Dict[str, str]
    progress_markers: Dict[str, str]
    closing_reflection: str


@dataclass
class LevelConfig:
    """Configuration for a specific learning level."""
    level: LearningLevel
    difficulty: str
    sequence: str
    duration_range: Tuple[int, int]
    focus_areas: List[str]
    content_characteristics: List[str]


class ProgressiveContentAnalyzer:
    """Analyzes source content and extracts insights by learning level."""
    
    def __init__(self, enrichment_engine: ContentEnrichmentEngine):
        self.enrichment_engine = enrichment_engine
        
    def extract_learning_levels(self, source_material: str) -> Dict[str, List[SourceInsight]]:
        """Extract insights categorized by learning level."""
        try:
            # Extract comprehensive insights from source
            logger.info("Extracting insights for progressive learning levels")
            all_insights = self.enrichment_engine.extract_source_insights(source_material, max_insights=12)
            
            # Categorize insights by learning level
            foundation_insights = self._categorize_foundation_insights(all_insights)
            application_insights = self._categorize_application_insights(all_insights)
            mastery_insights = self._categorize_mastery_insights(all_insights)
            
            logger.info(f"Categorized insights: {len(foundation_insights)} foundation, "
                       f"{len(application_insights)} application, {len(mastery_insights)} mastery")
            
            return {
                'foundation': foundation_insights[:4],  # Limit for focused learning
                'application': application_insights[:4],
                'mastery': mastery_insights[:4]
            }
            
        except Exception as e:
            logger.error(f"Failed to extract learning levels: {e}")
            return self._create_fallback_insights(source_material)
    
    def _categorize_foundation_insights(self, insights: List[SourceInsight]) -> List[SourceInsight]:
        """Select insights appropriate for foundation level."""
        foundation_keywords = ['basic', 'fundamental', 'definition', 'what is', 'core concept', 
                             'introduction', 'essential', 'foundation', 'simple', 'beginning']
        
        foundation_insights = []
        for insight in insights:
            insight_text = f"{insight.insight} {insight.application}".lower()
            if any(keyword in insight_text for keyword in foundation_keywords):
                foundation_insights.append(insight)
        
        # If not enough keyword matches, select insights with simpler language
        if len(foundation_insights) < 3:
            remaining = [ins for ins in insights if ins not in foundation_insights]
            simple_insights = sorted(remaining, key=lambda x: len(x.insight.split()))[:4]
            foundation_insights.extend(simple_insights)
            
        return foundation_insights[:4]
    
    def _categorize_application_insights(self, insights: List[SourceInsight]) -> List[SourceInsight]:
        """Select insights appropriate for application level."""
        application_keywords = ['how to', 'apply', 'practice', 'implement', 'use', 'daily',
                               'real-world', 'example', 'scenario', 'practical', 'action']
        
        application_insights = []
        for insight in insights:
            insight_text = f"{insight.insight} {insight.application}".lower()
            if any(keyword in insight_text for keyword in application_keywords):
                application_insights.append(insight)
        
        # Prioritize insights with strong application components
        if len(application_insights) < 3:
            remaining = [ins for ins in insights if ins not in application_insights]
            practical_insights = [ins for ins in remaining if len(ins.application) > 50]
            application_insights.extend(practical_insights[:4])
            
        return application_insights[:4]
    
    def _categorize_mastery_insights(self, insights: List[SourceInsight]) -> List[SourceInsight]:
        """Select insights appropriate for mastery level."""
        mastery_keywords = ['advanced', 'complex', 'integrate', 'nuance', 'sophisticated',
                           'expert', 'deep', 'comprehensive', 'synthesis', 'mastery']
        
        mastery_insights = []
        for insight in insights:
            insight_text = f"{insight.insight} {insight.application}".lower()
            if any(keyword in insight_text for keyword in mastery_keywords):
                mastery_insights.append(insight)
        
        # Select insights with longer, more complex descriptions
        if len(mastery_insights) < 3:
            remaining = [ins for ins in insights if ins not in mastery_insights]
            complex_insights = sorted(remaining, key=lambda x: len(x.insight), reverse=True)[:4]
            mastery_insights.extend(complex_insights)
            
        return mastery_insights[:4]
    
    def _create_fallback_insights(self, source_material: str) -> Dict[str, List[SourceInsight]]:
        """Create basic insights when extraction fails."""
        logger.warning("Using fallback insights for progressive learning")
        
        # Create simple fallback insights
        fallback_insight = SourceInsight(
            insight="Conceitos fundamentais são importantes para o aprendizado",
            application="Pratique diariamente para desenvolver compreensão",
            example="Comece com pequenos passos e construa conhecimento gradualmente",
            category="foundation"
        )
        
        return {
            'foundation': [fallback_insight],
            'application': [fallback_insight],
            'mastery': [fallback_insight]
        }


class LevelSpecificGenerator:
    """Generates content tailored to specific learning levels."""
    
    def __init__(self, enrichment_engine: ContentEnrichmentEngine):
        self.enrichment_engine = enrichment_engine
        self.level_configs = self._initialize_level_configs()
    
    def _initialize_level_configs(self) -> Dict[str, LevelConfig]:
        """Initialize configuration for each learning level."""
        return {
            'foundation': LevelConfig(
                level=LearningLevel.FOUNDATION,
                difficulty="beginner",
                sequence="content → quiz → content → quote → content → quiz",
                duration_range=(180, 300),
                focus_areas=["definitions", "core concepts", "basic understanding"],
                content_characteristics=["simple language", "clear examples", "foundational knowledge"]
            ),
            'application': LevelConfig(
                level=LearningLevel.APPLICATION,
                difficulty="intermediate",
                sequence="quote → content → quiz → content → quiz → quote",
                duration_range=(300, 420),
                focus_areas=["practical use", "real scenarios", "implementation"],
                content_characteristics=["action-oriented", "practical examples", "how-to focus"]
            ),
            'mastery': LevelConfig(
                level=LearningLevel.MASTERY,
                difficulty="advanced",
                sequence="content → content → quiz → quote → content → quiz",
                duration_range=(420, 600),
                focus_areas=["integration", "nuances", "complex scenarios"],
                content_characteristics=["sophisticated analysis", "edge cases", "deep connections"]
            )
        }
    
    def generate_level_content(self, level: str, insights: List[SourceInsight], 
                             title: str) -> List[Dict[str, Any]]:
        """Generate content items for a specific learning level."""
        try:
            config = self.level_configs.get(level, self.level_configs['foundation'])
            logger.info(f"Generating {level} level content with {len(insights)} insights")
            
            content_items = []
            for i, insight in enumerate(insights[:3]):  # Limit to 3 content items per level
                try:
                    content_text = self.enrichment_engine.generate_source_driven_content(
                        [insight], config.difficulty, title
                    )
                    
                    if content_text and len(content_text) >= 50:
                        content_item = {
                            "type": "content",
                            "content": content_text,
                            "author": "Ari"
                        }
                        
                        # Add level-appropriate tips
                        if insight.application:
                            tip_text = self._create_level_appropriate_tip(insight.application, level)
                            if tip_text:
                                content_item["tips"] = [tip_text]
                        
                        content_items.append(content_item)
                        logger.info(f"Generated {level} content item {i+1}: {len(content_text)} chars")
                        
                except Exception as e:
                    logger.warning(f"Failed to generate {level} content item {i+1}: {e}")
            
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to generate {level} level content: {e}")
            return self._create_fallback_content(level)
    
    def generate_level_quizzes(self, level: str, insights: List[SourceInsight], 
                              title: str) -> List[Dict[str, Any]]:
        """Generate quiz items for a specific learning level."""
        try:
            config = self.level_configs.get(level, self.level_configs['foundation'])
            logger.info(f"Generating {level} level quizzes")
            
            quiz_questions = self.enrichment_engine.generate_source_driven_questions(
                insights, config.difficulty, title, num_questions=3
            )
            
            quiz_items = []
            for i, quiz_data in enumerate(quiz_questions):
                try:
                    # Enhance questions with level-appropriate complexity
                    enhanced_question = self._enhance_question_for_level(
                        quiz_data['question'], level
                    )
                    
                    quiz_item = {
                        "type": "quiz",
                        "question": enhanced_question,
                        "options": quiz_data['options'],
                        "correctAnswer": quiz_data['correctAnswer'],
                        "explanation": quiz_data['explanation']
                    }
                    
                    quiz_items.append(quiz_item)
                    logger.info(f"Generated {level} quiz item {i+1}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process {level} quiz item {i+1}: {e}")
            
            return quiz_items
            
        except Exception as e:
            logger.error(f"Failed to generate {level} level quizzes: {e}")
            return self._create_fallback_quiz(level)
    
    def _create_level_appropriate_tip(self, application: str, level: str) -> Optional[str]:
        """Create tips appropriate for the learning level."""
        try:
            if level == 'foundation':
                tip_prefix = "💡 Dica básica: "
            elif level == 'application':
                tip_prefix = "🛠️ Na prática: "
            else:  # mastery
                tip_prefix = "🎓 Avançado: "
            
            tip_text = f"{tip_prefix}{application[:100]}"
            if len(tip_text) > 150:
                tip_text = tip_text[:145] + "..."
            
            return tip_text if len(tip_text) >= 20 else None
            
        except Exception as e:
            logger.warning(f"Failed to create {level} tip: {e}")
            return None
    
    def _enhance_question_for_level(self, question: str, level: str) -> str:
        """Enhance question complexity based on learning level."""
        try:
            if level == 'foundation':
                # Keep questions simple and direct
                if len(question) > 100:
                    question = question[:95] + "...?"
            elif level == 'application':
                # Add practical context if missing
                if "como" not in question.lower() and "aplicar" not in question.lower():
                    question = f"Como aplicar: {question}"
            else:  # mastery
                # Add complexity indicators if appropriate
                if len(question) < 50:
                    question = f"Em cenários complexos, {question.lower()}"
            
            # Ensure mobile compliance (15-120 chars)
            if len(question) > 120:
                question = question[:115] + "...?"
            elif len(question) < 15:
                question = f"Como entender {question.lower()}?"
            
            return question
            
        except Exception as e:
            logger.warning(f"Failed to enhance question for {level}: {e}")
            return question
    
    def _create_fallback_content(self, level: str) -> List[Dict[str, Any]]:
        """Create fallback content for a level."""
        fallback_content = {
            "type": "content",
            "content": f"Conceitos de {level} são fundamentais para o desenvolvimento pessoal e profissional.",
            "author": "Ari"
        }
        return [fallback_content]
    
    def _create_fallback_quiz(self, level: str) -> List[Dict[str, Any]]:
        """Create fallback quiz for a level."""
        fallback_quiz = {
            "type": "quiz",
            "question": f"Como aplicar conceitos de {level}?",
            "options": ["Praticar diariamente", "Ignorar", "Esperar", "Teorizar apenas"],
            "correctAnswer": 0,
            "explanation": f"A prática diária é essencial para dominar conceitos de {level}."
        }
        return [fallback_quiz]


class StoryThreadGenerator:
    """Generates narrative elements that connect learning levels."""
    
    def generate_narrative_thread(self, theme: str, levels: List[str]) -> NarrativeThread:
        """Generate a complete narrative thread for the learning journey."""
        try:
            logger.info(f"Generating narrative thread for theme: {theme}")
            
            journey_theme = theme or "Jornada de Aprendizado"
            
            opening_hook = self._generate_opening_hook(journey_theme, len(levels))
            level_transitions = self._generate_level_transitions(levels)
            progress_markers = self._generate_progress_markers(levels)
            closing_reflection = self._generate_closing_reflection(journey_theme)
            
            return NarrativeThread(
                journey_theme=journey_theme,
                opening_hook=opening_hook,
                level_transitions=level_transitions,
                progress_markers=progress_markers,
                closing_reflection=closing_reflection
            )
            
        except Exception as e:
            logger.error(f"Failed to generate narrative thread: {e}")
            return self._create_fallback_narrative(theme, levels)
    
    def _generate_opening_hook(self, theme: str, total_levels: int) -> str:
        """Create an engaging opening for the learning journey."""
        hooks = [
            f"Bem-vindo à sua jornada de {theme}! Em {total_levels} etapas, você desenvolverá compreensão completa.",
            f"Prepare-se para uma transformação em {theme} através de {total_levels} níveis progressivos.",
            f"Sua jornada de descoberta em {theme} começa agora, com {total_levels} etapas cuidadosamente estruturadas."
        ]
        return hooks[hash(theme) % len(hooks)]
    
    def _generate_level_transitions(self, levels: List[str]) -> Dict[str, str]:
        """Generate smooth transitions between levels."""
        transitions = {}
        
        transition_templates = {
            ('foundation', 'application'): "Agora que você domina os conceitos básicos, vamos aplicá-los na prática.",
            ('application', 'mastery'): "Com a prática em mãos, é hora de explorar nuances e cenários complexos.",
            ('foundation', 'mastery'): "Construindo sobre sua base sólida, vamos mergulhar em aspectos avançados."
        }
        
        for i in range(len(levels) - 1):
            current_level = levels[i]
            next_level = levels[i + 1]
            transition_key = f"{current_level}_to_{next_level}"
            
            template_key = (current_level, next_level)
            if template_key in transition_templates:
                transitions[transition_key] = transition_templates[template_key]
            else:
                transitions[transition_key] = f"Progredindo de {current_level} para {next_level}..."
        
        return transitions
    
    def _generate_progress_markers(self, levels: List[str]) -> Dict[str, str]:
        """Generate progress indicators for each level."""
        progress_markers = {}
        
        marker_templates = {
            'foundation': "🌱 Construindo sua base de conhecimento...",
            'application': "🛠️ Aplicando conhecimento na prática...", 
            'mastery': "🎓 Dominando conceitos avançados..."
        }
        
        for i, level in enumerate(levels):
            progress_text = marker_templates.get(level, f"📚 Nível {i+1}: {level}")
            progress_markers[level] = f"{progress_text} ({i+1}/{len(levels)})"
        
        return progress_markers
    
    def _generate_closing_reflection(self, theme: str) -> str:
        """Generate a closing reflection for the journey."""
        reflections = [
            f"Parabéns! Você completou sua jornada em {theme}. Continue aplicando estes insights em sua vida.",
            f"Sua transformação em {theme} está apenas começando. Use este conhecimento para crescer continuamente.",
            f"Com esta base sólida em {theme}, você está preparado para enfrentar novos desafios e oportunidades."
        ]
        return reflections[hash(theme) % len(reflections)]
    
    def _create_fallback_narrative(self, theme: str, levels: List[str]) -> NarrativeThread:
        """Create a basic narrative thread when generation fails."""
        return NarrativeThread(
            journey_theme=theme or "Aprendizado Progressivo",
            opening_hook="Bem-vindo à sua jornada de aprendizado!",
            level_transitions={f"{levels[i]}_to_{levels[i+1]}": "Progredindo para o próximo nível..." 
                             for i in range(len(levels)-1)},
            progress_markers={level: f"Nível {i+1}: {level}" for i, level in enumerate(levels)},
            closing_reflection="Parabéns por completar sua jornada de aprendizado!"
        )


class NarrativeSequenceOrchestrator:
    """Orchestrates the creation of multiple interconnected supertasks."""
    
    def __init__(self, enrichment_engine: ContentEnrichmentEngine):
        self.content_analyzer = ProgressiveContentAnalyzer(enrichment_engine)
        self.level_generator = LevelSpecificGenerator(enrichment_engine)
        self.story_generator = StoryThreadGenerator()
    
    def create_progressive_journey(self, source_material: str, title: str, 
                                 levels: List[str] = None, theme: str = None) -> Dict[str, Any]:
        """Create a complete progressive learning journey."""
        try:
            levels = levels or ['foundation', 'application', 'mastery']
            theme = theme or f"Dominando {title}"
            
            logger.info(f"Creating progressive journey: {len(levels)} levels for '{title}'")
            
            # Extract insights by learning level
            insights_by_level = self.content_analyzer.extract_learning_levels(source_material)
            
            # Generate narrative thread
            narrative_thread = self.story_generator.generate_narrative_thread(theme, levels)
            
            # Generate supertasks for each level
            supertasks = {}
            for level in levels:
                logger.info(f"Generating supertask for level: {level}")
                
                level_insights = insights_by_level.get(level, [])
                if not level_insights:
                    logger.warning(f"No insights found for level {level}, using fallback")
                    continue
                
                # Generate content and quizzes for this level
                content_items = self.level_generator.generate_level_content(
                    level, level_insights, title
                )
                quiz_items = self.level_generator.generate_level_quizzes(
                    level, level_insights, title
                )
                
                # Create level-specific supertask structure
                supertask = self._create_level_supertask(
                    level, content_items, quiz_items, narrative_thread, title
                )
                
                supertasks[level] = supertask
                logger.info(f"Generated supertask for {level}: {len(content_items)} content, {len(quiz_items)} quiz")
            
            # Create journey metadata
            journey_metadata = {
                'narrative_thread': narrative_thread,
                'levels': levels,
                'theme': theme,
                'total_supertasks': len(supertasks)
            }
            
            return {
                'supertasks': supertasks,
                'metadata': journey_metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to create progressive journey: {e}")
            return self._create_fallback_journey(title, levels)
    
    def _create_level_supertask(self, level: str, content_items: List[Dict], 
                               quiz_items: List[Dict], narrative_thread: NarrativeThread,
                               title: str) -> Dict[str, Any]:
        """Create a complete supertask for a specific level."""
        try:
            config = self.level_generator.level_configs.get(level)
            if not config:
                raise ValueError(f"Unknown level: {level}")
            
            # Create quotes (simple inspirational content)
            quotes = self._create_level_quotes(level, title)
            
            # Apply level-specific sequence
            sequence_items = self._apply_level_sequence(
                config.sequence, content_items, quiz_items, quotes
            )
            
            # Add narrative elements
            if level in narrative_thread.progress_markers:
                # Add progress marker as first item if it fits
                progress_marker = {
                    "type": "content",
                    "content": narrative_thread.progress_markers[level],
                    "author": "Ari"
                }
                # Only add if we have room (max 8 items)
                if len(sequence_items) < 8:
                    sequence_items.insert(0, progress_marker)
            
            # Create the supertask structure
            supertask = {
                "title": f"{title} - {level.capitalize()}",
                "dimension": "mentalHealth",
                "archetype": "sage",
                "relatedToType": "GENERIC",
                "relatedToId": f"{title.lower().replace(' ', '_')}_{level}",
                "estimatedDuration": config.duration_range[0],
                "coinsReward": self._calculate_level_reward(level),
                "flexibleItems": sequence_items[:8],  # Ensure mobile limit
                "metadata": {
                    "language": "portuguese",
                    "region": "brazil",
                    "created_at": "2025-08-06T00:00:00Z",
                    "updated_at": "2025-08-06T00:00:00Z",
                    "version": "1.1",
                    "learning_level": level,
                    "narrative_theme": narrative_thread.journey_theme
                }
            }
            
            return supertask
            
        except Exception as e:
            logger.error(f"Failed to create {level} supertask: {e}")
            return self._create_fallback_supertask(level, title)
    
    def _create_level_quotes(self, level: str, title: str) -> List[Dict[str, Any]]:
        """Create inspirational quotes appropriate for the learning level."""
        level_quotes = {
            'foundation': [
                {"type": "quote", "content": "Todo grande conhecimento começa com um primeiro passo.", "author": "Provérbio"},
                {"type": "quote", "content": "A base sólida é o alicerce de todo aprendizado duradouro.", "author": "Sábio"}
            ],
            'application': [
                {"type": "quote", "content": "Conhecimento sem ação é como semente sem terra.", "author": "Provérbio"},
                {"type": "quote", "content": "A prática transforma teoria em sabedoria.", "author": "Mestre"}
            ],
            'mastery': [
                {"type": "quote", "content": "Maestria é a arte de tornar o complexo simples.", "author": "Expert"},
                {"type": "quote", "content": "O verdadeiro domínio vem da integração profunda.", "author": "Sábio"}
            ]
        }
        
        return level_quotes.get(level, level_quotes['foundation'])
    
    def _apply_level_sequence(self, sequence: str, content_items: List[Dict], 
                             quiz_items: List[Dict], quotes: List[Dict]) -> List[Dict[str, Any]]:
        """Apply the sequence pattern to create ordered items."""
        try:
            sequence_types = [item.strip() for item in sequence.split(' → ')]
            sequence_items = []
            
            content_idx = quiz_idx = quote_idx = 0
            
            for seq_type in sequence_types:
                if seq_type == 'content' and content_idx < len(content_items):
                    sequence_items.append(content_items[content_idx])
                    content_idx += 1
                elif seq_type == 'quiz' and quiz_idx < len(quiz_items):
                    sequence_items.append(quiz_items[quiz_idx])
                    quiz_idx += 1
                elif seq_type == 'quote' and quote_idx < len(quotes):
                    sequence_items.append(quotes[quote_idx])
                    quote_idx += 1
                
                # Stop if we reach mobile limit
                if len(sequence_items) >= 8:
                    break
            
            # Ensure minimum items (at least 3)
            while len(sequence_items) < 3:
                if content_idx < len(content_items):
                    sequence_items.append(content_items[content_idx])
                    content_idx += 1
                elif quiz_idx < len(quiz_items):
                    sequence_items.append(quiz_items[quiz_idx])
                    quiz_idx += 1
                elif quote_idx < len(quotes):
                    sequence_items.append(quotes[quote_idx])
                    quote_idx += 1
                else:
                    break
            
            return sequence_items
            
        except Exception as e:
            logger.error(f"Failed to apply sequence: {e}")
            # Fallback to simple ordering
            all_items = content_items + quiz_items + quotes
            return all_items[:6]  # Safe mobile limit
    
    def _calculate_level_reward(self, level: str) -> int:
        """Calculate appropriate coin reward for learning level."""
        rewards = {
            'foundation': 100,
            'application': 150,
            'mastery': 200
        }
        return rewards.get(level, 100)
    
    def _create_fallback_supertask(self, level: str, title: str) -> Dict[str, Any]:
        """Create a basic fallback supertask."""
        return {
            "title": f"{title} - {level.capitalize()}",
            "dimension": "mentalHealth",
            "archetype": "sage", 
            "relatedToType": "GENERIC",
            "relatedToId": f"fallback_{level}",
            "estimatedDuration": 300,
            "coinsReward": 100,
            "flexibleItems": [
                {
                    "type": "content",
                    "content": f"Este é conteúdo de {level} para {title}.",
                    "author": "Ari"
                }
            ],
            "metadata": {
                "language": "portuguese",
                "region": "brazil", 
                "created_at": "2025-08-06T00:00:00Z",
                "updated_at": "2025-08-06T00:00:00Z",
                "version": "1.1"
            }
        }
    
    def _create_fallback_journey(self, title: str, levels: List[str]) -> Dict[str, Any]:
        """Create a basic fallback journey."""
        supertasks = {}
        for level in levels:
            supertasks[level] = self._create_fallback_supertask(level, title)
        
        return {
            'supertasks': supertasks,
            'metadata': {
                'narrative_thread': None,
                'levels': levels,
                'theme': f"Aprendendo {title}",
                'total_supertasks': len(supertasks)
            }
        }