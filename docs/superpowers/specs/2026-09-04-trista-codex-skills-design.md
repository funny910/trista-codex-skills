# Trista Codex Skills V1 Design

- Date: 2026-09-04
- Status: Design approved; implementation not started
- Repository: `funny910/trista-codex-skills`
- Visibility: Public
- License target: MIT

## 1. Purpose

This repository will provide a small, Codex-native skill pack for three recurring software-engineering modes:

1. making an explicitly requested code change;
2. reviewing code without changing it;
3. independently verifying a change without repairing it.

The pack turns broad engineering advice into explicit, testable contracts. It is deliberately smaller than a general agent framework: it does not add an orchestrator, state machine, model router, or external governance dependency.

## 2. Design source and adaptation

The design is informed by the public repository [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills), whose central observations are useful: think before editing, prefer simple solutions, keep changes surgical, and verify against the requested outcome.

This project adapts those observations for Codex by separating three authorities that should not be conflated:

- mutation authority for implementation;
- read-only authority for review;
- read-only, verdict-oriented authority for verification.

The wording, contracts, tests, and repository structure in this project will be original. This is not an official Andrej Karpathy or OpenAI project, and neither name implies endorsement.

## 3. Design goals

The V1 design optimizes for:

- clear routing from a user request to one skill;
- explicit mutation and read-only boundaries;
- protection of pre-existing work in a dirty working tree;
- the smallest complete change that satisfies the request;
- evidence proportional to the risk of the change;
- stable, machine-checkable skill structure;
- easy installation at user or repository scope;
- public-safe documentation with no private operational context.

## 4. Non-goals

V1 will not provide:

- automatic subagent delegation;
- model selection or model binding;
- an orchestration state machine, leases, or queues;
- adapters to external governance or orchestration systems;
- automatic pull requests, merges, releases, or deployments;
- GitHub write automation beyond normal user-directed repository work;
- a plugin marketplace package;
- language-specific test presets;
- automatic repair during review or verification;
- hidden escalation from read-only work to mutation.

These omissions are architectural boundaries, not unfinished work.

## 5. Repository structure

The completed V1 repository will use this layout:

```text
trista-codex-skills/
├── AGENTS.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── skills/
│   ├── codex-implement-change/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   └── openai.yaml
│   │   └── references/
│   │       ├── scope-and-ambiguity.md
│   │       ├── working-tree-safety.md
│   │       └── verification-baseline.md
│   ├── codex-readonly-review/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   └── openai.yaml
│   │   └── references/
│   │       └── review-severity.md
│   └── codex-verify-change/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       └── references/
│           ├── evidence-standard.md
│           └── verdict-rules.md
├── evals/
│   ├── routing-cases.json
│   └── behavior-cases.md
├── scripts/
│   └── validate_skills.py
├── tests/
│   └── test_skill_structure.py
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-09-04-trista-codex-skills-design.md
```

`SKILL.md` remains concise and routes to references only when their detail is needed. Repository-wide operating guidance belongs in `AGENTS.md`; task-specific behavior belongs in the applicable skill.

## 6. Shared principles

All three skills share the following principles:

### 6.1 Read before acting

Inspect the relevant instructions, repository state, and nearby implementation before deciding what to do. Do not infer authority from technical capability.

### 6.2 Preserve user work

Treat existing tracked and untracked changes as user-owned unless there is direct evidence otherwise. Do not erase, rewrite, or absorb unrelated work.

### 6.3 Match action to authority

Implementation may mutate only the authorized scope. Review and verification are strictly read-only. External actions require explicit user direction.

### 6.4 Prefer the smallest complete solution

Minimize conceptual and diff surface while still covering the requested behavior, necessary error paths, and relevant documentation or tests.

### 6.5 Use evidence, not confidence language

Claims must be backed by inspected code, command output, tests, or a clearly identified limitation. A successful command is evidence only for what that command actually exercises.

### 6.6 Report residual uncertainty

If verification is incomplete, say exactly what was not exercised and why. Do not silently convert missing evidence into success.

## 7. Skill contract: `codex-implement-change`

### 7.1 Intent

Use this skill when the user explicitly asks Codex to fix, add, change, remove, migrate, or refactor code or repository files.

### 7.2 Trigger examples

- “Fix this failing test.”
- “Add pagination to this endpoint.”
- “Refactor this module without changing behavior.”
- “Update the configuration and verify it.”

### 7.3 Exclusions

Do not select this skill when the user only asks for analysis, explanation, planning, review, audit, or verification. Do not infer permission to deploy, publish, merge, message third parties, or modify external systems.

### 7.4 Authority

The skill may modify files inside the repository scope authorized by the user. It may run safe, relevant inspection, formatting, build, lint, and test commands. It may not overwrite unrelated user changes or broaden the task into adjacent cleanup.

### 7.5 Required inputs

The workflow must establish:

- the requested outcome;
- the repository or directory in scope;
- applicable repository instructions;
- relevant existing changes;
- acceptance evidence that can reasonably be produced.

If a missing choice would materially change behavior, compatibility, public API, data, security, or cost, the skill pauses for the user. Minor implementation details are resolved locally using repository evidence and stated assumptions.

