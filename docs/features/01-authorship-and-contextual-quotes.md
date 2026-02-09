## 01 — Authorship and Contextual Quotes

### Goal
Ensure `content` items have `author: "Ari"` and add contextual `quote` items by experts listed in `ari_persona.yaml` to increase credibility.

### Changes
- Update `src/config/generation_prompts.yaml` to include an "authorship_and_quotes" section:
  - All `content` items use Ari as `author`.
  - At most one `quote` per level; quote must be relevant to the level focus and include `author` from the allowed list (BJ Fogg, Jason Hreha, Anna Lembke, Lieberman & Long, Martin Seligman, Abraham Maslow, Andrew Huberman, Michael Easter, Andrew Newberg).
  - Respect mobile v1.1 limits.

### Acceptance Criteria
- ≥90% of generated levels contain correctly authored content items.
- ≥80% of levels include an optional, contextual quote with a valid author.






