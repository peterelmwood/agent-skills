---
name: "bug-report-issue-author"
description: "Creates a high-quality bug report issue in the current GitHub repository, with architecture-first root-cause analysis, code-level research (file+line), impact/severity, regression risks, testing changes, and delivery/rollback implications. Use whenever the user asks to file, open, write up, draft, or improve a bug report, defect, or GitHub issue for something broken, even if they don't say 'bug report' (e.g. 'open an issue for this error', 'write this up so someone can fix it')."
---

# Bug Report Issue Author

When asked to create (or improve) a bug report issue, draft it for the current repository, get the user's approval, then create/update it so it is actionable for engineering: the same architecture-first, research-driven rigor as a feature request, but oriented toward remediation of a defect. See `references/example-issue.md` for the target tone and depth.

## Workflow

1. **Understand the defect.** Establish what the user observed, what they expected, and how to trigger it. If you can't tell what is broken or how to reach it, ask the user before researching.
2. **Check the environment.** Run `gh auth status` and confirm the current directory is a GitHub repo (`gh repo view`). If `gh` is missing or unauthenticated, continue anyway and deliver the final issue as a Markdown file instead of creating it (see Execution guidance).
3. **Check for duplicates.** Search existing issues with 2–3 keyword variations covering the symptom and the component, e.g. `gh issue list --search "<keywords>" --state all --limit 20`. If a matching open issue exists, show it to the user and ask whether to comment on or improve it instead of opening a new one. If a matching **closed** issue exists, the bug may be a regression; link it and say so.
4. **Learn the repo's conventions.** Look for issue templates in `.github/ISSUE_TEMPLATE/` (and `.github/ISSUE_TEMPLATE.md`). If a bug template exists, follow its headings and required fields, and fit the sections below into it rather than replacing it. List available labels with `gh label list` and pick existing ones (e.g. `bug`, a severity label if the repo has them); never invent labels.
5. **Reproduce and locate the root cause.** Confirm the defect where possible and pin the responsible code with concrete file + line references.
6. **Draft the issue** using the structure below, sized to the bug.
7. **Confirm before creating.** Show the user the proposed title, labels, and full body. Create or edit the issue only after they approve, applying any changes they ask for first. Filing an issue is visible to the whole team, so a wrong root-cause claim is much cheaper to fix in the draft.

## Required issue content

Use this structure in the issue body. If the repo has an issue template, its structure takes precedence. Preserve any original screenshots (`<img>` tags) and reviewer callouts (`> [!NOTE]` / `> [!WARNING]`) verbatim at the top.

**Scale to the bug.** For bugs with cross-cutting causes, several call sites, or production-only behavior, use all ten sections. For small, contained bugs (a typo, one wrong condition), keep sections 1–5 and collapse 6–10 into one short "Risks, testing & rollout" section. When a section genuinely doesn't apply, say so in a line rather than dropping it silently.

### 1) Bug summary (observed vs. expected)
- State precisely what happens now (**observed**) and what should happen (**expected**).
- Keep it concrete and reproducible; include numbered steps to reproduce and reference the specific flow/screen/field.
- Note the environment/version where it was seen, and whether you reproduced it yourself or are relying on the user's report.

### 2) Impact & severity
- Who is affected and how badly (data loss, blocked workflow, cosmetic, misrouting, etc.).
- Assign a severity (Low / Medium / High) with a one-line justification, using the repo's severity labels if it has them.

### 3) Root-cause analysis / code research
- Identify the responsible code with **file + line** references and short snippets.
- Explain *why* the defect occurs (the actual mechanism), not just where.
- Note any environment sensitivity (e.g., production-only, config-masked, timing).
- **Only cite paths and lines you actually opened in this session.** If the root cause is not confirmed, say so plainly, e.g. "Suspected root cause (not confirmed)", and state what evidence would confirm it. A confident but wrong root cause sends the fixer down the wrong path, so never present a guess as a finding.

### 4) Preliminary fix approach & pragmatic patterns
- Prefer reusing existing correct patterns/predicates/constants over new ad-hoc logic.
- Keep the fix in one shared source of truth so the defect cannot re-diverge.
- Separate domain logic from UI presentation.
- Note alternative fixes considered and why the recommended one wins.

### 5) Where to start (smallest slice)
- Suggest the smallest correctness slice (single function/predicate) plus a covering test first, then extend to related call sites.

### 6) Dangers / pitfalls & regression risks
- What could break, what must stay unchanged, and what to assert to prove no regression.
- Call out masking environments (dev/live-testing) that can hide the defect from manual checks.

### 7) End-user impact
- **Good:** the corrected behavior users will now see.
- **Tradeoff:** any behavior change or newly enforced constraint.

### 8) Testing changes
- Unit tests for the root-cause condition (including the previously failing case).
- Regression tests proving unaffected flows are unchanged.
- Production/config-sensitive assertions where dev cannot catch the defect.

### 9) Packaging / deployment changes
- Code-only vs. config/schema/contract change; rollout, monitoring, and rollback notes.
- Flag production-only defects for manual live verification before sign-off.
- Note whether any already-affected data needs a cleanup or backfill.

### 10) Additional concerns
- Related or duplicate issues found in step 3, including a closed issue this may regress.
- Opportunities to centralize logic to prevent recurrence, telemetry, wording.
- Open questions that need a decision before or during the fix.

## Execution guidance

- `gh` commands work the same in any shell (bash, zsh, PowerShell); use whichever is available.
  - Create: `gh issue create --title "<title>" --body-file "<path-to-body-file>" --label "<existing-label>"`
  - Improve existing: `gh issue edit <number> --repo <owner/repo> --body-file "<path-to-body-file>"`
- Write body files to a scratch/temp directory, **not** the repo, so they don't end up in a commit.
- **Fallback when `gh` is unavailable or unauthenticated:** save the finished issue as a Markdown file (title as the first heading, suggested labels listed under it), give it to the user, and tell them the one command or UI step needed to file it.
- Keep the title explicit and prefixed, e.g.:
  - `Bug: <component> <symptom> (<root-cause hint>)`
- Ensure the issue is specific enough to fix without guesswork. Include at least one concrete file + line pointer, labeled as suspected if it isn't confirmed.
- Preserve original screenshots and reviewer callouts verbatim.
- After creating, share the issue URL returned by `gh`.

## Agent steering (architecture-first)

If these agents are available in the environment, prefer this order:

1. `software-engineering-team:se-system-architecture-reviewer` (primary)
2. `rubber-duck` (secondary design/root-cause sanity check)
3. `general-purpose` (fallback)

If none of them are available, do the analysis below yourself; the issue content requirements are the same either way.

### Routing guidance

- Use the architecture reviewer when the bug involves:
  - cross-cutting behavior or shared-domain rules,
  - UI + backend contract implications,
  - environment/config-sensitive (e.g., production-only) defects,
  - fixes that risk regressions across multiple call sites.
- Instruct the selected agent to produce:
  - root-cause mechanism with file-impact analysis (verified paths only, suspected causes labeled),
  - the minimal shared-source-of-truth fix and why alternatives were rejected,
  - regression risk register + mitigations,
  - test/packaging/deployment impact (including production verification where dev masks the defect).
