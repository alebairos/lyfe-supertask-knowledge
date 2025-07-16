# Stage 3 Generation Pipeline Feature PRD

**TODO ID**: 23 - stage3-generation  
**Status**: In Progress  
**Dependencies**: stage1-preprocessing (TODO 22) - ✅ COMPLETED  
**Priority**: HIGH - Core Pipeline Component  
**Estimated Duration**: 4-6 hours  

## Overview

Implement the Stage 3 generation pipeline that transforms filled markdown templates into exact test.json structure-compliant supertask JSON files. This component completes the new 3-stage pipeline approach by converting preprocessed templates into platform-ready supertasks with Ari persona consistency.

## Current State Analysis

### Existing Infrastructure
- **Generation Prompts**: `src/config/generation_prompts.yaml` (346 lines) - ✅ COMPLETED
- **Configuration System**: Extended `src/lyfe_kt/config_loader.py` with 8 generation functions - ✅ COMPLETED
- **Template System**: `src/templates/knowledge_task_input_template.md` - ✅ COMPLETED
- **Stage 1 Pipeline**: `src/lyfe_kt/stage1_preprocessing.py` - ✅ COMPLETED
- **Test Coverage**: 38/38 generation prompts tests passing (100% success rate)

### Work Directory Structure
```
work/
├── 01_raw/                 # Stage 1 Input: Raw content files
├── 02_preprocessed/        # Stage 1 Output: Filled templates (.md)
│   ├── sample_filled_template.md
│   ├── sample_ari_analysis.json
│   └── sample_oracle_context.json
├── 03_output/              # Stage 3 Output: Final JSON supertasks
│   ├── sample_beginner.json
│   └── sample_advanced.json
└── reports/                # Processing reports
    └── generation_report.md
```

### Existing Components to Reuse
- **OpenAI Client**: `src/lyfe_kt/openai_client.py` - Robust LLM integration
- **Configuration Loading**: Generation prompts with validation and caching
- **Error Handling**: Established error patterns and logging
- **Progress Reporting**: CLI progress reporting system
- **Validation Framework**: Output validation for JSON structure compliance

## Requirements

### Core Functionality

#### 1. Template Processing
- **Input**: Filled markdown templates from `work/02_preprocessed/`
- **Processing**: Parse frontmatter and content sections
- **Validation**: Ensure template completeness and structure
- **Error Handling**: Graceful handling of malformed templates

#### 2. AI-Powered Generation
- **LLM Integration**: Use OpenAI GPT-4 for JSON generation
- **Prompt System**: Apply generation prompts with context substitution
- **Ari Persona**: Maintain consistent voice and framework integration
- **Difficulty Scaling**: Generate both beginner and advanced versions

#### 3. JSON Structure Compliance
- **Exact Format**: Match test.json structure precisely
- **Required Fields**: Preserve all mandatory fields
  - `title`, `dimension`, `archetype`, `relatedToType`, `relatedToId`
  - `estimatedDuration`, `coinsReward`, `flexibleItems`, `metadata`
- **FlexibleItems**: Proper array structure with type, content, options
- **Validation**: Comprehensive JSON structure validation

#### 4. Batch Processing
- **Multi-File**: Process multiple templates simultaneously
- **Progress Tracking**: Real-time progress reporting
- **Error Isolation**: Individual file error handling
- **Performance**: Efficient processing for production workloads

### Technical Requirements

#### 1. Generation Pipeline Components

##### TemplateProcessor
```python
class TemplateProcessor:
    """Process filled markdown templates for JSON generation."""
    
    def parse_template(self, template_path: str) -> Dict[str, Any]:
        """Parse template frontmatter and content sections."""
        
    def validate_template(self, template_data: Dict[str, Any]) -> bool:
        """Validate template completeness and structure."""
        
    def extract_metadata(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata for JSON generation."""
```

##### JSONGenerator
```python
class JSONGenerator:
    """Generate supertask JSON from processed templates."""
    
    def generate_supertask(self, template_data: Dict[str, Any], 
                          difficulty: str = "beginner") -> Dict[str, Any]:
        """Generate single supertask JSON with specified difficulty."""
        
    def generate_multiple_supertasks(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate both beginner and advanced versions."""
        
    def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
        """Validate generated JSON against test.json structure."""
```

##### GenerationPipeline
```python
class GenerationPipeline:
    """Main orchestration for Stage 3 generation."""
    
    def process_template(self, template_path: str, output_dir: str) -> Dict[str, Any]:
        """Process single template through generation pipeline."""
        
    def process_directory(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Process directory of templates with batch processing."""
        
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive processing report."""
```

#### 2. Configuration Integration
- **Generation Prompts**: Use `load_generation_prompts()` for prompt access
- **Difficulty Configuration**: Apply `get_difficulty_configuration()` for scaling
- **Preset Management**: Utilize `get_generation_preset()` for template types
- **Validation**: Employ `validate_generated_json_structure()` for compliance

#### 3. Error Handling
- **Custom Exceptions**: `GenerationError` for pipeline-specific errors
- **Graceful Degradation**: Continue processing other files on individual failures
- **Detailed Logging**: Comprehensive error reporting and debugging
- **Recovery Mechanisms**: Retry logic for transient failures

### Input/Output Specifications

#### Input: Filled Markdown Templates
```markdown
---
title: "Sample Habit Formation"
dimension: "physicalHealth"
archetype: "warrior"
difficulty: "beginner"
estimated_duration: 300
coins_reward: 50
---

# Sample Habit Formation

## Content Section
This is the main educational content...

## Quiz Section
1. What is the first step in habit formation?
   a) Set a large goal
   b) Start with tiny habits
   c) Focus on motivation
   d) Track everything

Correct: b) Start with tiny habits
Explanation: According to BJ Fogg's Tiny Habits framework...
```

