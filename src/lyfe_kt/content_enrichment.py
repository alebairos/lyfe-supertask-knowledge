"""
Content Enrichment System for Lyfe Supertask Knowledge Generator

This module implements intelligent content relevance and enrichment:
1. Source-driven content generation from actual insights
2. Chain-of-thought validation for content relevance  
3. Conditional enhancement (only when needed)
4. Meaningful quiz generation based on source wisdom

The goal: Transform generic educational content into enriching wisdom
that users can immediately apply to improve their lives.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EnhancementDecision(Enum):
    """Decisions from chain-of-thought validation."""
    APPROVED = "approved"  # Content already enriching
    ENHANCED = "enhanced"  # Needs specific improvements
    REGENERATED = "regenerated"  # Major gaps, start over


@dataclass
class SourceInsight:
    """Extracted insight from source material."""
    insight: str  # Core principle or wisdom
    application: str  # How to apply in daily life
    example: str  # Concrete example or scenario
    category: str  # Type of insight (e.g., "pillar", "strategy", "principle")


@dataclass
class ValidationResult:
    """Result from chain-of-thought content validation."""
    decision: EnhancementDecision
    relevance_score: float  # 0-1, how well content reflects source
    enrichment_score: float  # 0-1, how much users will be enriched
    improvements: List[str]  # Specific improvements needed
    reasoning: str  # Chain-of-thought explanation


class ContentEnrichmentEngine:
    """
    Intelligent content enrichment system that generates meaningful,
    source-driven content instead of generic educational templates.
    """
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client
        
    def extract_source_insights(self, source_material: str, max_insights: int = 5) -> List[SourceInsight]:
        """
        Extract specific, actionable insights from source material.
        
        Args:
            source_material: Raw content with wisdom to extract
            max_insights: Maximum number of insights to extract
            
        Returns:
            List of structured insights with applications
        """
        try:
            system_prompt = """Você é um especialista em extrair sabedoria prática de conteúdo educativo.

Sua tarefa: Analisar o material fornecido e extrair insights específicos e aplicáveis que enriqueceriam a compreensão e vida de alguém.

FOQUE EM:
- Sabedoria prática e princípios aplicáveis
- Estratégias e abordagens concretas
- Exemplos específicos e aplicações
- Conceitos-chave que podem ser pessoalmente aplicados

EVITE:
- Conceitos abstratos sem aplicação
- Informações genéricas ou óbvias
- Teoria sem conexão prática
- Definições sem valor aplicável

Retorne no formato JSON:
{
  "insights": [
    {
      "insight": "princípio ou sabedoria específica",
      "application": "como aplicar na vida diária",
      "example": "exemplo concreto ou cenário",
      "category": "tipo de insight (ex: pilar, estratégia, princípio)"
    }
  ]
}"""

            user_prompt = f"""Extraia até {max_insights} insights práticos e aplicáveis deste material:

{source_material}

Concentre-se em sabedoria que genuinamente enriqueceria a vida de alguém."""

            if not self.openai_client:
                logger.warning("No OpenAI client available, using fallback insights")
                return self._generate_fallback_insights(source_material)

            response = self.openai_client.generate_completion(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=800,
                temperature=0.7
            )

            if response and response.strip():
                try:
                    result = json.loads(response.strip())
                    insights = []
                    for insight_data in result.get('insights', []):
                        insights.append(SourceInsight(
                            insight=insight_data.get('insight', ''),
                            application=insight_data.get('application', ''),
                            example=insight_data.get('example', ''),
                            category=insight_data.get('category', 'principle')
                        ))
                    
                    logger.info(f"Extracted {len(insights)} source insights")
                    return insights
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse insights JSON: {e}")
                    return self._generate_fallback_insights(source_material)
            
            return self._generate_fallback_insights(source_material)
            
        except Exception as e:
            logger.error(f"Source insight extraction failed: {e}")
            return self._generate_fallback_insights(source_material)
    
    def validate_content_relevance(
        self, 
        content: str, 
        questions: List[Dict[str, Any]], 
        source_material: str
    ) -> ValidationResult:
        """
        Chain-of-thought validation of content relevance and enrichment value.
        
        Args:
            content: Generated content to validate
            questions: Generated quiz questions to validate
            source_material: Original source material for comparison
            
        Returns:
            ValidationResult with decision and improvements
        """
        try:
            system_prompt = """Você é um especialista em validação de conteúdo educativo que usa raciocínio passo-a-passo.

