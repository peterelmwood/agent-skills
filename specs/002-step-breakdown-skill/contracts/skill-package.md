# Contract: step-breakdown skill package

## Folder

```text
step-breakdown/
├── SKILL.md
└── scripts/
    └── check_plan.py
```

- Exactly these two files. No `evals/`, no caches (`__pycache__`), no other files.
- Both files are byte-identical to the issue #3 source as extracted in research R1:
  UTF-8, no BOM, LF, one trailing newline.
- `SKILL.md` starts with YAML frontmatter containing `name: step-breakdown` and a
  `description`.
- `SKILL.md` refers to the checker as `<this-skill-dir>/scripts/check_plan.py`, which
  resolves to the shipped file.

## Archive

- Path: `step-breakdown.skill` at the repo root.
- Format: zip.
- File entries: exactly `step-breakdown/SKILL.md` and `step-breakdown/scripts/check_plan.py`.
  Directory entries (`step-breakdown/`, `step-breakdown/scripts/`) are allowed.
- Every entry name uses `/`; none contains `\`.
- Each file entry's bytes equal the matching file in the folder.

## Repo invariants

- No file under any other skill folder or any other `*.skill` archive changes.
- `README.md` lists `step-breakdown` in: the skills table, the Quick start macOS/Linux copy
  command, the Quick start Windows copy command, and the Updating copy command; says "six"
  skills; and has a `### step-breakdown` section.
