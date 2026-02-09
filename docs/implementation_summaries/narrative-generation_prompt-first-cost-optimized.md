## Implementation Summary: Narrative Generation — Prompt‑First and Cost‑Optimized

### Objectives
- Ensure Ari is the author/voice of content items and uses contextual quotes from trusted experts defined in `src/config/ari_persona.yaml` to increase credibility.
- Maximize learning and engagement with clear difficulty progression (foundation → application → mastery) and habit formation.
- Favor prompt improvements over hardcoding; centralize rules in YAML prompts to keep behavior configurable.
- Reduce model cost/latency by minimizing requests while preserving mobile v1.1 constraints and schema compliance.

### Scope
- Applies to narrative workflows (default 3 levels), comprehensive journeys (5 levels), and single template generation paths.
- No UI change required; CLI remains the primary interface. Documentation updates guide usage.

### Design Principles
- Prompt‑first: All behavioral constraints and content style are defined or overridden in prompt YAMLs (`generation_prompts.yaml`, optionally `preprocessing_prompts.yaml`).
- Minimal requests: Prefer generators that produce entire supertasks in one call or per level (vs. per item), with structured post‑processing.
- Cohesive progression: Enforce distinct goals per level and varied item mix to avoid repetition.

### Implementation Plan
1) Prompt enhancements (primary lever)
   - In `generation_prompts.yaml`:
     - Add an "authorship_and_quotes" block that instructs:
       - All `content` items use Ari as `author`.
       - At most one `quote` item per level; author must be one of: BJ Fogg, Jason Hreha, Anna Lembke, Lieberman & Long, Martin Seligman, Abraham Maslow, Andrew Huberman, Michael Easter, Andrew Newberg — selected contextually.
       - Quote must be on‑topic and within mobile limits; include `author`.
     - Add a "level_intent" section with clear guidance for each level name (foundation, application, mastery; and for comprehensive: expansion, integration):
       - Foundation: definitions + core habits; recognition quizzes.
       - Application: routines and rules (timing, caffeine cutoff, exercise windows); scenario quizzes.
       - Expansion: introduce at least one new concept not used before (e.g., blue light); discrimination quizzes.
       - Integration: multi‑factor scenarios and trade‑offs.
       - Mastery: edge cases, relapse planning.
     - Add a "novelty_rules" section: require at least one new concept per non‑foundation level and disallow verbatim reuse.
     - Add a "micro_habit_and_celebration" section: each level ends with one micro‑action and a short celebration line in Ari’s voice.
     - Add a "sequence_profiles" section to allow default per‑level sequences; still permit custom `--sequence` to override.

2) Cost optimization
   - Prefer single‑call generation per level (already used by simplified/comprehensive flows). Ensure prompts request the full set of items per level (3–8) in one completion.
   - Only post‑process locally (validation, trimming, title/difficulty adjustments). Avoid per‑item enhancement calls.
   - Logically group validation (structure + mobile constraints) to a single pass per level.

3) Engagement hooks
   - Prompt rules require: micro‑habit at the end of each level, celebration language, and at least one contextual quote in levels that need inspiration.
   - Explanations vary by difficulty: didactic for foundation; scenario‑focused for application/integration; insight‑dense for mastery.

4) Validation and compliance
   - Keep `validate_generated_json_structure` and schema checks unchanged.
   - Add a light post‑generation check to ensure:
     - Ari is `author` for `content` items.
     - If `quote` exists: has `author` from the allowed list and stays within mobile char limits.
     - Novelty rule: detect repeated sentences across levels and request regeneration (single call) only if violations are severe.

### Expected Changes (Config‑Only)
- `src/config/generation_prompts.yaml` gains new sections and wording (no code branching). CLI signatures unchanged.
- Optional: `src/config/preprocessing_prompts.yaml` to seed level intents and extract candidate quotes/topics from source content.

### Risks and Mitigations
- Risk: Too strict novelty rules may reduce coherence.
  - Mitigation: Treat novelty as a soft constraint with warning; only regenerate on clear duplicates.
- Risk: Cost may increase if regeneration triggers frequently.
  - Mitigation: Cap retries to 1; surface improvement suggestions in report.

### Metrics of Success
- Reduced duplicate sentences across levels (≤10% overlap by sentence).
- Improved engagement markers in content: presence of micro‑habits and celebrations at each level (≥90% of levels).
- Quote usage: contextual, from allowed list (≥80% of levels where quote appears).
- Fewer OpenAI calls per narrative (≤ levels + 1 validations).

### Rollout
- Phase 1: Prompt updates + docs. Validate on 3–5 samples.
- Phase 2: Add optional flag `--engagement-profile=default` to allow future profiles.
- Phase 3: Remove legacy hardcoded branching if prompts prove sufficient.






