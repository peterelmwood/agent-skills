# Research: Add Step Breakdown Skill

No Technical Context item was marked NEEDS CLARIFICATION. The decisions below settle choices
found while extracting the issue's source and inspecting the repo.

## R1. Source of truth for the skill content

- **Decision**: Extract both files from the issue body fetched as JSON
  (`gh issue view 3 --json body`). `SKILL.md` is the text inside the ```` ````markdown ````
  fence; `check_plan.py` is the text inside the ```` ```python ```` fence. Each gets one
  trailing newline and is written as UTF-8 without BOM, with LF line endings.
- **Rationale**: The JSON body has no CRLFs and keeps every line intact. Console output such
  as `Format-List` wraps long lines (for example the `unreadable Needs entry` f-string), which
  would corrupt the Python file. Trial extraction gave 211 lines for `SKILL.md` and 210 for
  `check_plan.py`; the script compiles and the frontmatter starts with `name: step-breakdown`.
- **Alternatives considered**: Copy from the rendered GitHub page or terminal output.
  Rejected because of line wrapping and possible smart-quote or whitespace changes.

## R2. Line endings and encoding

- **Decision**: Commit with LF, UTF-8, no BOM.
- **Rationale**: Every existing skill file is stored as `i/lf w/lf` (`git ls-files --eol`).
  `core.autocrlf=true` is set locally, so files written with LF stay LF in the index. The
  checker reads its input as UTF-8 explicitly and reconfigures stdout to UTF-8.

## R3. Building the archive

- **Decision**: Build `step-breakdown.skill` with the README's Windows command
  (`[IO.Compression.ZipFile]::CreateFromDirectory(..., 'Optimal', $true)`) in PowerShell 7,
  after deleting any old archive. Then verify with Python's `zipfile`: file entries are
  exactly `step-breakdown/SKILL.md` and `step-breakdown/scripts/check_plan.py`, all names use
  `/`, and the bytes match the folder.
- **Rationale**: Issue §5 step 2 says to build it with the README's command, and there is no
  attached archive to reuse (unlike feature 001). `design-patterns.skill` was checked as a
  reference: its entries are files only, under `<name>/`, with `/` separators.
- **Alternatives considered**: Python `zipfile` or `Compress-Archive`. `Compress-Archive` is
  ruled out by README L260 (backslash separators). Python would work but isn't the
  documented workflow.
- **Note**: Directory entries, if the .NET command emits any, are allowed (same as feature
  001's contract).

## R4. Behaviour of the shipped checker

- **Decision**: Ship `check_plan.py` unchanged; verify it rather than modify it.
- **Rationale**: Trial runs on the extracted copy:
  - On the worked example in `SKILL.md`: 13 steps, 1 gate, ~6.8 h, available now 3, 6, 7, 8;
    gate 5 pending; `OK: no consistency errors`; exit 0. That matches the prose under the
    example ("Steps 3, 6, 7 and 8 are available now").
  - No argument: prints the module docstring and exits 2.
  - Exit codes: 0 clean, 1 errors, 2 usage. Over-30-minute steps without an exception and
    ticked-while-blocked steps are warnings, not errors.
- **Open check for implementation**: a broken plan (unknown ID, cycle, contradicting parallel
  line, missing done-check, no available step) and a cp1252 stdout run
  (`PYTHONIOENCODING=cp1252`) are in [quickstart.md](./quickstart.md).

## R5. README scope

- **Decision**: Edit the skills table, the Quick start macOS/Linux (L13) and Windows (L22)
  copy commands, the **Updating** copy command (L227), the "All five skills" sentence (L25,
  → six), and add a `### step-breakdown` section after `### peter-pr-review` with **When it
  runs**, **What it produces** and **What's inside**. Make a minimal tagline change (L3) to
  mention planning.
- **Rationale**: The issue lists the table, both Quick start commands, the count and the
  section. The Updating command is a third copy of the same list; leaving it out would
  silently skip the new skill on update. The tagline change is "optional" in the issue, but
  the repo now has a non-code skill, so the tagline would otherwise be inaccurate.
- **Alternatives considered**: Leave the tagline as is. Rejected as now inaccurate; issue §10
  leaves the call to the maintainer, so the change is kept to one clause.

## R6. Out of scope (confirmed)

Gist version of the skill, committing `evals/`, trigger-recall tuning, and external tool
sync. These are issue §10 open questions or explicit out-of-scope items.
