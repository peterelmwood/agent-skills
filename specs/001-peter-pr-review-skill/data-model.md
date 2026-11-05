# Data Model: Add Peter PR Review Skill

The "data" is files. Entities map to repo artifacts.

## Skill folder: `peter-pr-review/`

| Field | Value / rule |
|---|---|
| path | `peter-pr-review/` at the repo root |
| files | exactly `SKILL.md` + `references/examples-{backend,frontend,summaries-and-pushback,tests,typing}.md` (FR-002, FR-003) |
| SKILL.md front matter `name` | `peter-pr-review`, which must equal the folder name (FR-005) |
| SKILL.md front matter `description` | unchanged from the attachment |
| content | byte-identical to the issue attachments (FR-001, FR-002) |

**Relationships**: `SKILL.md` references each `references/*.md` file by relative path (FR-006).

## Reference file

| Field | Rule |
|---|---|
| name | `examples-<area>.md` |
| location | `peter-pr-review/references/` |
| referenced by | the "More examples (references/)" table in `SKILL.md` |

## Skill archive: `peter-pr-review.skill`

| Field | Rule |
|---|---|
| format | zip |
| root | a single `peter-pr-review/` prefix |
| file entries | the same 6 relative paths as the folder; directory entries are allowed (research R2) |
| separators | `/` only |
| content | each entry is byte-identical to its folder file (FR-004) |

**Lifecycle**: When the folder changes, the archive is rebuilt with the README's command. In this
feature the folder starts from the archive, so they start in sync.

## README entry

| Location in README | Change |
|---|---|
| Quick start sentence | "All four skills" → "All five skills" |
| Quick start (macOS/Linux) `cp -r` | add `peter-pr-review` |
| Quick start (Windows) `Copy-Item` | add `peter-pr-review` |
| "The skills" table | new row → `peter-pr-review/SKILL.md` |
| Per-skill sections | new `### peter-pr-review` section |
| "Updating" `cp -r` | add `peter-pr-review` |
