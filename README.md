# Trista Codex Skills

## Purpose

Trista Codex Skills is a small, Codex-native collection for three distinct software-engineering modes and narrative animated-short planning. The engineering skills separate implementation, read-only review, and independent verification. The planning skill turns stories into character assets, scene assets, and storyboard documents without generating media. Each skill preserves the user-authorized scope and existing work.

`README.md` is the canonical English documentation. [README.zh-CN.md](README.zh-CN.md) is the complete Chinese counterpart.

## Skill table

| Skill | Use it when | Mutation authority |
| --- | --- | --- |
| `codex-implement-change` | The user explicitly asks to fix, add, change, remove, migrate, or refactor repository files. | Yes — only within the user-authorized repository scope. |
| `codex-readonly-review` | The user asks for a code, diff, branch, or pull-request review, audit, or risk assessment without authorizing edits. | No — strictly read-only; it does not repair findings. |
| `codex-verify-change` | The user asks whether a change works, fixes a problem, meets acceptance criteria, or is ready according to available evidence. | No — strictly read-only; it does not repair failures. |
| `story-to-film-planner` | The user wants narrative animated-short planning from an idea, story, script, reference images, or an existing storyboard. Not for live-action, advertising, or product films. | Planning documents only; no media generation, editing, upload, or publication. |

Within the engineering trio, only `codex-implement-change` may mutate files, and only inside the repository scope the user authorized. `codex-readonly-review` and `codex-verify-change` are strictly read-only. `story-to-film-planner` may create or revise authorized planning documents; it does not authorize repository code changes or media production.

Verification begins with exactly one verdict: `VERIFIED` when all material criteria have sufficient positive evidence and no contradiction; `NOT_VERIFIED` when observed evidence contradicts a material criterion or shows a relevant failure; or `BLOCKED` when required evidence, access, environment, or criteria are unavailable or materially ambiguous.

## Routing examples

| Request | Route | Resulting authority |
| --- | --- | --- |
| “Fix the failing parser test.” | `codex-implement-change` | May edit only the requested repository scope. |
| “Review this pull request; do not edit files.” | `codex-readonly-review` | Read-only findings. |
| “Verify whether this fix meets the acceptance criteria.” | `codex-verify-change` | Read-only evidence and one verdict. |
| “Review the change, then fix only confirmed P1 findings.” | `codex-readonly-review`, then `codex-implement-change` | Review finishes first; mutation starts only in a separate, explicitly authorized repair phase. |
| “Explain why this function is slow; do not change it.” | No skill in this pack | Explanation remains read-only. |
| “Plan characters, scenes, and storyboards for this animated short; do not generate media.” | `story-to-film-planner` | May write requested planning documents and inspect reference images the user provides. |

For engineering tasks, analysis or planning alone does not authorize implementation. Failed verification does not trigger repair. No skill invokes another skill automatically, and mixed wording uses the stricter authority until mutation intent is clear.

The planning skill's body and rules are written in Chinese. Its U01–U08 entries are author-set default rules (`【默认规则】`): they apply without re-asking but are never recorded as the current user's confirmation, and a user's own request overrides them within its stated scope. Per-project creative choices are marked `【项目判断】`; only U08 acceptance standards are left for the user to calibrate. Outline, style, duration, aspect-ratio, sound, and subtitle decisions remain with the user. It normally delivers one project workbook that tracks SRC (source), AST (asset), SH (shot), optional CLIP (production clip), and D (decision) codes, reads only the method-library entries a question needs, and includes unverified, platform-neutral prompt drafts only when requested. Any future generation would require a fresh quote and explicit approval for each submission. The files pass the repository's static checks; this distribution does not claim a story trial or verified media results.

## Installation

The canonical skill sources are the directories under `skills/`. Install only the skill or skills you need. The supported destinations are:

- Repository-local: `.agents/skills/<skill-name>`
- Personal: `~/.agents/skills/<skill-name>`

If your Codex environment provides a skill installer, select `skills/<skill-name>` as the source and one of the destinations above as the target. Installer interfaces may vary by environment. Direct copying works from the repository root; set `skill_name` to an exact name in the skill table.

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

Repeat with `codex-readonly-review`, `codex-verify-change`, or `story-to-film-planner` as needed. Direct copying changes only the selected destination and does not require changes to unrelated Codex configuration.

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

- Keep the documented skill inventory, validator inventory, tests, and authority matrix in sync when an addition is explicitly requested.
- Keep implementation changes within explicit user-authorized scope; keep review and verification strictly read-only.
- Treat tracked and untracked work as user-owned and do not erase or absorb unrelated changes.
- Commit each skill independently and run both validation commands before publishing.
- Update both `README.md` and `README.zh-CN.md` whenever public behavior or installation changes.
- Do not commit credentials, tokens, cookies, authentication artifacts, customer data, private logs, proprietary source, private repository names, private infrastructure topology, local machine paths, or environment-specific identifiers.
- Keep examples generic and reproducible. Do not claim affiliation or endorsement that does not exist.

See [AGENTS.md](AGENTS.md) for the repository policy and [the design specification](docs/superpowers/specs/2026-09-04-trista-codex-skills-design.md) for the V1 contracts and the planning-skill extension.

## Attribution

The structure of this pack was inspired by the public [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills) repository. This repository's wording, contracts, tests, and Codex-specific separation of implementation, review, and verification authority are original. This project is not affiliated with or endorsed by that repository's authors, Andrej Karpathy, or OpenAI.

## License

This repository is available under the [MIT License](LICENSE). Copyright 2026 Trista.
