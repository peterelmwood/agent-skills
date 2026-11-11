# Research: Add Explain-Scope-First Skill

## R1: Getting the source bytes

- **Decision**: Fetch with `gh issue view 5 --repo peterelmwood/agent-skills --json body
  --jq .body > $S/issue5.md` and take the lines strictly between the ```` ````markdown ````
  opener (line 121) and the closing ```` ```` ```` (line 152) inside the collapsed
  "complete proposed source" `<details>` block. Result: 30 lines, 2,781 bytes, LF, one
  trailing newline, UTF-8 without BOM.
- **Rationale**: Console rendering wraps long lines; reading from the saved body keeps the
  long description and bullet lines intact. The four-backtick fence means no inner fence can
  end it early (the source has none anyway).
- **Alternatives**: Copying from the rendered issue page (rejected: smart quotes and wraps
  are easy to corrupt).

## R2: Supporting files

- **Decision**: `SKILL.md` only.
- **Rationale**: Issue §4 says "Use one instruction file; this workflow needs no scripts,
  dependencies, or reference library", and the issue supplies only one source file.

## R3: Skill count and placement

- **Decision**: Append after `asd-ste100` in the table and all three copy commands; change
  "All eight skills" to "All nine skills".
- **Rationale**: Issue §9 says to set the count from the folders that actually exist at merge
  time. The base branch `skills-step-breakdown-deepen-prompt-asd-ste100` has eight skill
  folders; this adds the ninth. The issue's line numbers (L13, L22, L227, "says five") were
  taken from `main` and are stale on this base; the matching lines were located by content.

## R4: Tagline

- **Decision**: Leave the README tagline unchanged.
- **Rationale**: It lists themes, not every skill (it already omits `deepen-prompt`), and is
  not made inaccurate by this addition.

## R5: Source review (adopted as-is)

The source covers every behavioral acceptance criterion in issue §2: the three-part
statement before mutation, tentative vs confirmed targets, concrete exclusions or an explicit
"none", no unconditional approval gate, honoring explicit waits, stopping at exclusions,
updating on correction, repeating only on material change, a description that excludes
no-change questions, and an honest completion report. No defects were found that justify
patching.

## Follow-ups

- **F1 (outstanding)**: Run the seven behavioral scenarios in issue §8 in a fresh Claude Code
  session with the skill installed, inspecting operation order and before/after state of
  excluded artifacts. Not run here; no results are claimed.
- **F2 (partly done)**: Issue §8 mentions a structural validator that previously failed for
  lack of PyYAML. That validator is not in this repo. Here the frontmatter was parsed with
  PyYAML 6.0.3 (`yaml.safe_load`): keys are exactly `name` and `description`, `name` is
  `explain-scope-first`, description is 287 characters. Archive/source parity is verified
  (quickstart §3). Running the original validator itself is still outstanding.
- **F3 (minor, wording)**: The description's trigger list is narrow by design ("scope check,
  readback before editing, or explicit boundaries"). If users phrase it as "tell me what
  you won't touch" without the words "scope" or "readback", discovery may miss it; consider
  adding that phrasing after the behavioral evals show whether it is needed.
- **F4 (minor)**: The source uses curly quotes around “nothing unrelated.” in the bullet.
  Harmless in Markdown; noted only because other skills use straight quotes.
