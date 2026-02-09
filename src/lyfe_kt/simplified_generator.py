"""
Simplified Supertask Generator v2.0

This module implements a radically simplified approach that trusts modern LLMs
to generate high-quality content directly, without complex post-processing.

Core Philosophy: Trust the AI, Minimize Processing
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from .openai_client import OpenAIClient

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """Simple request structure for content generation."""
    source_content: str
    difficulty: str
    sequence: str
    title: str
    theme: Optional[str] = None


class MasterPromptGenerator:
    """Creates comprehensive prompts that handle everything in one AI call."""
    
    def __init__(self):
        self.schema_constraints = self._load_schema_constraints()
        self.concept_cache = {}  # Cache for extracted concepts
    
    def _load_schema_constraints(self) -> str:
        """Load mobile schema constraints as a string."""
        return """
SCHEMA MOBILE v1.1 CONSTRAINTS:
- title: 1-200 caracteres
- content items: 50-300 caracteres (texto corrido, sem bullets ou quebras de linha)
- quiz questions: 15-120 caracteres
- quiz options: 3-60 caracteres cada
- quiz explanations: 30-250 caracteres
- tips: 20-150 caracteres cada
- quotes: 20-200 caracteres
- flexibleItems: 3-8 items total
- estimatedDuration: 180-600 segundos
- coinsReward: 1-1000
"""
    
    def create_complete_supertask_prompt(self, request: GenerationRequest) -> str:
        """Generate ONE comprehensive prompt that creates a complete supertask."""
        
        difficulty_guidance = self._get_difficulty_guidance(request.difficulty)
        sequence_guidance = self._get_sequence_guidance(request.sequence)
        
        prompt = f"""Você é Ari, um assistente de coaching inspirado no TARS do filme Interestelar. Crie um supertask JSON completo baseado no conteúdo fornecido.

REQUISITOS CRÍTICOS:
{self.schema_constraints}

DIFICULDADE: {request.difficulty}
{difficulty_guidance}

SEQUÊNCIA: {request.sequence}
{sequence_guidance}

QUALIDADE OBRIGATÓRIA:
- Português brasileiro PERFEITO (zero erros ortográficos)
- Autor: APENAS "Ari" (nunca criar autores fictícios como "Expert", "Sábio", "David Wilkerson", etc.)
- Citações: Use apenas "Ari" como autor, sem mencionar outros nomes no conteúdo das citações
- Conteúdo baseado no material fonte (não genérico)
- Texto móvel-otimizado (corrido, sem formatação especial)
- JSON válido e completo

CONTEÚDO FONTE:
{request.source_content}

Gere um JSON completo seguindo exatamente esta estrutura:

{{
  "title": "{request.title} - {request.difficulty.capitalize()}",
  "dimension": "mentalHealth",
  "archetype": "sage",
  "relatedToType": "GENERIC",
  "relatedToId": "{request.title.lower().replace(' ', '_')}_{request.difficulty}",
  "estimatedDuration": [duração apropriada 180-600],
  "coinsReward": [recompensa apropriada 1-1000],
  "flexibleItems": [
    // Gere 3-8 items seguindo a sequência {request.sequence}
    // Cada item deve ser tipo "content", "quiz" ou "quote"
    // Exemplo de content:
    {{
      "type": "content",
      "content": "[texto 50-300 chars baseado no fonte]",
      "author": "Ari",
      "tips": ["[dica prática 20-150 chars]"] // opcional
    }},
    // Exemplo de quiz:
    {{
      "type": "quiz", 
      "question": "[pergunta 15-120 chars]",
      "options": ["[opção 3-60 chars]", "[opção 3-60 chars]", "[opção 3-60 chars]", "[opção 3-60 chars]"],
      "correctAnswer": [índice 0-3],
      "explanation": "[explicação 30-250 chars]"
    }},
    // Exemplo de quote:
    {{
      "type": "quote",
      "content": "[citação inspiradora 20-200 chars]",
      "author": "Ari"
    }}
  ],
  "metadata": {{
    "language": "portuguese",
    "region": "brazil",
    "created_at": "2025-08-06T00:00:00Z",
    "updated_at": "2025-08-06T00:00:00Z",
    "version": "1.1"
  }}
}}

IMPORTANTE: Responda APENAS com o JSON válido, sem texto adicional."""

        return prompt
    
    def _get_difficulty_guidance(self, difficulty: str) -> str:
        """Get specific guidance for difficulty level."""
        guidance = {
            'beginner': """
FOCO INICIANTE:
- Conceitos fundamentais e definições básicas
- Linguagem simples e exemplos concretos
- "O que é isso?" e "Por que importa?"
- Preparar base para aprendizado futuro""",
            
            'intermediate': """
FOCO INTERMEDIÁRIO:
- Aplicação prática e cenários reais
- "Como usar?" e "Quando aplicar?"
- Exemplos específicos e ações concretas
- Construir sobre conhecimento básico""",
            
            'advanced': """
FOCO AVANÇADO:
- Integração complexa e nuances
- "Como conectar?" e "Casos especiais?"
- Cenários sofisticados e edge cases
- Assumir conhecimento fundamental"""
        }
        
        return guidance.get(difficulty, guidance['beginner'])
    
    def _get_sequence_guidance(self, sequence: str) -> str:
        """Get guidance for sequence pattern."""
        return f"""
