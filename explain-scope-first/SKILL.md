---
name: explain-scope-first
description: Before making requested changes, explain your understanding of the request and identify what will stay untouched. Use when the user asks for a scope check, a readback before editing, or explicit boundaries around a change. Does not apply to questions or analysis that require no changes.
---

# Explain scope first

Make your interpretation visible before acting so the user can spot a misunderstanding or an unwanted expansion of scope.

## Before changing anything

Read the request and relevant context. Read-only inspection is allowed when needed to understand the target and its dependencies; keep it focused. Before the first edit or other mutation, send a short, user-visible scope statement containing:

- **What I understand:** Restate the intended outcome in your own words, including the target and any constraints that materially affect the result. Describe what success looks like rather than repeating the request word for word.
- **What I will change:** Name the smallest set of areas or artifacts you expect to modify. Distinguish confirmed targets from tentative ones.
- **What I will not touch:** List concrete neighboring areas that could plausibly be affected but are outside the request. Use names the user can recognize, such as existing wording, calculations, account settings, other pages, public interfaces, or unrelated files. Avoid generic promises like “nothing unrelated.” If no meaningful adjacent area exists, say so briefly rather than inventing exclusions.

Keep this proportional to the task: a few sentences or short bullets usually suffice. Surface consequential assumptions. Do not claim that an uninspected dependency is guaranteed to remain unaffected.

## Then proceed within that scope

The readback is an explanation, not an automatic approval gate. Continue with already authorized work unless the user requested confirmation or an unresolved ambiguity would materially change the outcome. In those cases, ask the smallest necessary question and wait before dependent changes.

Treat the stated exclusions as commitments. If inspection reveals that completing the request would require touching an excluded area, stop before changing that area, explain the dependency, and resolve the boundary with the user. Do not quietly broaden the assignment or omit necessary work while claiming completion.

If the user corrects your interpretation, update the scope statement before proceeding. For a multi-step task, repeat it only when the intended outcome or boundaries materially change.

## When finished

Briefly report the result, how you checked it, and any remaining limitation or agreed change to the boundaries. Do not claim untouched areas were verified unless you actually checked them.
