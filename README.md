# agent-skills

Skills for Claude that help it write, review, and refactor code well, write GitHub issues engineers can act on, keep technical documentation in Simplified Technical English, and break big efforts into steps you can track for weeks.

## Quick start (Claude Code)

**macOS / Linux**

```sh
git clone https://github.com/peterelmwood/agent-skills.git
mkdir -p ~/.claude/skills
cd agent-skills
cp -r design-patterns react-anti-patterns bug-report-issue-author feature-request-issue-author peter-pr-review step-breakdown deepen-prompt asd-ste100 ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/peterelmwood/agent-skills.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
cd agent-skills
Copy-Item -Recurse -Force design-patterns, react-anti-patterns, bug-report-issue-author, feature-request-issue-author, peter-pr-review, step-breakdown, deepen-prompt, asd-ste100 "$HOME\.claude\skills\"
```

Then start a new Claude Code session. All eight skills are now installed. You don't have to call them: Claude uses one when your request matches it.

To install only some of them, copy just those folders (for example `cp -r design-patterns ~/.claude/skills/`).

## Quick start (Claude.ai / Claude Desktop)

1. Download the `.skill` file for each skill you want from this repo.
2. In Claude, open **Settings → Capabilities → Skills** and upload the file.

The `.skill` files are zip archives of the folders, packaged for upload.

---

## The skills

| Skill | Use it for |
|---|---|
| [`design-patterns`](design-patterns/SKILL.md) | Deciding how code or a database schema should be structured, and when a pattern isn't worth adding. |
| [`react-anti-patterns`](react-anti-patterns/SKILL.md) | Spotting common React mistakes and picking the right fix for each one. |
| [`bug-report-issue-author`](bug-report-issue-author/SKILL.md) | Turning a bug into a GitHub issue with a root-cause analysis and a proposed fix. |
| [`feature-request-issue-author`](feature-request-issue-author/SKILL.md) | Turning a feature idea into a GitHub issue with code research, risks, and a rollout plan. |
| [`peter-pr-review`](peter-pr-review/SKILL.md) | Reviewing a pull request or diff the way Peter does, on Django/DRF and React/TypeScript code, with inline comments and a review summary. |
| [`step-breakdown`](step-breakdown/SKILL.md) | Breaking a project or multi-week effort into a numbered checklist of small steps, with done-checks, dependencies, and waiting gates, that you can come back to for weeks. |
| [`deepen-prompt`](deepen-prompt/SKILL.md) | Making a task or prompt deeper, not bigger: how a top professional would frame it, what raw material and named methods they'd use, and what independent check would show the answer is right. |
| [`asd-ste100`](asd-ste100/SKILL.md) | Drafting, rewriting, or reviewing technical documentation in ASD-STE100 Simplified Technical English, or writing a reusable prompt that applies it, without claiming compliance that hasn't been verified. |

### design-patterns

This skill helps Claude apply design patterns and engineering principles with judgment, not by reflex. It draws on these sources:

- the Gang of Four patterns
- Fowler's refactorings and code smells
- Clean Code and Clean Architecture
- *Code Complete*
- TDD, XP, and Lean
- SICP's ideas about abstraction
- Google engineering practice and SRE reliability patterns
- Karwin's *SQL Antipatterns*

The skill follows these steps:

1. Name the *forces* that make the code hard to change, test, or understand.
2. Identify the code smell, if there is one.
3. Pick the smallest change that relieves those forces.
4. Make the change safely.
5. Check the result against a simplicity bar.

Sometimes the right answer is to leave the pattern out, and the skill treats that as a valid result.

**When it runs:** when you ask Claude to refactor or review code, or ask how to structure code. Requests like "this class is too big", "is this over-engineered?", "reduce coupling", "make this testable", and "design this table" all trigger it. It also runs for code migrations, such as VB.NET to C#, and for awkward or slow SQL.

**What's inside:**