Sua tarefa: Analisar se o conteúdo gerado é relevante, enriquecedor e baseado no material fonte.

Use este processo de CHAIN-OF-THOUGHT:

1. VERIFICAÇÃO DE RELEVÂNCIA:
   - O conteúdo se relaciona diretamente com insights do material fonte?
   - Alguém que leu o material original reconheceria esses conceitos?
   - As perguntas testam compreensão de sabedoria real, não conceitos abstratos?

2. AVALIAÇÃO DE ENRIQUECIMENTO:
   - Os usuários se sentirão mais conhecedores e capazes após este conteúdo?
   - Os usuários podem aplicar esse conhecimento em suas vidas diárias?
   - Este conteúdo fornece sabedoria aplicável ou apenas informação?

3. DECISÃO DE MELHORIA:
   - Este conteúdo precisa de melhorias? (Sim/Não)
   - Se sim, que melhorias específicas o tornariam mais significativo?
   - Se não, por que o conteúdo atual já é enriquecedor?

Retorne no formato JSON:
{
  "decision": "approved|enhanced|regenerated",
  "relevance_score": 0.0-1.0,
  "enrichment_score": 0.0-1.0,
  "improvements": ["melhoria específica 1", "melhoria específica 2"],
  "reasoning": "explicação detalhada do raciocínio"
}"""

            # Convert questions to string safely
            if questions:
                questions_text = json.dumps(questions, indent=2, ensure_ascii=False)
            else:
                questions_text = "Nenhuma pergunta gerada ainda"
            
            user_prompt = f"""VALIDAÇÃO CHAIN-OF-THOUGHT:

MATERIAL FONTE:
{source_material}

CONTEÚDO GERADO:
{content}

PERGUNTAS GERADAS:
{questions_text}

Analise passo-a-passo se este conteúdo é relevante e enriquecedor."""

            if not self.openai_client:
                logger.warning("No OpenAI client available, using fallback validation")
                return self._generate_fallback_validation()

            response = self.openai_client.generate_completion(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=600,
                temperature=0.3  # Lower temperature for more consistent analysis
            )

            if response and response.strip():
                try:
                    # Clean response and extract JSON
                    clean_response = response.strip()
                    if clean_response.startswith('```json'):
                        clean_response = clean_response.replace('```json', '').replace('```', '').strip()
                    
                    result = json.loads(clean_response)
                    
                    decision_str = result.get('decision', 'enhanced').lower()
                    decision = EnhancementDecision.ENHANCED  # default
                    if decision_str == 'approved':
                        decision = EnhancementDecision.APPROVED
                    elif decision_str == 'regenerated':
                        decision = EnhancementDecision.REGENERATED
                    
                    validation = ValidationResult(
                        decision=decision,
                        relevance_score=float(result.get('relevance_score', 0.5)),
                        enrichment_score=float(result.get('enrichment_score', 0.5)),
                        improvements=result.get('improvements', []),
                        reasoning=result.get('reasoning', 'No reasoning provided')
                    )
                    
                    logger.info(f"Content validation: {decision.value}, relevance: {validation.relevance_score:.2f}, enrichment: {validation.enrichment_score:.2f}")
                    return validation
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse validation JSON: {e}")
                    return self._generate_fallback_validation()
            
            return self._generate_fallback_validation()
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return self._generate_fallback_validation()
    
    def generate_source_driven_content(
        self, 
        insights: List[SourceInsight], 
        difficulty: str,
        topic_title: str
    ) -> str:
        """
        Generate meaningful content based on extracted source insights.
        
        Args:
            insights: Extracted insights from source material
            difficulty: 'beginner' or 'advanced'
            topic_title: Title of the topic
            
        Returns:
            Generated content that reflects source wisdom
        """
        if not insights:
            return f"Explore os conceitos fundamentais sobre {topic_title} e como aplicá-los em sua vida."
        
        try:
            # Select most relevant insights for difficulty level
            selected_insights = self._select_insights_for_difficulty(insights, difficulty)
            
            if difficulty == "beginner":
                system_prompt = f"""Você é um especialista em tornar sabedoria complexa acessível para iniciantes.

