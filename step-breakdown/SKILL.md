---
name: step-breakdown
description: Break a project, goal, or effort into a numbered checklist of small steps (each ~30 minutes or less, each with a concrete done-check), with explicit dependencies, waiting gates, and parallel markers, saved as one persistent markdown checklist the user can return to for weeks. Use this whenever the user asks to break down, chunk, decompose, or make a step-by-step plan / roadmap / checklist / action plan for a project, launch, migration, move, renovation, job search, study plan, or any multi-week effort — even if they don't say "steps" or "checklist" (e.g. "how do I even start on X", "turn this into tasks I can tick off", "I keep stalling on this project"). Also use it when the user comes back to update an existing *-steps.md plan. Not for a single quick task or for code-level implementation plans for an immediate coding session.
---

# Step Breakdown

Turn a project or effort into an ordered list of small, checkable steps, and save it as a single living checklist the user can come back to over weeks.

The user's original request, which this skill encodes:

> Break this project or effort into as many small steps as you can, in order. Each step should take under 30 min and have a clear done-check. The steps should be numbered and clear indication should be used when steps (one or multiple) can be performed in parallel. Put them in one artifact with checkboxes I can come back to for weeks.

## What the checklist must deliver

The user opens this file on many different days, often tired or distracted, and wants a reliable answer to **"what can I do right now?"** Everything below serves that one question:

- **Dependencies are the single source of truth.** Every step lists `Needs:`. A step is available when everything in its `Needs` is ticked — nothing else. File order is just a suggested reading order; numbers are stable IDs, not a schedule.
- **Waiting is a blocker, not a note.** Anything outside the user's control (an approval, a delivery, a reply, paint drying) is a **gate**: its own checkbox that is ticked only when the outside event happens. Steps that truly need that outcome list the gate in `Needs`, so ticking "Submit permit application" can never make "Start construction" look available.
- **Done-checks remove ambiguity.** Each step says what observable fact makes it finished.
- **Small steps lower the activation energy.** But only real, useful actions — padding and speculative detail make the file harder to trust.

## Process

### 1. Check for an existing plan

Before creating anything, look for an existing `<project-slug>-steps.md` (or any `*-steps.md` the user points to). If one exists, you are **updating**, not creating — go to "Updating an existing plan" below. Never overwrite a file that has ticked boxes or log entries.

### 2. Understand the effort

Use whatever context exists: the conversation, files, a repo, linked docs. If the project is too vague to break down meaningfully, ask at most 2–3 short questions (goal, finish line, hard constraints such as deadline, budget, people). If it's reasonably clear, proceed and write your assumptions into the header so the user can correct them.

### 3. Decompose — smallest *useful* actions

- **Target ~30 minutes or less** of focused work per step, starting with a concrete verb (Draft, Email, Book, Measure, Decide, Compare). If something genuinely can't be split meaningfully (moving day itself, a 2-hour exam, a pour that must be continuous), keep it whole and mark it `⚠ exception: <why>`. An honest 2-hour step beats a fake 30-minute one.
- **Detail near-term work fully; keep later phases coarse.** Steps in the first phase or two (and anything whose shape is already clear) get full detail. Work that depends on an unresolved decision or on research results stays as a single placeholder step marked `🔭 Expand after <ID>` — inventing 15 speculative sub-steps that the decision may invalidate is worse than useless. When the triggering step is done, expand the placeholder by splitting it (see "Splitting a step").
- **Include the unglamorous steps** people forget: gathering info/accounts/credentials, decisions, scheduling, buying supplies, telling stakeholders, testing, backing up, cleaning up, closing out.
- **Don't pad.** No trivia ("Open laptop"), no steps that exist only to raise the count. The step count is whatever the project needs.

### 4. Handle unknowns honestly

- **Never invent specifics.** If a contact, path, cost, URL, requirement, or quantity is unknown, write a visible placeholder: `[TBD: landlord's email]`, `[TBD: permit fee]`. A plausible-looking invented phone number is a trap the user will walk into weeks later.
- **Make research bounded.** When finding something out could take an unpredictable amount of time, write a timeboxed step with a concrete deliverable and an explicit "is that enough?" decision:
  `Research permit requirements (timebox 25 min)` → Done when: notes list what's known + open questions, **and** you've decided "enough to proceed" or added a follow-up research step.
- **Decisions are steps.** "Decide: X vs Y" with a done-check like "Choice and one-line reason recorded under Decisions". Steps that depend on the outcome list the decision in `Needs`.

### 5. Write a done-check for every step

