# Verification baseline

Use the lowest risk tier that fully reflects the changed behavior, then run the strongest safe checks available within scope.

| Risk | Typical change | Proportionate checks |
| --- | --- | --- |
| Low | Documentation, comments, or isolated non-behavioral configuration | Targeted syntax, format, link, or file validation |
| Medium | Contained behavior or a local refactor | Focused tests for the outcome plus relevant lint, type, or nearby regression checks |
| High | Public API, security, persistence, schema, migration, or broad behavior | Focused tests plus available broader suites, builds, integration checks, or safe migration validation |

A passing command supports only the behavior it exercised. Do not describe the change as fully verified when relevant failures, contradictory evidence, or untested material criteria remain.

In **Limitations**, name every relevant check that failed or was skipped, its exact result or reason, and the resulting uncertainty. Avoid checks that would mutate user-owned files or require unapproved external actions.
