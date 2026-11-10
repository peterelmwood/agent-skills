# Data Model: Add Step Breakdown Skill

There is no runtime data store. The entities are the files this feature adds and the plan
file format the skill produces, which `check_plan.py` parses.

## Skill package

| Field | Value / rule |
|---|---|
| Folder | `step-breakdown/` at the repo root |
| Files | `SKILL.md`, `scripts/check_plan.py` (exactly these two) |
| Frontmatter | `name: step-breakdown`; `description` with triggers and exclusions |
| Archive | `step-breakdown.skill`, zip, root `step-breakdown/`, `/` separators, same bytes as the folder |

## Step plan file (`<project-slug>-steps.md`)

Sections in order: title, header (Goal, Created/Steps/Active effort/Elapsed, Assumptions),
How to use this, Progress (phase checkboxes), phases, Decisions, Open questions, Progress log.

### Step

| Field | Rule | Checker behaviour |
|---|---|---|
| Line | `- [ ] **<ID>. <Verb + object>** · ~N min · Needs: <IDs or —>` | Parsed by `STEP` regex; indentation allowed for children |
| ID | `\d+[a-z]?`, unique, never renumbered | Duplicate → error |
| Needs | Comma-separated exact IDs, or `—` | Unknown ID → error; range or text → error |
| Estimate | `~N min` or `~N h` (ranges allowed; high end used) | Missing → warning; > 30 min without `exception` → warning |
| Done-check | Following line containing `Done when` | Missing → error |
| State | `[ ]` / `[x]` | Ticked with unticked Needs → warning |

### Gate (a step whose title contains `GATE`)

`active 0 min` plus `elapsed ~…`; no estimate check; not listed as available; listed under
"Waiting on" once its own Needs are satisfied.

### Parent

Marked `parent — done when …`; children are `<ID>a`, `<ID>b`, … Parent with no children →
error; children without the parent marker → warning; parent ticked with unticked children →
error; all children ticked but parent not → warning. A parent satisfies a `Needs` when it is
ticked or all its children are.

### Placeholder

Contains `🔭` (`🔭 Expand after <ID>`); no estimate; excluded from active effort.

### Parallel line

`> ⇉ **Can run in parallel: a, b, c** — …`. Every listed ID must exist and none may depend
on another, directly or transitively → error otherwise. `⚠` notes a shared-resource conflict.

## State transitions

`step: unticked → ticked` (done-check true). `gate: unticked → ticked` (outside event
happened). `step → parent` (split; ID kept, children added). `🔭 placeholder → parent`
(expanded after its trigger step is done). Plan-level: an update appends a Progress log row
and may add Open questions entries; nothing is deleted or renumbered.
