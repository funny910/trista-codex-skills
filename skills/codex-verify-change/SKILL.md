---
name: codex-verify-change
description: Use when a user asks whether a change works, fixes a reported problem, meets acceptance criteria, or is ready according to available evidence.
---

# Verifying a Change

## Core contract

Independently test the stated claim without modifying source, tests, configuration, snapshots, or user-owned untracked content. Verification is strictly read-only. A failed verification requires a new implementation instruction; it never triggers repair automatically.

## Workflow

1. Restate the claim and material criteria.
2. Map each criterion to observable evidence.
3. Inspect the current diff and repository state.
4. Run targeted checks, then broader checks when proportionate and available.
5. Compare observed results criterion by criterion.
6. Emit one verdict and its evidence.

Use only read-only inspections and checks. If a check may write caches or generated artifacts, isolate those effects outside tracked files and user-owned untracked content or report the evidence as unavailable.

## Verdicts

`VERIFIED` means every material criterion has sufficient positive evidence and no contradiction. `NOT_VERIFIED` means evidence contradicts a material criterion or demonstrates a relevant failure. `BLOCKED` means required evidence, access, environment, or criteria are unavailable or materially ambiguous.

## Output

Every result must begin with exactly one of `VERIFIED`, `NOT_VERIFIED`, or `BLOCKED`. Then give criterion evidence, commands or inspections, failures or blockers, and residual risk.

## References

- Read [evidence-standard.md](references/evidence-standard.md) when mapping a claim to checks.
- Read [verdict-rules.md](references/verdict-rules.md) when evidence is mixed or incomplete.
