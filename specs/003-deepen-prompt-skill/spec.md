# Feature Specification: Add Deepen Prompt Skill

**Feature Branch**: `003-deepen-prompt-skill`

**Created**: 2026-11-10

**Status**: Draft

**Input**: User description: "https://github.com/peterelmwood/agent-skills/issues/4"

The issue, titled "Feature: Add deepen-prompt skill for expert framing and verifiable task
prompts", contains a proposed draft (iteration 0) of a new skill, `deepen-prompt/SKILL.md`,
plus acceptance criteria for its behaviour, a skill-creator benchmark, and packaging. Given a
task or prompt, the skill names the assumed expert role, answers four questions (what a top
professional would do that wasn't asked for, the rawest material to start from, the specific
methods and tools, and an independent check of correctness), and rewrites the prompt so it is
deeper, not bigger: same deliverables, better inputs, method and definition of "done". It then
stops and offers to run the rewrite.

Like `step-breakdown`, it isn't about code. Unlike it, it is pure instruction: no `scripts/`
and, for v1, no `references/`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the skill in Claude Code and get a deeper prompt (Priority: P1)

A Claude Code user copies `deepen-prompt/` into their skills directory and starts a new
session. They paste a shallow prompt and say "go deeper on this, not wider". Claude replies
with one "Assuming: <role>" line, four labeled answers, the rewritten prompt in a fenced
block, and an offer to run it. It doesn't run the task.

**Why this priority**: This is the feature. The folder alone delivers it.

**Independent Test**: Give a session the skill and one of the issue's §8 prompts; check the
reply against the §8 assertions.

**Acceptance Scenarios**:

1. **Given** a prompt built on a digested input (a screenshot, a news article), **When** the
   user asks for a deeper version, **Then** the reply names the raw source, at least two
   specific methods or tools, and an independent check with how to get it.
2. **Given** any rewrite, **When** its deliverables are listed next to the original's,
   **Then** it asks for no new deliverables.
3. **Given** a niche field, **When** Claude doesn't know the specialist toolset, **Then** it
   says so and suggests how to find out, rather than inventing names.
4. **Given** a task too vague to pick an expert ("help me decide"), **When** the user asks
   to deepen it, **Then** Claude asks exactly one clarifying question and writes no rewrite.

---

### User Story 2 - Upload the skill to Claude.ai / Claude Desktop (Priority: P2)

A user downloads `deepen-prompt.skill` and uploads it in **Settings → Capabilities →
Skills**.

**Why this priority**: Same reach as every other skill in the repo, but secondary to the
folder.

**Independent Test**: The archive's file entries equal the folder's files, byte for byte,
with `/` separators.

---

### User Story 3 - Discover and install the skill from the README (Priority: P3)

A visitor reads the README, finds `deepen-prompt` in the skills table and its own section,
and installs it with the Quick start command.

**Why this priority**: Discovery; the skill works without it.

**Independent Test**: Every README command that copies skill folders includes
`deepen-prompt`, the count says seven, and the section has the same headings as the others.

---

### Edge Cases

- The raw source is out of the user's reach (paywalled data, production logs): the skill
  names it anyway and offers the best reachable substitute.
- The user wants research carried out, a prompt copy-edited, or something expanded into a
  longer deliverable: the skill shouldn't fire (description exclusions; trigger eval).
- The assumed expert role is wrong: the first line states it so the user can correct it.
- Verification by another LLM or by the user: not accepted as independent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST contain a top-level `deepen-prompt/` folder whose `SKILL.md` is
  the issue's "Skill source (proposed draft, iteration 0)" verbatim.
- **FR-002**: `SKILL.md` MUST have valid frontmatter with `name: deepen-prompt` and a
  description under 1024 characters.
- **FR-003**: `references/examples.md` MUST be added only if evals show the inline example
  isn't enough (issue §3, §5).
- **FR-004**: The published folder MUST NOT include development-only material (`evals/`,
  workspaces).
- **FR-005**: The repo root MUST contain `deepen-prompt.skill`, a zip of the folder whose
  file entries match the folder exactly, with `/` separators.
- **FR-006**: The README MUST add `deepen-prompt` to the skills table, both Quick start
  commands and the Updating command, update the skill count to seven, and add a per-skill
  section.
- **FR-007**: `.gitignore` MUST ignore `*-workspace/` so skill-creator eval output is never
  committed.
- **FR-008**: The change MUST NOT modify any existing skill folder or `.skill` archive.

### Key Entities

- **Skill folder** `deepen-prompt/`: `SKILL.md` only.
- **Archive** `deepen-prompt.skill`: zip of the folder, top-level directory included.
- **Eval set** (issue §8): 4 output evals with 9 assertions; 20 trigger queries (10 should,
  10 should not). Lives in an ignored or external workspace, not in the folder.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across the 4 output evals, with-skill runs pass more assertions than a
  no-skill baseline (issue §2 benchmark).
- **SC-002**: The results are reviewed in the skill-creator eval viewer before merging.
- **SC-003**: The trigger eval reaches ≥ 80% accuracy on held-out queries after `run_loop`
  description optimization.
- **SC-004**: The archive's file entries match the folder's files exactly.
- **SC-005**: Every README command that copies skill folders includes `deepen-prompt`.
- **SC-006**: No existing skill folder or archive changes.

## Assumptions

- The draft in the issue is adopted as-is; problems are recorded as follow-ups
  (research.md), not patched.
- `deepen-prompt` stays the name (issue §10 lists it as a placeholder; renaming is a
  maintainer decision before merge).
- This branch builds on `002-step-breakdown-skill`, so the count goes six → seven (issue §9
  merge note).
- SC-002 and SC-003 need the maintainer and, for SC-003, a platform where skill-creator's
  `run_eval.py` runs (see research R4).
