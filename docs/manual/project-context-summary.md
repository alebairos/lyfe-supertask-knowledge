## Project Context Summary

### What this project is
- **Lyfe Supertask Knowledge Generator**: Converts raw educational content into mobile‑ready “supertask” JSONs with consistent Ari persona voice and schema compliance.

### Architecture and flow
- **3 stages**:
  - **Stage 1 (Preprocess)**: Raw content → filled template markdown with YAML frontmatter (`02_preprocessed/`)
  - **Manual Review (optional)**
  - **Stage 3 (Generate)**: Templates → supertask JSONs (`03_output/`)
- **Working dirs**: `work/01_raw/ → work/02_preprocessed/ → work/03_output/ → work/reports/`
- **Archiving**: `lyfe-kt package` moves `work/` to timestamped `packages/<title>-<YYYY-MM-DD-HH-MM>/`, cleans `work/` (structure preserved)

### CLI entry points (Click)
- Binary: `lyfe-kt` (also `python -m lyfe_kt.cli ...`)
- Global options: `--log-file`, `--log-level`, `-v/--verbose`
- Core groups:
  - `stage1 process-file|process-directory|generate-report` (lower-level Stage 1 integration)
  - `preprocess file|directory|batch` (Stage 1 to templates + reports)
  - `generate template|directory|pipeline` (Stage 3 to JSON + reports)
  - `generate narrative|simple|journey|comprehensive` (progressive/simplified systems)
  - `package` (moves `work/` to `packages/`, optional `--keep-work`)

Example:

```bash
# Stage 1 → templates
lyfe-kt preprocess file work/01_raw/content.md work/02_preprocessed/ --progress

# Stage 3 → JSONs
lyfe-kt generate template work/02_preprocessed/template.md work/03_output/ --progress

# Full batch
lyfe-kt generate pipeline work/02_preprocessed work/03_output --difficulty both --progress

# Package results
lyfe-kt package --keep-work

# Comprehensive coverage generation
lyfe-kt generate comprehensive "packages/arthurcbrooks_mostmeaning_extracted_filled_template-2025-08-06-14-59/02_preprocessed/arthurcbrooks_mostmeaning_extracted_filled_template.md" work/03_output/ --levels 5 --progress
```

### Persona and configuration
- **Ari persona**: `src/config/ari_persona.yaml` with identity, communication rules, 9 frameworks, Oracle data strategy; validated via `validate_ari_config`.
- **Config loader**: `src/lyfe_kt/config_loader.py` loads:
  - App config: `src/config/config.yaml`
  - Preprocessing prompts: `src/config/preprocessing_prompts.yaml`
  - Generation prompts: `src/config/generation_prompts.yaml`
  - Caches + env overrides (`LYFE_KT_*`)
  - Oracle data directory: `/Users/alebairos/Projects/mahhp/oracle` (CSV-based)
- Prompts define strict JSON structure, difficulty rules, mobile v1.1 limits, and output formatting.

### Output and schema
- JSON must include: `title, dimension, archetype, relatedToType, relatedToId, estimatedDuration, coinsReward, flexibleItems, metadata`
- **Mobile v1.1 constraints** (from prompts):
  - content 50–300 chars, quote 20–200, quiz question 15–120, options 3–60, explanation 30–250, total 3–8 items

### Tests
- Extensive test suite in `tests/` for CLI, config loader, preprocessing/generation, schema checks, persona consistency.
- End‑to‑end pipeline tests validate required fields, flexibleItems, difficulty differentiation, and metadata.

### Notable modules
- `src/lyfe_kt/cli.py`: all commands
- `src/lyfe_kt/stage1_preprocessing.py`, `stage3_generation.py`, `simplified_generator.py`, `progressive_narrative.py`, `content_packager.py`, `json_normalizer.py`, `output_validation.py`
- `src/config/supertask_schema_v1.0.json`, `src/config/supertask_schema_v1.1.json` for mobile optimization context

### Status/Docs
- Docs: `docs/manual/*`, `docs/features/*`, `docs/implementation_summaries/*` describe features (mobile schema v1.1, progressive narratives, simplified v2 system, packaging, prompts auditing).
- The UI tester expects files from `work/03_output/` or `packages/*/03_output/`.

### Key points
- 3‑stage pipeline with `work/` and `packages/`
- CLI offers preprocess, generate, package, plus simplified and journey modes
- Strict JSON structure + mobile v1.1 constraints enforced by prompts and tests
- Ari persona enforced across stages with validation and Oracle data strategy


