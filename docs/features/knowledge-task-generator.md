# Knowledge Task Generator - Product Requirements Document

## Overview

The Knowledge Task Generator is an intelligent 3-stage pipeline that transforms raw content into structured, interactive supertasks for the Lyfe platform. It leverages Ari persona integration and configurable prompts to automatically create educational content with progressive learning steps, assessments, and gamification elements suitable for habit-based behavioral change.

## Problem Statement

Currently, creating knowledge tasks requires manual structuring of content into specific formats with quizzes, step-by-step progression, and proper metadata. This manual process is:
- Time-consuming for content creators
- Prone to inconsistencies in structure and quality
- Difficult to scale for large content volumes
- Limited in maintaining standardized learning experiences
- Lacks consistent persona voice across content

## Solution

A simplified 3-stage automated pipeline that:

### **Stage 1: Raw Data → Preprocessed Markdown**
```
work/01_raw/ (PDFs, txt, md, docs, etc.) 
    ↓ [LLM preprocessing with Ari persona]
work/02_preprocessed/ (.md template filled)
```

### **Stage 2: Manual Review/Edit (Optional)**
Human review/editing of .md files - optional step for quality assurance

### **Stage 3: Markdown → Supertask JSON(s)**
```
work/02_preprocessed/ (.md template)
    ↓ [LLM generation with Ari persona]
work/04_output/ (1 or more supertask.json files)
```

## Target Users

### Primary Users
- **Content Creators**: Educators, subject matter experts who write educational content
- **Content Managers**: Platform administrators who oversee knowledge content
- **Development Team**: Engineers who need to bulk-import educational content

### Secondary Users
- **End Users (Learners)**: Benefit from consistently structured, high-quality knowledge tasks
- **Habit Coaches**: Can leverage generated content for habit-specific learning

## Content Authoring Persona

### Ari Life Coach Integration
All generated knowledge tasks will be authored by **Ari**, the TARS-inspired life coach persona that serves as the primary life management coach in the Lyfe platform. This ensures consistency in tone, style, and coaching methodology across all knowledge content.

#### Ari's Characteristics
- **Identity**: Male life coach with TARS-inspired personality (direct yet warm, intelligent conciseness)
- **Communication Style**: Intelligent brevity with maximum engagement
- **Expertise**: 9 integrated expert frameworks (Tiny Habits, Behavioral Design, Dopamine Nation, etc.)
- **Philosophy**: "Every word matters. Maximum engagement through intelligent brevity. Sustainable change starts small."
- **Language**: Masculine forms in Portuguese ("Ari, seu treinador de vida", "Eu sou um coach")

#### Ari's Expert Frameworks
1. **Tiny Habits (BJ Fogg)** - Micro-habit methodology and celebration
2. **Behavioral Design (Jason Hreha)** - Behavior matching and strategy
3. **Dopamine Nation (Anna Lembke)** - Dopamine balance and detox protocols
4. **The Molecule of More (Lieberman)** - Dual system balance
5. **Flourish (Martin Seligman)** - PERMA model integration
6. **Hierarquia de Maslow** - Needs hierarchy approach
7. **Protocolos Huberman** - Neuroplasticity and circadian optimization
8. **Scarcity Brain (Michael Easter)** - Scarcity loop identification
9. **Words Can Change Your Mind (Andrew Newberg)** - Compassionate communication

#### Content Authoring Guidelines
- **Tone**: Encouraging but realistic, evidence-based without being academic
- **Style**: Concise, action-oriented, question-heavy approach
- **Focus**: Micro-habits, behavioral change, and sustainable transformation
- **Methodology**: Integrates BJ Fogg's Tiny Habits, Huberman Protocols, PERMA model, and other frameworks
- **Engagement**: Progressive engagement from brief questions to deeper coaching support

## Functional Requirements

### Core Features

