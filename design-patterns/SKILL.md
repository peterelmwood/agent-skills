---
name: design-patterns
description: "Apply design patterns and engineering principles with judgment, not reflex — GoF patterns, Fowler's refactorings and smells, Clean Code/Clean Architecture, Code Complete, TDD and XP, Lean, SICP abstraction, Google engineering practice, SRE reliability patterns, and Karwin's SQL Antipatterns. Use whenever the user is designing, writing, reviewing, or refactoring code or a schema and the real question is 'how should this be structured,' even if they never say 'pattern.' Triggers: refactor this, this class is too big, how should I structure, what pattern fits, is this over-engineered, code review, reduce coupling, make this testable, clean up this method, design the module/API boundary, migrations (e.g. VB.NET to C#) where structure can improve, schema/table design, ugly or slow queries, choosing between patterns. Also use it when the right answer is 'don't use a pattern here' — that judgment is the point."
---

# Design Patterns, Applied Intelligently

The goal is not to know patterns. The goal is to recognize the *forces* in a piece of code — the pressures that make it hard to change, test, or understand — and respond with the smallest structure that relieves them. A pattern is a named, pre-tested response to a recurring set of forces. Applying one where the forces aren't present adds indirection and nothing else.

So the skill has two halves, and the second matters as much as the first:

1. Know the catalog well enough to spot when a pattern fits.
2. Know the costs well enough to decline when it doesn't.

## The core loop

Follow this sequence whether you're writing new code, reviewing, or refactoring. Skipping to "which pattern?" is the most common mistake.

### 1. Name the forces before naming a solution

Ask what is actually hard here. Typical forces:

- **Variation**: something will have multiple implementations (payment providers, file formats, pricing rules). Which axis varies, and how often?
- **Coupling**: a change in one place forces a change somewhere far away.
- **Construction**: creating an object is complicated, conditional, or has to be deferred.
- **Lifecycle / state**: behavior changes depending on what happened earlier.
- **Cross-cutting concerns**: logging, caching, auth, retries smeared across unrelated code.
- **Testability**: you can't test X without standing up Y, Z, and a database.
- **Comprehension**: a reader can't hold the thing in their head (McConnell's whole book is about this one).

If you can't name a force, you don't need a pattern. Write the simple version.

### 2. Identify the smell, if there is one

Smells are the symptoms; patterns and refactorings are the treatments. Fowler's catalog is the diagnostic vocabulary — Long Method, Feature Envy, Shotgun Surgery, Primitive Obsession, Speculative Generality, and so on. Naming the smell precisely usually narrows the fix to one or two moves. See `references/refactoring-smells.md`.

A particularly important smell to watch for in your own output is **Speculative Generality**: abstraction added for a future that hasn't arrived. Patterns are a frequent carrier of it.

### 3. Choose the smallest intervention

Rank candidate responses from cheapest to most structural, and stop at the first that resolves the force:

