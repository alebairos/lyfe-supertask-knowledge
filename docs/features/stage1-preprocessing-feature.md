# Stage 1 Preprocessing Pipeline Feature PRD

**TODO ID**: 22 - stage1-preprocessing  
**Status**: Pending  
**Dependencies**: generation-prompts (TODO 21)  
**Priority**: HIGH - Core Pipeline Component  
**Estimated Duration**: 4-6 hours  

## Overview

Implement the Stage 1 preprocessing pipeline that transforms raw content from multiple file formats into filled markdown templates using Ari persona and Oracle data integration. This replaces the current Stage 1 implementation with a new 3-stage pipeline approach.

## Current State Analysis

### Existing Implementation
- **Current Stage 1**: `src/lyfe_kt/stage1_functions.py` (600+ lines) - JSON-to-JSON processing
- **Integration Layer**: `src/lyfe_kt/stage1_integration.py` (748 lines) - Pipeline orchestration
- **CLI Interface**: Stage 1 commands in `src/lyfe_kt/cli.py`
- **Test Coverage**: 273 tests passing (100% success rate)

### Work Directory Structure
```
work/
├── 01_raw/                 # Stage 1 Input: Raw content files (multiple formats)
│   └── levantar_da_cama/   # Example: test.json, PNG files
├── 02_preprocessed/        # Stage 1 Output: Filled templates (.md)
│   └── levantar_da_cama/   # Example: filled template files
├── 03_output/              # Stage 3 Output: Final JSON supertasks
│   └── levantar_da_cama/   # Example: generated supertask JSON files
└── reports/                # Analysis and compliance reports
    ├── supertask_analysis.md
    ├── json_format_compliance_success.md
    └── final_compliance_report.md
```

### Reuse Opportunities
- **Batch Processing**: Stage 1 integration layer provides robust batch processing
- **Error Handling**: Existing error resilience patterns can be adapted
- **Progress Reporting**: CLI progress reporting system can be extended
- **Validation**: Output validation framework can validate template compliance

## Requirements

### Core Functionality

#### 1. Multi-Format Input Processing
- **Supported Formats**: `.md`, `.json`, `.pdf`, `.txt`, `.docx`
- **Content Extraction**: Format-specific parsing and content extraction
- **Metadata Preservation**: Maintain source file metadata and structure
- **Error Handling**: Graceful handling of malformed or unsupported files

#### 2. Ari Persona Integration
- **Voice Application**: Apply Ari's communication patterns throughout content
- **Framework Integration**: Natural integration of 9 expert frameworks
- **Cultural Context**: Brazilian Portuguese forms and cultural sensitivity
- **Coaching Style**: TARS-inspired brevity with engagement progression

#### 3. Oracle Data Integration
- **Contextual Enhancement**: Use filtered Oracle data for content enrichment
- **Habit Context**: Reference relevant habits from filtered habitos.csv
- **Trail Patterns**: Apply learning progression patterns from Trilhas.csv
- **Objective Mapping**: Connect content to relevant objectives

#### 4. Template Generation
- **Template Filling**: Generate filled `knowledge_task_input_template.md`
- **Content Enhancement**: AI-powered content improvement with Ari voice
- **Structure Compliance**: Ensure template adherence with all required sections
- **Variable Substitution**: Dynamic content based on input analysis

### Work Directory Management

#### 1. Stage-Based Organization (3-Stage Pipeline)
```
work/
├── 01_raw/                      # Stage 1 Input: Raw content files
│   ├── [topic_name]/            # Organized by topic/content area
│   │   ├── source.md            # Primary content file
│   │   ├── reference.pdf        # Supporting materials
│   │   └── metadata.json        # Optional metadata
│   └── batch_[timestamp]/       # Batch processing organization
├── 02_preprocessed/             # Stage 1 Output → Stage 3 Input: Filled templates
│   ├── [topic_name]/            # Matching input organization
│   │   ├── filled_template.md   # Main preprocessed output
│   │   ├── ari_analysis.json    # Ari persona analysis results
│   │   └── oracle_context.json  # Applied Oracle data context
│   └── batch_[timestamp]/       # Batch results organization
├── 03_output/                   # Stage 3 Output: Final JSON supertasks
│   ├── [topic_name]/            # Final supertask outputs
│   │   ├── beginner_supertask.json    # Beginner difficulty version
│   │   ├── advanced_supertask.json    # Advanced difficulty version
│   │   └── generation_metadata.json   # Generation process metadata
│   └── batch_[timestamp]/       # Batch generation results
└── reports/                     # Execution reports
    ├── supertasks_2024-12-15_14-30-25.md    # Single report per execution
    ├── supertasks_2024-12-15_16-45-12.md    # Format: supertasks_YYYY-MM-DD_HH-MM-SS.md
    └── supertasks_2024-12-16_09-15-33.md    # Each contains complete analysis
```