#### Stage 1: Preprocessing Pipeline
- **File Format Support**: Accept various formats (.md, .json, .pdf, .txt, .docs) as primary input
- **Content Analysis**: Process raw content using Ari persona-informed LLM prompts
- **Template Population**: Fill the redesigned `.md` template with structured content
- **Ari Voice Integration**: Apply Ari's communication style and framework integration
- **Metadata Extraction**: Generate appropriate supertask metadata (dimension, archetype, etc.)

#### Stage 2: Human Review (Optional)
- **Manual Editing**: Allow human review and editing of populated templates
- **Quality Assurance**: Enable content creators to refine Ari's voice and content accuracy
- **Flexibility**: Optional step that can be skipped for automated workflows

#### Stage 3: Generation Pipeline
- **Template Processing**: Convert populated `.md` templates to supertask JSON format
- **Batch Generation**: Create multiple supertasks from single template when appropriate
- **Difficulty Scaling**: Generate both beginner (50%) and advanced (50%) versions by default
- **JSON Structure**: Ensure exact compliance with supertask format (flexibleItems structure)
- **Validation**: Comprehensive output validation against platform requirements

### Advanced Features

#### 1. Ari Persona Engine
- **Framework Integration**: Apply Ari's 9 expert frameworks appropriately to content
- **TARS-Inspired Brevity**: Implement intelligent conciseness rules
- **Portuguese Consistency**: Maintain masculine forms and cultural authenticity
- **Behavioral Science**: Integrate evidence-based approaches naturally
- **Coaching Style**: Progressive engagement from questions to deeper support

#### 2. Content Intelligence
- **Topic Recognition**: Identify main themes and subtopics automatically
- **Difficulty Assessment**: Analyze content complexity for appropriate user targeting
- **Learning Objective Extraction**: Derive clear behavioral change goals
- **Prerequisite Detection**: Identify content dependencies and sequencing
- **Scalable Processing**: Handle batch processing with consistent analysis results

#### 3. Template Management
- **Supertask Template**: Updated template matching exact JSON structure from test.json
- **Flexible Items**: Support for content, quote, and quiz item types
- **Metadata Compliance**: Ensure all required fields (dimension, archetype, relatedToType, etc.)
- **Title Convention**: Automatic "Beginner"/"Advanced" labeling in titles
- **Author Attribution**: Proper author attribution for content and quotes

#### 4. Configuration Management
- **Ari Persona Config**: Dedicated configuration file with complete persona definition
- **Preprocessing Prompts**: Configurable prompts for Stage 1 processing
- **Generation Prompts**: Configurable prompts for Stage 3 generation
- **Oracle Data Integration**: Access to Ari's catalog of habits, trails, and objectives

## Technical Specifications

### Template Structure
The updated `knowledge_task_input_template.md` includes:
- **Complete Metadata**: All supertask JSON fields covered
- **Flexible Items Structure**: Content, quote, and quiz item templates
- **Ari Voice Guidelines**: Specific instructions for persona consistency
- **Content Requirements**: Minimum/maximum item counts and progression rules
- **Title Convention**: Beginner/Advanced designation requirements

### Ari Persona Prompt Strategy
**Recommended Approach: Single prompt with filtered data**

Based on Oracle directory analysis:
- **LyfeCoach**: 20KB (include in full - core persona definition)
- **habitos.csv**: 16KB (filter to essential elements only)  
- **Trilhas.csv**: 32KB (filter to relevant trail structures)
- **Objetivos.csv**: 4KB (include in full - small dataset)
- **Total Context**: ~35-40KB filtered (optimal for LLM efficiency)

### Content Generation Requirements
- **Difficulty Balance**: 50% beginner, 50% advanced supertasks by default
- **Title Naming**: Unique titles with explicit "Beginner" or "Advanced" designation
- **JSON Compliance**: Exact match to test.json structure with all required fields
- **Progressive Enhancement**: Simple preprocessing approach with minimal complexity
- **Framework Integration**: Natural integration of Ari's behavioral science frameworks

