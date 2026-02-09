## 03 — Sequence Profiles and Engagement Hooks

### Goal
Increase engagement and variety across levels with minimal complexity.

### Changes
- Add `sequence_profiles` to `generation_prompts.yaml` with defaults per level:
  - Foundation: `content → quiz → content`
  - Application: `content → quiz → content → quiz`
  - Expansion: `content → quote → content → quiz`
  - Integration: `content → quiz → content → quote → quiz`
  - Mastery: `content → quiz → content → quiz`
- Add `micro_habit_and_celebration` rules: each level ends with one specific micro‑habit and a short celebration line (Ari voice).
- Preserve `--sequence` CLI option to override.

### Acceptance Criteria
- Each level matches the default profile unless `--sequence` is provided.
- Levels end with a micro‑habit and celebration line (≥90%).






