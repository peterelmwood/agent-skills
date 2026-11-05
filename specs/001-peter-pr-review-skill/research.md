# Research: Add Peter PR Review Skill

No Technical Context item was marked NEEDS CLARIFICATION. The decisions below settle the open
choices found while inspecting the issue's attachments and the repo.

## R1. Source of truth for skill content

- **Decision**: Use the files from inside the issue's nested package
  (`peter-pr-review.skill.zip` → `peter-pr-review.skill` → `peter-pr-review/...`).
- **Rationale**: The package carries the intended `references/` layout, which the loose
  attachments lack. The six packaged files were compared with the six loose attachments, and all
  six are byte-identical (`cmp`), so nothing is lost either way.
- **Alternatives considered**: Build the folder from the loose attachments. This gives the same
  bytes, but the layout would have to be inferred, so it was rejected as needless.

## R2. Archive: reuse the attached package or rebuild it

- **Decision**: Commit the attached inner `peter-pr-review.skill` unchanged.
- **Rationale**: It is the author's own upload-ready package. Its entries are exactly the six
  files with `/` separators, and its content matches the folder. Rebuilding it on Windows with the
  README's .NET command would add directory entries, giving a different but equally valid
  archive. That would churn bytes for no benefit.
- **Alternatives considered**: Rebuild it with the README's PowerShell/.NET snippet, to match how
  the other archives were made (they contain directory entries). This was rejected for now. The
  quickstart still checks that a rebuilt archive would be content-equivalent, so the README's
  "rebuild after editing" workflow stays valid for future edits.
- **Note**: Because the attached archive has no directory entries, "exactly the six files" in
  FR-004 means six *file* entries. Directory entries (`peter-pr-review/`,
  `peter-pr-review/references/`) are allowed if the archive is ever rebuilt.

## R3. The outer `.zip` wrapper

- **Decision**: Do not commit `peter-pr-review.skill.zip`.
- **Rationale**: GitHub issue attachments don't accept `.skill`, so the author zipped it for
  upload. The repo convention is `<name>.skill` only.

## R4. Sensitive-content scan (FR-012)

- **Decision**: Grep for credential keywords (password, secret, token, api key), internal host
  suffixes (`.internal`, `.local`, `.corp`) and `github.com/<owner>/` links.
- **Result**: No credentials and no internal hosts. External links are public docs only
  (refactoring.guru, react.dev, developer.mozilla.org, a public
  `final-form/react-final-form-arrays` README). The skill's header states that project
  identifiers were neutralized, and sampled examples use neutral domain names (orders, invoices,
  customers). **Nothing to report.**

## R5. README wording and placement

- **Decision**:
  1. Add a table row after `feature-request-issue-author`.
  2. Add `peter-pr-review` to both quick-start copy commands and to the "Updating" command.
  3. Change "All four skills" to "All five skills".
  4. Add a `### peter-pr-review` section after the issue-author section and before `---` / "How
     skills work". It follows the house pattern: what it does, **When it runs**, output behavior,
     **What's inside** tree.
  5. Intro line ("Skills for Claude that help it write, review, and refactor code well…"): no
     change needed, since it already covers review.
- **Rationale**: This matches the existing structure. Every place that lists all the skills must
  list the new one (FR-008, FR-010).
- **Alternatives considered**: A separate "Personal style skills" heading. This was rejected
  because one skill doesn't need its own category.

## R6. Agent context update

- **Decision**: Skip it. This spec-kit install has no `update-agent-context` script
  (`.specify/scripts/powershell/` contains only `check-prerequisites`, `common`,
  `create-new-feature`, `setup-plan` and `setup-tasks`), and the repo has no `CLAUDE.md` to
  refresh.
