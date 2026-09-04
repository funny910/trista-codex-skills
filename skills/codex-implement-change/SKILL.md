---
name: codex-implement-change
description: Use when a user explicitly asks to fix, add, change, remove, migrate, or refactor repository code or files and authoring changes is in scope.
---

# Implementing an Authorized Change

## Core contract

Translate the request into an observable outcome. Mutate only the authorized repository scope; preserve existing work; do not infer permission to publish, merge, deploy, or message others.

## Workflow

1. Read repository instructions and inspect status.
2. Locate the smallest relevant path and acceptance evidence.
3. Resolve material ambiguity before editing.
4. Make the smallest complete patch.
5. Review the diff for accidental scope growth.
6. Run proportionate safe verification and report evidence.

## Stop conditions

Pause for missing authority, destructive conflicts, materially ambiguous behavior, unavailable required access, or a security/data trade-off that needs the user's choice.

## Output

Report Changed, Verification, and Limitations in that order, with file paths and exact failed or skipped checks.

## References

- Read [scope-and-ambiguity.md](references/scope-and-ambiguity.md) when a choice can alter behavior, compatibility, data, security, or cost.
- Read [working-tree-safety.md](references/working-tree-safety.md) when existing changes are present.
- Read [verification-baseline.md](references/verification-baseline.md) when choosing checks.
