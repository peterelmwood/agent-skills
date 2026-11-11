---
name: deepen-prompt
description: "Make a task or prompt deeper, not bigger, by asking how a top professional in that field would actually approach it. Answers four questions: what the expert would do that wasn't asked for, the rawest source material they'd start from instead of an already-digested summary, the specific named methods and tools they'd use, and what independent evidence (other than Claude or the user) would show the result is right. Then it rewrites the prompt to ask for exactly that. Use whenever someone wants to go deeper, be more rigorous, approach something 'like a pro/expert/specialist would', make an answer verifiable, asks 'what am I missing in how I framed this', or says they keep getting surface-level answers, even if they never say 'deeper'. Not for copy-editing, shortening, or formatting prompts, not for expanding something into a longer deliverable, and not for actually carrying out research (do the task instead)."
---

# Deepen a prompt

Users who reach for this skill have noticed that asking for "better" gets them *more*: more sections, more options, more caveats. What they want is what an expert would bring: a sharper framing, better inputs, real methods, and a way to know the answer is right. The rewritten prompt should be about the same size as the original and noticeably harder to answer badly.

## The loop

### 1. Pick the expert, and say who you picked
Name the field and role on the first line ("Assuming: tenant-rights attorney reviewing a lease"). Everything that follows depends on this choice, and stating it lets the user correct you cheaply. If the task is too vague to pick a field (e.g. "help me decide"), ask one clarifying question and stop. A guessed domain produces confident advice about the wrong problem.

### 2. What would they do that the user isn't asking for?
Look for the move a strong practitioner makes before answering: checking a premise, reframing the question, splitting it, asking for a baseline, or refusing to answer from the given inputs. Be specific to this field and this task. "Think carefully" or "consult an expert" tells the user nothing.

### 3. What's the rawest material?
Every summary, screenshot, dashboard, or news article has already made choices about what matters. Name the primary source the expert would want instead (the logs, the ordinance text, the dataset, the original contract, the object itself). Contrast it with what the user has. If the raw source is out of reach, name it anyway and give the best substitute the user can actually get.

### 4. Which methods and tools?
Name them concretely: `git bisect`, `EXPLAIN ANALYZE`, a difference-in-differences comparison, a pin-type moisture meter, a title search. Named tools are what turn advice into something the user can act on. If you don't know the specialist toolset for a niche field, say so and suggest how to find out (a trade association, a conservator, the standard's issuing body). An invented tool name does more harm than an honest gap.

### 5. What, other than you or the user, shows it's right?
Name an independent check and how to get it: a test that fails before and passes after, a measurement, the primary source itself, a reproducible benchmark, a licensed or credentialed reviewer, or a real-world outcome to watch for. Asking another model, or asking the user whether it looks right, is not independent. Both share the blind spots you're trying to escape.

### 6. Rewrite. Deeper, not bigger.
Before writing, list the deliverables the original prompt asks for. Write the rewrite so it:
- swaps the digested inputs for the raw ones (or asks the user to supply them),
- names the methods to use,
- builds the independent check into what "done" means.

Then compare deliverables again. If the rewrite asks for anything new, cut it. Depth comes from inputs, method, and verification, not from more outputs.

### 7. Stop and offer
End with the rewritten prompt in a fenced block and offer to run it. The user should see the reframing before any work starts, because a wrong expert framing is cheap to fix now and expensive later.

## Output format

Assuming: <field / role>

**1. What a top professional would do that you aren't asking for**
**2. Rawest material to start from** (vs. what you have now)
**3. Methods and tools**
**4. What would show it's right** (independent of me and you)

**Rewritten prompt**
```text
<prompt>
```

Want me to run this?

## Example

User: "deeper version of this: 'Here's a Grafana screenshot of our nightly ETL runtime — it went from 22 to 31 minutes in October. Tell me why it got slower.'"

Assuming: data engineer debugging a pipeline performance regression.

1. They'd pin down *when* it changed and line that up with deploys, data volume, and infrastructure changes before forming any theory. A screenshot invites guessing at causes.
2. Per-run job logs with per-stage timings, row counts per stage, query plans from before and after, and the deploy/config history for the window. Not the aggregated chart.
3. Stage-level timing diff; `EXPLAIN (ANALYZE, BUFFERS)` on the slowest stage, before vs. after; `git log` / `git bisect` over the deploys in the window; a check of whether input row counts grew.
4. Re-run the suspected stage on a September snapshot with current code, and on current data with September code. The regression should follow whichever one is the cause.

```text
Using the attached per-run logs for Sept 15–Oct 31 (per-stage timings and row counts), the deploy history for that window, and EXPLAIN (ANALYZE, BUFFERS) output for the slowest stage from one run before and one after the change: identify the stage where runtime increased, determine whether the cause is data volume, a code/config change, or infrastructure, and propose a confirming experiment (old code on new data or new data on old code) that would show the cause.
```
