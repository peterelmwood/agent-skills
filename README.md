# agent-skills

Skills for Claude that help it write, review, and refactor code well, and write GitHub issues engineers can act on.

## Quick start (Claude Code)

**macOS / Linux**

```sh
git clone https://github.com/peterelmwood/agent-skills.git
mkdir -p ~/.claude/skills
cd agent-skills
cp -r design-patterns react-anti-patterns bug-report-issue-author feature-request-issue-author ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/peterelmwood/agent-skills.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
cd agent-skills
Copy-Item -Recurse -Force design-patterns, react-anti-patterns, bug-report-issue-author, feature-request-issue-author "$HOME\.claude\skills\"
```

Then start a new Claude Code session. All four skills are now installed. You don't have to call them: Claude uses one when your request matches it.

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

Each skill is also published as a single-file gist ([bug report](https://gist.github.com/peterelmwood/96292c79fc4a4d79ccf4d56c028d9982), [feature request](https://gist.github.com/peterelmwood/0e4d46e228da29c54bc17036b8dbb135)). The gists contain only `SKILL.md`. This repo also includes the example issue each skill uses as its model.

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
cp -r design-patterns react-anti-patterns bug-report-issue-author feature-request-issue-author ~/.claude/skills/
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