Sua tarefa: Criar conteúdo que introduza insights fundamentais de forma clara e aplicável.

FOQUE EM:
- Apresentar conceitos básicos de forma clara
- Mostrar como aplicar na vida diária
- Preparar para compreensão mais profunda
- Usar linguagem simples e exemplos concretos

REGRAS CRÍTICAS DE SCHEMA MOBILE (v1.1):
- OBRIGATÓRIO: 50-300 caracteres (contando espaços)
- PROIBIDO: Bullet points (-, •), listas numeradas, quebras de linha (\n)
- ESTILO: Texto corrido, fluido, otimizado para tela mobile
- FOCO: Um conceito por item de conteúdo
- Use português brasileiro
- Seja prático e aplicável
- Tom conversacional e direto"""

                insights_text = "\n".join([f"- {insight.insight}: {insight.application}" for insight in selected_insights])
                user_prompt = f"Crie conteúdo introdutório baseado nestes insights sobre {topic_title}:\n\n{insights_text}"
                
            else:  # advanced
                system_prompt = f"""Você é um especialista em aprofundar sabedoria para usuários avançados.

Sua tarefa: Criar conteúdo que explore aplicações sofisticadas e integrações de insights.

FOQUE EM:
- Aplicações complexas e nuançadas
- Integração de múltiplos conceitos
- Cenários avançados e desafios
- Conexões profundas entre ideias