### Configuration Structure
```yaml
# src/config/ari_persona.yaml
ari_persona:
  identity:
    name: "Ari"
    role: "Life Management Coach"
    personality: "TARS-inspired"
    language_forms: "masculine_portuguese"
  
  communication:
    style: "intelligent_brevity"
    engagement_progression: ["question", "validation", "precision", "action", "support"]
    forbidden_phrases: ["I understand that...", "It's important to note...", ...]
  
  frameworks:
    tiny_habits:
      focus: "micro_habits_celebration"
      application: "behavior_design"
    # ... other frameworks
  
  content_guidelines:
    tone: "encouraging_realistic"
    focus: "actionable_evidence_based"
    methodology: "behavioral_change_sustainable"
```

## Implementation Strategy

### Phase 1: Template and Configuration (Week 1)
1. **Updated Template**: Complete redesign of knowledge_task_input_template.md
2. **Ari Persona Config**: Create comprehensive ari_persona.yaml configuration  
3. **Preprocessing Prompts**: Design Stage 1 prompts with Ari persona integration
4. **Generation Prompts**: Design Stage 3 prompts for supertask creation

### Phase 2: Pipeline Implementation (Week 2)
1. **Stage 1 Functions**: Implement preprocessing with Ari persona application
2. **Stage 3 Functions**: Implement generation with JSON compliance and validation
3. **CLI Integration**: Add preprocessing and generation commands
4. **Batch Processing**: Enable directory-level processing capabilities

### Phase 3: Ari Integration and Testing (Week 3)
1. **Framework Application**: Integrate Ari's 9 expert frameworks
2. **Voice Consistency**: Implement TARS-inspired brevity and Portuguese validation
3. **Comprehensive Testing**: Create test suite for persona consistency
4. **Quality Assurance**: Validate against existing supertask samples

### Phase 4: Production Ready (Week 4)
1. **Documentation**: Complete user guides and technical documentation
2. **Performance Optimization**: Optimize for batch processing and API efficiency
3. **Error Handling**: Comprehensive error scenarios and recovery
4. **Production Deployment**: Ready for integration with Lyfe platform

## Expected Benefits

### Content Quality
- **Consistency**: Unified Ari coaching voice across all knowledge tasks
- **Engagement**: TARS-inspired brevity increases completion rates
- **Effectiveness**: Evidence-based frameworks enhance behavioral impact
- **Cultural Authenticity**: Proper Portuguese forms maintain user trust

### User Experience
- **Familiar Voice**: Users recognize Ari's coaching style from chat interactions
- **Trust Building**: Consistent persona builds user confidence
- **Learning Effectiveness**: Behavioral science integration improves outcomes
- **Scalability**: Automated generation enables rapid content expansion

### Development Efficiency
- **Simplified Pipeline**: 3-stage approach reduces complexity
- **Manual Override**: Optional human review maintains quality control
- **Batch Processing**: Efficient handling of multiple content sources
- **Template Driven**: Consistent structure ensures platform compatibility

## Quality Assurance

### Automated Validation
- **JSON Structure**: Verify exact compliance with supertask format
- **Persona Consistency**: Check for Ari's voice across all content
- **Framework Compliance**: Validate alignment with expert frameworks
- **Language Verification**: Automated Portuguese masculine form checks
- **Content Quality**: Assess learning objectives and quiz effectiveness

### Testing Strategy
- **Template Validation**: Ensure template covers all test.json fields
- **Voice Consistency**: Validate Ari's tone and style maintenance
- **Framework Integration**: Test proper framework application
- **Batch Processing**: Verify consistent results across multiple inputs
- **Edge Cases**: Handle malformed input and API failures gracefully

## Future Enhancements

- **Advanced Analytics**: Track supertask completion rates and engagement
- **Adaptive Difficulty**: Machine learning for optimal difficulty assignment
- **Personalized Content**: Adapt content based on user archetype and progress
- **Social Integration**: Collaborative learning and community features
- **Mobile Optimization**: Enhanced mobile learning experience
- **Gamification**: Advanced reward systems and achievement tracking

---

This updated approach represents a significant simplification and enhancement of the knowledge task generator, focusing on practical implementation with strong Ari persona integration and maintainable pipeline architecture. 