An observable fact someone could verify, not a feeling. Good: "Confirmation email received", "`npm test` passes", "3 quotes saved in /quotes". Bad: "Budget is good", "Understand the topic".

The last step(s) must close the loop on the whole effort: add a final step like "Confirm finish line" whose done-check restates the Goal line, so ticking everything really means the project is done.

### 6. Dependencies, gates, and parallel markers

- **`Needs:` on every step and gate**, listing exact IDs separated by commas (`Needs: 4, 7`), or `—` if it can start immediately. No ranges, no "previous step" implied by position. Only list *real* prerequisites — over-constraining hides parallelism; under-constraining lets people start things too early.
- **Gates** look like steps but are marked `⏳ GATE`, carry `active 0 min` plus an elapsed estimate (`elapsed ~2–4 weeks`), and their done-check is the outside event happening ("Approval letter received"), never the user's request for it.
- **Parallel markers summarize `Needs`; they never override it.** When several steps are mutually independent, put a one-line block above them:
  `> ⇉ **Can run in parallel: 8, 9, 10** — none depends on another.`
  Every ID in a parallel line must be independent of every other ID in it (directly or indirectly). If steps are independent by dependency but compete for the same person, tool, vehicle, or workspace, say so on the marker: `⚠ 8 and 9 both need the van — any order, not simultaneously.`
- **Numbering.** On creation, number steps 1…N in suggested order across the whole file (never restart per phase), so "step 27" means one thing forever. Group into phases with a milestone line once there are more than ~15 steps.

### 7. Splitting a step

When a step turns out to be too big (now or later), it becomes a **parent**:

- Keep the parent's ID, checkbox, and done-check. Mark it `parent — done when <children> are ticked` and remove its own time estimate (its time lives in the children).
- Add children indented underneath as `14a`, `14b`, `14c`, each with its own estimate, `Needs:` and done-check. The first child usually inherits the parent's `Needs`.
- The parent is ticked only when all its required children are ticked. Anything that said `Needs: 14` stays correct — it still waits for the whole of 14.
- Brand-new steps that aren't children of anything get the next unused number (N+1, N+2…) and can be placed wherever they read best; their `Needs` determine when they're available.

### 8. Consistency check before saving

Before you save (or re-save), verify:

