"""
Comprehensive CLI Pipeline Test for Lyfe Supertask Knowledge Generator

This test validates the complete pipeline from raw content to supertask JSON:
1. Stage 1: Raw content → Preprocessed templates
2. Stage 3: Templates → Supertask JSON files

The test ensures:
- Full pipeline integration works correctly
- Template compliance with supertask schema
- JSON format compliance with test.json structure
- Ari persona consistency throughout the pipeline
- Proper file structure and organization
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
from typing import Dict, Any

from src.lyfe_kt.cli import main
from src.lyfe_kt.config_loader import get_config, load_config


class TestCLIFullPipeline:
    """Test the complete CLI pipeline from raw content to supertask JSON."""
    
    @pytest.fixture
    def runner(self):
        """Create Click CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace with proper directory structure."""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create work directory structure
        (workspace / "work" / "01_raw").mkdir(parents=True)
        (workspace / "work" / "02_preprocessed").mkdir(parents=True)
        (workspace / "work" / "03_output").mkdir(parents=True)
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_raw_content(self, temp_workspace):
        """Create sample raw content for testing."""
        raw_content = """# Desenvolvendo Hábitos Matinais Saudáveis

## Introdução

Criar uma rotina matinal consistente é fundamental para o bem-estar físico e mental. Este guia apresenta estratégias baseadas em ciência comportamental para desenvolver hábitos matinais duradouros.

## Por que os Hábitos Matinais Importam

A manhã é o momento ideal para estabelecer o tom do dia. Quando criamos rotinas matinais consistentes:

- Reduzimos a fadiga de decisão
- Aumentamos a produtividade
- Melhoramos o bem-estar mental
- Fortalecemos a disciplina pessoal

## Estratégias para Implementação

### 1. Comece Pequeno

Seguindo os princípios de micro-hábitos, comece com ações extremamente simples:

- Beber um copo d'água ao acordar
- Fazer 5 respirações profundas
- Escrever uma frase de gratidão

### 2. Conecte a Gatilhos Existentes

Vincule novos hábitos a ações que já faz automaticamente:

- Após escovar os dentes → meditar por 2 minutos
- Após tomar café → ler uma página de livro
- Após se vestir → fazer alongamento

### 3. Prepare o Ambiente

Reduza a fricção preparando tudo na noite anterior:

- Deixe a roupa separada
- Prepare o café da manhã
- Coloque o livro ao lado da cama

## Conclusão

