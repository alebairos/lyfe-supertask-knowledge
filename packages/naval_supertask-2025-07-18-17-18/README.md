# Work Directory Structure

This directory contains the working files for the Lyfe Supertask Knowledge Generator, organized according to the 3-stage pipeline architecture.

## 📁 Directory Structure

```
work/
├── 01_raw/                    # Stage 1 Input: Raw content files
│   ├── sample.md             # Sample markdown content
│   └── levantar_da_cama_raw.json  # Raw JSON supertask example
├── 02_preprocessed/           # Stage 1 Output: Filled templates
│   ├── sample_filled_template.md        # Properly formatted template
│   ├── levantar_da_cama_preprocessed.json  # Preprocessed example
│   ├── sample_oracle_context.json       # Oracle data context
│   └── sample_ari_analysis.json         # Ari persona analysis
├── 03_output/                 # Stage 3 Output: Final JSON supertasks
│   └── (generated files go here)
└── reports/                   # Processing reports and analysis
    ├── final_compliance_report.md
    └── json_format_compliance_success.md
```

## 🔄 Pipeline Stages

### Stage 1: Raw → Preprocessed
- **Input**: Raw content files (`.md`, `.json`, `.pdf`, `.docx`)
- **Output**: Filled markdown templates with YAML frontmatter
- **Command**: `lyfe-kt preprocess file|directory`

### Stage 2: Manual Review (Optional)
- Review and edit filled templates in `02_preprocessed/`
- Ensure proper frontmatter and content structure

### Stage 3: Preprocessed → JSON
- **Input**: Filled markdown templates
- **Output**: Platform-ready supertask JSON files
- **Command**: `lyfe-kt generate template|directory`

## 🚀 Usage Examples

### Process Raw Content
```bash
# Single file
lyfe-kt preprocess file work/01_raw/sample.md work/02_preprocessed/

# Directory
lyfe-kt preprocess directory work/01_raw/ work/02_preprocessed/
```

### Generate Supertasks
```bash
# Single template
lyfe-kt generate template work/02_preprocessed/sample_filled_template.md work/03_output/

# Directory
lyfe-kt generate directory work/02_preprocessed/ work/03_output/

# With options
lyfe-kt generate template work/02_preprocessed/sample_filled_template.md work/03_output/ \
  --difficulty both --progress --report generation_report.json
```

## 📋 Template Format

Filled templates must have proper YAML frontmatter:

```yaml
---
title: "Your Task Title"
description: "Task description"
difficulty: "beginner"          # or "advanced"
dimension: "physicalHealth"     # physicalHealth, mentalHealth, relationships, etc.
archetype: "sage"              # sage, warrior, lover, etc.
estimated_duration: 420        # in seconds
coins_reward: 20              # reward points
language: "portuguese"
region: "Brazil"
learning_objectives:
  - "Objective 1"
  - "Objective 2"
---

# Content goes here...
```

## 📊 File Types

### Raw Content (01_raw/)
- `.md` - Markdown files
- `.json` - JSON supertasks
- `.pdf` - PDF documents
- `.docx` - Word documents
- `.txt` - Plain text files

### Preprocessed (02_preprocessed/)
- `.md` - Filled markdown templates
- `.json` - Context and analysis files

### Output (03_output/)
- `.json` - Final supertask JSON files
- `*_beginner.json` - Beginner difficulty
- `*_advanced.json` - Advanced difficulty

### Reports (reports/)
- `.md` - Processing reports
- `.json` - Analysis results

## 🛠️ Maintenance

### Cleaning Up
```bash
# Remove temporary files
find work/ -name "*.tmp" -delete

# Remove old reports
find work/reports/ -name "*_$(date -d '30 days ago' +%Y-%m-%d)*" -delete
```

### Backup
```bash
# Create backup
tar -czf work_backup_$(date +%Y%m%d).tar.gz work/
```

## 📝 Notes

- Always validate templates before generation
- Use `--progress` flag for detailed processing info
- Reports are automatically timestamped
- Oracle context integration is available for habit-related content
- Ari persona consistency is maintained throughout the pipeline 