#### 2. File Organization Standards
- **Topic-Based Grouping**: Organize files by content topic/theme
- **Timestamp Tracking**: Include processing timestamps in all outputs
- **Metadata Preservation**: Maintain source file relationships and lineage
- **Batch Processing**: Support for processing multiple files as batches

### Comprehensive Reporting System

#### 1. Single Execution Report
**Report File**: `work/reports/supertasks_YYYY-MM-DD_HH-MM-SS.md`

**Required Sections**:
```markdown
# Stage 1 Preprocessing Analysis Report
**Generated**: [ISO timestamp]
**Topic**: [content topic/theme]
**Input Directory**: work/01_raw/[topic_name]
**Output Directory**: work/02_preprocessed/[topic_name]

## Processing Summary
- **Total Files Processed**: [count]
- **Templates Generated**: [count] 
- **Success Rate**: [percentage]
- **Processing Duration**: [time]

## Input Analysis
### File Format Distribution
- **Markdown Files**: [count] ([percentage])
- **JSON Files**: [count] ([percentage])
- **PDF Files**: [count] ([percentage])
- **Text Files**: [count] ([percentage])

### Content Characteristics
- **Primary Language**: [detected language]
- **Content Complexity**: [beginner/intermediate/advanced]
- **Topic Areas**: [identified themes]
- **Estimated Learning Duration**: [minutes]

## Ari Persona Integration
### Framework Application
- **Tiny Habits**: [applied/not applied] - [reasoning]
- **Behavioral Design**: [applied/not applied] - [reasoning]
- **Huberman Protocols**: [applied/not applied] - [reasoning]
- **PERMA Model**: [applied/not applied] - [reasoning]
- **Flow Theory**: [applied/not applied] - [reasoning]
- **CBT Principles**: [applied/not applied] - [reasoning]
- **NLP Techniques**: [applied/not applied] - [reasoning]
- **Positive Psychology**: [applied/not applied] - [reasoning]
- **Mindfulness**: [applied/not applied] - [reasoning]

### Voice Consistency Analysis
- **TARS Brevity Score**: [0-100] - [assessment]
- **Portuguese Masculine Forms**: [compliance percentage]
- **Engagement Progression**: [linear/adaptive/dynamic]
- **Coaching Opportunities**: [count] identified

## Oracle Data Utilization
### Context Integration
- **Relevant Habits**: [count] from habitos.csv
- **Trail Patterns**: [count] from Trilhas.csv  
- **Objective Mapping**: [mapped/unmapped] to Objetivos.csv
- **LyfeCoach Integration**: [percentage] persona alignment

### Content Enhancement
- **Habit Formation Context**: [enhanced/standard]
- **Learning Progression**: [trail-based/custom]
- **Goal Alignment**: [objective-mapped/standalone]

## Template Compliance
### Structure Validation
- **Frontmatter Complete**: [✅/❌] - [missing fields if any]
- **Required Sections**: [✅/❌] - [checklist]
- **Content Organization**: [✅/❌] - [assessment]
- **Variable Substitution**: [✅/❌] - [success rate]

### Quality Metrics
- **Content Clarity**: [1-10 score] - [reasoning]
- **Educational Value**: [1-10 score] - [assessment]
- **Engagement Potential**: [1-10 score] - [analysis]
- **Ari Voice Authenticity**: [1-10 score] - [evaluation]

## Generated Templates
### [Template 1 Name]
- **Source**: `[source_file_path]`
- **Output**: `[template_file_path]`
- **Content Sections**: [count]
- **Learning Objectives**: [count]
- **Quiz Questions**: [count]
- **Estimated Duration**: [minutes]
- **Difficulty Level**: [beginner/advanced]

## Cross-File Analysis (for batch processing)
- **Common Themes**: [identified patterns across files]
- **Difficulty Distribution**: [beginner/advanced ratio]
- **Content Patterns**: [structural similarities]
- **Aggregate Metrics**: [average scores, framework application rates]

## Recommendations
### Content Improvements
- [Specific recommendations for content enhancement]
- [Suggested framework applications]
- [Learning objective refinements]

### Ari Voice Enhancements
- [Voice consistency improvements]
- [Framework integration suggestions]
- [Engagement optimization recommendations]

### Oracle Data Opportunities
- [Additional habit context suggestions]
- [Trail progression enhancements]
- [Objective alignment improvements]

## Error Log
### Processing Errors
- **File Parsing Errors**: [count] - [details if any]
- **Template Generation Errors**: [count] - [details if any]  
- **Ari Integration Warnings**: [count] - [details if any]
- **Oracle Context Issues**: [count] - [details if any]

## Next Steps
1. [Recommended actions for content improvement]
2. [Template refinement suggestions]
3. [Quality assurance recommendations]
```