Hábitos matinais saudáveis são construídos gradualmente. Comece pequeno, seja consistente e celebre cada pequena vitória. A chave é tornar as ações tão simples que seja impossível falhar.
"""
        
        raw_file = temp_workspace / "work" / "01_raw" / "habitos_matinais.md"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(raw_content)
        
        return str(raw_file)
    
    @pytest.fixture
    def config_setup(self):
        """Ensure configuration is loaded for tests."""
        try:
            config = get_config()
        except ValueError:
            load_config()
            config = get_config()
        return config
    
    def test_full_pipeline_single_file(self, runner, temp_workspace, sample_raw_content, config_setup):
        """
        Test complete pipeline with a single file:
        Raw content → Preprocessed template → Supertask JSON
        """
        # Stage 1: Preprocess raw content to template
        preprocess_output = temp_workspace / "work" / "02_preprocessed"
        
        # Run preprocessing command
        preprocess_result = runner.invoke(
            main,
            [
                'preprocess', 'file',
                sample_raw_content,
                str(preprocess_output),
                '--progress'
            ]
        )
        
        # Verify preprocessing succeeded
        assert preprocess_result.exit_code == 0, f"Preprocessing failed: {preprocess_result.output}"
        
        # Check that template was generated
        template_files = list(preprocess_output.glob("*.md"))
        assert len(template_files) > 0, "No template files generated in preprocessing"
        
        template_file = template_files[0]
        assert template_file.exists(), "Template file was not created"
        
        # Verify template has proper structure
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        assert template_content.startswith('---'), "Template missing frontmatter"
        assert 'title:' in template_content, "Template missing title in frontmatter"
        assert 'dimension:' in template_content, "Template missing dimension in frontmatter"
        
        # Stage 3: Generate supertask JSON from template
        generation_output = temp_workspace / "work" / "03_output"
        
        # Run generation command
        generation_result = runner.invoke(
            main,
            [
                'generate', 'template',
                str(template_file),
                str(generation_output),
                '--progress'
            ]
        )
        
        # Verify generation succeeded
        assert generation_result.exit_code == 0, f"Generation failed: {generation_result.output}"
        
        # Check that JSON files were generated
        json_files = list(generation_output.glob("*.json"))
        assert len(json_files) > 0, "No JSON files generated"
        
        # Verify JSON structure compliance
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Verify required fields
            required_fields = [
                'title', 'dimension', 'archetype', 'relatedToType', 
                'relatedToId', 'estimatedDuration', 'coinsReward', 'flexibleItems'
            ]
            
            for field in required_fields:
                assert field in json_data, f"Missing required field: {field} in {json_file.name}"
            
            # Verify flexibleItems structure
            flexible_items = json_data['flexibleItems']
            assert isinstance(flexible_items, list), "flexibleItems must be a list"
            
            for item in flexible_items:
                assert 'type' in item, "flexibleItem missing 'type' field"
                assert item['type'] in ['content', 'quote', 'quiz'], f"Invalid flexibleItem type: {item['type']}"
                
                if item['type'] == 'quiz':
                    assert 'options' in item, "Quiz item missing 'options'"
                    assert 'correctAnswer' in item, "Quiz item missing 'correctAnswer'"
                    assert isinstance(item['options'], list), "Quiz options must be a list"
                    assert isinstance(item['correctAnswer'], int), "correctAnswer must be integer"
            
            # Verify metadata presence
            assert 'metadata' in json_data, "Missing metadata field"
            metadata = json_data['metadata']
            assert 'generated_by' in metadata, "Missing generation metadata"
            assert 'ari_persona_applied' in metadata, "Missing Ari persona metadata"
    
    def test_full_pipeline_directory_batch(self, runner, temp_workspace, config_setup):
        """
        Test complete pipeline with directory batch processing:
        Multiple raw files → Multiple templates → Multiple supertask JSONs
        """
        # Create multiple raw content files
        raw_dir = temp_workspace / "work" / "01_raw"
        
        # Sample content 1: Physical Health
        content1 = """# Exercícios Matinais Simples

## Introdução
Exercícios matinais simples podem transformar seu dia. Este guia apresenta uma rotina de 10 minutos para começar o dia com energia.

## Benefícios dos Exercícios Matinais
- Acelera o metabolismo
- Melhora o humor
- Aumenta a energia para o dia
- Fortalece o sistema imunológico

## Rotina de 10 Minutos

### Aquecimento (2 minutos)
- Alongamento dos braços
- Rotação do pescoço
- Marcha no lugar

### Exercícios principais (6 minutos)
- 20 polichinelos
- 10 flexões (adaptadas se necessário)
- 15 agachamentos
- Prancha por 30 segundos

### Relaxamento (2 minutos)
- Respiração profunda
- Alongamento final

## Conclusão
Consistência é mais importante que intensidade. Comece devagar e aumente gradualmente.
"""
        
        # Sample content 2: Mental Health
        content2 = """# Técnicas de Mindfulness para Iniciantes

## Introdução
Mindfulness é uma prática simples que pode reduzir o estresse e melhorar o bem-estar mental. Este guia apresenta técnicas básicas para iniciantes.

## O que é Mindfulness
Mindfulness é a prática de estar presente no momento atual, observando pensamentos e sensações sem julgamento.

## Benefícios Científicos
- Reduz ansiedade e estresse
- Melhora a concentração
- Aumenta a autorregulação emocional
- Fortalece o sistema imunológico

## Técnicas Básicas

### Respiração Consciente
1. Sente-se confortavelmente
2. Feche os olhos suavemente
3. Observe sua respiração natural
4. Quando a mente divagar, volte à respiração

### Scanner Corporal
1. Deite-se confortavelmente
2. Comece pelos pés
3. Observe cada parte do corpo
4. Note sensações sem tentar mudá-las

