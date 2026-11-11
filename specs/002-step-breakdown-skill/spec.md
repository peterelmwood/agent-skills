# Feature Specification: Add Step Breakdown Skill

**Feature Branch**: `002-step-breakdown-skill`

**Created**: 2026-11-10

**Status**: Draft

**Input**: User description: "https://github.com/peterelmwood/agent-skills/issues/3" (the oldest open issue)

The issue, titled "Feature: Add step-breakdown skill for turning multi-week efforts into
dependency-aware checklists", contains the complete, already-tested source of a new skill
(`step-breakdown/SKILL.md` and `step-breakdown/scripts/check_plan.py`) in collapsed sections,
plus acceptance criteria for packaging it and documenting it in the README. The skill turns a
large, fuzzy effort (a migration, a move, a launch, a talk submission) into one persistent
Markdown checklist (`<project-slug>-steps.md`) of small steps with stable IDs, done-checks,
explicit dependencies, waiting gates and parallel markers, and keeps that file up to date
when the user comes back with progress.

Every existing skill in the repo is about code. This is the first that isn't, and the first
with a `scripts/` folder.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the skill in Claude Code and get a usable step plan (Priority: P1)

A developer who has cloned `agent-skills` copies the `step-breakdown` folder into their
skills directory, like any other skill in the repo, and starts a new session. They ask
Claude to "break down moving apartments in 6 weeks". Claude saves one
`<project-slug>-steps.md` file with numbered steps, done-checks, `Needs:` lists, gates and
parallel markers, runs the bundled checker, and replies with the path, the step count, the
active effort and the steps available right now.

**Why this priority**: This is the feature. A Claude Code user can get the full value from
the folder alone, before the archive or README exist.

**Independent Test**: Copy only `step-breakdown/` into `~/.claude/skills/`, ask a fresh
session for a breakdown of a multi-week effort, then run the bundled checker on the file it
saved. The checker reports no errors and lists at least one available step.

**Acceptance Scenarios**:

1. **Given** the repo root, **When** a user looks for the skill, **Then** a top-level
   `step-breakdown/` folder exists containing `SKILL.md` and `scripts/check_plan.py`, and
   both match the source in issue #3.
2. **Given** `step-breakdown/SKILL.md`, **When** its frontmatter is read, **Then** it has
   `name: step-breakdown` and a `description` that says when to use the skill and excludes
   single quick tasks and code-level implementation plans for an immediate coding session.
3. **Given** a well-formed plan file, **When** the checker is run on it, **Then** it prints
   the step and gate counts, the total active effort and the "available now" list, reports
   no errors, and exits successfully.
4. **Given** a plan file with a duplicate ID, an unknown `Needs` reference, a dependency
   cycle, a parallel line that contradicts `Needs`, a step with no done-check, or no
   available step, **When** the checker is run, **Then** it reports each problem and exits
   with a failure status.
5. **Given** a plan file containing emoji (✅ ⏳ ⇉ 🔭 ⚠), **When** the checker runs in a
   Windows console whose default encoding isn't UTF-8, **Then** it reads the file and prints
   its report without an encoding error.

---

### User Story 2 - Return to an existing plan with progress (Priority: P2)

A user who created a plan last week comes back and says "I finished 1–12 and the permit came
through". The skill updates the same file in place: it ticks the reported steps and gate,
keeps every existing tick, note, decision and log row, adds a dated Progress log row, and
re-runs the checker. If the user reports something that the file says is still blocked, the
skill ticks what is clearly true and records the conflict under **Open questions** instead
of silently overwriting either version.

**Why this priority**: The issue's core complaint is that plans stop being useful after the
first sitting. Updating in place is what makes the file last for weeks, but it builds on a
plan created in Story 1.

**Independent Test**: Read `SKILL.md` and confirm it instructs the agent to check for an
existing `*-steps.md`, update it in place, preserve existing content, flag conflicts under
Open questions, log the update and re-run the check; and that it never overwrites a file that
has ticked boxes or log entries.

**Acceptance Scenarios**:

1. **Given** an existing plan with ticked boxes and log rows, **When** the user reports
   progress, **Then** the skill edits that file in place and no ticked box, note, decision,
   `📎` line or log row is lost.
