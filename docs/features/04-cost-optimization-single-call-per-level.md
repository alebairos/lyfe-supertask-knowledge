## 04 — Cost Optimization: Single Call per Level

### Goal
Reduce model cost and latency without compromising narrative quality.

### Changes
- Use one model completion per level to generate all items (3–8) in a single response.
- Avoid per-item AI enhancement calls; perform validation and formatting locally.
- Consolidate structure and mobile-limit validation into a single pass per level.
- Limit regeneration to one retry on severe validation failures.

### Acceptance Criteria
- Average number of OpenAI calls per 3-level narrative ≤ 4.
- Validation passes without regeneration in ≥85% of runs.






