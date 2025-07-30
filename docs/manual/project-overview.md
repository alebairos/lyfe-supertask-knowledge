# Lyfe Supertask Knowledge Generator - Project Overview

## 🎯 Project Goal

The **Lyfe Supertask Knowledge Generator** is an AI-powered tool designed to convert raw educational content into structured, gamified learning tasks called "supertasks" for the Lyfe platform. The system:

- **Transforms** various content formats (markdown, JSON, PDF, DOCX) into standardized educational tasks
- **Integrates** the "Ari" persona (a TARS-inspired coaching voice) throughout all generated content
- **Applies** Oracle data (habits catalog, learning trails, objectives) for context-aware content enhancement
- **Generates** both beginner and advanced difficulty versions of each task
- **Ensures** platform compliance with specific JSON schema requirements

## 🔄 Pipeline Architecture

The system uses a **3-stage pipeline** approach:

```mermaid
graph LR
    A[01_raw/] --> B[Stage 1: Preprocessing]
    B --> C[02_preprocessed/]
    C --> D[Stage 2: Manual Review]
    D --> E[Stage 3: Generation]
    E --> F[03_output/]
    
    style A fill:#ffeb3b
    style C fill:#4caf50
    style F fill:#2196f3
```

## 📋 Pipeline Stages Breakdown

### **Stage 1: Raw Content → Preprocessed Templates**
```bash
lyfe-kt preprocess file|directory
```

**Input** (`01_raw/`):
- `.md` - Markdown files with content
- `.json` - Raw JSON supertasks
- `.pdf` - PDF documents
- `.docx` - Word documents
- `.txt` - Plain text files

**Processing**:
- Content extraction using `ContentExtractor`
- Ari persona analysis and voice integration
- Oracle data context application (habits, trails, objectives)
- Template filling with YAML frontmatter generation

**Output** (`02_preprocessed/`):
- `*_filled_template.md` - Structured markdown templates with YAML frontmatter
- `*_ari_analysis.json` - Ari persona analysis results
- `*_oracle_context.json` - Applied Oracle data context

**Example Output Structure**:
```yaml
---
title: "Your Task Title"
description: "Task description"
difficulty: "beginner"
dimension: "physicalHealth"
archetype: "sage"
estimated_duration: 420
coins_reward: 20
language: "portuguese"
region: "Brazil"
learning_objectives:
  - "Objective 1"
  - "Objective 2"
---

# Structured content with Ari's voice...
```

### **Stage 2: Manual Review (Optional)**
- Human review and editing of filled templates
- Quality assurance for content accuracy
- Template structure validation

### **Stage 3: Preprocessed Templates → Platform-Ready JSON**
```bash
lyfe-kt generate template|directory
```

**Input** (`02_preprocessed/`):
- `*_filled_template.md` - Completed markdown templates with frontmatter

**Processing**:
- Template parsing and validation
- JSON structure generation with schema compliance
- Ari persona consistency enforcement
- Difficulty variant generation (beginner/advanced)
- Format validation against supertask schema

**Output** (`03_output/`):
- `*_beginner.json` - Beginner difficulty supertask
- `*_advanced.json` - Advanced difficulty supertask

**Example JSON Structure**:
```json
{
  "title": "Task Title - Beginner",
  "description": "...",
  "dimension": "physicalHealth",
  "archetype": "sage",
  "relatedToType": "habit",
  "relatedToId": "123",
  "estimatedDuration": 420,
  "coinsReward": 20,
  "flexibleItems": [
    {
      "type": "multipleChoice",
      "content": "Question with Ari's voice",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": "A"
    }
  ],
  "metadata": {
    "generatedAt": "2025-01-26T...",
    "ariPersonaVersion": "1.0",
    "sourceFile": "..."
  }
}
```

## 🔧 Key Features

- **Multi-format Support**: Handles various input file types
- **Ari Persona Integration**: Consistent coaching voice with 9 expert frameworks
- **Oracle Data Context**: Habits catalog, learning trails, and objectives integration
- **Batch Processing**: Directory-level operations with progress reporting
- **Quality Validation**: Schema compliance and content quality assessment
- **Packaging System**: Organized output with execution logs and audit trails

## 📊 Current Status

- **Progress**: 41% complete (19/46 TODOs)
- **Phase**: Hybrid Solution Implementation
- **Testing**: 273 tests passing
- **Architecture**: Simplified 3-stage pipeline (previously 4-stage)

The tool is designed for production use in the Lyfe platform ecosystem, generating high-quality, gamified educational content with consistent persona integration and platform compliance.

## 🛠️ Usage Commands

### Preprocessing Stage
```bash
# Process a single file
lyfe-kt preprocess path/to/file.md

# Process entire directory
lyfe-kt preprocess path/to/directory/
```

### Generation Stage
```bash
# Generate from a single template
lyfe-kt generate path/to/template.md

# Generate from all templates in directory
lyfe-kt generate path/to/directory/
```

### Full Pipeline
```bash
# Run complete pipeline on a package
lyfe-kt full-pipeline package_name
```

## 📁 Directory Structure

```
packages/package_name/
├── 01_raw/              # Input files
├── 02_preprocessed/     # Filled templates and analysis
├── 03_output/           # Final JSON supertasks
└── reports/             # Execution logs and reports
``` 