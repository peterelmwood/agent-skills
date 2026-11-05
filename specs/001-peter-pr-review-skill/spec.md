# Feature Specification: Add Peter PR Review Skill

**Feature Branch**: `001-peter-pr-review-skill`

**Created**: 2026-11-05

**Status**: Draft

**Input**: User description: "https://github.com/peterelmwood/agent-skills/issues/1"

The issue, titled "Add Peter Review Skill", carries the skill as attachments: a `SKILL.md`,
five reference files (`examples-backend.md`, `examples-frontend.md`, `examples-tests.md`,
`examples-typing.md`, `examples-summaries-and-pushback.md`), and `peter-pr-review.skill.zip`.
The zip holds a packaged `peter-pr-review.skill` whose contents are byte-identical to the six loose
attachments, laid out as `peter-pr-review/SKILL.md` and `peter-pr-review/references/*.md`.

The skill (`name: peter-pr-review`) teaches Claude to review a pull request in Peter's style. Peter
is a senior reviewer on Django/DRF backends and React/TypeScript frontends. The skill can produce
inline comments and a review summary in his voice, weighted toward his 2025 reviews.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the skill in Claude Code from the repo (Priority: P1)

A developer who has cloned `agent-skills` wants the Peter-style review skill available in Claude
Code. They copy the `peter-pr-review` folder into their skills directory, as they would any other
skill in the repo, and start a new session. When they ask Claude to "review this PR like Peter",
the skill loads and can open its reference files.

**Why this priority**: This is the core deliverable of the issue. Without the skill folder in the
repo, nothing else has any value.

**Independent Test**: Copy only `peter-pr-review/` into a clean skills directory. Confirm that
Claude Code lists `peter-pr-review` among the available skills, and that every `references/` path
named in `SKILL.md` exists in the copied folder.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repo, **When** the user lists the top-level folders, **Then** a
   `peter-pr-review/` folder sits beside the existing skill folders, holding `SKILL.md` and a
   `references/` folder with the five example files.
2. **Given** the folder has been copied to `~/.claude/skills/`, **When** the user starts Claude
   Code and asks which skills are available, **Then** `peter-pr-review` is listed with its
   description.
3. **Given** `SKILL.md` names `references/examples-*.md` files, **When** each named path is
   resolved relative to the skill folder, **Then** every file exists.

---

### User Story 2 - Upload the skill to Claude.ai / Claude Desktop (Priority: P2)

A user who doesn't use Claude Code downloads `peter-pr-review.skill` from the repo and uploads it in
**Settings → Capabilities → Skills**, the same way as the other `.skill` files.

**Why this priority**: The repo promises a `.skill` archive for every skill folder. Shipping the
folder without its archive breaks that convention, but the folder alone already serves Claude Code
users.

**Independent Test**: List the archive's entries. Confirm that its file entries are exactly the
folder's six files under a single `peter-pr-review/` root (directory entries are allowed), with `/`
path separators, and that each entry's bytes match the matching file in the folder.

**Acceptance Scenarios**:

1. **Given** the repo root, **When** the user looks for the archive, **Then**
   `peter-pr-review.skill` sits next to `peter-pr-review/`, following the `<name>.skill` naming of
   the other skills.
2. **Given** the archive, **When** its entries are listed, **Then** it contains
   `peter-pr-review/SKILL.md` and the five `peter-pr-review/references/examples-*.md` entries, and
   no other file entries. Directory entries are allowed.
3. **Given** the archive and the folder, **When** each entry is compared to its file, **Then** the
   contents are identical.

---

### User Story 3 - Discover and understand the skill from the README (Priority: P3)

A visitor reading the repo README wants to know that the Peter review skill exists, what it does,
when it triggers, and how to install it alongside the others.

**Why this priority**: The README is how people find skills, but the skill works without it.

**Independent Test**: Read the README and check that the skills table, the quick-start commands,
the update command, and a per-skill section all include `peter-pr-review`, and that counts and
wording such as "All four skills" are corrected.

**Acceptance Scenarios**:

1. **Given** the README skills table, **When** the user reads it, **Then** it has a
   `peter-pr-review` row that links to `peter-pr-review/SKILL.md`, with a one-line "Use it for"
   description.
2. **Given** the Claude Code quick start (macOS/Linux and Windows) and the "Updating" section,
   **When** the user copies all skills with the commands shown, **Then** `peter-pr-review` is
   included in each command.
3. **Given** the README text, **When** the user reads statements about how many skills the repo
   has, **Then** the count matches the number of skill folders.