```
design-patterns/
├── SKILL.md                              core workflow and judgment rules
└── references/
    ├── gof-patterns.md                   Gang of Four catalog, with when to use and when to skip each pattern
    ├── refactoring-smells.md             Fowler's smells and the refactorings that fix them
    ├── clean-code-architecture.md        Clean Code and Clean Architecture
    ├── code-complete.md                  construction practices from Code Complete
    ├── process-and-testing.md            TDD, XP, and Lean
    ├── sicp-abstraction.md               abstraction barriers and composition
    ├── google-and-sre.md                 code review, readability, and reliability patterns
    └── sql-antipatterns.md               schema and query antipatterns
```

### react-anti-patterns

This skill is a catalog of React anti-patterns. For each one, it gives the patterns that can replace it and explains which fits in which situation. The idea behind it is that most React bugs are *modeling* bugs, not React bugs. Typical examples:

- state that shouldn't exist
- effects that should be event handlers
- components that do three jobs at once
- validation that trusts unchecked data

The skill covers these tools and features:

- TanStack Query, Router, Table, and Form
- Zod
- MSW
- Vitest
- React 19 features: `useEffectEvent`, the React Compiler, and Actions

**When it runs:** any time Claude writes, reviews, refactors, or debugs React or TypeScript code. Mentions of `useEffect`, re-renders, prop drilling, state that's out of sync, forms, validation, data fetching, tables, routing, or component tests all trigger it.

**What's inside:**

```
react-anti-patterns/
├── SKILL.md                              smell table, principles, review checklist
└── references/
    ├── state.md                          derived and duplicated state
    ├── effects.md                        effects that should be events or derivations
    ├── component-responsibilities.md     splitting components that do too much
    ├── prop-drilling.md                  composition, context, and when to use each
    ├── data-fetching.md                  TanStack Query instead of fetching inside effects
    ├── validation.md                     Zod at the edges of the app
    ├── tanstack-table.md                 table-specific pitfalls
    └── testing.md                        Vitest, Testing Library, and MSW
```

### bug-report-issue-author and feature-request-issue-author

These two skills write GitHub issues for the repository you're working in. One handles bugs and the other handles feature requests. Both follow the same steps:

1. **Clarify.** Pin down what's broken, or what the feature is for. If the request is too vague, Claude asks before it starts researching.
2. **Check the environment.** Confirm `gh` is installed and signed in, and that the current folder is a GitHub repo.
3. **Look for duplicates.** Search existing issues, including closed ones. For a bug, a matching closed issue may mean a regression.
4. **Follow the repo's conventions.** Use the repo's issue templates if it has any, and only use labels that already exist.
5. **Research the code.** Find the files involved, with line numbers.
6. **Draft the issue.** Write the issue body in ten sections, shortened for small issues.
7. **Get your approval.** Show you the title, labels, and full body. Claude files the issue only after you approve it.

Both skills only cite file paths that Claude actually opened. A root cause or path that hasn't been confirmed is labeled as suspected, so whoever picks up the issue isn't sent the wrong way.

| | Bug report | Feature request |
|---|---|---|
| **Title format** | `Bug: <component> <symptom> (<root-cause hint>)` | `Feature: <what changes> for <who/where>` |
| **Opens with** | Observed vs. expected behavior, steps to reproduce, and severity | Problem statement, goal, and acceptance criteria |
| **Core research** | Root cause: where the defect is and *why* it happens | Files to change, and existing code to reuse |
| **Rest of the issue** | Fix approach, where to start, regression risks, user impact, tests, rollout and rollback, open questions | Design approach, where to start, pitfalls, user impact, tests, rollout, open questions |

**When they run:** when you ask Claude to file, open, write up, draft, or improve an issue, even if you don't say "bug report" or "feature request". Requests like "open an issue for this error" and "write this up as a ticket for engineering" both trigger them.

