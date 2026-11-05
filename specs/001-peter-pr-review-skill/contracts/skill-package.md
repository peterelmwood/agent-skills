# Contract: Skill package layout

This is the interface every consumer relies on: Claude Code's skill loader, the Claude.ai/Desktop
upload, and README readers.

## Folder contract (Claude Code)

```text
peter-pr-review/
├── SKILL.md            # YAML front matter: name: peter-pr-review, description: <one paragraph>
└── references/
    ├── examples-backend.md
    ├── examples-frontend.md
    ├── examples-summaries-and-pushback.md
    ├── examples-tests.md
    └── examples-typing.md
```

- `SKILL.md` MUST start with `---` front matter containing `name` and `description`.
- `name` MUST equal the folder name.
- Every `references/<file>` path written in `SKILL.md` MUST exist.

## Archive contract (Claude.ai / Claude Desktop upload)

- File: `peter-pr-review.skill` (zip).
- Every entry path starts with `peter-pr-review/` and uses `/` separators.
- File entries match the folder contract one-to-one. Optional directory entries are allowed.
- Entry bytes equal the folder file bytes.

## README contract

- Every command that copies "all skills" lists `peter-pr-review`.
- The skills table links to `peter-pr-review/SKILL.md`.
- Any skill count matches the number of top-level skill folders.
