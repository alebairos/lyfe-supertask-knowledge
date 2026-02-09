## 02 — Level Intents and Novelty Enforcement

### Goal
Make progression salient (foundation → application → expansion → integration → mastery) and reduce repetition.

### Changes
- Add `level_intent` and `novelty_rules` to `generation_prompts.yaml`:
  - Foundation: definitions + core habits; recognition quizzes.
  - Application: routines and rules; scenario quizzes.
  - Expansion: introduce at least one new concept not used before (e.g., blue light effects, morning light exposure, temperature 18–21 °C).
  - Integration: multi‑factor scenarios and trade‑offs.
  - Mastery: edge cases and relapse planning.
- Soft constraint: detect repeated sentences and nudge the model to vary wording.

### Acceptance Criteria
- Each non‑foundation level introduces ≥1 new concept.
- Sentence overlap across levels ≤10% by simple duplicate detection.