#### Output: Supertask JSON
```json
{
  "title": "Sample Habit Formation - Beginner",
  "dimension": "physicalHealth",
  "archetype": "warrior",
  "relatedToType": "HABITBP",
  "relatedToId": "habit_formation_basics",
  "estimatedDuration": 300,
  "coinsReward": 50,
  "flexibleItems": [
    {
      "type": "content",
      "content": "This is the main educational content...",
      "author": "Ari"
    },
    {
      "type": "quiz",
      "content": "What is the first step in habit formation?",
      "options": [
        "Set a large goal",
        "Start with tiny habits",
        "Focus on motivation",
        "Track everything"
      ],
      "correctAnswer": 1,
      "explanation": "According to BJ Fogg's Tiny Habits framework..."
    }
  ],
  "metadata": {
    "generated_by": "lyfe-kt-stage3",
    "generation_timestamp": "2025-01-16T10:30:00Z",
    "ari_persona_applied": true,
    "difficulty_level": "beginner",
    "source_template": "sample_filled_template.md"
  }
}
```

### Quality Assurance Requirements

#### 1. Validation Standards
- **JSON Structure**: 100% compliance with test.json format
- **Required Fields**: All mandatory fields present and correctly typed
- **FlexibleItems**: Proper array structure with valid types
- **Ari Voice**: Consistent persona voice throughout content

#### 2. Testing Requirements
- **Unit Tests**: Core functionality testing for each component
- **Integration Tests**: End-to-end pipeline testing
- **Real Data Testing**: Sample template processing verification
- **Error Scenario Testing**: Malformed input and API failure handling

#### 3. Performance Standards
- **Processing Speed**: < 30 seconds per template
- **Memory Usage**: Efficient memory management for batch processing
- **API Optimization**: Efficient LLM token usage
- **Scalability**: Support for 100+ templates in single batch

### Integration Requirements

#### 1. CLI Integration
- **Command**: `lyfe-kt generate` for Stage 3 processing
- **Options**: 
  - `--input-dir`: Input directory with templates
  - `--output-dir`: Output directory for JSON files
  - `--difficulty`: Generate specific difficulty level
  - `--batch-size`: Batch processing size
- **Progress**: Real-time progress reporting
- **Error Handling**: Proper exit codes and error messages

#### 2. Pipeline Integration
- **Stage 1 Output**: Direct consumption of Stage 1 preprocessing output
- **Work Directory**: Proper work directory organization
- **Report Generation**: Consistent reporting format
- **Configuration**: Seamless integration with existing config system

### Implementation Plan

#### Phase 1: Core Implementation (3-4 hours)
1. **TemplateProcessor Class**: Markdown parsing and validation
2. **JSONGenerator Class**: AI-powered JSON generation
3. **GenerationPipeline Class**: Main orchestration
4. **Error Handling**: Custom exceptions and logging

#### Phase 2: CLI Integration (1 hour)
1. **Command Implementation**: Add generate command group
2. **Option Handling**: Command-line argument processing
3. **Progress Reporting**: Real-time feedback integration
4. **Error Handling**: Proper exit codes and messages

#### Phase 3: Testing & Validation (1-2 hours)
1. **Unit Tests**: Core functionality testing
2. **Integration Tests**: End-to-end pipeline testing
3. **Real Data Testing**: Sample template processing
4. **Performance Testing**: Batch processing validation

### Dependencies and Risks

#### Dependencies
- **Generation Prompts**: `src/config/generation_prompts.yaml` - ✅ COMPLETED
- **Stage 1 Pipeline**: Must produce valid filled templates - ✅ COMPLETED
- **OpenAI API**: Reliable API access for generation
- **Configuration System**: Generation prompt loading functions - ✅ COMPLETED

#### Risk Mitigation
- **API Failures**: Implement retry logic and fallback mechanisms
- **Template Parsing**: Robust error handling for malformed templates
- **JSON Validation**: Comprehensive validation before output
- **Performance**: Implement batch processing optimization

### Success Metrics

#### Functional Metrics
- **Template Processing**: 100% success rate for valid templates
- **JSON Compliance**: 100% compliance with test.json structure
- **Ari Voice**: Consistent persona voice across all generated content
- **Difficulty Scaling**: Successful generation of both beginner/advanced versions

#### Performance Metrics
- **Processing Speed**: < 30 seconds per template average
- **Batch Processing**: Support for 50+ templates per batch
- **Memory Usage**: < 500MB peak memory usage
- **API Efficiency**: Optimized token usage for cost effectiveness

#### Quality Metrics
- **Test Coverage**: 95%+ test coverage for new functionality
- **Error Handling**: Graceful handling of all error scenarios
- **Validation**: 100% validation success for compliant JSON
- **Documentation**: Complete API documentation and examples

### Future Enhancements

#### Planned Improvements
1. **Advanced Template Types**: Support for multiple template variants
2. **Quality Scoring**: Automated quality assessment for generated content
3. **Performance Optimization**: Parallel processing for batch operations
4. **API Integration**: REST API endpoints for external integration
5. **Monitoring**: Real-time performance and quality metrics

#### Technical Debt Considerations
- **Template Parsing**: May need enhancement for complex templates
- **Error Recovery**: Advanced recovery mechanisms for API failures
- **Caching**: Result caching for repeated template processing
- **Optimization**: Further LLM prompt optimization for efficiency

---

**Implementation Status**: Ready to begin implementation  
**Next Steps**: Start with Phase 1 core implementation  
**Estimated Completion**: 4-6 hours total development time 