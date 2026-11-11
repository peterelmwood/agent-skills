# Implementation Plan: Add Explain-Scope-First Skill

**Branch**: `004-explain-scope-first-skill` | **Date**: 2026-11-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-explain-scope-first-skill/spec.md`

## Summary

Add the `explain-scope-first` skill from issue #5 verbatim as a one-file skill folder,
package it as `explain-scope-first.skill`, and document it in the README. Content and
documentation only; no code, scripts or dependencies.

## Technical Context

**Language/Version**: Markdown (skill instructions); PowerShell 7 for packaging; Python 3
(`zipfile`, standard library) for verification
**Primary Dependencies**: None
**Storage**: Files in the repo
**Testing**: Scripted byte/zip/grep checks in [quickstart.md](./quickstart.md); behavioral
scenarios from issue §8 are manual and outstanding
**Target Platform**: Claude Code (`~/.claude/skills/`), Claude.ai / Claude Desktop upload
**Project Type**: Skill package (folder + archive + README entry)
**Constraints**: Source bytes identical to the issue; LF in committed blobs despite
`core.autocrlf=true`; archive entries use `/`
**Scale/Scope**: 1 skill file (30 lines), 1 archive, README edits

## Constitution Check

No project constitution applies in this worktree. The package conventions from
`specs/001-peter-pr-review-skill/contracts/skill-package.md` are followed: frontmatter
`name` matches the folder, archive uses `/` separators with identical bytes, README lists
the skill.

## Project Structure

### Documentation (this feature)

```text
specs/004-explain-scope-first-skill/
├── spec.md
├── plan.md
├── research.md
├── quickstart.md
├── tasks.md
└── checklists/
    └── requirements.md
```

### Source (repository root)

```text
explain-scope-first/
└── SKILL.md                 # verbatim from issue #5
explain-scope-first.skill    # zip of the folder (folder name as top-level entry)
README.md                    # table row, three copy commands, count, section
```

**Structure Decision**: Same layout as `deepen-prompt/` (single `SKILL.md`, no supporting
folders), because issue §4 says the workflow needs no scripts or references.

## Complexity Tracking

None.
