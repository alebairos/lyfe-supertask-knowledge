# Ari Persona Configuration - Feature Requirements Document

## Overview

This feature implements a comprehensive Ari persona configuration system that serves as the foundation for all Ari life coach integration throughout the Lyfe Supertask Knowledge Generator. The configuration will define Ari's identity, communication patterns, expert frameworks, and Oracle data integration strategy to ensure consistent coaching voice across all generated content.

## Current State Analysis

### Existing Implementation

**What's Already Implemented:**
- **Ari Pattern Analysis**: `src/lyfe_kt/stage1_functions.py` contains `analyze_ari_persona_patterns()` with comprehensive coaching opportunity detection
- **Content Integration**: Existing modules in `content_analyzer.py`, `json_normalizer.py`, and `output_validation.py` have Ari persona enhancement capabilities
- **Configuration Infrastructure**: Robust YAML configuration loading system in `config_loader.py` with environment variable support
- **Template Integration**: `knowledge_task_input_template.md` includes Ari voice guidelines and coaching methodology references
- **Documentation Foundation**: Comprehensive Ari persona documentation in `ari-persona-integration-summary.md` and `knowledge-task-generator.md`

**Current Gaps:**
- **No dedicated Ari configuration file**: The `src/config/ari_persona.yaml` doesn't exist yet
- **Oracle data not integrated**: Analysis done but filtering/integration not implemented
- **Framework definitions scattered**: Ari's 9 expert frameworks referenced but not systematically defined
- **Communication patterns not structured**: TARS-inspired brevity rules exist in documentation but not in config

### Code Reuse Opportunities

**Existing Patterns to Follow:**
- **Configuration Loading**: Use existing `config_loader.py` patterns with `load_config()` and environment variable support
- **YAML Structure**: Follow existing `config.yaml` and `llm_prompts.yaml` patterns for consistent structure
- **Validation Patterns**: Leverage existing validation patterns from `input_validation.py` and `output_validation.py`
- **Error Handling**: Use existing error handling patterns from `Stage1ProcessingError` and `ContentAnalyzerError`

**Dependencies on Existing Components:**
- **Configuration System**: Extends existing `config_loader.py` functionality
- **Ari Analysis Functions**: Integrates with existing `analyze_ari_persona_patterns()` in `stage1_functions.py`
- **Content Enhancement**: Works with existing Ari enhancement code in `json_normalizer.py`
- **Validation System**: Integrates with existing `_validate_ari_persona()` in `output_validation.py`

## Requirements

### Functional Requirements

**FR1: Core Ari Identity Configuration**
- Define Ari's complete identity (name, role, personality, language forms)
- Specify coaching philosophy and core principles
- Include cultural context and Portuguese masculine form requirements

**FR2: Communication Pattern Definition**
- Implement TARS-inspired brevity rules with specific word limits
- Define engagement progression patterns (opening → validation → precision → action → support)
- Specify forbidden phrases and preferred communication styles
- Include coaching question templates and response patterns

**FR3: Expert Framework Integration**
- Configure all 9 expert frameworks with specific application rules
- Define framework-specific focus areas and application strategies
- Include formula/principle definitions for each framework
- Specify content triggers for framework activation

**FR4: Oracle Data Integration Strategy**
- Define data filtering rules for optimal LLM context (~44KB target)
- Specify inclusion/exclusion criteria for habits, trails, and objectives
- Configure dynamic context optimization parameters
- Include dimension mapping (SF, TG, SM, E, R) and priority settings

**FR5: Configuration Loading and Validation**
- Extend existing config loader to handle Ari persona configuration
- Implement validation for all configuration sections
- Support environment variable overrides for development/production
- Provide clear error messages for configuration issues

### Non-Functional Requirements

**NFR1: Performance**
- Configuration loading should complete in <100ms
- Oracle data filtering should produce <50KB optimized context
- Memory usage should not exceed 10MB for configuration data

**NFR2: Maintainability**
- Configuration should be human-readable and editable
- Clear section organization and comprehensive comments
- Validation should provide specific error locations and suggestions

**NFR3: Extensibility**
- Easy addition of new frameworks or communication patterns
- Flexible Oracle data filtering rules
- Support for different cultural/language adaptations

**NFR4: Integration**
- Seamless integration with existing configuration system
- Compatible with existing Ari analysis and enhancement functions
- Support for A/B testing different configuration variants

## Implementation Approach

### Architecture

**Configuration File Structure:**
```yaml
# src/config/ari_persona.yaml
ari_persona:
  identity:           # Core identity configuration
  communication:      # TARS-inspired communication patterns
  expert_frameworks:  # 9 framework definitions with application rules
  oracle_integration: # Data filtering and context optimization
  validation_rules:   # Configuration validation parameters
  cultural_context:   # Portuguese language and Brazilian cultural settings
```

**Integration Points:**
- **Config Loader Enhancement**: Extend `config_loader.py` to load Ari persona configuration
- **Analysis Integration**: Connect with existing `analyze_ari_persona_patterns()` function
- **Content Enhancement**: Integrate with existing Ari enhancement code in multiple modules
- **Validation Extension**: Work with existing persona validation in `output_validation.py`

### New Components to Create

**Configuration Module Extension:**
- `load_ari_persona_config()` function in `config_loader.py`
- `validate_ari_config()` function for configuration validation
- Environment variable support for Ari-specific settings

**Helper Functions:**
- Oracle data filtering utilities
- Framework applicability checking functions
- Communication pattern validation functions

### Existing Components to Modify

**Configuration Loader (`src/lyfe_kt/config_loader.py`):**
- Add Ari persona configuration loading capability
- Extend validation to include Ari configuration sections
- Add Oracle data integration functionality

