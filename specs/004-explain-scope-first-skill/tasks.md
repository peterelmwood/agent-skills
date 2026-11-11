# Tasks: Add Explain-Scope-First Skill

**Input**: Design documents from `/specs/004-explain-scope-first-skill/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: The repo has no test harness. Verification uses the scripted checks in
[quickstart.md](./quickstart.md) (§1–§5), run as tasks below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story the task belongs to (US1–US3)

`$S` is a new, empty scratch folder outside the repo.

---

## Phase 1: Setup

- [X] T001 Create branch `004-explain-scope-first-skill` from `skills-step-breakdown-deepen-prompt-asd-ste100`.
- [X] T002 Fetch the issue body with `gh issue view 5 --repo peterelmwood/agent-skills --json body --jq .body > $S/issue5.md` (research R1).

## Phase 2: Foundational

- [X] T003 Confirm `explain-scope-first/` and `explain-scope-first.skill` don't exist and `README.md` doesn't mention `explain-scope-first`.
- [X] T004 Decide supporting files: none, `SKILL.md` only (research R2).

---

## Phase 3: User Story 1 - Install and use in Claude Code (Priority: P1) 🎯 MVP

- [X] T005 [US1] Extract the ```` ````markdown ```` fence to `explain-scope-first/SKILL.md`: LF, one trailing newline, UTF-8 without BOM (FR-001).
- [X] T006 [US1] Run quickstart §1: byte match against the issue, one file in the folder, `name: explain-scope-first` (FR-001, FR-002).
- [X] T007 [US1] Review the source against issue acceptance criteria 1–11 (FR-003–FR-007). Record gaps as follow-ups in research.md; don't edit the file (research R5).

## Phase 4: User Story 2 - Upload to Claude.ai / Claude Desktop (Priority: P2)

- [X] T008 [US2] Build `explain-scope-first.skill` with the README's PowerShell 7 command (quickstart §2, FR-008).
- [X] T009 [US2] Run quickstart §3 against the committed blobs: one entry, no `\`, identical bytes (SC-002).

## Phase 5: User Story 3 - Discover in the README (Priority: P3)

- [X] T010 [P] [US3] Add `explain-scope-first` after `asd-ste100` in the Quick start `cp -r`, `Copy-Item` and Updating `cp -r` commands; change "All eight skills" to "All nine skills"; add the table row after `asd-ste100`; leave the tagline (research R3, R4).
- [X] T011 [US3] Add `### explain-scope-first` after the `### asd-ste100` section: what it does, **When it runs**, **What it produces**, **What's inside** tree (FR-009).
- [X] T012 [US3] Run quickstart §4 grep checks (SC-003).

## Phase 6: Polish

- [X] T013 Run quickstart §5 scope check: empty (FR-010, SC-004).
- [X] T014 Commit on `004-explain-scope-first-skill` referencing issue #5. No push, PR or issue edits.
- [X] T015 Record quickstart §6 (behavioral scenarios from issue §8) as outstanding follow-up F1 for the maintainer; skills load at session start, and no results are claimed (SC-005).

## Dependencies

- T001–T002 → T003–T004 → US1 (T005–T007) → US2 (T008–T009, packages the folder).
- US3 (T010–T012) depends only on T004 (the "What's inside" tree) and can run alongside US1–US2.
- T013–T015 run last.