1. **Rename / extract / inline** (Fowler's basic moves). A well-named method often *is* the fix.
2. **Language feature.** Modern languages absorb many GoF patterns outright: first-class functions replace Strategy and Command in most cases; `yield`/iterators replace Iterator; records and pattern matching replace a lot of Visitor; DI containers replace hand-rolled Factories; `IDisposable`/context managers handle resource lifecycle. Reach for the pattern only when the language feature can't carry the weight (see the "modern substitutes" column in `references/gof-patterns.md`).
3. **A principle applied locally** — SOLID, Tell-Don't-Ask, Law of Demeter — without introducing a named structure.
4. **A GoF pattern**, chosen by force, not by familiarity. Verify with the "forces → pattern" map in `references/gof-patterns.md`.
5. **An architectural boundary** (Clean Architecture layers, ports & adapters, bounded contexts). Expensive; justify it with a concrete change you expect to need to make.

### 4. Make the change safely

- If tests exist, run them before and after. If they don't and the change is non-trivial, write a characterization test first (Beck/Fowler): capture current behavior, *then* refactor.
- Refactor in small, behavior-preserving steps. Never mix a refactor with a feature change in one step; the diff becomes unreviewable and the test signal becomes ambiguous.
- Prefer TDD's red → green → refactor rhythm for new behavior: the test tells you the interface you *wish* you had, which is better design input than guessing.

### 5. Check the result against the simplicity bar

Before finishing, ask Beck's four rules of simple design, in priority order: passes the tests, reveals intention, no duplication, fewest elements. If your pattern added elements without improving intention-revealing or removing duplication, back it out.

## Judgment calls: when to decline a pattern

Say this explicitly to the user when it applies. They asked for intelligent use; "no" is sometimes the intelligent answer.

- **Only one implementation exists and none is planned.** Don't add an interface + factory for a single concrete class. Add the seam when the second implementation arrives — that's a cheap refactor (Extract Interface), and you'll know its real shape by then.
- **The variation is already handled by a language feature.** A `Func<T,R>` parameter beats a one-method Strategy interface. A `switch` on a sealed record hierarchy beats Visitor for a closed, stable set of types.
- **The code is small and local.** A 40-line script does not need Clean Architecture. McConnell's threshold: structure should scale with the size and lifespan of the thing.
- **The abstraction would hide the thing a reader needs to see.** Indirection has a reading cost. If every call traverses three interfaces to reach one line of logic, the pattern is working against comprehension.
- **It's a framework-shaped problem.** If the user is on ASP.NET Core, Django, Spring, etc., the framework already provides the DI, middleware (Chain of Responsibility), ORM (Repository/Unit of Work), and observer (events) machinery. Use the framework's version; don't duplicate it.

When you do decline, offer the "trigger" that would change the answer: "if a second provider shows up, extract an `IPaymentGateway` then."

## Patterns that are usually worth it

Some structures pay for themselves almost immediately and shouldn't be held back by the above caution:

- **Dependency injection via constructor** — testability is a force that's nearly always present.
- **Value objects over primitives** for domain concepts with rules (Money, Email, DateRange). Fixes Primitive Obsession and centralizes validation.
- **Pure core, impure shell** (functional core / imperative shell; SICP's data abstraction; Clean Architecture's dependency rule). Keep business logic free of I/O so it can be tested without mocks.
- **Explicit state machines** when behavior depends on more than two states and transitions have rules. Boolean flags multiply; an enum + transition table or State pattern doesn't.
- **Null Object / Optional** at boundaries to eliminate null-check cascades.
- **Guard clauses** over nested conditionals (Fowler: Replace Nested Conditional with Guard Clauses).

## Working across the reference material

Load only the reference you need. Each is self-contained and organized by *problem*, not by book chapter, so you can jump to the force you've identified.

| You're facing… | Read |
|---|---|
| Object creation, structure, or behavior that needs a named OO structure; deciding between similar patterns (Strategy vs State, Decorator vs Proxy, Factory Method vs Abstract Factory) | `references/gof-patterns.md` |
| Existing code with a smell; deciding which refactoring move to make and in what order | `references/refactoring-smells.md` |
| Naming, function size, class responsibilities, SOLID, module/layer boundaries, where to put a dependency | `references/clean-code-architecture.md` |
| Routine design, defensive programming, variable scope, control flow, complexity management, when to comment | `references/code-complete.md` |
| Writing tests first, characterization tests, test smells, how to make legacy code testable, XP practices, flow and waste in the dev process | `references/process-and-testing.md` |
| Abstraction barriers, closures, higher-order composition, data vs. procedure, when "functional" beats "object" | `references/sicp-abstraction.md` |
| Schema design, keys, nulls, trees in SQL, query antipatterns, ORM pitfalls | `references/sql-antipatterns.md` |
| Code review culture, readability, dependency management at scale, reliability patterns (retries, backoff, circuit breakers, SLOs) | `references/google-and-sre.md` |

## Output conventions

When recommending a change:

- **Lead with the diagnosis** (force + smell), then the proposed structure, then the code. The user should be able to disagree with the diagnosis before reading 80 lines of refactored code.
- **Name the pattern once** and explain it in terms of the user's domain, not the textbook's (say "a `PaymentGateway` interface with `Worldpay` and `Stripe` implementations," not "the Strategy pattern lets you define a family of algorithms…").
- **Show before/after** for refactors, with the change isolated. For larger refactors, list the ordered sequence of safe steps rather than presenting the end state as one leap.
- **State the trade-off** you accepted: what got more complex, what got simpler, and what you'd revisit if circumstances change.
- **Match the language's idiom.** C# has records, pattern matching, `IEnumerable`, DI built into the host; Python has first-class functions, protocols, dataclasses, context managers; SQL has window functions and CTEs. Pattern implementations copied from a Java-era textbook into these languages look wrong and usually are.
- Keep the simple-design rules in view: if the "after" has more moving parts than the "before" and no concrete force justifies them, say so and offer the simpler version too.
