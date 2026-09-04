# Working-tree safety

Use this reference when the repository is not clean.

- Run `git status --short` before editing. Inspect the relevant diffs and untracked paths so pre-existing work is distinguishable from the requested patch.
- Treat all pre-existing tracked and untracked changes as user-owned. Limit edits to authorized files and hunks; do not absorb adjacent cleanup.
- When requested work overlaps an existing edit, preserve both only when they can be separated confidently. Otherwise pause and describe the conflict.
- Never use destructive cleanup such as `git reset --hard`, `git checkout --`, `git clean`, or deletion of untracked work. Do not stash, restore, or rewrite pre-existing changes without explicit authorization.
- Review the final status and diff against the recorded baseline, and report any overlap or uncertainty.