REGRAS CRÍTICAS DE SCHEMA MOBILE (v1.1):
- OBRIGATÓRIO: 50-300 caracteres (contando espaços)
- PROIBIDO: Bullet points (-, •), listas numeradas, quebras de linha (\n)
- ESTILO: Texto corrido, fluido, otimizado para tela mobile
- FOCO: Um conceito por item de conteúdo
- Use português brasileiro
- Assuma conhecimento básico
- Tom conversacional e sofisticado"""

                insights_text = "\n".join([f"- {insight.insight}: {insight.application} (Exemplo: {insight.example})" for insight in selected_insights])
                user_prompt = f"Crie conteúdo avançado baseado nestes insights sobre {topic_title}:\n\n{insights_text}"

            if not self.openai_client:
                return self._generate_fallback_content(selected_insights, difficulty)

            response = self.openai_client.generate_completion(
                prompt=user_prompt,
                system_message=system_prompt,
                max_tokens=200,
                temperature=0.7
            )

            if response and response.strip():
                content = response.strip()
                
                # Clean any unwanted prefixes and formatting
                content = re.sub(r'^(Content|Conteúdo|Item):\s*', '', content, flags=re.IGNORECASE)
                
                # CRITICAL: Clean mobile-incompatible formatting
                content = re.sub(r'^[-•]\s*', '', content, flags=re.MULTILINE)  # Remove bullet points
                content = re.sub(r'^\d+\.\s*', '', content, flags=re.MULTILINE)  # Remove numbered lists
                content = content.replace('\n- ', '. ')  # Convert bullet lines to sentences
                content = content.replace('\n', ' ')  # Remove all line breaks
                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                
                # Ensure content meets mobile character limits (50-300 chars)
                if len(content) > 300:
                    # Truncate at sentence boundary if possible
                    sentences = content.split('.')
                    truncated = ""
                    for sentence in sentences:
                        if len(truncated + sentence + ".") <= 295:
                            truncated += sentence + "."
                        else:
                            break
                    content = truncated if truncated else content[:295] + "..."
                elif len(content) < 50:
                    # Pad with additional context if too short
                    content = f"{content} Esta aplicação prática pode transformar sua experiência diária."
                
                return content

            return self._generate_fallback_content(selected_insights, difficulty)
            
        except Exception as e:
            logger.error(f"Source-driven content generation failed: {e}")
            return self._generate_fallback_content(insights, difficulty)
    
    def generate_source_driven_questions(
        self, 
        insights: List[SourceInsight], 
        difficulty: str,
        topic_title: str,
        num_questions: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Generate meaningful quiz questions based on source insights.
        
        Args:
            insights: Extracted insights from source material
            difficulty: 'beginner' or 'advanced'
            topic_title: Title of the topic
            num_questions: Number of questions to generate
            
        Returns:
            List of quiz questions that test understanding of source wisdom
        """
        if not insights:
            return self._generate_fallback_questions(topic_title, difficulty, num_questions)
        
        try:
            questions = []
            selected_insights = self._select_insights_for_difficulty(insights, difficulty)
            
            for i, insight in enumerate(selected_insights[:num_questions]):
                if difficulty == "beginner":
                    question = self._generate_recognition_question(insight, topic_title)
                else:  # advanced
                    question = self._generate_application_question(insight, topic_title)
                
                if question:
                    questions.append(question)
            
            # Fill remaining questions if needed
            while len(questions) < num_questions and len(questions) < len(insights):
                remaining_insights = [ins for ins in insights if ins not in selected_insights[:len(questions)]]
                if remaining_insights:
                    additional_insight = remaining_insights[0]
                    if difficulty == "beginner":
                        question = self._generate_recognition_question(additional_insight, topic_title)
                    else:
                        question = self._generate_application_question(additional_insight, topic_title)
                    
                    if question:
                        questions.append(question)
                else:
                    break
            
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Source-driven question generation failed: {e}")
            return self._generate_fallback_questions(topic_title, difficulty, num_questions)
    
    def enhance_content_conditionally(
        self, 
        content: str, 
        questions: List[Dict[str, Any]], 
        validation: ValidationResult,
        source_insights: List[SourceInsight]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Conditionally enhance content based on validation results.
        Only improve when validation identifies specific needs.
        
        Args:
            content: Original generated content
            questions: Original generated questions
            validation: Validation result with enhancement decision
            source_insights: Source insights for reference
            
        Returns:
            Tuple of (enhanced_content, enhanced_questions)
        """
        if validation.decision == EnhancementDecision.APPROVED:
            logger.info("Content approved, no enhancement needed")
            return content, questions
        
        elif validation.decision == EnhancementDecision.ENHANCED:
            logger.info(f"Enhancing content based on {len(validation.improvements)} improvements")
            return self._apply_specific_improvements(content, questions, validation.improvements, source_insights)
        
        elif validation.decision == EnhancementDecision.REGENERATED:
            logger.info("Regenerating content due to major relevance gaps")
            return self._regenerate_with_source_focus(validation.reasoning, source_insights)
        
        return content, questions
    
    # Private helper methods
    
    def _select_insights_for_difficulty(self, insights: List[SourceInsight], difficulty: str) -> List[SourceInsight]:
        """Select most appropriate insights for difficulty level."""
        if difficulty == "beginner":
            # Prefer foundational insights and principles
            foundational = [ins for ins in insights if ins.category in ['principle', 'pillar', 'foundation']]
            return foundational[:3] if foundational else insights[:3]
        else:
            # Prefer strategic and complex insights
            advanced = [ins for ins in insights if ins.category in ['strategy', 'integration', 'application']]
            return advanced[:3] if advanced else insights[:3]
    
    def _generate_recognition_question(self, insight: SourceInsight, topic_title: str) -> Optional[Dict[str, Any]]:
        """Generate a mobile-optimized question that tests recognition of insight."""
        try:
            # Create mobile-optimized question (15-120 chars)
            clean_topic = topic_title.replace("Encontrando Significado na Vida", "encontrar significado")
            question_text = f"Como aplicar {clean_topic} no dia a dia?"
            
            # Ensure question is within mobile limits
            if len(question_text) > 120:
                question_text = question_text[:115] + "...?"
            elif len(question_text) < 15:
                question_text = f"Como praticar {clean_topic}?"
            
            # Generate mobile-optimized options (3-60 chars each)
            application_short = insight.application[:55] if len(insight.application) > 55 else insight.application
            options = [
                application_short,  # Correct answer
                "Ignorar completamente",
                "Esperar motivação",
                "Apenas teoria"
            ]
            
            # Ensure all options are within mobile limits (3-60 chars)
            options = [opt[:60] if len(opt) > 60 else opt for opt in options]
            options = [opt if len(opt) >= 3 else f"Op {i+1}" for i, opt in enumerate(options)]
            
            # Mobile-optimized explanation (30-250 chars)
            explanation = f"Esta aplicação funciona porque {insight.application[:80]}."
            if len(explanation) > 250:
                explanation = explanation[:245] + "..."
            elif len(explanation) < 30:
                explanation = f"{explanation} Pequenos passos geram grandes mudanças."
            
            return {
                'question': question_text,
                'options': options,
                'correctAnswer': 0,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.warning(f"Failed to generate recognition question: {e}")
            return None
    
    def _generate_application_question(self, insight: SourceInsight, topic_title: str) -> Optional[Dict[str, Any]]:
        """Generate a mobile-optimized question that tests application of insight."""
        try:
            # Create mobile-optimized integration question (15-120 chars)
            clean_topic = topic_title.replace("Encontrando Significado na Vida", "significado")
            insight_short = insight.insight[:30] if len(insight.insight) > 30 else insight.insight
            question_text = f"Como integrar {insight_short} com {clean_topic}?"
            
            # Ensure question is within mobile limits
            if len(question_text) > 120:
                question_text = f"Como integrar {insight_short[:20]}... com outros aspectos?"
                if len(question_text) > 120:
                    question_text = "Como integrar este conceito com outros aspectos?"
            elif len(question_text) < 15:
                question_text = f"Como aplicar {insight_short}?"
            
            # Generate mobile-optimized sophisticated options (3-60 chars each)
            options = [
                "Combinar estratégias",  # Correct answer - shortened
                "Aplicar isoladamente",
                "Evitar complexidade", 
                "Usar ocasionalmente"
            ]
            
            # Ensure all options are within mobile limits (3-60 chars)
            options = [opt[:60] if len(opt) > 60 else opt for opt in options]
            options = [opt if len(opt) >= 3 else f"Op {i+1}" for i, opt in enumerate(options)]
            
            # Mobile-optimized explanation (30-250 chars)
            explanation = f"A integração maximiza o impacto porque {insight.application[:120]}."
            if len(explanation) > 250:
                explanation = explanation[:245] + "..."
            elif len(explanation) < 30:
                explanation = f"{explanation} Múltiplas abordagens são mais eficazes."
            
            return {
                'question': question_text,
                'options': options,
                'correctAnswer': 0,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.warning(f"Failed to generate application question: {e}")
            return None
    
    def _apply_specific_improvements(
        self, 
        content: str, 
        questions: List[Dict[str, Any]], 
        improvements: List[str],
        source_insights: List[SourceInsight]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Apply specific improvements identified by validation."""
        enhanced_content = content
        enhanced_questions = questions.copy()
        
        for improvement in improvements:
            if "mais específico" in improvement.lower() or "specific" in improvement.lower():
                # Make content more specific to source insights
                if source_insights:
                    insight_examples = ", ".join([ins.example[:20] + "..." if len(ins.example) > 20 else ins.example for ins in source_insights[:1] if ins.example])
                    if insight_examples and len(enhanced_content) + len(insight_examples) + 12 < 280:  # Leave room for "Exemplos: "
                        enhanced_content = f"{enhanced_content} Exemplos: {insight_examples}"
            
            elif "aplicável" in improvement.lower() or "practical" in improvement.lower():
                # Make content more practical
                if source_insights:
                    practical_tip = source_insights[0].application
                    if practical_tip and len(enhanced_content) + len(practical_tip) + 12 < 280:  # Leave room for "Aplicação: "
                        enhanced_content = f"{enhanced_content} Aplicação: {practical_tip[:40]}"
            
            elif "perguntas" in improvement.lower() or "questions" in improvement.lower():
                # Improve questions to be more source-specific
                for i, question in enumerate(enhanced_questions):
                    if i < len(source_insights):
                        insight = source_insights[i]
                        enhanced_questions[i]['explanation'] = f"{insight.application} {insight.example}"[:250]
        
        # Ensure final enhanced content stays within mobile limits
        if len(enhanced_content) > 300:
            # Truncate at sentence boundary if possible
            sentences = enhanced_content.split('.')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + ".") <= 295:
                    truncated += sentence + "."
                else:
                    break
            enhanced_content = truncated if truncated else enhanced_content[:295] + "..."
        
        return enhanced_content, enhanced_questions
    
    def _regenerate_with_source_focus(
        self, 
        reasoning: str, 
        source_insights: List[SourceInsight]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Regenerate content with stronger focus on source material."""
        if not source_insights:
            return "Conteúdo focado em aplicação prática dos conceitos apresentados.", []
        
        # Generate new content directly from insights
        main_insight = source_insights[0]
        new_content = f"{main_insight.insight} Aplicação prática: {main_insight.application}"
        
        # Generate new questions based on insights
        new_questions = []
        for insight in source_insights[:2]:
            question = {
                'question': f"Como aplicar: {insight.insight[:60]}?",
                'options': [
                    insight.application,
                    "Abordagem genérica",
                    "Evitar aplicação",
                    "Teoria apenas"
                ],
                'correctAnswer': 0,
                'explanation': f"{insight.application} {insight.example}"[:250]
            }
            new_questions.append(question)
        
        return new_content, new_questions
    
    def _generate_fallback_insights(self, source_material: str) -> List[SourceInsight]:
        """Generate fallback insights when AI extraction fails."""
        return [
            SourceInsight(
                insight="Aplicar conceitos na vida diária",
                application="Identificar uma área para melhoria e criar um plano simples",
                example="Escolher um hábito pequeno e praticá-lo consistentemente",
                category="principle"
            )
        ]
    
    def _generate_fallback_validation(self) -> ValidationResult:
        """Generate fallback validation when AI analysis fails."""
        return ValidationResult(
            decision=EnhancementDecision.ENHANCED,
            relevance_score=0.6,
            enrichment_score=0.6,
            improvements=["Tornar mais específico ao material fonte", "Adicionar aplicações práticas"],
            reasoning="Validação automática - conteúdo pode ser melhorado com mais especificidade"
        )
    
    def _generate_fallback_content(self, insights: List[SourceInsight], difficulty: str) -> str:
        """Generate fallback content when AI generation fails."""
        if insights:
            main_insight = insights[0]
            if difficulty == "beginner":
                return f"Conceito fundamental: {main_insight.insight}. Como aplicar: {main_insight.application}"
            else:
                return f"Aplicação avançada: {main_insight.insight}. Integração: {main_insight.application} {main_insight.example}"
        
        return "Explore os conceitos apresentados e identifique formas práticas de aplicá-los em sua vida."
    
    def _generate_fallback_questions(self, topic_title: str, difficulty: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI generation fails."""
        if difficulty == "beginner":
            return [{
                'question': f"Qual o primeiro passo para aplicar {topic_title}?",
                'options': ["Identificar uma área específica", "Estudar mais teoria", "Esperar inspiração", "Evitar mudanças"],
                'correctAnswer': 0,
                'explanation': "Começar com uma área específica permite foco e progresso mensurável."
            }]
        else:
            return [{
                'question': f"Como integrar {topic_title} com outros aspectos da vida?",
                'options': ["Criar conexões sistemáticas", "Manter separado", "Aplicar raramente", "Evitar complexidade"],
                'correctAnswer': 0,
                'explanation': "Integração sistemática maximiza o impacto e cria mudanças duradouras."
            }]