### 7.6 Workflow

1. Translate the request into an observable outcome.
2. Read applicable instructions and inspect repository status.
3. Locate the smallest relevant code path and its tests.
4. Identify constraints, ambiguity, and protected existing work.
5. Implement a minimal complete patch.
6. Review the diff for accidental scope growth.
7. Run the strongest safe verification available within task scope.
8. Report the result, evidence, files changed, and remaining limitations.

### 7.7 Output contract

The final response states:

- what changed and the resulting behavior;
- which verification ran and whether it passed;
- any material limitation, skipped check, or required follow-up;
- links to changed files when the environment supports them.

### 7.8 Stop conditions

Stop and request direction when:

- the target or authority is materially ambiguous;
- the change requires destructive treatment of user work;
- required access or approval is unavailable;
- the only viable solution expands into a meaningfully different project;
- a discovered security or data risk changes the requested trade-off.

## 8. Skill contract: `codex-readonly-review`

### 8.1 Intent

Use this skill when the user asks for a code review, pull-request review, branch review, audit, critique, or bug/risk assessment without asking for edits.

### 8.2 Trigger examples

- “Review this pull request.”
- “Audit this diff for regressions.”
- “Find correctness issues in this branch.”
- “Review this implementation, but do not change files.”

### 8.3 Exclusions

Do not edit files, apply patches, reformat code, create commits, post review comments, or repair findings. A request to “review and fix” is treated as two explicit phases: complete the review first, then implement only findings the user has authorized for repair.

### 8.4 Authority

The skill is strictly read-only. It may inspect files, diffs, history, tests, logs, and repository metadata. It may run non-mutating checks when safe. If a tool would write caches, snapshots, generated files, or lockfiles, avoid it or isolate it only when that behavior is proven safe.

### 8.5 Workflow

1. Establish the review target and comparison base.
2. Read applicable instructions and inspect the changed surface.
3. Trace behavior beyond the diff where necessary.
4. Check correctness, regressions, security, data handling, concurrency, compatibility, and test coverage as relevant.
5. Validate each candidate finding against concrete evidence.
6. Rank actionable findings by severity.
7. Report findings first; include a clean-review statement if none meet the threshold.

### 8.6 Finding contract

Each finding includes:

- severity;
- concise title;
- file and line or smallest useful location;
- evidence and triggering scenario;
- user-visible or system impact;
- focused remediation direction.

Speculation is not a finding. Style preferences are omitted unless they create a concrete maintenance, correctness, or policy risk.

### 8.7 Severity model

- `P0 — Critical`: immediate catastrophic security, data, availability, or safety impact.
- `P1 — High`: likely production breakage, exploitable vulnerability, or major data/correctness failure.
- `P2 — Medium`: real defect with bounded impact or a credible regression in common use.
- `P3 — Low`: limited-impact defect or maintainability issue with a concrete failure mode.

### 8.8 Output contract

Findings appear in severity order. The response separates findings from questions and residual risks. If no actionable finding is supported, it says so directly and summarizes what was inspected.

## 9. Skill contract: `codex-verify-change`

### 9.1 Intent

Use this skill when the user asks whether a change works, meets acceptance criteria, fixes a reported problem, or is ready according to available evidence.

### 9.2 Trigger examples

- “Verify this fix.”
- “Check whether the acceptance criteria are met.”
- “Confirm that this branch solves the bug.”
- “Independently validate the implementation.”

### 9.3 Exclusions

Do not repair failures, alter tests to make them pass, update snapshots, edit configuration, or broaden the acceptance criteria. A request to fix a verification failure requires a new, explicit implementation instruction.

### 9.4 Authority

The skill is strictly read-only. It may inspect repository state and run safe checks whose side effects are either absent or confined to disposable artifacts. It must not change tracked source or user-owned untracked content.

### 9.5 Workflow

1. Restate the claim or acceptance criteria being verified.
2. Identify the implementation and evidence required for each criterion.
3. Inspect the relevant diff and current repository state.
4. Run targeted checks first, followed by broader checks when proportionate and available.
5. Compare observed results with each criterion.
6. Issue exactly one verdict and attach the supporting evidence.

### 9.6 Verdicts

- `VERIFIED`: all material criteria have sufficient positive evidence and no contradictory evidence remains.
- `NOT_VERIFIED`: observed evidence contradicts at least one material criterion or demonstrates a relevant failure.
- `BLOCKED`: a verdict cannot be reached because required evidence is unavailable, access is missing, the environment is unsuitable, or the criteria are materially ambiguous.

`BLOCKED` is not a softer form of success. `NOT_VERIFIED` does not necessarily mean the implementation is universally wrong; it means the stated claim is not supported by the observed evidence.

### 9.7 Output contract

The response includes:

- the verdict as the first material result;
- a criterion-by-criterion evidence summary;
- commands or inspections performed;
- failures or blockers with exact scope;
- residual risk and untested areas.

## 10. Routing and interaction rules

The three skills are mutually distinct but can be invoked in a user-directed sequence.

