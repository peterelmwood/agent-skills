# agent-skills

Skills for Claude that help it write, review, and refactor code well.

## Quick start (Claude Code)

**macOS / Linux**

```sh
git clone https://github.com/peterelmwood/agent-skills.git
mkdir -p ~/.claude/skills
cp -r agent-skills/design-patterns agent-skills/react-anti-patterns ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/peterelmwood/agent-skills.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse agent-skills\design-patterns, agent-skills\react-anti-patterns "$HOME\.claude\skills\"
```

Then start a new Claude Code session. Both skills are now installed. You don't have to call them: Claude uses one when your request matches it.

## Quick start (Claude.ai / Claude Desktop)

1. Download `design-patterns.skill` and/or `react-anti-patterns.skill` from this repo.
2. In Claude, open **Settings → Capabilities → Skills** and upload the file.

The `.skill` files are zip archives of the folders, packaged for upload.

---

## The skills

| Skill | Use it for |
|---|---|
| [`design-patterns`](design-patterns/SKILL.md) | Deciding how code or a database schema should be structured, and when a pattern isn't worth adding. |
| [`react-anti-patterns`](react-anti-patterns/SKILL.md) | Spotting common React mistakes and picking the right fix for each one. |

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
cp -r design-patterns react-anti-patterns ~/.claude/skills/
```

On Windows, run the same `Copy-Item` command from the quick start.

### Uninstalling

Delete the skill's folder from `~/.claude/skills/` (or from the project's `.claude/skills/`).

---

## Repository layout

- `design-patterns/` and `react-anti-patterns/` hold the skill source, readable on GitHub.
- `*.skill` files are the same folders zipped for upload to Claude.ai or Claude Desktop.

If you edit a folder, rebuild its archive so the two stay in sync. Run this from the repo root:

```sh
rm design-patterns.skill && zip -r design-patterns.skill design-patterns
```