2. **Given** a step that turns out too big, **When** it is split, **Then** it keeps its ID as
   a parent (`14` → `14a`, `14b`), anything that needed `14` stays correct, new unrelated
   steps take the next unused number, and nothing is renumbered.
3. **Given** a user report that contradicts the file, **When** the skill applies it, **Then**
   the conflict appears under **Open questions** with the IDs involved and is mentioned in
   the reply.

---

### User Story 3 - Upload the skill to Claude.ai / Claude Desktop (Priority: P3)

A user who doesn't use Claude Code downloads `step-breakdown.skill` from the repo and
uploads it under **Settings → Capabilities → Skills**, the same way as the other `.skill`
files.

**Why this priority**: The repo ships a `.skill` archive for every skill folder. The folder
alone already serves Claude Code users.

**Independent Test**: List the archive's entries and compare them with the folder.

**Acceptance Scenarios**:

1. **Given** the repo root, **When** a user looks for the archive, **Then**
   `step-breakdown.skill` sits next to `step-breakdown/`, following the `<name>.skill` naming
   of the other skills.
2. **Given** the archive, **When** its entries are listed, **Then** its file entries are
   exactly `step-breakdown/SKILL.md` and `step-breakdown/scripts/check_plan.py`, under a
   single `step-breakdown/` root with `/` path separators (directory entries allowed).
3. **Given** the archive and the folder, **When** each entry is compared with its file,
   **Then** the contents are identical.
4. **Given** an environment where scripts can't run, **When** the skill is used, **Then**
   `SKILL.md` tells the agent to do the consistency checks by reading the file instead.

---

### User Story 4 - Discover and install the skill from the README (Priority: P4)

A visitor reading the README wants to know the step-breakdown skill exists, what it does,
when it runs, what it produces and how to install it with the others.

**Why this priority**: Discoverability. The skill works without it, but nobody finds it.

**Independent Test**: Read the README and follow its install and update commands on a clean
machine; confirm the new skill is copied along with the others.

**Acceptance Scenarios**:

1. **Given** the README's skills table, **When** a visitor reads it, **Then** there is a row
   for `step-breakdown` linking to `step-breakdown/SKILL.md`.
2. **Given** the README's Quick start (macOS/Linux and Windows) and Updating copy commands,
   **When** a user runs any of them, **Then** `step-breakdown` is copied along with every
   other skill folder.
3. **Given** the Quick start's installed-skills sentence, **When** it is read, **Then** it
   says six skills, not five.
4. **Given** the per-skill sections, **When** a visitor reads them, **Then** a
   `### step-breakdown` section exists in the same shape as the others: what it does, when
   it runs, what it produces and a **What's inside** tree.

---

### Edge Cases

- A user says "start over" on an existing plan: the shipped `SKILL.md` never overwrites a
  file that has ticked boxes or log entries, so the old file and its progress survive. An
  explicit "start over → new file name" instruction (issue §6) is not in the adopted source
  and is a follow-up outside this feature.
- The checker is run with no argument or with too many: it prints its usage and exits with
  a distinct status, without a traceback.
- The plan file contains no recognisable steps: the checker says so and exits with a failure
  status.
- A step is ticked while one of its `Needs` is not: the checker warns about a possible
  conflict rather than failing.
- A parent is ticked while some children aren't: the checker reports an error.
- Python isn't available (for example on Claude.ai): the skill falls back to a manual
  checklist.
