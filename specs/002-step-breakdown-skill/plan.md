# Implementation Plan: Add Step Breakdown Skill

**Branch**: `002-step-breakdown-skill` | **Date**: 2026-11-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-step-breakdown-skill/spec.md`

## Summary

Add the `step-breakdown` skill from issue #3 to the repo. That means three things: a
readable skill folder (`step-breakdown/SKILL.md` plus `scripts/check_plan.py`), an
upload-ready `step-breakdown.skill` archive at the repo root, and README updates so the
skill shows up in the skills table, the install and update commands, the skill count and a
per-skill section.

The approach is to copy, not author. Both files are extracted verbatim from the issue's
collapsed source sections, with the fences stripped and LF line endings (see
[research.md](./research.md) R1). Unlike feature 001, there is no attached archive, so
`step-breakdown.skill` is built with the README's documented command. Verification is
scripted: the checker is run against the worked example in `SKILL.md`, a deliberately broken
plan and a forced non-UTF-8 console, then the archive is compared with the folder and the
README is grepped.

## Technical Context

**Language/Version**: Markdown (skill content and README); YAML frontmatter in `SKILL.md`;
Python 3.8+ standard library for `scripts/check_plan.py` (as shipped by the issue)
**Primary Dependencies**: None at runtime beyond Python's standard library. For packaging and
verification: .NET `System.IO.Compression` (README's Windows command) or `zip`, Python's
`zipfile` for listing and comparing, `git`, and `gh` (to fetch the issue body)
**Storage**: Files in the git repo
**Testing**: Scripted checks in [quickstart.md](./quickstart.md): extraction diff against the
issue, checker runs (clean, broken, no-arg, cp1252 stdout), archive entry and content
comparison, README grep checks and `git diff --stat` to confirm existing skills are untouched
**Target Platform**: Claude Code (`~/.claude/skills/` or `<project>/.claude/skills/`) and
Claude.ai / Claude Desktop skill upload; checker on Windows, macOS and Linux
**Project Type**: Content repository (agent skills), one folder plus one `.skill` archive per
skill
**Performance Goals**: N/A
**Constraints**: Skill content must match the issue's source exactly (FR-001). No `evals/`
folder (FR-002). Archive paths must use `/` (README L260). Existing skill folders and
archives must not change (FR-012). Files committed with LF, like the rest of the repo.
**Scale/Scope**: 2 new skill files (~211 + ~210 lines), 1 new archive, 1 README edit across
6 places (tagline, table, 3 copy commands, count sentence) plus 1 new section

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled spec-kit template
(`[PRINCIPLE_N_NAME]` placeholders), so there are no ratified principles to check against.
The de-facto conventions from the README and feature 001 are used instead:

| Convention | Status |
|---|---|
| One top-level folder per skill, `SKILL.md` + optional supporting folders | ✅ `step-breakdown/` (adds the repo's first `scripts/`, justified by the issue §4) |
| `<name>.skill` zip at the root, kept in sync with the folder | ✅ built with the README command, verified identical |
| Archive paths use `/`, not `\` | ✅ .NET `CreateFromDirectory` on PowerShell 7 / `zip`; verified |
| README skills table, install and update commands list every skill | ✅ planned README edits |
| No development-only material in the published skill | ✅ no `evals/` |

**Post-design re-check**: still passes. The only new structure is `scripts/`, which the issue
justifies and which `SKILL.md` makes optional by falling back to manual checks.

## Project Structure

### Documentation (this feature)

```text
specs/002-step-breakdown-skill/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output (validation guide)
├── contracts/
│   ├── skill-package.md # Layout contract for the folder + archive
│   └── check-plan-cli.md# Command-line contract for check_plan.py
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
step-breakdown/                          # NEW: skill source
├── SKILL.md
└── scripts/
    └── check_plan.py
step-breakdown.skill                     # NEW: upload archive (zip)
README.md                                # EDIT: tagline, table, quick start x2, count, section, updating
```

**Structure Decision**: Follow the existing flat layout: one top-level folder plus a sibling
`.skill` archive, like `peter-pr-review/` and `peter-pr-review.skill`. Nothing else in the
repo changes.

## Complexity Tracking

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| First `scripts/` folder in the repo | Cycle detection, transitive parallel-independence and availability checks are mechanical and easy for a model to get subtly wrong (issue §4) | Prose-only checks: kept as the fallback in `SKILL.md`, but unreliable as the primary check |
