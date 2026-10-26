# Code Complete (McConnell) — Construction Practices

Read this for questions at the level of a single routine, variable, conditional, or loop; for defensive programming; and for the overarching question of managing complexity. McConnell's organizing theme: **software's primary technical imperative is managing complexity**, and most construction decisions should be judged by whether they reduce the amount a reader must hold in mind at once.

## Contents
1. Managing complexity
2. Design heuristics (the toolbox)
3. Routine design
4. Variables
5. Conditionals and loops
6. Defensive programming
7. Pseudocode Programming Process
8. Comments and self-documenting code
9. Code tuning: when and how
10. Size, scale, and proportion

---

## 1. Managing complexity

Two kinds of complexity: *essential* (the problem is hard) and *accidental* (we made it hard). Construction practices exist to minimize accidental complexity and to partition essential complexity into pieces a human can reason about one at a time.

Principles that follow:
- **Minimize what a reader needs to know.** Information hiding (Parnas): each module hides a design decision likely to change. Ask "what secret does this module keep?" If the answer is "none," it's not a module, it's a folder.
- **Keep coupling loose, cohesion tight.** Good coupling is small (few parameters), visible (obvious, not through globals), and flexible (easy to change). Functional cohesion (a routine does one operation) is the goal; coincidental cohesion (unrelated stuff in one place) is the failure.
- **Form consistent abstractions.** A class should present a consistent level of abstraction in its interface. Don't mix `AddEmployee()` with `NextItemInList()` — one is domain level, the other is data-structure level.
- **Design for change.** Identify the areas likely to change (business rules, hardware dependencies, I/O, non-standard language features, difficult design areas) and isolate them behind interfaces. Don't isolate everything; most code won't change.

## 2. Design heuristics (the toolbox)

McConnell's "design is a heuristic process" list, usable as a checklist when a design isn't coming together:

- Find real-world objects (and their attributes, operations, relationships)
- Form consistent abstractions
- Encapsulate implementation details
- Inherit when it simplifies (and only then — prefer containment)
- Hide secrets (information hiding)
- Identify areas likely to change
- Keep coupling loose
- Look for common design patterns
- Aim for strong cohesion
- Build hierarchies
- Formalize class contracts (preconditions/postconditions/invariants)
- Assign responsibilities
- Design for test
- Avoid failure (think about how it breaks)
- Choose binding time consciously (compile, load, run)
- Make central points of control
- Consider using brute force (simple and correct beats clever and wrong)
- Draw a diagram
- Keep your design modular

Try several of these on a stuck design; the ones that produce insight tell you what kind of problem you have.

## 3. Routine design

**Reasons to create a routine** (beyond "reduce duplication"): reduce complexity by hiding detail; introduce an intermediate, understandable abstraction; avoid duplicate code; support subclassing with fewer overrides; hide sequences; hide pointer/handle operations; improve portability; simplify complicated boolean tests; improve performance in one place. Even a one-line routine can be justified if it names a concept.

**Cohesion of a routine** — strongest to weakest: functional (one thing), sequential (steps share data, in order), communicational (same data, different operations), temporal (done at the same time, e.g., `Startup()`), procedural (same order, unrelated), logical (selected by a flag — a smell), coincidental (no relationship). Aim for functional; accept sequential/communicational; refactor the rest.

