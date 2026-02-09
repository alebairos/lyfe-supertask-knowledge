## Lyfe KT CLI: Commands and Parameters

This reference documents all available commands, arguments, options, defaults, and expected outputs. Use it to simplify usage and identify redundant code paths for removal.

### Global
- Binary: `lyfe-kt` (or `python -m lyfe_kt.cli`)
- Global options:
  - `--log-file PATH` (default: `logs/lyfe-kt.log`)
  - `--log-level {DEBUG|INFO|WARNING|ERROR}` (default: `INFO`)
  - `-v, --verbose` (sets DEBUG)
  - `-h, --help`
  - `--version`

Outputs: logs to file + stdout messages; non‑zero exit on failure.

## Quick Flow
1) Preprocess raw `.md` → filled template `.md` in `work/02_preprocessed/`
2) Generate supertask JSON(s) in `work/03_output/`
3) Package to `packages/<title>-<timestamp>/` and clean `work/`

---

## Stage 1: Preprocess

### preprocess file
- Synopsis:
  ```bash
  lyfe-kt preprocess file INPUT_FILE.md OUTPUT_DIR [--report] [--progress]
  ```
- Arguments:
  - `INPUT_FILE`: existing file (.md, .json, .pdf, .txt, .docx)
  - `OUTPUT_DIR`: directory to write outputs
- Options:
  - `--report`: generate a report in `…/reports/`
  - `--progress`: live progress messages
- Outputs: `*_filled_template.md`, `*_ari_analysis.json`, `*_oracle_context.json`

### preprocess directory
- Synopsis:
  ```bash
  lyfe-kt preprocess directory INPUT_DIR OUTPUT_DIR [--report] [--progress]
  ```
- Arguments:
  - `INPUT_DIR`: directory with supported files
  - `OUTPUT_DIR`: destination directory
- Options:
  - `--report`: always generates a comprehensive report
  - `--progress`
- Outputs: batched templates under `OUTPUT_DIR` + `work/reports/…`

### preprocess batch
- Synopsis:
  ```bash
  lyfe-kt preprocess batch INPUT_DIR OUTPUT_DIR [--comprehensive-reports] [--progress]
  ```
- Options:
  - `--comprehensive-reports`: include deep analysis
  - `--progress`
- Notes: Advanced batch; similar outputs to `preprocess directory` with richer reporting.

## Stage 3: Generate

### generate template
- Synopsis:
  ```bash
  lyfe-kt generate template TEMPLATE_FILE.md OUTPUT_DIR \
    [--difficulty {beginner|advanced|both}] [--sequence "content → quiz → …"] \
    [--report PATH] [--progress]
  ```
- Defaults:
  - `--difficulty both`
- Options:
  - `--sequence`: custom narrative order. Rules:
    - Use Unicode arrow `→` separators
    - Allowed items: `content`, `quiz`, `quote`
    - Length: 3–8 items
    - Must include at least one of each type; invalid falls back to default
  - `--report PATH`: saves generation report
  - `--progress`
- Outputs: `…_beginner.json`, `…_advanced.json` in `OUTPUT_DIR`

### generate directory
- Synopsis:
  ```bash
  lyfe-kt generate directory INPUT_DIR OUTPUT_DIR [--difficulty {beginner|advanced|both}] [--report PATH] [--progress]
  ```
- Batch converts all templates in `INPUT_DIR`.

### generate pipeline
- Synopsis:
  ```bash
  lyfe-kt generate pipeline INPUT_DIR OUTPUT_DIR [--difficulty {beginner|advanced|both}] [--report PATH] [--progress]
  ```
- Notes: Runs directory generation + comprehensive summary/report.

### generate narrative
- Synopsis:
  ```bash
  lyfe-kt generate narrative TEMPLATE_FILE.md OUTPUT_DIR \
    [--levels N] [--progression "foundation → application → mastery"] \
    [--theme STR] [--continuity {low|medium|high}] [--report PATH] [--progress]
  ```
- Defaults:
  - `--levels 3`
  - `--progression "foundation → application → mastery"`
  - `--continuity medium`
- Outputs: multiple level JSONs + `narrative_metadata.json` + `narrative_journey_report.md`

### generate simple
- Synopsis:
  ```bash
  lyfe-kt generate simple TEMPLATE_FILE.md OUTPUT_DIR \
    [--difficulty {beginner|intermediate|advanced}] \
    [--sequence "content → quiz → content → quote → content → quiz"] \
    [--theme STR] [--progress]
  ```
