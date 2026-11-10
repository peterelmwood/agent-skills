# Tasks: Add Step Breakdown Skill

**Input**: Design documents from `/specs/002-step-breakdown-skill/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/skill-package.md,
contracts/check-plan-cli.md, quickstart.md

**Tests**: The spec doesn't ask for automated tests, and the repo has no test harness.
Verification uses the scripted checks in [quickstart.md](./quickstart.md) (§1–§8), run as
tasks below. Fixture plan files live in the scratch folder, not in the repo.

**Organization**: Tasks are grouped by user story so each story can be delivered and checked
on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story the task belongs to (US1–US4)

## Path Conventions

All paths are relative to the repo root. `$S` is a new, empty scratch folder outside the
repo, used for the fetched issue body, extracted files and fixture plans.

---

## Phase 1: Setup

**Purpose**: Get the source from issue #3 into the scratch folder.

- [ ] T001 Fetch the issue body as JSON with `gh issue view 3 --repo peterelmwood/agent-skills --json body > $S/issue3.json` (research R1; don't use console-formatted output, which wraps long lines).
- [ ] T002 Extract the ````` ````markdown ````` fence to `$S/extract/SKILL.md` and the ```` ```python ```` fence to `$S/extract/check_plan.py` with a short Python script run with `python -I`: normalise to LF, append one trailing newline, write UTF-8 without BOM. Confirm 211 and 210 lines, `name: step-breakdown` on line 2, and `python -I -m py_compile $S/extract/check_plan.py` succeeds.

---

## Phase 2: Foundational

**Purpose**: Blocking checks before anything is added.

- [ ] T003 Confirm nothing named `step-breakdown` exists yet at the repo root (`step-breakdown/`, `step-breakdown.skill`) and that `README.md` doesn't mention `step-breakdown`; confirm the current branch is `002-step-breakdown-skill`.

**Checkpoint**: Source extracted and verified; target paths are free.

---

## Phase 3: User Story 1 - Install the skill in Claude Code and get a usable step plan (Priority: P1) 🎯 MVP

**Goal**: A top-level `step-breakdown/` folder that works when copied into `~/.claude/skills/`.

**Independent Test**: quickstart §1, §2, §3 and §4 pass against `step-breakdown/`.

- [ ] T004 [US1] Copy `$S/extract/SKILL.md` to `step-breakdown/SKILL.md` byte-for-byte (FR-001, FR-003).
- [ ] T005 [P] [US1] Copy `$S/extract/check_plan.py` to `step-breakdown/scripts/check_plan.py` byte-for-byte (FR-001, FR-008).
- [ ] T006 [US1] Run quickstart §1: `cmp` both files against `$S/extract/`, confirm `find step-breakdown -type f` lists exactly the two files (no `evals/`, no `__pycache__`; FR-002), and `git ls-files --eol` after staging shows `i/lf` for both.
- [ ] T007 [P] [US1] Run quickstart §2: save the worked example from `step-breakdown/SKILL.md` as `$S/example-steps.md` and run the checker. Expect 13 steps, 1 gate, 3 done, available `3, 6, 7, 8`, gate `5` waiting, `OK`, exit 0 (SC-002).
- [ ] T008 [P] [US1] Run quickstart §3: write `$S/broken-steps.md` (unknown `Needs` ID, 2-step cycle, `⇉` line contradicting `Needs`, step with no `Done when`, duplicate ID, `~45 min` step with no exception) and `$S/stuck-steps.md` (every step needs an unticked gate). Expect exit 1 with each planted error reported, the 45-minute step as a warning, and `no step is available right now` for the second file (FR-007, SC-003).
- [ ] T009 [US1] Run quickstart §4: no-argument run prints usage and exits 2; `PYTHONIOENCODING=cp1252` run on `$S/example-steps.md` prints the `⏳` gate line with no `UnicodeEncodeError` and exits 0 (FR-008, SC-004). Run with `python -B` to avoid creating `step-breakdown/scripts/__pycache__`; remove it if it appears.

**Checkpoint**: The folder alone is installable via `cp -r step-breakdown ~/.claude/skills/`.

---

## Phase 4: User Story 2 - Return to an existing plan with progress (Priority: P2)

**Goal**: Confirm the shipped instructions cover in-place updates, splitting and conflicts.

**Independent Test**: Every item below is found in `step-breakdown/SKILL.md`.

