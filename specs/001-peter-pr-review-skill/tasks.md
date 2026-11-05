# Tasks: Add Peter PR Review Skill

**Input**: Design documents from `/specs/001-peter-pr-review-skill/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/skill-package.md, quickstart.md

**Tests**: The spec doesn't ask for automated tests, and the repo has no test harness.
Verification uses the scripted checks in [quickstart.md](./quickstart.md) (V1–V6), run as tasks.

**Organization**: Tasks are grouped by user story so each story can be delivered and checked on
its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task belongs to (US1, US2, US3)

## Path Conventions

All paths are relative to the repo root. `$SRC` is the scratch folder with the issue #1
attachments. It contains the loose files plus the nested package unzipped to
`$SRC/z2/peter-pr-review/` (research R1).

---

## Phase 1: Setup

**Purpose**: Get the source material from issue #1 into a local scratch folder.

- [X] T001 Download all seven attachments of https://github.com/peterelmwood/agent-skills/issues/1 into a new empty scratch folder `$SRC`. Unzip `peter-pr-review.skill.zip`, then unzip the inner `peter-pr-review.skill` into `$SRC/z2/`.
- [X] T002 Confirm that each of the six loose attachments is byte-identical to its counterpart under `$SRC/z2/peter-pr-review/` (`cmp`). If any differ, stop and report, since the package is authoritative (spec Edge Cases).

---

## Phase 2: Foundational

**Purpose**: Blocking checks before any file is added.

- [X] T003 Confirm that nothing named `peter-pr-review` exists yet at the repo root (`peter-pr-review/`, `peter-pr-review.skill`) and that `README.md` has no `peter-pr-review` mention (spec Edge Case: name collision).
- [X] T004 Run the sensitive-content scan from research R4 over `$SRC/z2/peter-pr-review/`. Report any credential, internal-host or private-repo hits to the maintainer without editing the content (FR-012).

**Checkpoint**: The source is verified and the target paths are free.

---

## Phase 3: User Story 1 - Install the skill in Claude Code from the repo (Priority: P1) 🎯 MVP

**Goal**: Add a `peter-pr-review/` folder that Claude Code can load.

**Independent Test**: quickstart V1 and V3 pass. V6 is the manual install smoke test.

- [X] T005 [US1] Copy `$SRC/z2/peter-pr-review/SKILL.md` to `peter-pr-review/SKILL.md`, unchanged (FR-001).
- [X] T006 [P] [US1] Copy the five `$SRC/z2/peter-pr-review/references/examples-*.md` files to `peter-pr-review/references/`, unchanged (FR-002).
- [X] T007 [US1] Run quickstart V1 (hash comparison, exactly six files, FR-003) and V3 (`name: peter-pr-review` front matter, every `references/` path resolves; FR-005, FR-006) against `peter-pr-review/`.

**Checkpoint**: The folder alone is installable via `cp -r peter-pr-review ~/.claude/skills/`.

---

## Phase 4: User Story 2 - Upload the skill to Claude.ai / Claude Desktop (Priority: P2)

**Goal**: Ship `peter-pr-review.skill` in sync with the folder.

**Independent Test**: quickstart V2a–V2c pass.

- [X] T008 [US2] Copy `$SRC/z/peter-pr-review.skill` (the inner package, not the outer `.zip`; research R2, R3) to `peter-pr-review.skill` at the repo root.
- [X] T009 [US2] Run quickstart V2: the file entries equal the folder files, no `\` separators, and the extracted tree has no diff against `peter-pr-review/` (FR-004).

**Checkpoint**: The archive is uploadable and matches the folder.

---

## Phase 5: User Story 3 - Discover and understand the skill from the README (Priority: P3)

**Goal**: Have the README list, explain and install the new skill (research R5).

**Independent Test**: quickstart V4a–V4d pass.

- [X] T010 [US3] In `README.md` quick start, add `peter-pr-review` to the macOS/Linux `cp -r` command and the Windows `Copy-Item` command. Change "All four skills are now installed" to "All five skills are now installed" (FR-008, FR-010).
- [X] T011 [US3] In the `README.md` "The skills" table, add a row after `feature-request-issue-author`: `` [`peter-pr-review`](peter-pr-review/SKILL.md) `` with a "Use it for" line about reviewing a PR or diff in Peter's style (Django/DRF and React/TypeScript), with inline comments and a summary (FR-007).
- [X] T012 [US3] In `README.md`, add a `### peter-pr-review` section after the issue-author section, before the `---` and "How skills work". Match the house style: a short description of what it does (distilled from Peter's reviews and weighted toward 2025), the review areas it checks, **When it runs**, output behavior (it drafts `path:line` comments plus a summary and verdict, and does not post unless asked), and a **What's inside** tree for `peter-pr-review/` with one-line descriptions of the five reference files (FR-009).
- [X] T013 [US3] In the `README.md` "Updating" section, add `peter-pr-review` to the `cp -r` command (FR-008).
- [X] T014 [US3] Run quickstart V4a–V4d against `README.md`.

**Checkpoint**: The README is complete and consistent.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 Run quickstart V5 (`git diff --stat main` over the existing skill folders and archives) to confirm nothing outside the new files and `README.md` changed (FR-011, SC-005).
- [X] T016 Rerun quickstart V1–V4 together as a final regression pass, and record the results in the implementation summary.
- [ ] T017 Stage only `peter-pr-review/`, `peter-pr-review.skill`, `README.md` and `specs/001-peter-pr-review-skill/` with explicit `git add <paths>`, never `git add .`. Confirm with `git status --short` that `.specify/` and `.claude/` stay unstaged (plan Constraints). Commit only if the user approves.

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003–T004)** → the user stories.
- **US1 (T005–T007)** has no dependency on the other stories.
- **US2 (T008–T009)**: T008 is independent, but T009 compares against the folder, so it needs T005–T006.
- **US3 (T010–T014)**: T010–T013 edit the same file (`README.md`), so they run in sequence. The tree in T012 describes the folder from US1. T014 needs T010–T013.
- **Polish (T015–T017)** comes after all the stories. T017 is last.

## Parallel Opportunities

- T005 and T006 (different files).
- T008 can run alongside T005–T006 (a different file).
- Once Foundational is done, US1 and the README edits (T010–T013) can proceed in parallel because they touch different files.

```text
Parallel batch A: T005, T006, T008
Then:             T007, T009
Sequential:       T010 → T011 → T012 → T013 → T014
Finally:          T015 → T016 → T017
```

## Implementation Strategy

- **MVP**: Phases 1–3 (US1), which make the skill installable in Claude Code.
- **Increment 2**: US2 adds the upload archive.
- **Increment 3**: US3 makes the skill discoverable in the README.
- Each increment is independently verifiable with its quickstart checks.
