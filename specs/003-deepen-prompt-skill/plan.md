# Implementation Plan: Add Deepen Prompt Skill

**Branch**: `003-deepen-prompt-skill` | **Date**: 2026-11-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-deepen-prompt-skill/spec.md`

## Summary

Add the `deepen-prompt` skill from issue #4: a one-file skill folder
(`deepen-prompt/SKILL.md`), an upload-ready `deepen-prompt.skill` archive, README updates
(table, three copy commands, count, per-skill section), and `*-workspace/` in `.gitignore`.

As in feature 002, the approach is to copy, not author: `SKILL.md` is extracted verbatim
from the issue's ````` ````markdown ````` fence (research R1). The archive is built with the
README's PowerShell 7 command. The issue's skill-creator evals are run where the tooling
allows it, with output kept outside the repo (research R4).

## Technical Context

**Language/Version**: Markdown with YAML frontmatter
**Primary Dependencies**: None at runtime. For packaging and checks: .NET
`System.IO.Compression`, Python `zipfile` and `yaml`, `git`, `gh`, skill-creator's
`quick_validate.py`
**Storage**: Files in the git repo
**Testing**: Scripted checks in [quickstart.md](./quickstart.md); output evals from issue §8
**Target Platform**: Claude Code skills directory; Claude.ai / Claude Desktop upload
**Project Type**: Content repository (agent skills)
**Constraints**: `SKILL.md` matches the issue exactly; no `evals/` in the folder; archive
paths use `/`; existing skills untouched; LF, UTF-8 without BOM
**Scale/Scope**: 1 new file (67 lines), 1 archive, README (5 edits + 1 section), 1
`.gitignore` line

## Constitution Check

No ratified constitution (see feature 002's plan). Repo conventions:

| Convention | Status |
|---|---|
| One top-level folder per skill, `SKILL.md` + optional supporting folders | ✅ `deepen-prompt/SKILL.md` only |
| `<name>.skill` zip at the root, in sync with the folder | ✅ built with README command, verified |
| Archive paths use `/` | ✅ verified |
| README table, install and update commands list every skill | ✅ |
| No development-only material in the published skill | ✅ no `evals/`; workspace ignored |

## Project Structure

### Documentation (this feature)

```text
specs/003-deepen-prompt-skill/
├── plan.md
├── research.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

The folder/archive/README contract is the one in
`specs/001-peter-pr-review-skill/contracts/skill-package.md`; no new contract or data model
is needed for a single instruction file.

### Source Code (repository root)

```text
deepen-prompt/            # NEW
└── SKILL.md
deepen-prompt.skill       # NEW
README.md                 # EDIT: table, quick start x2, count, section, updating
.gitignore                # EDIT: *-workspace/
```

**Structure Decision**: Same flat layout as every other skill.

## Complexity Tracking

None. No `references/` or `scripts/` (FR-003; research R3).