1. Every ID is unique.
2. Every ID in every `Needs` exists.
3. No dependency cycles.
4. Every parallel line lists only mutually independent IDs, and any shared-resource conflict is flagged.
5. Every step and gate has a done-check; every parent has children; every `⚠ exception` has a reason.
6. The final steps' done-checks together satisfy the Goal line.
7. At least one step is available right now (otherwise the user can't start).

If Python is available, run the bundled checker, fix anything it reports, and re-run until clean:

```bash
python <this-skill-dir>/scripts/check_plan.py <path-to-steps.md>
```

It checks items 1–5 and 7 and prints the total active effort and the "available now" list. Item 6 needs your judgment. If Python isn't available, do the checks by reading the file carefully.

## Output: one checklist file

In Claude Code, save to the current project directory (or wherever the user indicates) as `<project-slug>-steps.md` and give the full path. In environments with artifacts, produce one markdown artifact. Use GitHub-style checkboxes (`- [ ]`) so it renders as tickable boxes in VS Code, Obsidian, GitHub, etc.

Structure:

```markdown
# <Project name> — Step Plan

**Goal / finish line:** <one sentence: what "done" looks like for the whole effort>
**Created:** <YYYY-MM-DD> · **Steps:** <N> (+ <G> gates) · **Active effort:** ~<hours> h (approximate; excludes waiting) · **Expected elapsed time:** ~<weeks>, mostly driven by <the longest gates>
**Assumptions:** <bullets, or "none">

## How to use this
- A step is **available** when everything in its `Needs` is ticked. Pick any available step; file order is only a suggestion.
- Tick `[x]` only when the done-check is true. Tick a ⏳ GATE only when the outside event has actually happened.
- ⇉ lines show steps you can do in any order or at the same time (watch for ⚠ shared-resource notes).
- Step too big? Split it into 14a, 14b… under it; 14 is ticked when its children are. Never renumber.
- Log dates and notes in the Progress log at the bottom.

## Progress
- [ ] Phase 1: <name> (steps 1–9)
- [ ] Phase 2: <name> (steps 10–24)

---

## Phase 1 — <name>
*Milestone: <what's true when this phase is complete>*

- [ ] **1. <Verb + object>** · ~15 min · Needs: —
  ✅ Done when: <observable check>

…

---

## Decisions
- <Decision step ID>: <choice + reason, filled in when decided>

## Open questions
- <unresolved items, each with the ID it blocks; also conflicting reports, see below>

## Progress log
| Date | Steps done | Notes |
|------|-----------|-------|
|      |           |       |
```

Optional per-step lines when useful: `📎` for a link/file/contact (or a `[TBD: …]` placeholder).

## Worked example

This excerpt (a garage-to-office conversion) shows the difficult cases: a bounded research step, a decision, an approval gate, parallel steps with a shared-resource conflict, a coarse placeholder, and a split step mid-project.

```markdown
## Phase 1 — Plan & approvals
*Milestone: permit approved and all quotes in hand*

- [x] **1. Measure the garage and sketch a floor plan** · ~25 min · Needs: —
  ✅ Done when: Sketch with dimensions saved as `garage-plan.jpg`

- [x] **2. Research permit requirements (timebox 25 min)** · ~25 min · Needs: —
  ✅ Done when: Notes list required documents + fee or open questions, and you've marked "enough to apply" or added a follow-up step
  📎 Permit office: [TBD: city permit office phone]

- [ ] **3. Decide: DIY electrical vs licensed electrician** · ~20 min · Needs: 1
  ✅ Done when: Choice + one-line reason recorded under Decisions

- [x] **4. Submit permit application** · ~30 min · Needs: 1, 2
  ✅ Done when: Application reference number saved here: [TBD: ref #]

- [ ] **5. ⏳ GATE: Permit approved** · active 0 min · elapsed ~2–4 weeks · Needs: 4
  ✅ Done when: Approval letter received (not when the application is sent)

> ⇉ **Can run in parallel: 6, 7, 8** — none depends on another. ⚠ 6 and 7 are both business-hours phone calls; 8 can be done any evening.

- [ ] **6. Request 3 insulation quotes** · ~30 min · Needs: 1
  ✅ Done when: 3 written quotes saved in `/quotes`
- [ ] **7. Request 2 flooring quotes** · ~25 min · Needs: 1
  ✅ Done when: 2 written quotes saved in `/quotes`
- [ ] **8. Shortlist 3 desks under [TBD: budget]** · ~20 min · Needs: —
  ✅ Done when: 3 links + prices listed under 📎

## Phase 2 — Build
- [ ] **9. Electrical work** · 🔭 Expand after 3 · Needs: 3, 5
  ✅ Done when: Replaced by concrete child steps once the decision in 3 is made

- [ ] **10. Install insulation** · parent — done when 10a–10c are ticked · Needs: 5, 6
  ✅ Done when: Walls insulated and photographed for the inspector
  - [ ] **10a. Buy batts and vapour barrier** · ~30 min · Needs: 6
    ✅ Done when: Materials delivered to the garage
  - [ ] **10b. Insulate all four walls** · ~3 h ⚠ exception: one continuous job; stopping midway leaves the barrier open · Needs: 10a, 5
    ✅ Done when: No exposed stud bays remain
  - [ ] **10c. Photograph each wall for the inspector** · ~10 min · Needs: 10b
    ✅ Done when: 4+ photos saved in `/inspection`

- [ ] **11. Book drywall installer** · ~15 min · Needs: 10
  ✅ Done when: Date confirmed by email
```

Read it the way the user will. Step 4 is ticked, but 10b is still blocked by gate 5. Steps 3, 6, 7 and 8 are available now. Step 11's `Needs: 10` stays valid even though 10 was split.

## After writing

Reply briefly in chat with:
- the file path, the number of steps and gates, and the approximate active effort
- the steps available right now (3–6 of them, from the checker's "available now" list)
- the longest gates or waits, so the user can start them early
- any assumptions or `[TBD]` placeholders worth filling in soon

Don't paste the whole checklist into chat if it's saved as a file.

## Updating an existing plan

When the user returns ("I finished 1–12", "step 20 turned out bigger", "the permit came through"):

- **Edit the file in place, and preserve what's there.** Keep every ticked box, note, decision, `📎` line and log row. Only change what the user's update requires.
- **Apply the update.** Tick what's done, tick gates whose events happened, split steps with the parent/child rules, expand `🔭` placeholders whose trigger is now done, and add new steps with the next unused numbers.
- **Flag conflicts instead of silently resolving them.** The user might report something done that the file says is blocked ("I installed insulation" while gate 5 is unticked), or say something that contradicts a recorded decision or an earlier log entry. In those cases, don't silently overwrite either version. Tick what is clearly true, add an entry under **Open questions** that names the conflict and the IDs involved, and mention it in your reply.
- **Log the update.** Append a row to the Progress log with today's date.
- **Re-run the consistency check**, then reply with what changed and what's available now.