PADRÃO DE SEQUÊNCIA:
- Siga exatamente: {sequence}
- Distribua o conteúdo naturalmente pelos tipos
- Mantenha coerência narrativa entre items
- Cada tipo deve complementar os outros"""

    def extract_comprehensive_concepts(self, source_content: str) -> Dict[str, Any]:
        """Extract ALL key concepts from source material systematically."""
        
        # Check cache first
        content_hash = str(hash(source_content))
        if content_hash in self.concept_cache:
            return self.concept_cache[content_hash]
        
        extraction_prompt = f"""Analise este conteúdo e extraia TODOS os conceitos principais de forma sistemática.

CONTEÚDO FONTE:
{source_content}

Identifique e organize:
1. CONCEITOS PRINCIPAIS (todos os temas centrais abordados)
2. APLICAÇÕES PRÁTICAS para cada conceito
3. EXEMPLOS CONCRETOS mencionados
4. NÍVEL DE COMPLEXIDADE de cada conceito

Responda APENAS com JSON válido:
{{
    "main_concepts": [
        {{
            "name": "Nome do Conceito",
            "description": "Descrição clara do conceito",
            "practical_applications": ["aplicação 1", "aplicação 2"],
            "examples": ["exemplo 1", "exemplo 2"],
            "complexity_levels": ["basic", "intermediate", "advanced"],
            "source_quotes": ["citação relevante do texto"]
        }}
    ],
    "total_concepts": 5,
    "primary_theme": "tema principal do conteúdo",
    "coverage_areas": ["área 1", "área 2", "área 3"]
}}

GARANTA que TODOS os conceitos importantes do material sejam incluídos, não apenas os mais óbvios."""

        return {"extraction_prompt": extraction_prompt, "content_hash": content_hash}
    
    def assign_concepts_to_levels(self, concepts: List[Dict], num_levels: int = 5) -> Dict[str, List[Dict]]:
        """Strategically assign concepts to levels for comprehensive coverage."""
        

        # Strategic assignment for 5+ levels
        level_strategy = {
            1: {'name': 'foundation', 'focus': 'basic understanding', 'concept_count': 2},
            2: {'name': 'application', 'focus': 'practical application', 'concept_count': 2}, 
            3: {'name': 'expansion', 'focus': 'new concepts', 'concept_count': 2},
            4: {'name': 'integration', 'focus': 'combine concepts', 'concept_count': 3},
            5: {'name': 'mastery', 'focus': 'advanced integration', 'concept_count': len(concepts)}
        }
        
        assignment = {}
        concept_index = 0
        
        for level_num in range(1, min(num_levels + 1, 6)):
            level_info = level_strategy[level_num]
            level_name = level_info['name']
            
            if level_num <= 3:  # Foundation, Application, Expansion
                end_index = min(concept_index + level_info['concept_count'], len(concepts))
                assignment[level_name] = concepts[concept_index:end_index]
                concept_index = end_index
            else:  # Integration, Mastery
                assignment[level_name] = concepts  # All concepts for advanced levels
        
        return assignment
    
    def create_comprehensive_level_prompt(self, request: GenerationRequest, level: str, 
                                        assigned_concepts: List[Dict], all_concepts: List[Dict]) -> str:
        """Create level-specific prompt ensuring comprehensive coverage."""
        
        level_guidance = self._get_comprehensive_level_guidance(level, assigned_concepts, all_concepts)
        difficulty_guidance = self._get_difficulty_guidance(request.difficulty)
        sequence_guidance = self._get_sequence_guidance(request.sequence)
        
        concepts_text = self._format_concepts_for_prompt(assigned_concepts)
        all_concepts_text = self._format_concepts_for_prompt(all_concepts)
        
        prompt = f"""Você é Ari, um assistente de coaching inspirado no TARS do filme Interestelar. Crie um supertask JSON completo com COBERTURA ABRANGENTE dos conceitos designados.

REQUISITOS CRÍTICOS:
{self.schema_constraints}

NÍVEL: {level.upper()}
{level_guidance}

CONCEITOS PARA ESTE NÍVEL:
{concepts_text}

TODOS OS CONCEITOS DO MATERIAL (para contexto):
{all_concepts_text}

DIFICULDADE: {request.difficulty}
{difficulty_guidance}

SEQUÊNCIA: {request.sequence}  
{sequence_guidance}

QUALIDADE OBRIGATÓRIA:
- Português brasileiro PERFEITO (zero erros ortográficos)
- Autor: APENAS "Ari" (nunca criar autores fictícios)
- Citações: Use apenas "Ari" como autor
- COBERTURA COMPLETA dos conceitos designados
- Conteúdo específico baseado no material fonte
- Texto móvel-otimizado (corrido, sem formatação especial)
- JSON válido e completo

CONTEÚDO FONTE:
{request.source_content}

Gere um JSON completo seguindo exatamente esta estrutura:

{{
  "title": "{request.title} - {level.capitalize()}",
  "dimension": "mentalHealth",
  "archetype": "sage", 
  "relatedToType": "GENERIC",
  "relatedToId": "{request.title.lower().replace(' ', '_')}_{level}",
  "estimatedDuration": [duração apropriada 180-600],
  "coinsReward": [recompensa apropriada 1-1000],
  "flexibleItems": [
    // Gere 3-8 items seguindo a sequência {request.sequence}
    // GARANTA que todos os conceitos designados sejam abordados
    // Distribua os conceitos naturalmente pelos items
    // Cada item deve ser tipo "content", "quiz" ou "quote"
    // Exemplo de content:
    {{
      "type": "content",
      "content": "[texto 50-300 chars cobrindo conceito específico]",
      "author": "Ari",
      "tips": ["[dica prática 20-150 chars]"] // opcional
    }},
    // Exemplo de quiz:
    {{
      "type": "quiz",
      "question": "[pergunta 15-120 chars sobre conceito específico]",
      "options": ["[opção 3-60 chars]", "[opção 3-60 chars]", "[opção 3-60 chars]", "[opção 3-60 chars]"],
      "correctAnswer": [índice 0-3],
      "explanation": "[explicação 30-250 chars]"
    }},
    // Exemplo de quote:
    {{
      "type": "quote",
      "content": "[citação inspiradora 20-200 chars relacionada aos conceitos]",
      "author": "Ari"
    }}
  ],
  "metadata": {{
    "language": "portuguese",
    "region": "brazil",
    "created_at": "2025-08-06T00:00:00Z",
    "updated_at": "2025-08-06T00:00:00Z",
    "version": "1.1"
  }}
}}

IMPORTANTE: Responda APENAS com o JSON válido, sem texto adicional."""

        return prompt
    
    def _get_comprehensive_level_guidance(self, level: str, assigned_concepts: List[Dict], all_concepts: List[Dict]) -> str:
        """Get specific guidance for comprehensive level generation."""
        
        assigned_names = [c.get('name', 'Conceito') for c in assigned_concepts]
        all_names = [c.get('name', 'Conceito') for c in all_concepts]
        
        guidance_map = {
            'foundation': f"""
FOCO FOUNDATION:
- Introduza os conceitos fundamentais: {', '.join(assigned_names)}
- Estabeleça definições básicas e importância
- Prepare base sólida para níveis futuros
- Mencione brevemente que existem outros pilares: {', '.join([n for n in all_names if n not in assigned_names])}
- O que são esses conceitos e por que são importantes""",
            
            'application': f"""
FOCO APPLICATION:
- Aplique praticamente os conceitos já introduzidos: {', '.join(assigned_names)}
- Demonstre como usar na vida real
- Cenários concretos e ações específicas
- Construa sobre o conhecimento foundation
- Como implementar e quais são os primeiros passos""",
            
            'expansion': f"""
FOCO EXPANSION:
- Introduza novos conceitos importantes: {', '.join(assigned_names)}
- Conecte brevemente com conceitos anteriores
- Explore definições e relevância dos novos conceitos
- Prepare para integração futura
- Quais outros pilares existem e como se relacionam""",
            
            'integration': f"""
FOCO INTEGRATION:
- Combine todos os conceitos: {', '.join(all_names)}
- Mostre interconexões e sinergias
- Cenários complexos que envolvem múltiplos conceitos
- Como tudo se conecta e como usar em conjunto
- Balanceamento e priorização entre conceitos""",
            
            'mastery': f"""
FOCO MASTERY:
- Domínio avançado de todos os conceitos: {', '.join(all_names)}
- Casos especiais, nuances e edge cases
- Integração sofisticada em situações complexas
- Como lidar com conflitos e adaptação a contextos únicos
- Assumir conhecimento profundo de todos os pilares"""
        }
        
        return guidance_map.get(level, guidance_map['foundation'])
    
    def _format_concepts_for_prompt(self, concepts: List[Dict]) -> str:
        """Format concepts list for inclusion in prompts."""
        if not concepts:
            return "Nenhum conceito específico designado."
        
        formatted = []
        for i, concept in enumerate(concepts, 1):
            name = concept.get('name', f'Conceito {i}')
            desc = concept.get('description', 'Sem descrição')
            apps = concept.get('practical_applications', [])
            examples = concept.get('examples', [])
            
            formatted.append(f"""
{i}. {name}
   - Descrição: {desc}
   - Aplicações: {', '.join(apps[:2]) if apps else 'A definir'}
   - Exemplos: {', '.join(examples[:2]) if examples else 'A definir'}""")
        
        return '\n'.join(formatted)

    def create_progressive_level_prompt(self, request: GenerationRequest, level: str) -> str:
        """Create prompt for specific level in progressive journey."""
        
        level_mapping = {
            'foundation': 'beginner',
            'application': 'intermediate', 
            'mastery': 'advanced'
        }
        
        mapped_difficulty = level_mapping.get(level, 'beginner')
        level_request = GenerationRequest(
            source_content=request.source_content,
            difficulty=mapped_difficulty,
            sequence=request.sequence,
            title=f"{request.title} - {level.capitalize()}",
            theme=request.theme
        )
        
        return self.create_complete_supertask_prompt(level_request)


class CoverageValidator:
    """Validates comprehensive coverage of source concepts."""
    
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
    
    def validate_complete_coverage(self, journey: List[Dict[str, Any]], source_concepts: List[Dict]) -> Dict[str, Any]:
        """Verify that the journey covers all important source concepts."""
        
        journey_text = self._format_journey_for_validation(journey)
        concepts_text = self._format_concepts_for_validation(source_concepts)
        
        validation_prompt = f"""Analise se esta jornada de aprendizado cobre TODOS os conceitos principais do material fonte.

CONCEITOS DO MATERIAL FONTE:
{concepts_text}

JORNADA GERADA:
{journey_text}