- [ ] T010 [US2] Check `step-breakdown/SKILL.md` covers: checking for an existing `*-steps.md` before creating; never overwriting a file with ticks or log rows; preserving ticks, notes, decisions, `📎` lines and log rows; flagging conflicts under **Open questions**; appending a dated Progress log row; re-running the check; and split rules (`14` → `14a`, next unused number, never renumber) (FR-006, FR-009). Record any gap as an issue comment rather than editing the file (content is adopted as-is).
- [ ] T011 [P] [US2] Using a copy of `$S/example-steps.md`, tick 10a–10c without ticking parent 10 and run the checker: expect the "all children ticked — tick the parent" warning and step 11 not yet available; then tick 10 and confirm step 11 becomes available once gate 5 is ticked (parent/child availability, data-model Parent rules).

**Checkpoint**: Update and split behaviour is documented in the skill and its parent/child rules are enforced by the checker.

---

## Phase 5: User Story 3 - Upload the skill to Claude.ai / Claude Desktop (Priority: P3)

**Goal**: An upload-ready `step-breakdown.skill` archive that matches the folder.

**Independent Test**: quickstart §5 passes.

- [ ] T012 [US3] Ensure `step-breakdown/` contains only the two files (no `__pycache__`), then build `step-breakdown.skill` at the repo root with the README's PowerShell 7 command (`[IO.Compression.ZipFile]::CreateFromDirectory("$PWD\step-breakdown", "$PWD\step-breakdown.skill", 'Optimal', $true)`), deleting any existing archive first (research R3, FR-010).
- [ ] T013 [US3] Run quickstart §5: file entries are exactly `step-breakdown/SKILL.md` and `step-breakdown/scripts/check_plan.py`, no entry contains `\`, and each entry's bytes equal the folder file (SC-005).
- [ ] T014 [P] [US3] Confirm `step-breakdown/SKILL.md` has the "If Python isn't available, do the checks by reading the file carefully" fallback (US3 scenario 4).

**Checkpoint**: The archive can be uploaded alongside the other `.skill` files.

---

## Phase 6: User Story 4 - Discover and install the skill from the README (Priority: P4)

**Goal**: The README lists, installs, updates and describes the new skill.

**Independent Test**: quickstart §6 passes.

- [ ] T015 [US4] In `README.md`, add `step-breakdown` to the Quick start macOS/Linux `cp -r` command (L13), the Windows `Copy-Item` command (L22) and the Updating `cp -r` command (L227), after `peter-pr-review` in each (FR-011, research R5).
- [ ] T016 [US4] In `README.md`, change "All five skills" (L25) to "All six skills", add a `step-breakdown` row to the skills table after `peter-pr-review` linking `step-breakdown/SKILL.md`, and widen the tagline (L3) by one clause to mention planning (research R5).
- [ ] T017 [US4] In `README.md`, add a `### step-breakdown` section after the `### peter-pr-review` section, in the same shape as the others: what it does, **When it runs** (including the code-planning exclusion and a "try it" prompt such as "break down moving apartments in 6 weeks"), **What it produces** (one `<project-slug>-steps.md` with IDs, `Needs`, done-checks, gates, parallel markers, Decisions, Open questions, Progress log; the checker's report), and a **What's inside** tree (`SKILL.md`, `scripts/check_plan.py`, noting Python 3.8+ stdlib and the manual fallback).
- [ ] T018 [US4] Run quickstart §6 grep checks against `README.md` and confirm the new section's headings match the existing per-skill sections.

**Checkpoint**: All four stories done.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T019 Run quickstart §7: no changes outside `specs/002-step-breakdown-skill/`, `step-breakdown/`, `step-breakdown.skill` and `README.md` (FR-012, SC-007).
- [ ] T020 Commit the skill folder, archive and README on `002-step-breakdown-skill`, referencing issue #3.
- [ ] T021 Record that quickstart §8 (manual smoke test in a fresh Claude Code session, macOS/Linux and Windows per issue §8) is left for the maintainer; it can't be run from this session because skills load at session start.

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → **Foundational (T003)** → user stories.
- **US1 (T004–T009)** is the MVP and blocks US3 (the archive packages the folder) and US2's
  checker run (T011 needs the shipped checker and T007's example file).
- **US2 (T010–T011)** depends on US1 only.
- **US3 (T012–T014)** depends on US1. T012 must run after T009 so no `__pycache__` is
  packaged.
- **US4 (T015–T018)** depends only on Foundational; it can run in parallel with US1–US3
  because it touches only `README.md`.
- **Polish (T019–T021)** runs last.

## Parallel Opportunities

- T004 and T005 (different files).
- T007 and T008 (separate fixture files, read-only checker).
- T011 alongside T012–T014.
- The whole of US4 (README) alongside US1–US3.

## Implementation Strategy

1. **MVP**: Phases 1–3. Stop and validate: the folder installs and the checker behaves as
   contracted.
2. Add US2 verification, then the archive (US3), then the README (US4).
3. Polish: scope check and commit. The manual smoke test is handed to the maintainer.