- Notes: One fast single‑call generator; writes a single JSON.

### generate journey
- Synopsis:
  ```bash
  lyfe-kt generate journey TEMPLATE_FILE.md OUTPUT_DIR \
    [--levels N] [--progression "foundation → application → mastery"] \
    [--sequence "…"] [--theme STR] [--progress]
  ```
- Notes: Parallel simplified journeys; outputs per-level JSONs + metadata/report.

### generate comprehensive
- Synopsis:
  ```bash
  lyfe-kt generate comprehensive TEMPLATE_FILE.md OUTPUT_DIR \
    [--levels 5] [--sequence "…"] [--theme STR] [--validate-coverage] [--progress]
  ```
- Defaults:
  - `--levels 5`
  - `--validate-coverage` enabled
- Outputs: `level_1_foundation.json … level_5_mastery.json`, `comprehensive_metadata.json`, `comprehensive_report.md`

## Packaging

### package
- Synopsis:
  ```bash
  lyfe-kt package [TITLE] [--output-dir DIR] [--keep-work] [--session-id ID]
  ```
- Behavior:
  - Auto-detects title from outputs if not provided
  - Copies `work/01_raw`, `02_preprocessed`, `03_output`, `reports` into `packages/<title>-<timestamp>/`
  - Cleans `work/` structure unless `--keep-work`
- Outputs: package path printed; folder contains full audit trail.

## Status and Version
- `lyfe-kt status` → prints version + readiness
- `lyfe-kt version` → prints semantic version

## Lower-level Stage 1 (advanced)

### stage1 process-file
- Synopsis:
  ```bash
  lyfe-kt stage1 process-file INPUT_FILE OUTPUT_FILE \
    [--no-ai-analysis] [--no-validation] [--config PATH] [--progress] \
    [--output-format {json|pretty}]
  ```

### stage1 process-directory
- Synopsis:
  ```bash
  lyfe-kt stage1 process-directory INPUT_DIR OUTPUT_DIR \
    [--no-ai-analysis] [--no-validation] [--config PATH] [--progress] \
    [--pattern PAT] [--report PATH] [--save-results PATH] [--continue-on-error]
  ```

### stage1 generate-report
- Synopsis:
  ```bash
  lyfe-kt stage1 generate-report RESULTS.json \
    [--output PATH] [--format {markdown|json|text}] [--type {technical|content}]
  ```

## Key Parameters and Defaults
- `--sequence` (template/simple/journey): enforced by `SequenceParser`
  - Defaults to: `content → quiz → content → quote → content → quiz`
  - Invalid input logs a warning and falls back to default
- `--difficulty`
  - `beginner|advanced|both` (template/directory/pipeline)
  - `beginner|intermediate|advanced` (simple)
- `--levels` (narrative/journey/comprehensive): default 3, 3, 5 respectively
- Reports
  - Preprocess: `work/reports/...`
  - Generate: user‑provided `--report` path or auto in output dirs
- Work directories
  - `work/01_raw/`, `work/02_preprocessed/`, `work/03_output/`, `work/reports/`
  - Packaging moves these into `packages/<title>-<timestamp>/`

## Examples
```bash
# 1) Raw .md → template
lyfe-kt preprocess file work/01_raw/content.md work/02_preprocessed/ --progress

# 2) Template → both difficulties
lyfe-kt generate template work/02_preprocessed/content_filled_template.md work/03_output/ \
  --difficulty both --progress

# 3) Custom sequence (must include all types, 3–8 items)
lyfe-kt generate template work/02_preprocessed/content_filled_template.md work/03_output/ \
  --sequence "content → quote → quiz → content" --progress

# 4) Comprehensive 5‑level coverage
lyfe-kt generate comprehensive "packages/.../02_preprocessed/xyz_filled_template.md" work/03_output/ \
  --levels 5 --progress

# 5) Package results
lyfe-kt package --keep-work
```

## De‑duplication opportunities
- Prefer `preprocess directory` over `preprocess batch` unless you need the extended reporting flag.
- `generate pipeline` subsumes `generate directory` when you want a consolidated report; otherwise keep one.
- Consider consolidating `narrative` and `journey` if only one multi‑level path is used by teams.
- Keep one comprehensive mode (`generate comprehensive`) as the single source for full coverage journeys.






