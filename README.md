# Trista Codex Skills

## Purpose

Trista Codex Skills is a small, Codex-native pack for three distinct software-engineering modes: implementing an explicitly requested repository change, reviewing code without changing it, and independently verifying a change without repairing it. The skills turn those modes into explicit authority and evidence contracts while preserving existing user work.

`README.md` is the canonical English documentation. [README.zh-CN.md](README.zh-CN.md) is the complete Chinese counterpart.

## Skill table

| Skill | Use it when | Mutation authority |
| --- | --- | --- |
| `codex-implement-change` | The user explicitly asks to fix, add, change, remove, migrate, or refactor repository files. | Yes — only within the user-authorized repository scope. |
| `codex-readonly-review` | The user asks for a code, diff, branch, or pull-request review, audit, or risk assessment without authorizing edits. | No — strictly read-only; it does not repair findings. |
| `codex-verify-change` | The user asks whether a change works, fixes a problem, meets acceptance criteria, or is ready according to available evidence. | No — strictly read-only; it does not repair failures. |

Only `codex-implement-change` may mutate files, and only inside the repository scope the user authorized. `codex-readonly-review` and `codex-verify-change` are strictly read-only.

Verification begins with exactly one verdict: `VERIFIED` when all material criteria have sufficient positive evidence and no contradiction; `NOT_VERIFIED` when observed evidence contradicts a material criterion or shows a relevant failure; or `BLOCKED` when required evidence, access, environment, or criteria are unavailable or materially ambiguous.

## Routing examples

| Request | Route | Resulting authority |
| --- | --- | --- |
| “Fix the failing parser test.” | `codex-implement-change` | May edit only the requested repository scope. |
| “Review this pull request; do not edit files.” | `codex-readonly-review` | Read-only findings. |
| “Verify whether this fix meets the acceptance criteria.” | `codex-verify-change` | Read-only evidence and one verdict. |
| “Review the change, then fix only confirmed P1 findings.” | `codex-readonly-review`, then `codex-implement-change` | Review finishes first; mutation starts only in a separate, explicitly authorized repair phase. |
| “Explain why this function is slow; do not change it.” | No skill in this pack | Explanation remains read-only. |

Analysis or planning alone does not authorize implementation. Failed verification does not trigger repair. No skill invokes another skill automatically, and mixed wording uses the stricter authority until mutation intent is clear.

## Installation

The canonical skill sources are the directories under `skills/`. Install only the skill or skills you need. The supported destinations are:

- Repository-local: `.agents/skills/<skill-name>`
- Personal: `~/.agents/skills/<skill-name>`

If your Codex environment provides a skill installer, select `skills/<skill-name>` as the source and one of the destinations above as the target. Installer interfaces may vary by environment. Direct copying works from the repository root; set `skill_name` to any one of the three exact names in the skill table.

Repository-local installation:

```bash
skill_name=codex-implement-change
mkdir -p ".agents/skills/$skill_name"
cp -R "skills/$skill_name/." ".agents/skills/$skill_name/"
```

Personal installation:

```bash
skill_name=codex-implement-change
mkdir -p "$HOME/.agents/skills/$skill_name"
cp -R "skills/$skill_name/." "$HOME/.agents/skills/$skill_name/"
```

Repeat with `codex-readonly-review` or `codex-verify-change` as needed. Direct copying changes only the selected destination and does not require changes to unrelated Codex configuration.

## Validation

From the repository root, run both dependency-free checks:

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

The validator checks the exact skill inventory, required files, frontmatter, local references, Codex metadata, and unfinished markers. The unit suite covers the repository structure and validator rejection cases. Routing and behavior fixtures under `evals/` are reviewable expectations, not an automated model-evaluation harness.

## Boundaries and non-goals

This pack is not a general agent framework. V1 provides no orchestration runtime or state machine, automatic model selection or routing, automatic subagent routing or delegation, pull-request creation, merge, release, or deployment automation. It also does not provide external governance adapters, a plugin marketplace package, language-specific test presets, automatic repair during review or verification, or hidden escalation from read-only work to mutation.

Technical capability never grants authority. Existing tracked and untracked work remains user-owned; the implementation skill does not permit destructive cleanup, unrelated scope growth, publication, merge, deployment, messaging, or external-system changes unless the user separately authorizes that action.

## Contribution and public-safety rules

- Preserve the three-skill inventory and the mutation matrix above.
- Keep implementation changes within explicit user-authorized scope; keep review and verification strictly read-only.
- Treat tracked and untracked work as user-owned and do not erase or absorb unrelated changes.
- Commit each skill independently and run both validation commands before publishing.
- Update both `README.md` and `README.zh-CN.md` whenever public behavior or installation changes.
- Do not commit credentials, tokens, cookies, authentication artifacts, customer data, private logs, proprietary source, private repository names, private infrastructure topology, local machine paths, or environment-specific identifiers.
- Keep examples generic and reproducible. Do not claim affiliation or endorsement that does not exist.

See [AGENTS.md](AGENTS.md) for the repository policy and [the design specification](docs/superpowers/specs/2026-09-04-trista-codex-skills-design.md) for the authoritative V1 contracts.

## Attribution

The structure of this pack was inspired by the public [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills) repository. This repository's wording, contracts, tests, and Codex-specific separation of implementation, review, and verification authority are original. This project is not affiliated with or endorsed by that repository's authors, Andrej Karpathy, or OpenAI.

## License

This repository is available under the [MIT License](LICENSE). Copyright 2026 Trista.