4. **Given** the per-skill sections, **When** the user reaches the `peter-pr-review` section,
   **Then** it explains what the skill does, when it runs, what it produces (a draft review that is
   not posted unless asked), and shows a "What's inside" tree that matches the folder.

---

### Edge Cases

- **Attachment drift**: The loose attachments and the zipped package could differ. They have been
  verified as byte-identical; if they ever differ, the zipped `.skill` package is the authoritative
  source because it carries the intended folder layout.
- **Nested zip**: The issue's `.zip` wraps a `.skill`, which is itself a zip. Only the inner
  `peter-pr-review.skill` is committed. The outer `.zip` wrapper is not added to the repo.
- **Archive path separators**: If the archive is rebuilt on Windows, it must use `/` separators,
  following the README's existing guidance; backslashes would break the upload.
- **Sensitive content**: The skill quotes real review comments. Its header says project-specific
  identifiers have been replaced with neutral ones. The content is published as supplied; the only
  check is a scan for leftover private hostnames, internal repo URLs, or credentials. Anything found
  is reported to the maintainer rather than silently edited.
- **Name collision**: No existing folder, archive or README entry is named `peter-pr-review`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST contain a top-level `peter-pr-review/` folder whose `SKILL.md` is
  byte-identical to the `SKILL.md` attached to issue #1.
- **FR-002**: The folder MUST contain `references/examples-backend.md`,
  `references/examples-frontend.md`, `references/examples-tests.md`,
  `references/examples-typing.md`, and `references/examples-summaries-and-pushback.md`, each
  byte-identical to the matching attachment.
- **FR-003**: The folder MUST contain no files other than those six.
- **FR-004**: The repo MUST contain `peter-pr-review.skill` at the root: a zip archive whose entries
  are exactly the six files under a `peter-pr-review/` root, with `/` separators, and with contents
  identical to the folder. "Entries" means file entries; directory entries such as
  `peter-pr-review/references/` are allowed.
- **FR-005**: The `SKILL.md` front matter MUST declare `name: peter-pr-review`, matching the folder
  and archive names.
- **FR-006**: Every `references/...` path mentioned in `SKILL.md` MUST resolve to a file in the
  folder.
- **FR-007**: The README skills table MUST include a `peter-pr-review` row linking to
  `peter-pr-review/SKILL.md`.
- **FR-008**: The README Claude Code quick start (both platforms) and the "Updating" command MUST
  include `peter-pr-review` in the list of folders copied.
- **FR-009**: The README MUST include a `peter-pr-review` section, in the same style as the others,
  that covers what the skill does, when it runs, its output behavior (it drafts the review and does
  not post it unless asked), and a "What's inside" tree.
- **FR-010**: Any README statement giving the number of skills MUST match the number of skill
  folders after the change.
- **FR-011**: The change MUST NOT modify the existing skills' folders or `.skill` archives.
- **FR-012**: The skill content MUST be scanned for leftover private hostnames, internal
  repository URLs, and credentials before commit, and any hits MUST be reported to the maintainer.

### Key Entities

- **Skill folder**: `peter-pr-review/`, the readable source holding `SKILL.md` and `references/`.
- **Skill archive**: `peter-pr-review.skill`, the folder zipped for upload. It must stay in sync
  with the folder.
- **Reference file**: one of five `examples-*.md` files that `SKILL.md` points Claude to, each
  covering one review area.
- **README entry**: the table row, install commands, and per-skill section that make the skill
  discoverable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 6 of 6 skill files in the repo are byte-identical to the issue's attachments.
- **SC-002**: The archive's entry list matches the folder's file list exactly (6 entries, 0 extras,
  0 missing), and 6 of 6 entries match their files' contents.
- **SC-003**: 100% of the `references/` paths named in `SKILL.md` resolve to existing files.
- **SC-004**: A user following the README quick start, with no other instructions, ends up with all
  five skills installed, `peter-pr-review` included.
- **SC-005**: 0 files under the existing four skills' folders or archives change.

## Assumptions

- The skill content is final as attached. Its wording, examples and rankings are adopted unchanged,
  and editing the skill's text is out of scope.
- The folder name is `peter-pr-review`, taken from the skill's front matter and the archive name,
  even though the issue title says "Peter Review Skill".
- The skill is not published as a gist. The README's gist links only cover the two issue-author
  skills.
- Spec-kit scaffolding (`.specify/`, `.claude/skills/speckit-*`) is tooling for this workflow and is
  not part of the skill feature itself.
- No test harness exists in the repo. Verification is done by file comparisons and archive listing
  rather than automated tests.