| User intent | Selected skill | Mutation allowed |
|---|---|---:|
| Change repository behavior or files | `codex-implement-change` | Yes, within scope |
| Assess code and report defects | `codex-readonly-review` | No |
| Decide whether a claim is supported | `codex-verify-change` | No |

Additional routing rules:

- Analysis or planning alone does not trigger implementation.
- “Review and fix” runs review first and does not silently repair every observation; repair scope must be explicit in the original request or confirmed afterward.
- A failed verification does not automatically trigger implementation.
- No skill invokes another skill automatically.
- When wording is mixed, the stricter authority applies until mutation intent is clear.

## 11. Progressive disclosure

Each `SKILL.md` contains only the routing description, core contract, workflow, output format, and pointers to deeper material.

References are loaded selectively:

- implementation loads scope guidance for consequential ambiguity;
- implementation loads working-tree safety when existing changes are present;
- implementation loads the verification baseline when choosing checks;
- review loads severity guidance when classifying a candidate finding;
- verification loads evidence standards when mapping checks to claims;
- verification loads verdict rules when evidence is mixed or incomplete.

Reference files do not repeat the full skill contract.

## 12. Codex metadata

Each skill includes `agents/openai.yaml` with:

- a human-readable display name;
- a concise description that distinguishes its authority from the other two skills;
- an invocation prompt that names the skill explicitly using `$skill-name`;
- implicit invocation enabled;
- no model binding, external dependency, or hidden tool requirement.

The YAML metadata complements, but does not replace, the `SKILL.md` frontmatter description used for routing.

## 13. Installation and distribution

The canonical source lives under `skills/` in this repository. Users may install only the skill or skills they need.

Supported destinations:

- user scope: `~/.agents/skills/<skill-name>`;
- repository scope: `.agents/skills/<skill-name>`.

The README will document installation through Codex's skill installer as well as direct copying. Installation instructions will not mutate unrelated Codex configuration.

## 14. Validation strategy

V1 includes structural validation and behavior-oriented evaluation fixtures.

### 14.1 Structural validator

`scripts/validate_skills.py` will fail when:

- an expected skill directory or required file is missing;
- `SKILL.md` lacks valid frontmatter;
- the frontmatter name differs from the directory name;
- a description is empty or fails to distinguish the skill's trigger;
- a referenced local file does not exist;
- `agents/openai.yaml` lacks required interface fields;
- its default prompt does not name the corresponding skill;
- placeholder markers such as `TODO` or `TBD` remain in shipped skill content.

The validator uses the Python standard library so that V1 has no runtime package dependency.

### 14.2 Automated tests

`tests/test_skill_structure.py` exercises the validator and asserts the expected three-skill inventory. The test suite will include negative fixtures or temporary mutations that prove invalid structure is rejected.

### 14.3 Routing cases

`evals/routing-cases.json` records positive and negative prompts for each skill, including mixed requests. Each case specifies the expected skill and whether mutation is allowed.

### 14.4 Behavior cases

`evals/behavior-cases.md` defines manually inspectable scenarios for:

- dirty working-tree preservation;
- ambiguous scope;
- review findings with insufficient evidence;
- verification with mixed test outcomes;
- read-only requests that tempt repair;
- unavailable tooling or access;
- explicit external-action boundaries.

V1 does not claim a model-evaluation harness. These fixtures make expected behavior reviewable and provide inputs for future automation.

## 15. Public repository safety

The public repository must not contain:

- credentials, tokens, cookies, or authentication artifacts;
- customer data, private logs, or proprietary source snippets;
- private repository names or internal system topology;
- local machine paths or environment-specific identifiers;
- claims of affiliation or endorsement that do not exist.

Examples remain generic and reproducible.

## 16. Documentation and license

- `README.md` is the canonical English overview.
- `README.zh-CN.md` provides a complete Chinese introduction and usage guide.
- Skill instruction files are canonical in English to keep routing language consistent across Codex environments.
- The repository uses the MIT License.
- Attribution credits the source of inspiration without presenting this project as a derivative official package.

## 17. Acceptance criteria for V1

V1 is complete only when all of the following are true:

1. Exactly the three designed skills exist under `skills/`.
2. Each skill has valid frontmatter and Codex metadata.
3. Implementation is the only skill that authorizes repository mutation.
4. Review and verification contracts explicitly prohibit repair.
5. Verification always resolves to `VERIFIED`, `NOT_VERIFIED`, or `BLOCKED`.
6. Reference links resolve and progressive disclosure is preserved.
7. The structural validator passes.
8. The automated tests pass.
9. Routing and behavior fixtures cover positive, negative, and mixed-intent cases.
10. Both READMEs explain scope, installation, usage, limitations, attribution, and license.
11. No credential, private operational detail, placeholder, or unintended generated artifact is committed.
12. The final diff is reviewed against this design before release.

## 18. Implementation gate

This document records the approved architecture and skill contracts. Its commit is a design-only checkpoint. No skill implementation is authorized by this checkpoint alone.

The next stage is:

1. owner review of this committed specification;
2. a detailed implementation plan derived from the approved specification;
3. implementation only after that plan is accepted for execution.

