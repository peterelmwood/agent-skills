# Tasks: Add Deepen Prompt Skill

**Input**: Design documents from `/specs/003-deepen-prompt-skill/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: No test harness in the repo. Verification uses the scripted checks in
[quickstart.md](./quickstart.md) and the issue §8 output evals, run as tasks below.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story the task belongs to (US1–US3)

`$S` is a scratch folder outside the repo.

---

## Phase 1: Setup

- [X] T001 Create branch `003-deepen-prompt-skill` from `002-step-breakdown-skill`.
- [X] T002 Fetch the issue body as JSON with `gh issue view 4 --repo peterelmwood/agent-skills --json body > $S/issue4.json` (research R1).

## Phase 2: Foundational

- [X] T003 Confirm `deepen-prompt/` and `deepen-prompt.skill` don't exist and the README doesn't mention `deepen-prompt`.

---

## Phase 3: User Story 1 - Install the skill and get a deeper prompt (Priority: P1) 🎯 MVP

- [X] T004 [US1] Extract the ````` ````markdown ````` fence to `deepen-prompt/SKILL.md` with `python -I`: LF, one trailing newline, UTF-8 without BOM (FR-001). Confirm 67 lines and `name: deepen-prompt` on line 2.
- [X] T005 [US1] Parse the frontmatter (exactly `name` and `description`, description ≤ 1024 chars) and run skill-creator's `quick_validate.py` (FR-002).
- [X] T006 [US1] Run the 4 issue §8 output evals with the skill and as a no-skill baseline; save and grade outside the repo (research R4, SC-001). Result: 23/24 vs 10/24.
- [X] T007 [US1] Decide on `references/examples.md` from the eval outputs: not needed (research R3, FR-003).
- [X] T008 [US1] Review `SKILL.md` against the issue's behaviour criteria and record gaps as follow-ups in research.md without editing the file.

## Phase 4: User Story 2 - Upload to Claude.ai / Claude Desktop (Priority: P2)

- [X] T009 [US2] Confirm `deepen-prompt/` contains only `SKILL.md`, then build `deepen-prompt.skill` with the README's PowerShell 7 command (research R2, FR-005).
- [X] T010 [US2] Run quickstart §2: entries are exactly `deepen-prompt/SKILL.md`, no `\`, bytes identical (SC-004).

## Phase 5: User Story 3 - Discover from the README (Priority: P3)

- [X] T011 [P] [US3] Add `deepen-prompt` after `step-breakdown` in the Quick start `cp -r` (L13), `Copy-Item` (L22) and Updating `cp -r` (L253) commands; change "All six skills" to "All seven skills" (FR-006).
- [X] T012 [US3] Add a skills-table row after `step-breakdown` and a `### deepen-prompt` section after `### step-breakdown` with what it does, **When it runs**, **What it produces** and **What's inside** (FR-006).
- [X] T013 [US3] Run quickstart §3 grep checks (SC-005).

## Phase 6: Polish

- [X] T014 [P] Append `*-workspace/` to `.gitignore` and run quickstart §4 (FR-007).
- [X] T015 Run quickstart §5: no changes outside `specs/003-deepen-prompt-skill/`, `deepen-prompt/`, `deepen-prompt.skill`, `README.md` and `.gitignore` (FR-008, SC-006).
- [X] T016 Commit on `003-deepen-prompt-skill`, referencing issue #4.
- [X] T017 Record the acceptance criteria that couldn't be met in this session (below and in the implementation report).

---

## Outstanding (maintainer, not done in this session)

These issue #4 acceptance criteria are **not met yet**:

- **Eval viewer review (SC-002).** The iteration-1 output evals were run and graded
  informally (one run per config, self-graded, no `aggregate_benchmark`), but nobody has
  reviewed them in skill-creator's `eval-viewer/generate_review.py --benchmark`.
- **Trigger eval and `run_loop` description optimization (SC-003).** Not run:
  skill-creator's `run_eval.py` uses `select.select()` on a subprocess pipe, which fails on
  Windows (research R4). Run quickstart §7 on macOS/Linux/WSL, apply `best_description` if
  held-out accuracy ≥ 80%, and rebuild the archive.
- **Name decision** (issue §10): `deepen-prompt` is still a placeholder.
- **Manual smoke test** in a fresh Claude Code session (quickstart §7).

## Dependencies & Execution Order

Setup → Foundational → US1 (T004–T008) → US2 (archive packages the folder). US3 (README) and
T014 touch other files and can run alongside US1–US2. T015–T017 run last.
