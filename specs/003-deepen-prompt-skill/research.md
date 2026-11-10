# Research: Add Deepen Prompt Skill

**Feature**: [spec.md](./spec.md) | **Date**: 2026-11-10

## R1. Source of truth for the skill content

**Decision**: Extract the ````` ````markdown ````` fence under "Skill source (proposed draft,
iteration 0)" from `gh issue view 4 --json body`, normalise to LF, add one trailing newline,
write UTF-8 without BOM.

**Rationale**: Console-formatted `gh` output wraps long lines and would corrupt the
one-line `description`. The outer fence is four backticks, so the inner ```` ```text ````
fences in the draft survive extraction intact.

**Result**: 67 lines, `name: deepen-prompt` on line 2, frontmatter parses as YAML with
exactly `name` and `description` (919 characters, under the 1024 limit), and skill-creator's
`quick_validate.py` reports "Skill is valid!".

## R2. Building the archive

**Decision**: README's PowerShell 7 command,
`[IO.Compression.ZipFile]::CreateFromDirectory("$PWD\deepen-prompt", "$PWD\deepen-prompt.skill", 'Optimal', $true)`.

**Result**: one entry, `deepen-prompt/SKILL.md`, `/` separator, bytes identical to the
folder file (checked with Python `zipfile`).

## R3. `references/examples.md`

**Decision**: Not added.

**Rationale**: The issue makes it conditional on evals showing outputs stay generic. In the
iteration-1 output evals (R4), all three with-skill rewrites named concrete raw sources,
methods and checks specific to their field (e.g. `EXPLAIN (ANALYZE, BUFFERS)`, ORS 90.323, a
denatured-alcohol / lacquer-thinner spot test), so there is no evidence the inline example
is insufficient.

## R4. skill-creator evals

skill-creator is available locally (synced skill with `scripts/`, `eval-viewer/`, `agents/`)
and the `claude` CLI is on the path.

**Output evals (run, informally)**: the 4 §8 prompts were each run once with the skill
(a subagent told to read `deepen-prompt/SKILL.md` and follow it) and once as a no-skill
baseline. Outputs and grading are in an external workspace
(`<scratchpad>/deepen-prompt-workspace/iteration-1/`), not in the repo. Grading against the
§8 assertions, done by the implementing agent rather than skill-creator's grader agent:

| Eval | With skill | Baseline |
|---|---|---|
| 1 etl-regression-screenshot | 7/7 | 4/7 |
| 2 rent-ordinance-lease | 6/7 | 2/7 |
| 3 walnut-dresser-niche | 8/8 | 3/8 |
| 4 ambiguous-help-me-decide | 2/2 | 1/2 |
| **Total** | **23/24 (96%)** | **10/24 (42%)** |

The one with-skill miss is the deliverables check on eval 2 (see Follow-up 3). "Does not
execute the rewritten task" passed in every run, with and without the skill, so it doesn't
discriminate on these prompts. Caveats: one run per configuration, self-graded, no
`aggregate_benchmark`, and not reviewed in the eval viewer (which needs the maintainer).

**Trigger eval / `run_loop` (not run)**: `scripts/run_eval.py` reads the nested
`claude -p` stream with `select.select()` on a subprocess pipe, which Windows doesn't support
(it only accepts sockets), so `run_eval`/`run_loop` can't run on this machine. It would also
start up to ~300 nested `claude -p` sessions (20 queries × 3 runs × 5 iterations) and write
temporary command files under the project's `.claude/commands/`. Left for the maintainer to
run on macOS/Linux/WSL from a scratch directory.

**`evals/evals.json` (not committed)**: the issue gives the eval set as tables, not a file,
and the package contract requires the archive to match the folder exactly; committing
`deepen-prompt/evals/` would either break that or ship eval material. Kept in the external
workspace instead.

## R5. README scope

Table row after `step-breakdown`; `deepen-prompt` appended after `step-breakdown` in the two
Quick start commands (L13, L22) and the Updating command (L253; the issue's L227 predates
feature 002); "All six skills" → "All seven skills"; a `### deepen-prompt` section after
`### step-breakdown`. The tagline (L3) is unchanged: it doesn't claim to list every use, so
it isn't inaccurate.

## Follow-ups (found during implementation)

The skill content is adopted as-is, so these are recorded rather than patched:

1. **Name.** Issue §10 calls `deepen-prompt` a placeholder (alternatives: `go-deeper`,
   `expert-reframe`, `depth-not-breadth`). Decide before merging; a rename touches the
   folder, archive, frontmatter, README and these specs.
2. **Example vs. output format.** The "Output format" section uses bold numbered labels, a
   **Rewritten prompt** heading and a closing "Want me to run this?", but the worked
   "Example" uses a plain numbered list, no heading and no closing offer. In the evals the
   model followed the format section, but the example could be aligned with it.
3. **Deliverable creep on eval 2.** The with-skill rewrite added "flag anything the news
   article gets wrong" and "what I should ask the Rental Services Office" to the original
   two deliverables (summary, does it affect my lease). The step 6 self-check didn't catch
   additions phrased as sub-parts of an existing deliverable. Consider making the check
   explicit about sub-deliverables.
4. **Trigger eval and description optimization** still to run (R4), then the eval viewer
   review; both are merge criteria in issue §2.
5. **Description length.** 919 of 1024 characters; `run_loop` output may need trimming.

## R6. Out of scope (confirmed)

Running the rewritten prompt automatically, general prompt polishing, per-domain reference
libraries (issue §2), and the §10 open questions ("deepen and do" mode, provenance in answer
2, whether 80% is the right bar).
