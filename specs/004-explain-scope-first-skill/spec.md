# Feature Specification: Add Explain-Scope-First Skill

**Feature Branch**: `004-explain-scope-first-skill`
**Created**: 2026-11-10
**Status**: Implemented (behavioral evaluations outstanding)
**Input**: User description: "https://github.com/peterelmwood/agent-skills/issues/5"

Issue #5, "Feature: Add explain-scope-first skill for stating intent and boundaries before
changes", follows the repo's ten-section feature template. It supplies the complete source
for `explain-scope-first/SKILL.md`: before the first edit or other mutation, the assistant
sends a short scope statement (what it understands, what it will change, what it will not
touch), then proceeds within that scope without imposing an approval gate, stops before
crossing a stated exclusion, and reports results without claiming unchecked areas were
verified.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the skill in Claude Code and use it (Priority: P1)

A user copies `explain-scope-first/` into `~/.claude/skills/`. In a new session they ask for
a change and say "explain scope first". Claude sends a scope statement before its first edit,
then does the work inside that scope.

**Independent Test**: Copy only `explain-scope-first/` into `~/.claude/skills/`, start a new
session and ask "Change the Save button label to Submit; explain scope first; leave
validation alone."

**Acceptance Scenarios**:

1. **Given** the repo root, **When** the user looks for the skill, **Then**
   `explain-scope-first/` exists with only `SKILL.md`, identical to the issue source.
2. **Given** `explain-scope-first/SKILL.md`, **When** its frontmatter is parsed, **Then** it
   has `name: explain-scope-first` and a `description` scoped to explicit scope/readback
   requests that excludes questions and analysis requiring no changes.
3. **Given** an already authorized narrow edit, **When** the skill runs, **Then** the scope
   statement precedes the first mutation and work continues without an unrequested
   confirmation question.
4. **Given** "wait for my approval", **When** the skill runs, **Then** no mutation happens
   before approval.
5. **Given** an excluded area that proves necessary, **When** discovered, **Then** Claude
   stops before changing it, explains the dependency and resolves the boundary with the user.

---

### User Story 2 - Upload the skill to Claude.ai / Claude Desktop (Priority: P2)

A user downloads `explain-scope-first.skill` and uploads it in **Settings → Capabilities →
Skills**.

**Independent Test**: The archive's file entries equal the folder's files, use `/`
separators and have identical bytes.

**Acceptance Scenarios**:

1. **Given** `explain-scope-first.skill`, **When** listed, **Then** its only file entry is
   `explain-scope-first/SKILL.md`, with no `\` in any name and bytes identical to the
   committed blob.

---

### User Story 3 - Discover the skill in the README (Priority: P3)

A reader finds the skill in the table, installs it with the copy commands, and reads a
section that explains what it does.

**Independent Test**: README grep checks in [quickstart.md](./quickstart.md) §4.

**Acceptance Scenarios**:

1. **Given** the README, **When** read, **Then** `explain-scope-first` is in the skills table
   (after `asd-ste100`), in all three copy commands, the count says "All nine skills", and a
   `### explain-scope-first` section has **When it runs**, **What it produces** and
   **What's inside**.

### Edge Cases

- A pure question ("Explain how this function works."): the description excludes it, so no
  scope ritual.
- A standalone item with no meaningful neighboring area: the skill says so instead of
  inventing exclusions.
- The user corrects the target after the readback: the scope statement is updated before
  dependent work continues.
- A long multi-step task: the statement is repeated only when outcome or boundaries
  materially change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST contain `explain-scope-first/SKILL.md` identical to the issue's
  fenced source (fence stripped, LF, one trailing newline, UTF-8 without BOM), and no other
  file in that folder (issue §4: one instruction file).
- **FR-002**: The `SKILL.md` frontmatter MUST have `name: explain-scope-first` matching the
  folder.
- **FR-003**: The skill MUST require a user-visible scope statement before the first
  mutation, covering understood outcome, expected targets (tentative marked) and concrete
  exclusions (issue AC 1–4).
- **FR-004**: The skill MUST NOT impose an unconditional approval gate, and MUST honor
  explicit requests to wait and resolve material ambiguity first (AC 5–6).
- **FR-005**: The skill MUST treat exclusions as commitments, update scope on correction,
  and repeat it only on material change (AC 7–9).
- **FR-006**: The description MUST NOT activate the workflow for questions or analysis that
  require no changes (AC 10).
- **FR-007**: The completion report MUST NOT claim untouched areas were verified unless
  checked (AC 11).
- **FR-008**: The repo MUST contain `explain-scope-first.skill`, built with the README's
  documented command and matching the folder (AC 12).
- **FR-009**: The README MUST list, install, update and describe the skill (AC 12).
- **FR-010**: No other skill folder or archive may change.

### Key Entities

- **Skill folder** `explain-scope-first/`: `SKILL.md` only.
- **Archive** `explain-scope-first.skill`: zip of the folder, folder name as the top-level
  entry.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A byte comparison of `SKILL.md` against a fresh extraction from the issue shows
  no difference.
- **SC-002**: The archive check prints one expected entry, no `\`, and identical bytes to the
  committed blob.
- **SC-003**: The README grep checks in quickstart §4 return the expected hits.
- **SC-004**: `git diff --stat` against `skills-step-breakdown-deepen-prompt-asd-ste100`,
  excluding `specs/`, `explain-scope-first/`, `explain-scope-first.skill` and `README.md`,
  is empty.
- **SC-005** (outstanding): the seven behavioral scenarios in issue §8 pass in a fresh
  Claude Code session.

## Assumptions

- The issue's source is adopted as-is; problems are recorded as follow-ups in
  [research.md](./research.md), not patched.
- The skill count is set from the folders that exist on the base branch (nine), per issue §9.
- Behavioral evaluations need a fresh session with the skill installed and are left to the
  maintainer; no results are claimed here.
