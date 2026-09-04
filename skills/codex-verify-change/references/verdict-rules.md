# Verdict rules

Emit exactly one verdict:

- `VERIFIED`: every material criterion has sufficient positive evidence and no contradictory evidence remains.
- `NOT_VERIFIED`: observed evidence contradicts a material criterion or demonstrates a relevant failure. Scope this verdict to the stated claim and observed evidence; it is not a universal claim that the implementation always fails.
- `BLOCKED`: required evidence, access, environment, or criteria are unavailable or materially ambiguous. This is not success.

A focused pass plus related broader-suite failures is `NOT_VERIFIED`, not success. If a broader failure could materially bear on the claim but its relevance cannot be resolved with available read-only evidence, use `BLOCKED`. If required direct evidence is unavailable and no contradictory evidence exists, the verdict MUST be `BLOCKED`; insufficient proof must not be converted into `NOT_VERIFIED` or `VERIFIED`.

A failed or blocked verification ends with the verdict and evidence. Repair requires a new implementation instruction; do not modify source, tests, configuration, snapshots, or user-owned untracked content.
