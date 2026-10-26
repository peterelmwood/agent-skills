---
name: "feature-request-issue-author"
description: "Creates a high-quality feature request issue in the current GitHub repository, with architecture-first analysis, file-level implementation research, risks, UX impact, and delivery changes. Use whenever the user asks to file, open, write up, draft, or improve a feature request, enhancement, or new-feature GitHub issue, even if they don't say 'feature request' (e.g. 'open an issue for adding X', 'write this up as a ticket for engineering')."
---

# Feature Request Issue Author

When asked to create (or improve) a feature request issue, draft it for the current repository, get the user's approval, then create/update it so it is actionable for engineering. See `references/example-issue.md` for the target tone and depth.

## Workflow

1. **Clarify the request.** Establish who the feature is for, what problem it solves, and what "done" looks like. If the request is too vague to write an actionable issue, ask the user before researching.
2. **Check the environment.** Run `gh auth status` and confirm the current directory is a GitHub repo (`gh repo view`). If `gh` is missing or unauthenticated, continue anyway and deliver the final issue as a Markdown file instead of creating it (see Execution guidance).
3. **Check for duplicates.** Search existing issues with 2–3 keyword variations, e.g. `gh issue list --search "<keywords>" --state all --limit 20`. If a matching open issue exists, show it to the user and ask whether to comment on or improve it instead of opening a new one. Link related or previously closed issues in section 10.
4. **Learn the repo's conventions.** Look for issue templates in `.github/ISSUE_TEMPLATE/` (and `.github/ISSUE_TEMPLATE.md`). If a feature/enhancement template exists, follow its headings and required fields, and fit the sections below into it rather than replacing it. List available labels with `gh label list` and pick existing ones (e.g. `enhancement`); never invent labels.
5. **Research the code.** Find where the app currently handles the behavior, flows, or components the feature touches, and identify likely files to change.
6. **Draft the issue** using the structure below, sized to the feature.
7. **Confirm before creating.** Show the user the proposed title, labels, and full body. Create or edit the issue only after they approve, applying any changes they ask for first. Filing an issue is visible to the whole team, so a wrong assumption is much cheaper to fix in the draft.

## Required issue content

Use this structure in the issue body, tailored to the specific feature. If the repo has an issue template, its structure takes precedence.

**Scale to the feature.** For large or cross-cutting features, use all ten sections. For small, contained changes, keep sections 1–5 and collapse 6–10 into one short "Risks, testing & rollout" section. When a section genuinely doesn't apply, say so in a line rather than dropping it silently.

### 1) Problem statement
- Describe the current behavior or gap, and who is affected.
- State the concrete cost of the gap (confusion, failed or manual work, support burden, lost opportunity).

### 2) Goal / outcome
- Describe the desired behavior from the user's point of view.
- List clear, testable acceptance criteria.
- Note anything explicitly out of scope.

### 3) Preliminary code research
- List likely files/modules to update (UI, APIs/services, data models, shared utilities, configuration, tests).
- For each, include **why it is relevant** and the likely change scope.
- Call out existing code or patterns the feature can reuse.
- **Only cite paths you actually opened in this session**, with line numbers where they help. Mark anything you are inferring rather than confirming, e.g. "(likely — not verified)". A confident but wrong path wastes more of the implementer's time than no path, so never guess a file name that looks plausible.

### 4) Pragmatic design patterns
- Prefer extending existing abstractions and conventions in the repo over introducing new ones.
- Keep domain/business logic separate from presentation and infrastructure.
- Define clear contracts (inputs, outputs, error cases) at module and API boundaries.
- Avoid duplicating logic across code paths; centralize shared rules.
- Note any alternative designs considered and why the recommended one wins.

### 5) Where to start
- Suggest the smallest end-to-end vertical slice that delivers user-visible value.
- Describe how to extend from that slice to the full feature.
- Recommend landing shared building blocks plus tests before broad rollout.

### 6) Dangers / pitfalls
- Inconsistent behavior between related code paths or entry points.
- Regressions in existing functionality the feature touches.
- Hidden coupling, performance, or security implications.
- Incorrect assumptions about data, users, or edge cases.
- Accessibility or usability regressions for any UI changes.

### 7) End-user impact (good and bad)
- **Good:** the concrete benefits users will see.
- **Bad/Tradeoff:** added complexity, behavior changes users must adapt to, or new constraints.

### 8) Testing changes
- Unit tests for new logic.
- Integration/end-to-end tests for the main flows the feature affects, including error states.
- Regression tests for existing behavior that must not change.
- Accessibility checks for any new or changed UI.

### 9) Packaging/deployment changes
- Note whether changes are code-only vs. config/schema/data migration/API contract.
- Mention rollout strategy (feature flag if needed), monitoring, and rollback plan.
- Call out any release notes or updates to user documentation/support scripts.

### 10) Additional concerns
- Telemetry/metrics to measure whether the feature achieves its goal.
- Localization and wording consistency.
- Backward compatibility with existing data, clients, and integrations.
- Related or duplicate issues found in step 3.
- Open questions that need a decision before or during implementation.

## Execution guidance

- `gh` commands work the same in any shell (bash, zsh, PowerShell); use whichever is available.
  - Create: `gh issue create --title "<title>" --body-file "<path-to-body-file>" --label "<existing-label>"`
  - Improve existing: `gh issue edit <number> --repo <owner/repo> --body-file "<path-to-body-file>"`
- Write body files to a scratch/temp directory, **not** the repo, so they don't end up in a commit.
- **Fallback when `gh` is unavailable or unauthenticated:** save the finished issue as a Markdown file (title as the first heading, suggested labels listed under it), give it to the user, and tell them the one command or UI step needed to file it.
- Keep the title explicit and outcome-focused, in the form:
  - `Feature: <what changes> for <who/where>`
- Ensure the issue is specific enough to be implemented without guesswork.
- After creating, share the issue URL returned by `gh`.

## Agent steering (architecture-first)

If these agents are available in the environment, prefer this order:

1. `software-engineering-team:se-system-architecture-reviewer` (primary)
2. `rubber-duck` (secondary design sanity check)
3. `general-purpose` (fallback)

If none of them are available, do the analysis below yourself; the issue content requirements are the same either way.

### Routing guidance

- Use the architecture reviewer when the request includes:
  - cross-cutting behavior spanning multiple modules or layers,
  - shared domain rule or data model design,
  - UI + backend contract implications,
  - rollout/risk decisions.
- Instruct the selected agent to produce:
  - bounded-context/file-impact analysis (verified paths only),
  - decision tradeoffs and chosen architecture,
  - pragmatic patterns (reuse of existing abstractions, clear contracts, separation of concerns),
  - risk register + mitigation,
  - test/packaging/deployment impact.