Para cada conceito do material fonte, identifique:
1. EM QUAL NÍVEL foi abordado (se foi)
2. QUALIDADE da cobertura (inexistente/superficial/boa/excelente)
3. CONCEITOS FALTANDO ou mal cobertos

Responda APENAS com JSON válido:
{{
    "coverage_analysis": [
        {{
            "concept_name": "Nome do Conceito",
            "covered_in_level": "foundation/application/expansion/integration/mastery/não_coberto",
            "coverage_quality": "inexistente/superficial/boa/excelente",
            "evidence": "onde aparece na jornada",
            "suggestions": "como melhorar a cobertura"
        }}
    ],
    "overall_coverage_score": 85,
    "missing_concepts": ["conceito não abordado"],
    "improvement_suggestions": [
        {{
            "level": "expansion",
            "add_concept": "Conceito Faltante",
            "reason": "por que adicionar"
        }}
    ],
    "coverage_summary": "resumo da análise"
}}"""

        try:
            response = self.openai_client.generate_completion(validation_prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Coverage validation failed: {e}")
            return {"coverage_analysis": [], "overall_coverage_score": 0, "error": str(e)}
    
    def suggest_coverage_improvements(self, coverage_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable suggestions for improving coverage."""
        
        suggestions = []
        
        # Missing concepts
        missing = coverage_analysis.get('missing_concepts', [])
        if missing:
            suggestions.append(f"Adicionar conceitos faltantes: {', '.join(missing)}")
        
        # Poor coverage
        poor_coverage = [
            item['concept_name'] for item in coverage_analysis.get('coverage_analysis', [])
            if item.get('coverage_quality') in ['inexistente', 'superficial']
        ]
        
        if poor_coverage:
            suggestions.append(f"Melhorar cobertura superficial de: {', '.join(poor_coverage)}")
        
        # Specific improvements
        improvements = coverage_analysis.get('improvement_suggestions', [])
        for imp in improvements:
            level = imp.get('level', 'unknown')
            concept = imp.get('add_concept', 'conceito')
            reason = imp.get('reason', 'melhorar cobertura')
            suggestions.append(f"Nível {level}: adicionar {concept} ({reason})")
        
        return suggestions
    
    def _format_journey_for_validation(self, journey: List[Dict[str, Any]]) -> str:
        """Format journey data for validation prompt."""
        formatted_levels = []
        
        for i, level_data in enumerate(journey, 1):
            title = level_data.get('title', f'Nível {i}')
            items = level_data.get('flexibleItems', [])
            
            content_items = [item.get('content', '') for item in items if item.get('type') == 'content']
            quiz_items = [item.get('question', '') for item in items if item.get('type') == 'quiz']
            quote_items = [item.get('content', '') for item in items if item.get('type') == 'quote']
            
            level_summary = f"""
NÍVEL {i}: {title}
- Conteúdos: {' | '.join(content_items[:2])}...
- Quizzes: {' | '.join(quiz_items[:2])}...
- Citações: {' | '.join(quote_items[:1])}..."""
            
            formatted_levels.append(level_summary)
        
        return '\n'.join(formatted_levels)
    
    def _format_concepts_for_validation(self, concepts: List[Dict]) -> str:
        """Format concepts for validation prompt."""
        formatted = []
        for i, concept in enumerate(concepts, 1):
            name = concept.get('name', f'Conceito {i}')
            desc = concept.get('description', 'Sem descrição')
            formatted.append(f"{i}. {name}: {desc}")
        
        return '\n'.join(formatted)


