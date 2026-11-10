# Tasks: Add ASD-STE100 Prompt-Constraint Skill

**Input**: Design documents from `/specs/005-asd-ste100-skill/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: The repo has no test harness. Verification uses the scripted checks in
[quickstart.md](./quickstart.md) (§1–§5), run as tasks below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story the task belongs to (US1–US3)

`$S` is a new, empty scratch folder outside the repo.

---

## Phase 1: Setup

- [X] T001 Create branch `005-asd-ste100-skill` from `002-step-breakdown-skill`.
- [X] T002 Fetch the issue body as JSON with `gh issue view 6 --repo peterelmwood/agent-skills --json body > $S/issue6.json` (research R1).
- [X] T003 Extract the ```` ````markdown ```` fence to `$S/extract/SKILL.md` and the ```` ````yaml ```` fence to `$S/extract/agents/openai.yaml` with `python -I`: LF, one trailing newline, UTF-8 without BOM. Confirm 47 and 4 lines, frontmatter parses with `name: asd-ste100`, and `openai.yaml` parses.

## Phase 2: Foundational

- [X] T004 Confirm `asd-ste100/` and `asd-ste100.skill` don't exist and `README.md` doesn't mention `asd-ste100`.
- [X] T005 Decide whether to keep `agents/openai.yaml` and record it (research R2: keep).

---

## Phase 3: User Story 1 - Install and use in Claude Code (Priority: P1) 🎯 MVP

- [X] T006 [US1] Copy `$S/extract/SKILL.md` to `asd-ste100/SKILL.md` byte-for-byte (FR-001).
- [X] T007 [P] [US1] Copy `$S/extract/agents/openai.yaml` to `asd-ste100/agents/openai.yaml` byte-for-byte (FR-001, research R2).
- [X] T008 [US1] Run quickstart §1: `cmp` both files, frontmatter name check, `find` lists exactly two files (FR-002).
- [X] T009 [US1] Check `SKILL.md` reproduces no standard or dictionary text (FR-003, research R3) and covers the STE-inspired vs verified-conformance distinction with approved meanings, parts of speech, technical names and technical verbs (FR-004), and that the description scopes use to STE requests (FR-005). Record gaps as follow-ups in research.md; don't edit the file.

## Phase 4: User Story 2 - Upload to Claude.ai / Claude Desktop (Priority: P2)

- [X] T010 [US2] Build `asd-ste100.skill` with the README's PowerShell 7 command (quickstart §2, FR-006).
- [X] T011 [US2] Run quickstart §3: entries exactly the folder's two files, no `\`, identical bytes (SC-002).

## Phase 5: User Story 3 - Discover in the README (Priority: P3)

- [X] T012 [P] [US3] Add `asd-ste100` after `step-breakdown` in the Quick start `cp -r` (L13), `Copy-Item` (L22) and Updating `cp -r` (L253) commands; change "All six skills" to "All seven skills"; add the table row after `step-breakdown`; add one tagline clause (research R5).
- [X] T013 [US3] Add `### asd-ste100` after `### step-breakdown`: what it does, STE-inspired vs verified conformance, **When it runs**, **What it produces**, **What's inside** tree including `agents/openai.yaml`.
- [X] T014 [US3] Run quickstart §4 grep checks (SC-003).

## Phase 6: Polish

- [X] T015 Run quickstart §5 scope check: empty (FR-008, SC-004).
- [X] T016 Commit on `005-asd-ste100-skill` referencing issue #6. No push, PR or issue edits.
- [X] T017 Leave quickstart §6 (manual smoke test in a new Claude Code session) for the maintainer; skills load at session start.

## Dependencies

- T001–T003 → T004–T005 → US1 (T006–T009) → US2 (T010–T011, packages the folder).
- US3 (T012–T014) depends only on T005 (the "What's inside" tree) and can run alongside US1–US2.
- T015–T017 run last.