#### 2. Report Content (All-in-One)
**Note**: All analysis sections are included in the single execution report file.

**Additional Sections** (when processing multiple files):
- **Cross-File Analysis**: Common themes, difficulty distribution, content patterns
- **Aggregate Metrics**: Average quality scores, framework application rates
- **Batch Overview**: Total files processed, success rate, processing time

### Implementation Architecture

#### 1. Enhanced Stage 1 Functions
**File**: `src/lyfe_kt/stage1_preprocessing.py` (new file)

**Core Classes**:
```python
class PreprocessingPipeline:
    """Main preprocessing pipeline orchestrator."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ari_persona = load_ari_persona()
        self.oracle_data = load_oracle_data_filtered()
        self.preprocessing_prompts = load_preprocessing_prompts()
    
    def process_file(self, input_path: str, output_dir: str) -> Dict[str, Any]:
        """Process single file through preprocessing pipeline."""
        
    def process_directory(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """Process directory through preprocessing pipeline."""
        
    def generate_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate comprehensive preprocessing report."""

class ContentExtractor:
    """Multi-format content extraction."""
    
    def extract_markdown(self, file_path: str) -> Dict[str, Any]:
    def extract_json(self, file_path: str) -> Dict[str, Any]:
    def extract_pdf(self, file_path: str) -> Dict[str, Any]:
    def extract_text(self, file_path: str) -> Dict[str, Any]:

class AriIntegrator:
    """Ari persona integration and voice application."""
    
    def analyze_content_for_frameworks(self, content: str) -> Dict[str, Any]:
    def apply_ari_voice(self, content: str) -> str:
    def identify_coaching_opportunities(self, content: str) -> List[Dict[str, Any]]:

class TemplateGenerator:
    """Template filling and generation."""
    
    def fill_template(self, content: Dict[str, Any], analysis: Dict[str, Any]) -> str:
    def validate_template(self, template: str) -> Dict[str, Any]:
```

#### 2. CLI Integration  
**File**: `src/lyfe_kt/cli.py` (extension)

**New Commands**:
```bash
# Single file preprocessing
lyfe-kt preprocess file input.md work/02_preprocessed/ --report

# Directory preprocessing  
lyfe-kt preprocess directory work/01_raw/ work/02_preprocessed/ --report

# Batch preprocessing with reporting
lyfe-kt preprocess batch work/01_raw/ work/02_preprocessed/ --comprehensive-reports
```

#### 3. Configuration Integration
**Files**: Existing configuration system

**Required Configurations**:
- **Ari Persona**: `src/config/ari_persona.yaml` (existing)
- **Preprocessing Prompts**: `src/config/preprocessing_prompts.yaml` (existing)
- **Oracle Data Filters**: Oracle data loading configuration (existing)
- **Template Settings**: Template generation and validation rules