**Naming routines**: describe everything the routine does (if that's a long name, it does too much); avoid meaningless verbs (`Handle`, `Perform`, `Process`, `DealWith`); use a strong verb + object for procedures (`PrintReport`), a description of the return value for functions (`CurrentPenColor`); establish conventions for common operations (`GetX`/`SetX`, `IsX`).

**Parameters**: put input first, modified middle, output last (or follow language convention); keep them under seven; pass the whole object if the routine uses most of it, individual fields if it uses one or two; don't use parameters as working variables; document assumptions about them (units, ranges, null-ability); check them (see §6).

**Return values**: have a single return point unless multiple returns clearly improve readability (guard clauses do); never return a reference to local data; set the return value in every path.

**Macros/inline**: avoid in languages with real functions.

## 4. Variables

- **Declare close to first use**, in the smallest scope possible. Initialize at declaration. In C#, prefer `var` or explicit types consistently; in Python, don't pre-declare.
- **Live time and span**: *span* is lines between references; *live time* is lines between first and last reference. Minimize both. A variable live for 100 lines is 100 lines a reader must track. Group related statements; extract routines to shrink live time.
- **Single purpose.** Don't reuse `temp` for two meanings. Don't let a variable have hidden meanings (`pageCount == -1` means "error" — use a separate flag or an exception).
- **Naming**: the name should fully and accurately describe what the variable represents (`trainVelocity`, not `v`; `numberOfPeopleOnTheUsOlympicTeam` is too long — `olympicTeamSize`). Length 10–16 characters is the sweet spot. Qualifiers (`Total`, `Count`, `Max`, `Index`) go at the end. Boolean names should sound true/false (`done`, `error`, `found`, `success`), and avoid negatives (`notFound` → `found`).
- **Fundamental types**: integers (watch overflow, integer division); floats (never compare for equality; beware accumulating error; use decimal types for money); strings (avoid magic strings; be careful with length and encoding); booleans (use them to document and simplify tests); enums (use them for named sets, define a "none"/"unknown" first element, use them to make the compiler check ranges); named constants (replace magic numbers); arrays (0-based vs 1-based confusion; consider a collection class).
- **Globals**: avoid. If forced, hide behind access routines, give them a clear naming convention, and document them. Most "need a global" cases are "need to pass this through three layers" and the fix is a parameter object or a scoped context, not a global.

## 5. Conditionals and loops

**Conditionals**:
- Put the normal case in the `if`, the unusual in the `else`; or use guard clauses to dispatch the unusual cases early and leave the normal case unindented.
- Order cases by frequency when it aids readability (and sometimes performance).
- Use `switch` for simple, finite discriminations; order alphabetically or by frequency; always handle the default (make it an error if the set is supposed to be exhaustive); don't rely on fall-through.
- Encapsulate complex booleans in a well-named function or variable: `if (IsEligibleForDiscount(customer))`, not three `&&`-joined comparisons.
- Use positive forms (`if (found)` not `if (!notFound)`).
- Use table-driven methods when a conditional is really a lookup (tax rates by bracket, message by error code, behavior by state). Tables beat long `if-else` chains for readability and changeability. Three kinds: direct access (index into array), indexed (lookup table maps key to index), stair-step (ranges).

**Loops**:
- Choose the loop type that matches the structure: `for` when the count is known, `while` when it's not, `foreach` for collections (prefer it — no index bugs).
- Keep loop body short enough to see at once; nest loops at most three deep; if deeper, extract the inner loop to a routine.
- One way in, one way out. Avoid `break`/`continue` tangles; if a loop needs several `break`s, it needs a `while` with a clear condition.
- Use meaningful loop variable names in nested loops (`row`/`column`, not `i`/`j`).
- Put housekeeping at the ends; don't modify the loop index inside the body; don't use the loop index after the loop.
- Avoid empty loops and loops that do their work in the condition.

**Deep nesting** is the enemy. Fixes: re-test part of the condition; convert to `if-else-if`; convert to `switch`; extract the nested part to a routine; use guard clauses; use polymorphism; use a table; rewrite.

**Structured programming**: sequence, selection, iteration. `goto` and its relatives (early exits from deeply nested code) are acceptable only when the structured version is clearly worse.

## 6. Defensive programming

The idea: a routine shouldn't be broken by bad data, even when that data comes from a sibling routine you wrote.

- **Protect against invalid input.** Check parameters at the boundary. Decide what to do with bad data: return a neutral value, substitute the closest legal value, return the previous result, log it, return an error code, throw, shut down. The choice depends on *correctness vs. robustness*: a pacemaker should shut down rather than guess; a video game should guess rather than crash.
- **Assertions** for things that should *never* be false — programmer errors, not runtime conditions. Use them for preconditions, postconditions, and invariants; don't put executable code in them; never use them to validate user input.
- **Error handling** for things that *can* legitimately go wrong at runtime. Use exceptions (or results) for exceptional conditions, not for normal control flow. Throw at the right abstraction level (a `Customer` class shouldn't throw `IOException`). Include all information needed to diagnose in the message. Don't catch and swallow.
- **Barricades**: designate some routines as boundary ("the barricade") that sanitize all input; everything inside the barricade can assume clean data and use assertions. This is Clean Architecture's boundary applied to data validation. Convert external data to the internal type at the barricade.
- **Debugging aids**: build them in early (checkers, dumps, invariant verifiers); plan to remove or disable them in production (compile-time flags, config); leave assertions on in production if the cost is acceptable — a crash is better than silent corruption.
- **How much is too much**: defensive code is code, and it has bugs too. Decide which parts of the system really need it. Validate at boundaries, trust internally.

## 7. Pseudocode Programming Process (PPP)

A construction method for a routine, useful when you're not sure how to start:

1. Check prerequisites: is the routine's job clear? Is its name chosen? How will you test it?
2. Write the routine in high-level, English-like pseudocode — intent, not implementation. Each line should be something you'd say to a colleague, not a language statement.
3. Refine the pseudocode until each line is one or two statements' worth of code.
4. Turn the pseudocode into comments and write the code under each.
5. Review: does each pseudocode line still make sense as a comment? Is it at the right level? If so, the routine is documented and structured. If a comment now looks silly beside its code, delete it.
6. Compile, test, clean up.

The payoff: the design happens in the easy-to-change medium (prose), and the comments come for free. It's also an early detector of routines that do too much — pseudocode that runs long is a signal to split.

## 8. Comments and self-documenting code

The best documentation is the code itself: good names, clear structure, consistent abstraction, named constants, enumerated types. Comments are a secondary layer.

Kinds of comments: repeat of the code (bad), explanation of the code (usually means the code should be rewritten), marker (temporary), summary of the code (good — a paragraph of code summarized in a line), description of intent (good — what the code is *trying* to do), information that can't be expressed in code (good — units, references, design rationale, legal).

Comment at the level of *intent*. Comment the *why*, especially for anything that looks wrong but isn't ("negative step because the list is sorted descending"). Document surprises. Avoid abbreviations. Keep comments near the code they describe and keep them maintained — an incorrect comment is worse than none.

Avoid endline comments on single statements (they encourage trivial content). Comment paragraphs of code, not every line. Comment data declarations (units, ranges, flags). Comment control structures (what the loop does, not that it's a loop). Routine headers: purpose, parameters, return, assumptions, limitations, global effects, source of algorithm if non-obvious.

## 9. Code tuning: when and how

- **Correctness first.** Then measure. The "Pareto" observation holds: most of the time is in a small fraction of the code, and your guess about which fraction is usually wrong.
- Efficiency comes from design (algorithms, data structures, I/O strategy) far more than from code-level tricks. A better algorithm beats any amount of micro-optimization.
- Code tuning (loop unrolling, strength reduction, caching, inlining) is a last resort, after profiling, and must be re-measured — the compiler often already does it, and tuned code is harder to read.
- Don't trade correctness or clarity for unmeasured speed. If a tuned version is kept, comment why and record the measurement.

## 10. Size, scale, and proportion

McConnell's data on project size: communication paths grow quadratically with team size; defects per line and effort per line grow with project size; the mix of activities shifts (small project = mostly construction; large project = mostly design, integration, and documentation).

The practical implication for a design conversation: **choose structure proportionate to size and lifespan.** A 500-line utility and a 500,000-line product need different amounts of ceremony. Patterns, layers, and formal interfaces are investments with a payback period; on a small or short-lived codebase they don't pay back. When unsure, build the simple version and add structure when a concrete change demands it — that's cheaper than building structure you remove later, and much cheaper than maintaining structure nobody needed.