class SimplifiedGenerator:
    """Core simplified generator that trusts AI to do everything."""
    
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        self.prompt_generator = MasterPromptGenerator()
        self.quality_reviewer = QualityReviewer()
    
    def generate_supertask(self, request: GenerationRequest) -> Dict[str, Any]:
        """Generate complete supertask in ONE AI call."""
        try:
            logger.info(f"Generating {request.difficulty} supertask: {request.title}")
            
            # Create comprehensive prompt
            prompt = self.prompt_generator.create_complete_supertask_prompt(request)
            
            # Single AI call - let GPT-4 do everything
            response = self.openai_client.generate_completion(
                prompt=prompt,
                system_message="Você é um especialista em criação de conteúdo educacional JSON. Responda apenas com JSON válido.",
                max_tokens=2000,
                temperature=0.3  # Lower for consistency
            )
            
            # Parse JSON response
            try:
                supertask = json.loads(response.strip())
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                # Try to extract JSON from response
                supertask = self._extract_json_from_response(response)
            
            # Light quality review (only critical issues)
            supertask = self.quality_reviewer.review_if_needed(supertask, request)
            
            logger.info(f"Successfully generated supertask: {len(supertask.get('flexibleItems', []))} items")
            return supertask
            
        except Exception as e:
            logger.error(f"Supertask generation failed: {e}")
            return self._create_emergency_fallback(request)
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from potentially malformed response."""
        try:
            # Remove markdown code blocks
            cleaned = re.sub(r'```json\s*', '', response)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            
            # Find JSON object boundaries
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = cleaned[start:end]
                return json.loads(json_str)
            
            raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            raise
    
    def _create_emergency_fallback(self, request: GenerationRequest) -> Dict[str, Any]:
        """Create minimal fallback supertask when AI generation fails."""
        return {
            "title": f"{request.title} - {request.difficulty.capitalize()}",
            "dimension": "mentalHealth",
            "archetype": "sage",
            "relatedToType": "GENERIC", 
            "relatedToId": f"fallback_{request.difficulty}",
            "estimatedDuration": 300,
            "coinsReward": 100,
            "flexibleItems": [
                {
                    "type": "content",
                    "content": f"Este conteúdo sobre {request.title} foi criado para o nível {request.difficulty}.",
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


class QualityReviewer:
    """Minimal quality reviewer that only fixes critical issues."""
    
    def review_if_needed(self, supertask: Dict[str, Any], request: GenerationRequest) -> Dict[str, Any]:
        """ONLY fix critical issues, don't recreate content."""
        try:
            # Enforce authorship/quote constraints before identifying issues
            supertask = self._sanitize_authorship_and_quotes(supertask)
            issues = self._identify_critical_issues(supertask)
            
            if not issues:
                logger.info("No critical issues found, returning supertask as-is")
                return supertask
            
            logger.warning(f"Found critical issues: {issues}")
            return self._minimal_fix(supertask, issues, request)
            
        except Exception as e:
            logger.error(f"Quality review failed: {e}")
            return supertask  # Return as-is if review fails
    
    def _identify_critical_issues(self, supertask: Dict[str, Any]) -> List[str]:
        """Identify only critical issues that must be fixed."""
        issues = []
        
        # Check for missing required fields
        required_fields = ['title', 'dimension', 'archetype', 'relatedToType', 
                          'relatedToId', 'estimatedDuration', 'coinsReward', 
                          'flexibleItems', 'metadata']
        
        for field in required_fields:
            if field not in supertask:
                issues.append(f"missing_{field}")
        
        # Check for fake authors (not Ari)
        if self._has_fake_authors(supertask):
            issues.append("fake_authors")
        
        # Check for critical schema violations
        if not self._validate_critical_schema(supertask):
            issues.append("schema_violation")
        
        return issues
    
    def _has_fake_authors(self, supertask: Dict[str, Any]) -> bool:
        """Check if any items have fake authors (not Ari)."""
        try:
            for item in supertask.get('flexibleItems', []):
                author = item.get('author')
                if author and author != 'Ari':
                    # Allow some variations of Ari
                    if author.lower() not in ['ari', 'ari (coach)', 'ari - coach']:
                        return True
            return False
        except:
            return False
    
    def _validate_critical_schema(self, supertask: Dict[str, Any]) -> bool:
        """Validate only critical schema constraints."""
        try:
            # Check flexibleItems count
            items = supertask.get('flexibleItems', [])
            if len(items) < 3 or len(items) > 8:
                return False
            
            # Check basic item structure
            for item in items:
                if 'type' not in item:
                    return False
                
                item_type = item.get('type')
                if item_type not in ['content', 'quiz', 'quote']:
                    return False
                
                # Basic content checks
                if item_type == 'content' and 'content' not in item:
                    return False
                if item_type == 'quiz' and not all(k in item for k in ['question', 'options', 'correctAnswer', 'explanation']):
                    return False
                if item_type == 'quote' and not all(k in item for k in ['content', 'author']):
                    return False
            
            return True
            
        except:
            return False
    
    def _minimal_fix(self, supertask: Dict[str, Any], issues: List[str], request: GenerationRequest) -> Dict[str, Any]:
        """Apply minimal fixes for critical issues only."""
        try:
            logger.info(f"Applying minimal fixes for: {issues}")
            
            # Fix fake authors
            if "fake_authors" in issues:
                supertask = self._fix_fake_authors(supertask)
            
            # Fix missing fields with minimal defaults
            if any(issue.startswith("missing_") for issue in issues):
                supertask = self._fix_missing_fields(supertask, request)
            
            # Fix critical schema violations
            if "schema_violation" in issues:
                supertask = self._fix_critical_schema(supertask)
            
            return supertask
            
        except Exception as e:
            logger.error(f"Minimal fix failed: {e}")
            return supertask
    
    def _fix_fake_authors(self, supertask: Dict[str, Any]) -> Dict[str, Any]:
        """Replace fake authors with Ari."""
        try:
            for item in supertask.get('flexibleItems', []):
                if 'author' in item and item['author'] != 'Ari':
                    if item['author'].lower() not in ['ari', 'ari (coach)', 'ari - coach']:
                        item['author'] = 'Ari'
            return supertask
        except:
            return supertask

    def _sanitize_authorship_and_quotes(self, supertask: Dict[str, Any]) -> Dict[str, Any]:
        """Cap quotes at one; ensure quote author from allowed list; default content author to 'Ari'."""
        try:
            items = supertask.get('flexibleItems', [])
            if not isinstance(items, list):
                return supertask
            quote_seen = False
            sanitized_items: List[Dict[str, Any]] = []
            # Allowed experts (mirror stage3/progressive)
            allowed_authors = [
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
            for item in items:
                item_type = item.get('type')
                if item_type == 'quote':
                    if quote_seen:
                        continue
                    quote_seen = True
                    author = item.get('author')
                    if author not in allowed_authors:
                        item = {**item, 'author': allowed_authors[0]}
                    sanitized_items.append(item)
                elif item_type == 'content':
                    if not item.get('author'):
                        item = {**item, 'author': 'Ari'}
                    sanitized_items.append(item)
                else:
                    sanitized_items.append(item)
            supertask['flexibleItems'] = sanitized_items[:8]
            return supertask
        except Exception:
            return supertask
    
    def _fix_missing_fields(self, supertask: Dict[str, Any], request: GenerationRequest) -> Dict[str, Any]:
        """Add minimal defaults for missing required fields."""
        defaults = {
            'title': f"{request.title} - {request.difficulty.capitalize()}",
            'dimension': 'mentalHealth',
            'archetype': 'sage',
            'relatedToType': 'GENERIC',
            'relatedToId': f"{request.title.lower().replace(' ', '_')}_{request.difficulty}",
            'estimatedDuration': 300,
            'coinsReward': 100,
            'flexibleItems': [],
            'metadata': {
                'language': 'portuguese',
                'region': 'brazil',
                'created_at': '2025-08-06T00:00:00Z',
                'updated_at': '2025-08-06T00:00:00Z',
                'version': '1.1'
            }
        }
        
        for key, default_value in defaults.items():
            if key not in supertask:
                supertask[key] = default_value
        
        return supertask
    
    def _fix_critical_schema(self, supertask: Dict[str, Any]) -> Dict[str, Any]:
        """Fix critical schema violations."""
        try:
            items = supertask.get('flexibleItems', [])
            
            # Ensure minimum items
            while len(items) < 3:
                items.append({
                    "type": "content",
                    "content": "Conteúdo adicional para completar os requisitos mínimos.",
                    "author": "Ari"
                })
            
            # Limit maximum items
            if len(items) > 8:
                items = items[:8]
            
            supertask['flexibleItems'] = items
            return supertask
            
        except:
            return supertask


class SimplifiedNarrativeGenerator:
    """Generate multiple levels in parallel for progressive journeys."""
    
    def __init__(self, openai_client: OpenAIClient):
        self.generator = SimplifiedGenerator(openai_client)
        self.prompt_generator = MasterPromptGenerator()
    
    def generate_progressive_journey(self, request: GenerationRequest, 
                                   levels: List[str] = None) -> Dict[str, Any]:
        """Generate multiple levels in parallel."""
        try:
            levels = levels or ['foundation', 'application', 'mastery']
            logger.info(f"Generating progressive journey: {len(levels)} levels")
            
            # Generate ALL levels in parallel
            supertasks = {}
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all generation tasks
                futures = {}
                for level in levels:
                    level_prompt = self.prompt_generator.create_progressive_level_prompt(request, level)
                    level_request = GenerationRequest(
                        source_content=request.source_content,
                        difficulty=self._map_level_to_difficulty(level),
                        sequence=request.sequence,
                        title=f"{request.title} - {level.capitalize()}",
                        theme=request.theme
                    )
                    
                    futures[level] = executor.submit(self.generator.generate_supertask, level_request)
                
                # Collect results
                for level, future in futures.items():
                    try:
                        supertasks[level] = future.result()
                        logger.info(f"Generated {level} supertask successfully")
                    except Exception as e:
                        logger.error(f"Failed to generate {level} supertask: {e}")
                        supertasks[level] = self.generator._create_emergency_fallback(
                            GenerationRequest(request.source_content, level, request.sequence, request.title)
                        )
            
            return {
                'supertasks': supertasks,
                'journey_report': self._create_simple_report(supertasks, request.title),
                'metadata': {
                    'levels': levels,
                    'theme': request.theme or request.title,
                    'total_supertasks': len(supertasks)
                }
            }
            
        except Exception as e:
            logger.error(f"Progressive journey generation failed: {e}")
            return self._create_fallback_journey(request, levels)
    
    def _map_level_to_difficulty(self, level: str) -> str:
        """Map level names to difficulty levels."""
        mapping = {
            'foundation': 'beginner',
            'application': 'intermediate',
            'mastery': 'advanced'
        }
        return mapping.get(level, 'beginner')
    
    def _create_simple_report(self, supertasks: Dict[str, Any], title: str) -> str:
        """Create simple journey report."""
        try:
            report_lines = [
                f"# Learning Journey: {title}",
                "",
                "## 🎯 Journey Overview",
                f"**Total Levels**: {len(supertasks)}",
                f"**Generated**: 2025-08-06",
                ""
            ]
            
            level_emojis = {"foundation": "📚", "application": "🛠️", "mastery": "🎓"}
            
            for i, (level, supertask) in enumerate(supertasks.items()):
                emoji = level_emojis.get(level, "⭐")
                duration = supertask.get('estimatedDuration', 300)
                items = len(supertask.get('flexibleItems', []))
                reward = supertask.get('coinsReward', 100)
                
                report_lines.extend([
                    f"## {emoji} Level {i+1}: {level.capitalize()} ({duration//60} min)",
                    f"**Items**: {items}",
                    f"**Reward**: {reward} coins",
                    ""
                ])
            
            total_duration = sum(st.get('estimatedDuration', 300) for st in supertasks.values())
            total_reward = sum(st.get('coinsReward', 100) for st in supertasks.values())
            
            report_lines.extend([
                "## 📊 Journey Summary", 
                f"**Total Time**: {total_duration//60} minutes",
                f"**Total Reward**: {total_reward} coins",
                "",
                "---",
                "*Generated by Simplified Supertask Generator v2.0*"
            ])
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"# Learning Journey Report\n\nGenerated {len(supertasks)} levels successfully."
    
    def _create_fallback_journey(self, request: GenerationRequest, levels: List[str]) -> Dict[str, Any]:
        """Create fallback journey when generation fails."""
        supertasks = {}
        for level in levels:
            level_request = GenerationRequest(
                request.source_content, level, request.sequence, f"{request.title} - {level.capitalize()}"
            )
            supertasks[level] = self.generator._create_emergency_fallback(level_request)
        
        return {
            'supertasks': supertasks,
            'journey_report': f"# Fallback Journey: {request.title}\n\nGenerated {len(levels)} basic levels.",
            'metadata': {'levels': levels, 'theme': request.title, 'total_supertasks': len(supertasks)}
        }


class ComprehensiveNarrativeGenerator:
    """Generates comprehensive journeys with full concept coverage validation."""
    
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        self.generator = SimplifiedGenerator(openai_client)
        self.coverage_validator = CoverageValidator(openai_client)
    
    def is_fallback_content(self, supertask: Dict[str, Any]) -> bool:
        """Simple check - if it's fallback, retry once."""
        return (
            "fallback" in supertask.get('title', '').lower() or 
            len(supertask.get('flexibleItems', [])) == 1
        )
        
    def generate_comprehensive_journey(self, request: GenerationRequest, 
                                     num_levels: int = 5, 
                                     validate_coverage: bool = True) -> Dict[str, Any]:
        """Generate journey with comprehensive concept coverage and validation."""
        
        try:
            logger.info(f"Starting comprehensive journey generation: {num_levels} levels")
            
            # Step 1: Extract all concepts from source material
            logger.info("Extracting comprehensive concepts from source material")
            concept_extraction = self.generator.prompt_generator.extract_comprehensive_concepts(request.source_content)
            
            # Get concepts via AI
            concepts_response = self.openai_client.generate_completion(concept_extraction["extraction_prompt"])
            try:
                concepts_data = json.loads(concepts_response)
                all_concepts = concepts_data.get('main_concepts', [])
                logger.info(f"Extracted {len(all_concepts)} concepts from source material")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse concept extraction: {e}")
                # Fallback to simple generation
                return self._generate_simple_fallback(request, num_levels)
            
            # Step 2: Assign concepts to levels strategically
            logger.info("Assigning concepts to levels strategically")
            concept_assignment = self.generator.prompt_generator.assign_concepts_to_levels(all_concepts, num_levels)
            
            # Step 3: Generate levels with comprehensive prompts
            logger.info(f"Generating {num_levels} levels with comprehensive coverage")
            supertasks = {}
            level_names = list(concept_assignment.keys())[:num_levels]
            
            # Generate all levels in parallel for efficiency
            with ThreadPoolExecutor(max_workers=min(num_levels, 3)) as executor:
                level_futures = {}
                
                for level_name in level_names:
                    assigned_concepts = concept_assignment.get(level_name, [])
                    level_request = GenerationRequest(
                        source_content=request.source_content,
                        difficulty=self._map_level_to_difficulty(level_name),
                        sequence=request.sequence,
                        title=f"{request.title} - {level_name.capitalize()}",
                        theme=request.theme
                    )
                    
                    # Create comprehensive prompt
                    prompt = self.generator.prompt_generator.create_comprehensive_level_prompt(
                        level_request, level_name, assigned_concepts, all_concepts
                    )
                    
                    # Submit for generation
                    future = executor.submit(self._generate_level_with_prompt, prompt, level_name)
                    level_futures[level_name] = future
                
                # Collect results
                for level_name, future in level_futures.items():
                    try:
                        supertask = future.result(timeout=120)  # 2 minute timeout per level
                        supertasks[level_name] = supertask
                        logger.info(f"Generated {level_name} level successfully")
                    except Exception as e:
                        logger.error(f"Failed to generate {level_name} level: {e}")
                        supertasks[level_name] = self._create_emergency_level(request, level_name)
            
            # Step 4: Validate coverage if requested
            coverage_report = {}
            if validate_coverage and len(supertasks) > 0:
                logger.info("Validating comprehensive coverage")
                journey_data = list(supertasks.values())
                coverage_analysis = self.coverage_validator.validate_complete_coverage(journey_data, all_concepts)
                
                coverage_score = coverage_analysis.get('overall_coverage_score', 0)
                logger.info(f"Coverage validation score: {coverage_score}%")
                
                coverage_report = {
                    'coverage_score': coverage_score,
                    'coverage_analysis': coverage_analysis,
                    'improvement_suggestions': self.coverage_validator.suggest_coverage_improvements(coverage_analysis)
                }
                
                # Log coverage issues
                if coverage_score < 80:
                    logger.warning(f"Low coverage score ({coverage_score}%). Consider regenerating.")
                    missing = coverage_analysis.get('missing_concepts', [])
                    if missing:
                        logger.warning(f"Missing concepts: {', '.join(missing)}")
            
            # Step 5: Generate comprehensive report
            journey_report = self._generate_comprehensive_report(
                request, supertasks, all_concepts, concept_assignment, coverage_report
            )
            
            logger.info(f"Comprehensive journey completed: {len(supertasks)} levels")
            
            return {
                'supertasks': supertasks,
                'journey_report': journey_report,
                'metadata': {
                    'levels': list(supertasks.keys()),
                    'theme': request.theme or request.title,
                    'total_supertasks': len(supertasks),
                    'total_concepts': len(all_concepts),
                    'concept_assignment': concept_assignment,
                    'coverage_validation': coverage_report,
                    'generation_method': 'comprehensive_coverage'
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive journey generation failed: {e}")
            return self._generate_simple_fallback(request, num_levels)
    
    def _generate_level_with_prompt(self, prompt: str, level_name: str) -> Dict[str, Any]:
        """Generate a single level using comprehensive prompt."""
        try:
            response = self.openai_client.generate_completion(prompt)
            supertask = json.loads(response)
            
            # Apply quality review
            reviewed_supertask = self.generator.quality_reviewer.review_if_needed(
                supertask, GenerationRequest("", "beginner", "", level_name)
            )
            
            # Check for fallback content and retry once if needed
            if self.is_fallback_content(reviewed_supertask):
                logger.warning(f"Retrying {level_name} due to fallback content")
                response = self.openai_client.generate_completion(prompt)
                supertask = json.loads(response)
                reviewed_supertask = self.generator.quality_reviewer.review_if_needed(
                    supertask, GenerationRequest("", "beginner", "", level_name)
                )
            
            logger.info(f"Successfully generated {level_name} supertask: {len(reviewed_supertask.get('flexibleItems', []))} items")
            return reviewed_supertask
            
        except Exception as e:
            logger.error(f"Level generation failed for {level_name}: {e}")
            raise
    
    def _map_level_to_difficulty(self, level_name: str) -> str:
        """Map level names to difficulty levels."""
        mapping = {
            'foundation': 'beginner',
            'application': 'intermediate',
            'expansion': 'intermediate', 
            'integration': 'advanced',
            'mastery': 'advanced'
        }
        return mapping.get(level_name, 'beginner')
    
    def _create_emergency_level(self, request: GenerationRequest, level_name: str) -> Dict[str, Any]:
        """Create emergency fallback level."""
        emergency_request = GenerationRequest(
            source_content=request.source_content,
            difficulty=self._map_level_to_difficulty(level_name),
            sequence=request.sequence,
            title=f"{request.title} - {level_name.capitalize()} (Fallback)",
            theme=request.theme
        )
        
        return self.generator._create_emergency_fallback(emergency_request)
    
    def _generate_simple_fallback(self, request: GenerationRequest, num_levels: int) -> Dict[str, Any]:
        """Generate simple fallback journey when comprehensive fails."""
        logger.warning("Falling back to simple journey generation")
        
        narrative_generator = SimplifiedNarrativeGenerator(self.openai_client)
        level_names = ['foundation', 'application', 'expansion', 'integration', 'mastery'][:num_levels]
        
        return narrative_generator.generate_progressive_journey(request, level_names)
    
    def _generate_comprehensive_report(self, request: GenerationRequest, supertasks: Dict[str, Any], 
                                     all_concepts: List[Dict], concept_assignment: Dict[str, List[Dict]], 
                                     coverage_report: Dict[str, Any]) -> str:
        """Generate detailed comprehensive journey report."""
        
        try:
            total_items = sum(len(st.get('flexibleItems', [])) for st in supertasks.values())
            total_duration = sum(st.get('estimatedDuration', 300) for st in supertasks.values())
            total_reward = sum(st.get('coinsReward', 50) for st in supertasks.values())
            
            coverage_score = coverage_report.get('coverage_score', 'N/A')
            
            report_lines = [
                f"# Comprehensive Learning Journey: {request.title}",
                "",
                "## 📊 Journey Overview",
                f"- **Levels Generated**: {len(supertasks)}",
                f"- **Total Items**: {total_items}",
                f"- **Estimated Duration**: {total_duration//60} minutes", 
                f"- **Total Rewards**: {total_reward} coins",
                f"- **Source Concepts**: {len(all_concepts)}",
                f"- **Coverage Score**: {coverage_score}{'%' if isinstance(coverage_score, (int, float)) else ''}",
                "",
                "## 🎯 Concept Coverage Strategy",
                ""
            ]
            
            # Add concept assignment details
            for level_name, concepts in concept_assignment.items():
                if level_name in supertasks:
                    concept_names = [c.get('name', 'Unknown') for c in concepts]
                    report_lines.extend([
                        f"### {level_name.capitalize()}",
                        f"- **Focus**: {', '.join(concept_names) if concept_names else 'General concepts'}",
                        f"- **Items**: {len(supertasks[level_name].get('flexibleItems', []))}",
                        f"- **Duration**: {supertasks[level_name].get('estimatedDuration', 300)//60} min",
                        ""
                    ])
            
            # Add coverage analysis
            if coverage_report:
                report_lines.extend([
                    "## 📋 Coverage Validation",
                    f"**Overall Score**: {coverage_score}{'%' if isinstance(coverage_score, (int, float)) else ''}",
                    ""
                ])
                
                improvements = coverage_report.get('improvement_suggestions', [])
                if improvements:
                    report_lines.extend([
                        "### Improvement Suggestions:",
                        *[f"- {suggestion}" for suggestion in improvements],
                        ""
                    ])
            
            # Add source concepts list
            report_lines.extend([
                "## 📚 Source Concepts Identified",
                *[f"- **{c.get('name', f'Concept {i}')}**: {c.get('description', 'No description')}" 
                  for i, c in enumerate(all_concepts, 1)],
                "",
                "---",
                "*Generated by Comprehensive Coverage System v1.0*"
            ])
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {e}")
            return f"# Comprehensive Journey: {request.title}\n\nGenerated {len(supertasks)} levels with concept coverage validation."