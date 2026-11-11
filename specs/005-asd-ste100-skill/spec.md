# Feature Specification: Add ASD-STE100 Prompt-Constraint Skill

**Feature Branch**: `005-asd-ste100-skill`
**Created**: 2026-11-10
**Status**: Implemented
**Input**: User description: "https://github.com/peterelmwood/agent-skills/issues/6"

Issue #6, "Add ASD-STE100 Simplified Technical English prompt-constraint skill", is a short
request (not the repo's ten-section feature template). It supplies the complete source for an
`asd-ste100` skill: `asd-ste100/SKILL.md` and an optional `asd-ste100/agents/openai.yaml`
(Codex UI metadata kept "to preserve the original generated skill"). The skill uses
ASD-STE100 Simplified Technical English (STE) as a prompt constraint for creating reusable
prompts, drafting or rewriting technical text, and reviewing text. It must keep technical
meaning and keep STE-inspired output apart from verified conformance.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the skill in Claude Code and use it (Priority: P1)

A user who cloned `agent-skills` copies `asd-ste100/` into `~/.claude/skills/`. In a new
session they ask Claude to rewrite a procedure in Simplified Technical English, or to write
a reusable STE prompt. Claude picks the skill from its description and follows it.

**Independent Test**: Copy only `asd-ste100/` into `~/.claude/skills/`, start a new session
and ask "rewrite this maintenance procedure in Simplified Technical English".

**Acceptance Scenarios**:

1. **Given** the repo root, **When** the user looks for the skill, **Then** `asd-ste100/`
   exists with `SKILL.md` and `agents/openai.yaml`, both identical to the issue source.
2. **Given** `asd-ste100/SKILL.md`, **When** its frontmatter is parsed, **Then** it is valid
   YAML with `name: asd-ste100` and a `description` that limits use to requests for STE.
3. **Given** no official ASD-STE100 materials, **When** the user asks for an STE rewrite,
   **Then** the skill tells Claude to produce an STE-inspired draft, name the verification
   gaps and not claim compliance.

---

### User Story 2 - Upload the skill to Claude.ai / Claude Desktop (Priority: P2)

A user downloads `asd-ste100.skill` and uploads it in **Settings → Capabilities → Skills**.

**Independent Test**: The archive's file entries equal the folder's files, use `/`
separators and have identical bytes.

**Acceptance Scenarios**:

1. **Given** `asd-ste100.skill`, **When** listed, **Then** its file entries are exactly
   `asd-ste100/SKILL.md` and `asd-ste100/agents/openai.yaml`, with no `\` in any name.

---

### User Story 3 - Discover the skill in the README (Priority: P3)

A reader of the README finds the skill in the table, installs it with the copy commands, and
reads a section that explains what it does and the STE-inspired vs verified-conformance
distinction.

**Independent Test**: README grep checks in [quickstart.md](./quickstart.md) §4.

**Acceptance Scenarios**:

1. **Given** the README, **When** read, **Then** `asd-ste100` is in the skills table (after
   `step-breakdown`), in all three copy commands, the count says "All seven skills", and a
   `### asd-ste100` section has **When it runs**, **What it produces** and **What's inside**.

### Edge Cases

- A request for plain English or general editing that doesn't ask for STE: the description
  scopes the skill to STE requests, so it should not trigger.
- The user needs a specific (older, contractually required) issue of the standard: the skill
  says not to substitute a newer issue.
- Text mixes prose with code, UI labels or API names: those exact strings are preserved.
- A Claude-only install contains `agents/openai.yaml`: Claude ignores files the skill
  doesn't reference, so it is inert.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST contain `asd-ste100/SKILL.md` and `asd-ste100/agents/openai.yaml`
  whose content is identical to the issue's fenced source (fences stripped, LF, one trailing
  newline, UTF-8 without BOM).
- **FR-002**: The `SKILL.md` frontmatter MUST parse as YAML with `name: asd-ste100`.
- **FR-003**: The skill MUST NOT reproduce the ASD-STE100 standard or its dictionary.
- **FR-004**: The skill MUST keep STE-inspired output apart from verified conformance,
  including the checks for approved meanings, parts of speech, technical names and technical
  verbs (issue acceptance criterion 3).
- **FR-005**: The description MUST keep automatic discovery and MUST NOT impose STE on
  unrelated writing (issue acceptance criterion 4).
- **FR-006**: The repo MUST contain `asd-ste100.skill`, built with the README's documented
  command and matching the folder.
- **FR-007**: The README MUST list, install, update and describe the skill.
- **FR-008**: No other skill folder or archive may change.

### Key Entities

- **Skill folder** `asd-ste100/`: `SKILL.md` (entry point) and `agents/openai.yaml`
  (optional Codex metadata).
- **Archive** `asd-ste100.skill`: zip of the folder, folder name as the top-level entry.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A byte comparison of both files against a fresh extraction from the issue
  shows no difference.
- **SC-002**: The archive check prints the two expected entries, `True` (no `\`), `True`
  (identical bytes).
- **SC-003**: The README grep checks in quickstart §4 all return the expected hits.
- **SC-004**: `git diff --stat` against `002-step-breakdown-skill`, excluding `specs/`,
  `asd-ste100/`, `asd-ste100.skill` and `README.md`, is empty.

## Assumptions

- The issue's source is adopted as-is; problems are recorded as follow-ups in
  [research.md](./research.md), not patched.
- "Issue" inside the skill means an edition of the ASD-STE100 standard, not a GitHub issue.
- A manual smoke test in a fresh Claude Code session is left to the maintainer, because
  skills load at session start.
