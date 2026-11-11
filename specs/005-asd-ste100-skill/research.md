# Research: Add ASD-STE100 Prompt-Constraint Skill

## R1. Source of truth for the skill content

- **Decision**: Extract both files from the issue body fetched as JSON
  (`gh issue view 6 --json body`). `SKILL.md` is the text inside the ```` ````markdown ````
  fence; `agents/openai.yaml` is the text inside the ```` ````yaml ```` fence. Each gets one
  trailing newline, LF line endings, UTF-8 without BOM.
- **Rationale**: Same as feature 002 R1: console output wraps long lines. Extraction gave 47
  lines for `SKILL.md` and 4 for `openai.yaml`. The frontmatter parses with PyYAML to
  `name: asd-ste100` and a 259-character `description`; `openai.yaml` parses to an
  `interface` map with `display_name`, `short_description` and `default_prompt`.

## R2. Keep `agents/openai.yaml`?

- **Decision**: Keep it, at `asd-ste100/agents/openai.yaml`, exactly as proposed, and list it
  in the README "What's inside" tree as optional Codex metadata that Claude ignores.
- **Rationale**:
  - The issue includes it explicitly "to preserve the original generated skill", and its
    acceptance criteria ask for "the supplied instructions" with packaging adapted only as
    needed.
  - It doesn't break Claude. Claude Code and Claude.ai read `SKILL.md` and only open other
    files that `SKILL.md` points to; `SKILL.md` doesn't reference `agents/`, so the file is
    never loaded into context. An extra subfolder in the upload zip is allowed (other skills
    here ship `references/` and `scripts/`).
  - It doesn't contradict a convention that matters. No other skill has one, but the repo's
    convention is "`SKILL.md` + optional supporting folders", and the README describes the
    skills as portable. Keeping it also lets the same folder work in OpenAI Codex, which
    reads `agents/openai.yaml` for UI display.
  - `default_prompt` uses `$asd-ste100`, Codex's skill-mention syntax. It is display text
    only and has no effect in Claude.
- **Alternatives considered**: Drop the file (cleaner Claude-only layout, but diverges from
  the issue's source for no functional gain), or keep it outside the skill folder (breaks the
  Codex convention and the "self-contained folder" model).

## R3. Copyright check

- **Decision**: Ship as-is.
- **Rationale**: `SKILL.md` contains no rule text, rule numbers, dictionary entries or word
  lists from ASD-STE100. It says "Do not reproduce the standard or its dictionary in this
  skill" and points to the official site for copies. The only specific figures are the
  widely published 20/25-word sentence limits, stated as "usual" limits to verify against the
  applicable issue. The README section adds no standard text either.

## R4. Archive

- **Decision**: Build `asd-ste100.skill` with the README's PowerShell 7 command
  (`[IO.Compression.ZipFile]::CreateFromDirectory(..., 'Optimal', $true)`), then check with
  Python `zipfile`.
- **Result**: Entries `asd-ste100/SKILL.md`, `asd-ste100/agents/openai.yaml` (no directory
  entries), no `\`, bytes identical to the folder.

## R5. README scope

- **Decision**: Add the table row after `step-breakdown`; add `asd-ste100` to the Quick start
  `cp -r` and `Copy-Item` commands and the Updating `cp -r` command; "All six skills" → "All
  seven skills"; add a `### asd-ste100` section after `### step-breakdown`; add one clause to
  the tagline (L3) about technical documentation, following feature 002's precedent that the
  tagline should cover every kind of skill in the repo.
- **Section content**: what it does (three request types, meaning-first rules), the
  STE-inspired vs verified-conformance distinction, a note that the standard isn't bundled,
  **When it runs** (STE requests only), **What it produces**, **What's inside**.

## Follow-ups (found during implementation)

The skill content is adopted as-is, so these are recorded rather than patched:

1. **Minor punctuation.** `SKILL.md` has "https://www.asd-ste100.org/ ;" with a space before
   the semicolon (probably to stop the semicolon being read as part of the URL). Harmless;
   could be rewritten as a Markdown link.
2. **"Issue" is overloaded.** In the skill, "issue" means an edition of the ASD-STE100
   standard. In a GitHub-heavy repo (two other skills write GitHub issues) a reader may
   misread it. Consider "issue (edition) of the standard" on first use.
3. **No worked example.** Unlike most skills here, there is no before/after example or sample
   review output. One short example of each could make outputs more consistent, as long as it
   quotes no standard text.
4. **Trigger recall.** The description says "Use when STE is requested". Requests that say
   "Simplified Technical English" or "controlled English" without "STE" should still match
   via the description's first sentence, but this hasn't been tested in a live session.
5. **`$asd-ste100`** in `openai.yaml` is Codex syntax. If the repo ever drops non-Claude
   metadata, remove `agents/` and rebuild the archive.

## R6. Out of scope (confirmed)

Bundling any part of the standard or dictionary, automated STE checking tools, and live
trigger testing (left for the maintainer's smoke test).