## Conclusão
Pratique 5 minutos diariamente. A constância é mais importante que a duração.
"""
        
        # Write content files
        (raw_dir / "exercicios_matinais.md").write_text(content1, encoding='utf-8')
        (raw_dir / "mindfulness_iniciantes.md").write_text(content2, encoding='utf-8')
        
        # Stage 1: Batch preprocessing
        preprocess_output = temp_workspace / "work" / "02_preprocessed"
        
        preprocess_result = runner.invoke(
            main,
            [
                'preprocess', 'directory',
                str(raw_dir),
                str(preprocess_output),
                '--progress'
            ]
        )
        
        # Verify batch preprocessing succeeded
        assert preprocess_result.exit_code == 0, f"Batch preprocessing failed: {preprocess_result.output}"
        
        # Check that multiple templates were generated
        template_files = list(preprocess_output.glob("**/*.md"))
        assert len(template_files) >= 2, f"Expected at least 2 templates, got {len(template_files)}"
        
        # Stage 3: Batch generation
        generation_output = temp_workspace / "work" / "03_output"
        
        generation_result = runner.invoke(
            main,
            [
                'generate', 'pipeline',
                str(preprocess_output),
                str(generation_output),
                '--difficulty', 'both',
                '--progress'
            ]
        )
        
        # Verify batch generation succeeded
        assert generation_result.exit_code == 0, f"Batch generation failed: {generation_result.output}"
        
        # Check that multiple JSON files were generated
        json_files = list(generation_output.glob("**/*.json"))
        assert len(json_files) >= 2, f"Expected at least 2 JSON files, got {len(json_files)}"
        
        # Verify each generated JSON
        beginner_files = [f for f in json_files if 'beginner' in f.name]
        advanced_files = [f for f in json_files if 'advanced' in f.name]
        
        # Should have both difficulty levels
        assert len(beginner_files) >= 1, "Missing beginner-level supertasks"
        assert len(advanced_files) >= 1, "Missing advanced-level supertasks"
        
        # Verify content differentiation between difficulty levels
        for beginner_file in beginner_files:
            with open(beginner_file, 'r') as f:
                beginner_data = json.load(f)
            
            assert 'beginner' in beginner_data['title'].lower(), "Beginner file should have 'beginner' in title"
            assert beginner_data['metadata']['difficulty_level'] == 'beginner', "Metadata should reflect beginner difficulty"
        
        for advanced_file in advanced_files:
            with open(advanced_file, 'r') as f:
                advanced_data = json.load(f)
            
            assert 'advanced' in advanced_data['title'].lower(), "Advanced file should have 'advanced' in title"
            assert advanced_data['metadata']['difficulty_level'] == 'advanced', "Metadata should reflect advanced difficulty"
    
    def test_pipeline_error_handling(self, runner, temp_workspace, config_setup):
        """Test pipeline error handling for invalid inputs."""
        # Test with non-existent input file
        result = runner.invoke(
            main,
            [
                'preprocess', 'file',
                'nonexistent_file.md',
                str(temp_workspace / "output"),
                '--progress'
            ]
        )
        
        # Should handle error gracefully
        assert result.exit_code != 0, "Should fail with non-existent input file"
        assert "Error" in result.output or "error" in result.output, "Should show error message"
    
    def test_pipeline_output_validation(self, runner, temp_workspace, sample_raw_content, config_setup):
        """Test that pipeline output passes validation checks."""
        # Run complete pipeline
        preprocess_output = temp_workspace / "work" / "02_preprocessed"
        generation_output = temp_workspace / "work" / "03_output"
        
        # Preprocessing
        preprocess_result = runner.invoke(
            main,
            [
                'preprocess', 'file',
                sample_raw_content,
                str(preprocess_output),
            ]
        )
        assert preprocess_result.exit_code == 0
        
        # Generation
        template_file = list(preprocess_output.glob("*.md"))[0]
        generation_result = runner.invoke(
            main,
            [
                'generate', 'template',
                str(template_file),
                str(generation_output),
            ]
        )
        assert generation_result.exit_code == 0
        
        # Validate output files
        json_files = list(generation_output.glob("*.json"))
        
        for json_file in json_files:
            # Test JSON parsing
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Test required schema compliance
            self._validate_supertask_schema(json_data)
    
    def _validate_supertask_schema(self, json_data: Dict[str, Any]) -> None:
        """Validate that JSON data matches expected supertask schema."""
        # Required top-level fields
        required_fields = {
            'title': str,
            'dimension': str,
            'archetype': str,
            'relatedToType': str,
            'relatedToId': str,
            'estimatedDuration': int,
            'coinsReward': int,
            'flexibleItems': list,
            'metadata': dict
        }
        
        for field, expected_type in required_fields.items():
            assert field in json_data, f"Missing required field: {field}"
            assert isinstance(json_data[field], expected_type), f"Field {field} should be {expected_type.__name__}"
        
        # Validate dimension values
        valid_dimensions = ['physicalHealth', 'mentalHealth', 'relationships', 'work', 'spirituality']
        assert json_data['dimension'] in valid_dimensions, f"Invalid dimension: {json_data['dimension']}"
        
        # Validate archetype values
        valid_archetypes = ['warrior', 'explorer', 'sage', 'ruler']
        assert json_data['archetype'] in valid_archetypes, f"Invalid archetype: {json_data['archetype']}"
        
        # Validate relatedToType values
        valid_related_types = ['HABITBP', 'GENERIC']
        assert json_data['relatedToType'] in valid_related_types, f"Invalid relatedToType: {json_data['relatedToType']}"
        
        # Validate flexibleItems structure
        for i, item in enumerate(json_data['flexibleItems']):
            assert 'type' in item, f"flexibleItem {i} missing 'type'"
            assert item['type'] in ['content', 'quote', 'quiz'], f"Invalid flexibleItem type: {item['type']}"
            
            if item['type'] == 'quiz':
                assert 'options' in item, f"Quiz item {i} missing 'options'"
                assert 'correctAnswer' in item, f"Quiz item {i} missing 'correctAnswer'"
                assert isinstance(item['options'], list), f"Quiz options {i} must be list"
                assert isinstance(item['correctAnswer'], int), f"correctAnswer {i} must be int"
                assert 0 <= item['correctAnswer'] < len(item['options']), f"correctAnswer {i} out of range"
        
        # Validate metadata
        metadata = json_data['metadata']
        expected_metadata_fields = ['generated_by', 'ari_persona_applied', 'difficulty_level']
        for field in expected_metadata_fields:
            assert field in metadata, f"Missing metadata field: {field}"
    
    def test_ari_persona_consistency(self, runner, temp_workspace, sample_raw_content, config_setup):
        """Test that Ari persona is consistently applied throughout the pipeline."""
        # Run complete pipeline
        preprocess_output = temp_workspace / "work" / "02_preprocessed"
        generation_output = temp_workspace / "work" / "03_output"
        
        # Full pipeline
        preprocess_result = runner.invoke(
            main,
            ['preprocess', 'file', sample_raw_content, str(preprocess_output)]
        )
        assert preprocess_result.exit_code == 0
        
        template_file = list(preprocess_output.glob("*.md"))[0]
        generation_result = runner.invoke(
            main,
            ['generate', 'template', str(template_file), str(generation_output)]
        )
        assert generation_result.exit_code == 0
        
        # Verify Ari persona application
        json_files = list(generation_output.glob("*.json"))
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Check Ari persona metadata
            assert json_data['metadata']['ari_persona_applied'] is True, "Ari persona should be applied"
            
            # Check for Ari-style content (Portuguese, brevity, evidence-based)
            flexible_items = json_data['flexibleItems']
            
            for item in flexible_items:
                if item['type'] == 'content' and 'content' in item:
                    content = item['content']
                    # Ari prefers Portuguese and evidence-based content
                    assert any(portuguese_word in content.lower() for portuguese_word in 
                             ['você', 'ser', 'pode', 'quando', 'como', 'que', 'para']), \
                           "Content should be in Portuguese (Ari's preferred language)" 