**Module Exports (`src/lyfe_kt/__init__.py`):**
- Export new Ari configuration functions
- Maintain backward compatibility with existing exports

## Testing Strategy

### Types of Tests Needed

**Unit Tests:**
- Configuration loading and validation functions
- Oracle data filtering functionality
- Framework configuration parsing
- Communication pattern validation

**Integration Tests:**
- Integration with existing config loader
- Compatibility with existing Ari analysis functions
- End-to-end configuration loading and usage

**Validation Tests:**
- Invalid configuration handling
- Missing section error reporting
- Environment variable override functionality

### Test Data Requirements

**Valid Configuration Samples:**
- Complete Ari persona configuration with all sections
- Minimal valid configuration for testing defaults
- Cultural variant configurations (Portuguese vs. Brazilian)

**Invalid Configuration Samples:**
- Missing required sections
- Invalid framework definitions
- Malformed Oracle integration settings
- Invalid communication patterns

### Integration Testing Approach

**Existing System Integration:**
- Test with existing `analyze_ari_persona_patterns()` function
- Verify compatibility with content enhancement functions
- Ensure validation system integration works correctly

**Oracle Data Integration Testing:**
- Test filtering produces expected context size
- Verify all required Oracle data elements are included
- Test performance with large Oracle datasets

## Success Criteria

### Measurable Success Criteria

**Configuration Performance:**
- Configuration loads in <100ms
- Oracle data filtering produces 40-48KB optimized context
- Memory usage <10MB for complete configuration

**Integration Success:**
- 100% compatibility with existing Ari analysis functions
- No regressions in existing test suite (273 tests must still pass)
- Successful integration with all existing modules referencing Ari

**Content Quality:**
- Generated content passes Ari persona validation with >95% consistency
- Communication patterns correctly applied in content generation
- Framework integration properly triggered by content analysis

### Performance Benchmarks

**Loading Performance:**
- Cold start configuration loading: <200ms
- Warm configuration access: <10ms
- Oracle data filtering: <500ms

**Memory Efficiency:**
- Base configuration: <5MB
- With Oracle data: <15MB
- Cached configuration access: <1MB additional

### Quality Gates

**Configuration Completeness:**
- All 9 expert frameworks properly defined
- Complete communication pattern specification
- Comprehensive Oracle integration settings
- Full cultural context configuration

**Validation Coverage:**
- 100% of required configuration sections validated
- Clear error messages for all validation failures
- Environment variable override functionality tested

## Dependencies

### Other TODOs This Depends On

**Completed Dependencies:**
- ✅ **pipeline-redesign** (TODO 17): Architecture defined and ready for implementation
- ✅ **Existing configuration system**: `config_loader.py` provides foundation
- ✅ **Ari analysis functions**: `analyze_ari_persona_patterns()` ready for integration

**External Dependencies:**
- Oracle directory access: `/Users/alebairos/Projects/mahhp/oracle`
- Existing YAML configuration infrastructure
- PyYAML library for configuration parsing

### System Requirements

**Development Environment:**
- Python 3.9+ with existing project dependencies
- Access to Oracle data directory for integration
- Write access to `src/config/` directory

**Runtime Requirements:**
- PyYAML for configuration parsing (already installed)
- Python-dotenv for environment variable support (already installed)
- Compatible with existing logging and error handling systems

## Implementation Plan

### Phase 1: Core Configuration Structure (Day 1)
1. Create `src/config/ari_persona.yaml` with complete structure
2. Define all sections with comprehensive examples and comments
3. Include Oracle data integration specifications

### Phase 2: Configuration Loading (Day 2)
1. Extend `config_loader.py` with Ari persona loading capability
2. Implement validation functions for all configuration sections
3. Add environment variable override support

### Phase 3: Integration and Testing (Day 3)
1. Integrate with existing Ari analysis functions
2. Create comprehensive test suite covering all functionality
3. Verify compatibility with existing codebase

### Phase 4: Documentation and Validation (Day 4)
1. Update documentation with configuration usage examples
2. Run complete test suite to ensure no regressions
3. Validate Oracle data integration performance

## Risk Mitigation

### Potential Risks

**Configuration Complexity:**
- Risk: Overly complex configuration difficult to maintain
- Mitigation: Clear documentation, examples, and validation

**Performance Impact:**
- Risk: Large Oracle data integration affects loading performance
- Mitigation: Efficient filtering algorithms and caching strategies

**Backward Compatibility:**
- Risk: Breaking existing Ari analysis functionality
- Mitigation: Comprehensive integration testing and gradual rollout

### Contingency Plans

**Configuration Loading Issues:**
- Fallback to embedded default configuration
- Clear error messages guiding configuration fixes
- Graceful degradation without Ari persona enhancement

**Oracle Data Integration Problems:**
- Fallback to core persona without Oracle context
- Configurable Oracle data inclusion levels
- Performance monitoring and automatic optimization

## Expected Outcomes

### Immediate Benefits

**Development Efficiency:**
- Centralized Ari persona configuration eliminates scattered definitions
- Clear configuration structure accelerates future Ari enhancements
- Validation system prevents configuration-related bugs

**Content Quality:**
- Consistent Ari voice across all generated content
- Proper framework integration based on content analysis
- Optimized Oracle data context for enhanced coaching

### Long-Term Impact

**Scalability:**
- Easy addition of new frameworks or communication patterns
- Support for different cultural adaptations and languages
- Foundation for A/B testing different persona configurations

**Maintainability:**
- Clear separation of persona logic from implementation code
- Easy configuration updates without code changes
- Comprehensive validation prevents configuration drift

This feature serves as the critical foundation for all subsequent Ari persona integration work, enabling consistent, high-quality coaching voice across the entire knowledge generation pipeline. 