- A request to plan a code change for the current session ("plan out the implementation and
  then do it") should not trigger this skill; the description excludes it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST contain a top-level `step-breakdown/` folder holding `SKILL.md`
  and `scripts/check_plan.py`, with content taken from issue #3's collapsed source sections.
- **FR-002**: The published skill folder MUST NOT include development-only material such as
  an `evals/` folder, consistent with the existing skills.
- **FR-003**: `SKILL.md` MUST have `name: step-breakdown` frontmatter and a description that
  names when to use the skill and excludes single quick tasks and code-level implementation
  plans for an immediate coding session.
- **FR-004**: The skill MUST produce one `<project-slug>-steps.md` file in which every step
  and gate has a stable ID, a `Needs:` list and a `✅ Done when:` check.
- **FR-005**: The skill MUST treat `Needs:` as the only source of availability (file order is
  a suggestion only), represent outside waits as `⏳ GATE` checkboxes with 0 active minutes
  and a separate elapsed estimate, mark steps over 30 minutes with `⚠ exception: <why>`, use
  `[TBD: …]` for unknown specifics, and use `🔭 Expand after <ID>` for still-uncertain later
  phases.
- **FR-006**: The skill MUST split steps by keeping the parent ID (`14` → `14a`, `14b`), give
  new steps the next unused number, and never renumber.
- **FR-007**: The checker MUST report duplicate IDs, unknown `Needs` references, dependency
  cycles, parallel lines that contradict `Needs`, missing done-checks and plans where no step
  can be started; print total active effort and the "available now" list; and exit with a
  failure status when any error is found.
- **FR-008**: The checker MUST run on the Python standard library alone and read and print
  UTF-8 correctly on Windows consoles.
- **FR-009**: The skill MUST update an existing plan in place, preserving ticked boxes,
  notes, decisions and log rows, and list conflicting reports under **Open questions**.
- **FR-010**: The repo root MUST contain `step-breakdown.skill`, a zip archive of the folder
  built with the commands in the README's "Repository layout" section, whose entries match
  the folder's files byte for byte under a single `step-breakdown/` root.
- **FR-011**: The README MUST add `step-breakdown` to the skills table, to both Quick start
  copy commands and to the Updating copy command; change "All five skills" to six; widen the
  tagline by one clause to mention planning; and add a `### step-breakdown` section in the
  same shape as the existing per-skill sections.
- **FR-012**: The change MUST NOT modify any existing skill folder or `.skill` archive.

### Key Entities

- **Skill package**: The `step-breakdown/` folder (instructions plus checker script) and its
  `.skill` archive.
- **Step plan file**: The `<project-slug>-steps.md` checklist the skill produces for the
  user; contains steps, gates, parallel lines, Decisions, Open questions and a Progress log.
- **Step / gate**: A checklist item with a stable ID, `Needs:` list, estimate and done-check.
  A gate is an outside event with 0 active minutes and an elapsed estimate.
- **Parallel line**: A `⇉` line listing mutually independent step IDs, optionally flagging a
  shared-resource conflict.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can install the skill in Claude Code with one copy command and get a
  saved step plan from a fresh session with no further setup.
- **SC-002**: On a smoke-test plan produced by the skill (for example "move apartments in 6
  weeks"), the checker reports 0 errors and at least 1 available step.
- **SC-003**: On a deliberately broken plan, the checker catches 100% of planted errors
  (unknown ID, dependency cycle, parallel line contradicting `Needs`, missing done-check)
  and flags an over-30-minute step with no reason.
- **SC-004**: The checker completes on Windows and macOS/Linux with no encoding errors on
  plans containing emoji.
- **SC-005**: The `.skill` archive's file entries match the folder's 2 files exactly, with
  identical contents.
- **SC-006**: Every README install/update command that copies skill folders includes
  `step-breakdown`, and the README describes all six skills.
- **SC-007**: No existing skill folder or archive changes.

## Assumptions

- The skill source in issue #3 is final and tested; it is added as-is, not rewritten. Only
  layout-level adjustments (line endings, trailing newline) are acceptable.
- "Five" in the issue refers to the five skills on `main` after PR #2 (`design-patterns`,
  `react-anti-patterns`, `bug-report-issue-author`, `feature-request-issue-author`,
  `peter-pr-review`), so the new count is six.
- The README's **Updating** section copy command is in scope even though the issue lists only
  the two Quick start commands, because otherwise updating would silently skip the new
  skill.
- Widening the README tagline (L3) to mention planning is optional in the issue. Since the
  repo now holds a non-code skill, a minimal tagline adjustment is made.
- Out of scope (from the issue): Jira/Asana/GitHub Projects sync, calendar scheduling,
  code-level implementation plans, a gist version of this skill, committing the development
  `evals/` set, and further work on trigger recall.
- The repo's constitution is an unfilled template, so no project principles constrain this
  feature beyond the conventions set by existing skills and feature 001.
