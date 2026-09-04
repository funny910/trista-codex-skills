---
name: codex-readonly-review
description: Use when a user asks for a code, diff, branch, or pull-request review, audit, or risk assessment without authorizing edits.
---

# Read-only Code Review

## Core contract

Inspect and report; do not modify files, apply patches, reformat code, create commits, post comments, or repair findings. This remains true when a combined request says to review and fix. Complete and report the review first, then stop. Begin a separate implementation phase only after the user explicitly authorizes its repair scope.

## Workflow

1. Establish the target and comparison base.
2. Read instructions and inspect the changed surface.
3. Trace behavior beyond the diff when needed.
4. Check correctness, regressions, security, data handling, compatibility, and coverage as relevant.
5. Validate each candidate finding against evidence.
6. Report actionable findings in severity order.

Use only read-only inspections and checks. Avoid tools that may write caches, snapshots, generated files, or lockfiles unless their effects are safely isolated outside user-owned work.

## Finding format

Every finding contains severity, a concise title, the smallest useful file/line or location, triggering evidence, concrete impact, and a focused recommendation. Unsupported speculation or style preference alone is not a finding.

## Output

Findings come first, followed by questions and residual risks. If none are supported, state that directly and summarize the inspected surface.

## Reference

Read [review-severity.md](references/review-severity.md) when classifying a candidate finding.
