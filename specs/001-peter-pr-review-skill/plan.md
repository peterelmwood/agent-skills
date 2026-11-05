# Implementation Plan: Add Peter PR Review Skill

**Branch**: `001-peter-pr-review-skill` | **Date**: 2026-11-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-peter-pr-review-skill/spec.md`

## Summary

Add the `peter-pr-review` skill from issue #1 to the repo. That means three things: a readable
skill folder (`peter-pr-review/SKILL.md` plus five `references/examples-*.md` files), its
upload-ready `peter-pr-review.skill` archive at the repo root, and README updates so the skill shows
up in the skills table, the install and update commands, and a per-skill section.

The approach is copy, not author. The attachments are adopted byte-for-byte. The archive is the
author's own packaged `.skill` taken from inside the issue's zip, so it already matches the folder.
Verification is file hashes and archive listings, since the repo has no test harness.

## Technical Context

**Language/Version**: Markdown (skill content and README); YAML front matter in `SKILL.md`

**Primary Dependencies**: None at runtime. For packaging and verification: `unzip`/`zip` or .NET
`System.IO.Compression` (as documented in the README), `sha256sum`/`Get-FileHash`, `git`, and `gh`
(already used to read the issue)

**Storage**: Files in the git repo

**Testing**: Scripted checks (see [quickstart.md](./quickstart.md)): hash comparisons against the
attachments, archive entry listing, reference-path resolution, README grep checks, and
`git diff --stat` to confirm existing skills are untouched

**Target Platform**: Claude Code (`~/.claude/skills/` or `<project>/.claude/skills/`) and
Claude.ai / Claude Desktop skill upload

**Project Type**: Content repository (agent skills), one folder plus one `.skill` archive per skill

**Performance Goals**: N/A

**Constraints**: Content must be byte-identical to the issue attachments (FR-001/002). Archive
entries must use `/` separators (README guidance). Existing skills must not change (FR-011).
The feature commit stages only `peter-pr-review/`, `peter-pr-review.skill`, `README.md` and
`specs/001-peter-pr-review-skill/`. Spec-kit tooling (`.specify/`, `.claude/skills/speckit-*`) stays
out of it (spec Assumptions).

**Scale/Scope**: 6 skill files (~112 KB), 1 archive (~44 KB), and 1 README edited in 6 places

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled spec-kit template: every principle is a
`[PRINCIPLE_N_NAME]` placeholder. There are no ratified principles to check against, so the gate
**passes vacuously**. The README's de facto repo conventions are used as gates instead:

| Convention (from README) | Plan complies? |
|---|---|
| One top-level folder per skill, with `SKILL.md` + optional `references/` | ✅ `peter-pr-review/` |
| `<name>.skill` zip at the root, kept in sync with the folder | ✅ attached package, verified identical |
| Archive paths use `/`, not `\` | ✅ verified on the attached package |
| README skills table, install and update commands list every skill | ✅ planned README edits |

**Post-design re-check**: still passes. The design adds no new tooling, scripts or structure.

## Project Structure

### Documentation (this feature)

```text
specs/001-peter-pr-review-skill/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output (validation guide)
├── contracts/
│   └── skill-package.md # Layout contract for the folder + archive
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
peter-pr-review/                         # NEW: skill source
├── SKILL.md
└── references/
    ├── examples-backend.md
    ├── examples-frontend.md
    ├── examples-summaries-and-pushback.md
    ├── examples-tests.md
    └── examples-typing.md
peter-pr-review.skill                    # NEW: upload archive (zip)
README.md                                # EDIT: table, quick start x2, section, updating
```

**Structure Decision**: Follow the existing flat layout: one top-level folder plus a sibling
`.skill` archive, like `design-patterns/` and `design-patterns.skill`. Nothing else in the repo
changes.

## Complexity Tracking

No violations, so nothing to justify.
