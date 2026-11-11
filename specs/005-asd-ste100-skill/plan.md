# Implementation Plan: Add ASD-STE100 Prompt-Constraint Skill

**Branch**: `005-asd-ste100-skill` | **Date**: 2026-11-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-asd-ste100-skill/spec.md`

## Summary

Add the `asd-ste100` skill from issue #6: a skill folder (`asd-ste100/SKILL.md` plus
`agents/openai.yaml`), an upload-ready `asd-ste100.skill` archive at the repo root, and
README updates (table, three copy commands, skill count, per-skill section).

As with feature 002, the approach is to copy, not author: both files are extracted verbatim
from the issue body fetched as JSON (see [research.md](./research.md) R1). The archive is
built with the README's PowerShell 7 command and compared with the folder in Python.

## Technical Context

**Language/Version**: Markdown with YAML frontmatter (`SKILL.md`); YAML (`openai.yaml`)
**Primary Dependencies**: None at runtime. For packaging and checks: .NET
`System.IO.Compression` (PowerShell 7), Python `zipfile` and PyYAML, `git`, `gh`
**Storage**: Files in the git repo
**Testing**: Scripted checks in [quickstart.md](./quickstart.md)
**Target Platform**: Claude Code (`~/.claude/skills/`), Claude.ai / Claude Desktop upload
**Project Type**: Content repository (agent skills)
**Constraints**: Content identical to the issue (FR-001); no standard or dictionary text
(FR-003); archive paths use `/`; other skills unchanged (FR-008); LF line endings
**Scale/Scope**: 2 new files (47 + 4 lines), 1 archive, README edits in 7 places

## Constitution Check

`.specify/memory/constitution.md` isn't in this worktree and was an unfilled template in
earlier features, so the repo's de-facto conventions are used:

| Convention | Status |
|---|---|
| One top-level folder per skill, `SKILL.md` + optional supporting folders | ✅ `asd-ste100/` (adds an `agents/` folder; see research R2) |
| `<name>.skill` zip at the root, kept in sync with the folder | ✅ built with the README command, verified identical |
| Archive paths use `/`, not `\` | ✅ verified |
| README table, install and update commands list every skill | ✅ |
| No copyrighted third-party standard text in the repo | ✅ checked (research R3) |

## Project Structure

### Documentation (this feature)

```text
specs/005-asd-ste100-skill/
├── spec.md
├── plan.md              # This file
├── research.md
├── quickstart.md        # Validation guide
├── checklists/
│   └── requirements.md
└── tasks.md
```

No `data-model.md` or `contracts/`: the skill has no script or data format, and the
package layout is covered by spec FR-001/FR-006 and quickstart §2–§3.

### Source Code (repository root)

```text
asd-ste100/                  # NEW: skill source
├── SKILL.md
└── agents/
    └── openai.yaml
asd-ste100.skill             # NEW: upload archive (zip)
README.md                    # EDIT: tagline, table, quick start x2, count, section, updating
```

**Structure Decision**: Same flat layout as every other skill. Nothing else changes.

## Complexity Tracking

| Deviation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| First `agents/openai.yaml` in the repo | Issue ships it to preserve the original generated skill | Dropping it diverges from the issue's source; it is inert for Claude (research R2) |