**Requirements:** the [GitHub CLI](https://cli.github.com/) (`gh`), signed in with `gh auth login`. If `gh` isn't available, Claude saves the finished issue as a Markdown file and tells you how to file it yourself.

**What's inside:**

```
bug-report-issue-author/
├── SKILL.md                              steps, issue structure, how to file the issue
└── references/
    └── example-issue.md                  a complete example bug report

feature-request-issue-author/
├── SKILL.md                              steps, issue structure, how to file the issue
└── references/
    └── example-issue.md                  a complete example feature request
```

Each skill is also published as a gist ([bug report](https://gist.github.com/peterelmwood/96292c79fc4a4d79ccf4d56c028d9982), [feature request](https://gist.github.com/peterelmwood/0e4d46e228da29c54bc17036b8dbb135)). Gists can't contain folders, so the files sit side by side there: `SKILL.md` is saved under the skill's name, and `example-issue.md` sits next to it. Use this repo's folder (or `.skill` file) to install, since that keeps the `references/` path the skill expects.

### peter-pr-review

This skill has Claude review a pull request the way Peter does. It's distilled from about 595 pull requests Peter reviewed between 2023 and 2025, across Django/DRF, React/TypeScript, and .NET code. Where his habits changed over time, the 2025 reviews win.

The skill checks these areas, ranked by how often Peter raises them:

- functions that do too much, logic in the wrong layer, and passing more parameters than a function needs
- query count in Django: N+1 queries, missing `select_related`/`prefetch_related`, and per-row saves that could be bulk operations
- docstrings and "why" comments for anything unusual
- tests that are well named and actually prove the change
- type hints and TypeScript types that match what the code really returns
- formatting, serializer and QuerySet placement, naming, error handling, and REST semantics

Comments follow his voice: short for mechanical fixes, and longer with code, evidence, and a "Reasoning:" list for design, correctness, and typing problems.

**When it runs:** when you ask Claude to review a PR or diff "like Peter", to pre-review a branch before you request review, or to draft review comments in his voice.

**What it produces:** inline comments as `path:line` plus the comment text, followed by a summary and a verdict (**Request changes**, **Comment**, or **Approve**). Claude shows you the draft to edit. It doesn't post the review unless you ask it to.

**What's inside:**

```
peter-pr-review/
├── SKILL.md                              how Peter reviews, what he looks for, voice, and examples
└── references/
    ├── examples-backend.md               Django/DRF views, serializers, QuerySets, migrations, and queries
    ├── examples-tests.md                 pytest/Django and Vitest/Testing Library tests, fixtures, and mocks
    ├── examples-typing.md                Python type hints, TypeScript types, nullability, and casts
    ├── examples-frontend.md              React components, hooks, loaders, and MUI/AG Grid usage
    └── examples-summaries-and-pushback.md   review summaries, and replies when the author disagrees
```

### step-breakdown

This skill turns a large, fuzzy effort, such as a migration, a launch, a move, or a talk submission, into one Markdown checklist you can come back to for weeks. Each step is small (about 30 minutes or less), starts with a verb, and has a concrete done-check. The checklist answers one question on any day you open it: *what can I do right now?*

- **Dependencies decide what's available.** Every step lists `Needs:`. A step is available when everything it needs is ticked, so file order is only a suggestion.
- **Waits are gates.** Approvals, deliveries, and replies are `⏳ GATE` checkboxes, ticked only when the outside event happens, so ticking "Submit permit application" never makes "Start construction" look ready.
- **Parallel lines** (`⇉`) show steps you can do in any order or at the same time, with a `⚠` note when they compete for the same person or tool.
- **Nothing is invented.** Unknown details are `[TBD: …]` placeholders, and later phases that depend on an open decision stay as `🔭 Expand after <ID>` placeholders.
- **IDs are stable.** A step that turns out too big is split into `14a`, `14b`, … under `14`, and nothing is ever renumbered.

**When it runs:** when you ask Claude to break down, chunk, or make a step-by-step plan, roadmap, or checklist for a project or multi-week effort, even if you don't say "steps" ("how do I even start on X", "I keep stalling on this project"), and when you come back to update an existing plan. It doesn't run for a single quick task or for a code-level plan you're about to implement in the same session. If Claude answers inline instead, ask for a step plan: for example, "break down moving apartments in 6 weeks".

**What it produces:** one `<project-slug>-steps.md` file with numbered steps and gates, active-effort estimates, Decisions, Open questions, and a Progress log. When you report progress, Claude updates the same file in place: it keeps your ticks, notes, and log rows, and lists anything that conflicts with the file under **Open questions** instead of overwriting it. Before saving, it runs a consistency checker and tells you which steps are available now and which gates to start early.

**What's inside:**

```
step-breakdown/
├── SKILL.md                              process, dependency/gate/split rules, output template, worked example, update rules
└── scripts/
    └── check_plan.py                     consistency checker: IDs, Needs, cycles, parallel lines, done-checks, "available now"
```

`check_plan.py` needs Python 3.8 or later and uses only the standard library. Where scripts can't run (for example on Claude.ai), the skill does the same checks by reading the file.

### deepen-prompt

This skill is for when asking Claude to do something "better" only makes the answer bigger: more sections, more options, more caveats. Instead, it asks how a top professional in that field would approach the task, and rewrites your prompt to ask for that. It answers four questions:

- **What would an expert do that you aren't asking for?** A move specific to the field, such as checking a premise, reframing the question, or asking for a baseline first.
- **What's the rawest material?** The primary source the expert would start from (logs, the ordinance text, the dataset, the object itself), set against the summary, screenshot, or article you have now.
- **Which methods and tools?** Named concretely (`git bisect`, `EXPLAIN ANALYZE`, a pin-type moisture meter), not as categories. In a niche field where Claude doesn't know the specialist toolset, it says so and suggests how to find out instead of inventing names.
- **What, other than Claude or you, shows it's right?** An independent check and how to get it: a test, a measurement, the primary source, or a qualified reviewer. Asking another model, or asking you, doesn't count.

The rewrite keeps the same deliverables as your original prompt. It changes the inputs, the method, and what "done" means, not the amount of output.

**When it runs:** when you ask Claude to go deeper, be more rigorous, approach something "like a pro would", make an answer verifiable, or say "what am I missing in how I framed this", even if you don't say "deeper". It doesn't run for copy-editing, shortening, or formatting a prompt, for expanding something into a longer deliverable, or for actually carrying out research. If the task is too vague to pick an expert (for example "help me decide"), Claude asks one clarifying question instead of guessing. To try it: "deeper version of this: 'tell me why my nightly ETL got slower'".

**What it produces:** one line naming the assumed field or role (so you can correct it), four short labeled answers, and the rewritten prompt in a fenced block you can copy. It then stops and offers to run the rewritten prompt. Nothing is run until you say so.

**What's inside:**

```
deepen-prompt/
└── SKILL.md                              the loop (pick the expert, four questions, deeper-not-bigger rewrite), output format, worked example
```

### asd-ste100

This skill uses [ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/) (STE) as a writing constraint for English technical documentation, such as maintenance procedures, operating instructions, and descriptions. It handles three kinds of request:

- **Create a reusable prompt** that constrains a writing task to STE. If you only ask for the prompt, Claude gives you the prompt and doesn't also do the task.
- **Draft or rewrite** text under the constraint.
- **Review** existing text against it.

Technical meaning comes first. Facts, conditions, sequence, limits, units, identifiers, warnings, and the strength of "must" and "must not" are kept. Claude doesn't invent missing safety information or guess at an ambiguous instruction; it flags the ambiguity instead. Code, UI labels, API names, and other exact strings are left as they are.

The skill keeps two results apart:

- **STE-inspired** text follows practical defaults: short sentences (the usual limits are 20 words for procedures and 25 for descriptions), one instruction per step, active voice, one term per concept, and no idioms. This is what you get when the official materials aren't available.
- **Verified conformance** needs the ASD-STE100 issue that applies to your work, its dictionary (approved meanings and parts of speech), the rules for technical names and technical verbs, and any approved terminology for your project. A plain-language rewrite, a sentence-length check, or a model's self-check doesn't prove compliance, so Claude never claims compliance from those alone and never invents rule numbers.

The standard and its dictionary are copyrighted and aren't included. Get them through the official site, and give them to Claude (or tell it where they are) when you need a conformance check.

**When it runs:** when you ask for STE or ASD-STE100: to write, rewrite, or review technical documentation in Simplified Technical English, or to write a prompt that does. It doesn't apply STE to unrelated writing. To try it: "rewrite this maintenance procedure in Simplified Technical English".

**What it produces:** for a prompt request, a filled-in constraint prompt for your task. For drafting and rewriting, the text, plus short notes on anything that still needs checking. For a review, a list of findings with location, problem, suggested revision, and the rule reference where it's verified, with confirmed violations kept apart from editorial suggestions and from items that need the dictionary or a domain expert. A conformance assessment also says which issue of the standard and which materials were used.

**What's inside:**

```
asd-ste100/
├── SKILL.md                              basis, drafting defaults, prompt template, review and reporting rules
└── agents/
    └── openai.yaml                       optional display metadata for OpenAI Codex (Claude ignores it)
```

---

## How skills work

A skill is a folder with a `SKILL.md` file and, optionally, extra reference files. `SKILL.md` starts with a short header that holds the skill's `name` and `description`.

Claude loads skills in three stages:

1. **Description.** Claude always sees each installed skill's description. It uses the description to decide whether a skill fits your request. That's why you don't need to call a skill by name.
2. **`SKILL.md`.** When a skill fits, Claude reads its `SKILL.md`, which holds the main instructions.
3. **References.** Claude opens a file in `references/` only when the task needs that depth. The detailed material doesn't take up context until it's needed.

### Where to install

| Location | Scope |
|---|---|
| `~/.claude/skills/<skill-name>/` | You, in every project (personal) |
| `<your-project>/.claude/skills/<skill-name>/` | Everyone working in that repo (commit it to share with your team) |

To install a skill for one project only, copy its folder into that project's `.claude/skills/` instead of your home directory.

### Checking that a skill is installed

In Claude Code, ask *"What skills do you have available?"* The installed skills should appear in the list. You can also trigger one on purpose. For example, paste a large class and ask "is this over-engineered?"

### Updating

```sh
cd agent-skills
git pull
cp -r design-patterns react-anti-patterns bug-report-issue-author feature-request-issue-author peter-pr-review step-breakdown deepen-prompt asd-ste100 ~/.claude/skills/
```

On Windows, run the same `Copy-Item` command from the quick start.

### Uninstalling

Delete the skill's folder from `~/.claude/skills/` (or from the project's `.claude/skills/`).

---

## Repository layout

- Each top-level folder holds one skill's source, readable on GitHub.
- Each `*.skill` file is the same folder zipped for upload to Claude.ai or Claude Desktop.

If you edit a folder, rebuild its archive so the two stay in sync. Run one of these from the repo root, replacing `design-patterns` with the skill you changed.

**macOS / Linux** (needs `zip`)

```sh
rm -f design-patterns.skill && zip -r design-patterns.skill design-patterns
```

**Windows (PowerShell)**

```powershell
$skill = 'design-patterns'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Remove-Item "$skill.skill" -ErrorAction SilentlyContinue
[IO.Compression.ZipFile]::CreateFromDirectory("$PWD\$skill", "$PWD\$skill.skill", 'Optimal', $true)
```

The PowerShell command uses .NET's zip library instead of `Compress-Archive`. Older versions of `Compress-Archive` write Windows-style `\` separators into the archive, which can break the upload. Use PowerShell 7 or later: Windows PowerShell 5.1 has the same problem.