### Testing Strategy

#### 1. Unit Tests (Simple Approach)
**File**: `tests/test_stage1_preprocessing.py`

**Test Categories**:
- **Content Extraction Tests**: Each file format independently
- **Ari Integration Tests**: Framework application and voice consistency
- **Template Generation Tests**: Template filling and validation
- **Error Handling Tests**: Malformed inputs and edge cases

#### 2. Integration Tests
**Test Scenarios**:
- **Single File Processing**: Complete pipeline with real sample data
- **Directory Processing**: Batch processing with multiple file types
- **Report Generation**: Comprehensive report creation and validation
- **Cross-Format Processing**: Mixed file types in single batch

#### 3. Real Data Testing
**Test Data**: 
- Use existing `work/01_raw/levantar_da_cama/` as primary test case
- Create additional test cases with different file formats
- Validate against existing successful Stage 1 outputs

### Success Criteria

#### 1. Functional Requirements
- ✅ **Multi-Format Support**: Successfully process .md, .json, .pdf, .txt files
- ✅ **Template Generation**: Generate valid filled templates for all inputs
- ✅ **Ari Integration**: Apply persona consistently across all content
- ✅ **Oracle Enhancement**: Integrate Oracle data meaningfully

#### 2. Quality Requirements  
- ✅ **Report Generation**: Comprehensive reports for every processing run
- ✅ **Error Resilience**: Graceful handling of malformed inputs
- ✅ **Performance**: Process files in reasonable time (<5min per file)
- ✅ **Test Coverage**: 95%+ test coverage for new functionality

#### 3. Integration Requirements
- ✅ **CLI Compatibility**: Seamless integration with existing CLI
- ✅ **Configuration System**: Use existing configuration architecture
- ✅ **Directory Management**: Proper work directory organization
- ✅ **Report Standards**: Consistent reporting format and structure

### Implementation Plan

#### Phase 1: Core Implementation (2-3 hours)
1. **ContentExtractor Class**: Multi-format content extraction
2. **AriIntegrator Class**: Persona integration and voice application  
3. **TemplateGenerator Class**: Template filling and validation
4. **PreprocessingPipeline Class**: Main orchestration

#### Phase 2: CLI Integration (1 hour)
1. **Command Extensions**: Add preprocess command group
2. **Option Handling**: File/directory processing options
3. **Progress Reporting**: Real-time feedback integration
4. **Error Handling**: Proper exit codes and error messages

#### Phase 3: Testing & Validation (1-2 hours)  
1. **Unit Tests**: Core functionality testing
2. **Integration Tests**: End-to-end pipeline testing
3. **Real Data Testing**: Sample file processing verification
4. **Report Validation**: Report generation and format verification

### Dependencies and Risks

#### Dependencies
- **Ari Persona Configuration**: Must be completed (TODO 21 - generation-prompts)
- **Preprocessing Prompts**: Required for content transformation
- **Oracle Data Filters**: Needed for context enhancement
- **Template System**: Updated template structure compliance

#### Risk Mitigation
- **Performance Risk**: Implement chunked processing for large files
- **Memory Risk**: Use streaming for PDF and large file processing
- **Quality Risk**: Implement validation at each pipeline stage
- **Integration Risk**: Maintain backward compatibility with existing tests

### Documentation Updates

#### User Documentation
- **CLI Usage Guide**: Preprocessing command documentation
- **File Format Support**: Supported formats and processing behavior
- **Report Interpretation**: Understanding preprocessing reports
- **Best Practices**: Optimal input organization and processing workflows

#### Developer Documentation  
- **Architecture Overview**: Preprocessing pipeline design
- **Extension Guide**: Adding new file format support
- **Configuration Reference**: All preprocessing configuration options
- **Testing Guide**: Running and extending preprocessing tests

This comprehensive PRD ensures that the Stage 1 preprocessing implementation includes proper work directory organization, comprehensive reporting for every execution, and maintains the quality standards established in the existing pipeline while transitioning to the new 3-stage approach. 