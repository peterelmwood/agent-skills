# Testing & Process: TDD, XP (Beck), Lean (Poppendieck)

Read this when the question is how to make code testable, how to test-drive a design, how to safely change code you don't have tests for, or how team process affects design quality.

## Contents
1. TDD: the rhythm and why it produces better design
2. Test design: what good tests look like
3. Test smells
4. Making untested code testable
5. XP practices that bear on design
6. Simple design: Beck's four rules
7. Lean: waste, flow, and deferring decisions
8. How process shapes patterns

---

## 1. TDD: the rhythm and why it produces better design

**Red → Green → Refactor.**
1. Write a test for the next small increment of behavior. Run it; it fails (red). If it passes, you either already have the behavior or the test is wrong.
2. Write the *minimum* code to make it pass (green). Fake it if necessary — return the constant. Triangulate with a second test to force generalization.
3. Refactor: remove duplication between test and code, improve names, restructure. Tests stay green throughout.

Why this helps design, not just correctness:
- **You design the interface from the caller's side first.** The test is the first client. Awkward tests reveal awkward APIs before anyone else has to use them.
- **It forces dependency injection.** If a class is hard to instantiate in a test, you discover the hidden dependency immediately and fix it by making it explicit.
- **It keeps classes small.** A test that needs 40 lines of setup is telling you the class under test does too much.
- **It produces a regression suite as a side effect**, which makes the refactoring step safe — and refactoring is where patterns get introduced *in response to real duplication*, rather than speculatively.

Granularity: steps should be as small as you need to stay confident, and as large as you can get away with. When stuck, take smaller steps. When fluent, take bigger ones.

**The two strategies for the green step**: *fake it* (return a constant, then generalize), *obvious implementation* (if you know the answer, type it), *triangulation* (add a second example that the fake fails, forcing the real logic). Mix freely.

## 2. Test design: what good tests look like

- **Arrange / Act / Assert** (or Given/When/Then). One logical assertion per test — one *concept*, which might be several `Assert` calls about the same result. If a test needs two unrelated asserts, it's two tests.
- **Independent.** Tests shouldn't depend on order or on each other. Shared mutable fixtures are the usual culprit.
- **Fast.** A unit test suite should run in seconds. Anything touching a database, network, or file system is an integration test; keep those separate and fewer.
- **Readable as specification.** The test name states the behavior: `Withdraw_WhenBalanceInsufficient_ThrowsInsufficientFunds`, `test_order_total_includes_tax`. Someone should understand the class from the test names alone.
- **Deterministic.** No `DateTime.Now`, no random, no thread timing. Inject a clock; seed the random; use synchronous test doubles.
- **Test behavior, not implementation.** Assert on outputs and observable state changes, not on which private methods were called. Over-mocking produces tests that break on every refactor and catch no bugs.

**The test pyramid**: many unit tests (fast, isolated), fewer integration tests (real DB, real HTTP against a test server), fewest end-to-end tests (full system, slow, flaky). Invert it and you get a slow, fragile suite nobody trusts. Google's version — small/medium/large, with hermeticity requirements — makes the same point.

**Test doubles** (Meszaros's vocabulary, which Fowler popularized): *dummy* (passed but never used), *stub* (returns canned answers), *spy* (records calls for later assertion), *mock* (pre-programmed with expectations; fails if they're not met), *fake* (working implementation with a shortcut — in-memory repository). Prefer stubs and fakes for state-based testing; use mocks sparingly, for interactions that *are* the behavior (did we send the email?).

## 3. Test smells

- **Fragile tests** — break on refactors that don't change behavior. Cause: testing implementation (mock verification, private method access). Fix: assert on outcomes.
- **Obscure tests** — you can't tell what's being tested. Cause: too much setup, magic values, helper methods that hide the point. Fix: extract named builders/factories for fixtures; keep the relevant values visible in the test.
- **Slow tests** — people stop running them. Cause: I/O in unit tests. Fix: inject and fake the I/O.
- **Erratic / flaky tests** — pass sometimes. Cause: time, randomness, shared state, async races. Fix: control the source of nondeterminism.
- **Conditional logic in tests** — `if`/loops in the test body. Each branch is an untested path in your test. Fix: separate tests, or parameterized tests with a data table.
- **Test code duplication** — the same 15 lines of setup in 30 tests. Fix: builder pattern for fixtures (`new OrderBuilder().WithItem(...).Build()`), which is one of the places Builder is unambiguously worth it.
- **Mystery guest** — the test depends on a file or DB row defined elsewhere. Fix: make the data visible in or near the test.
- **Assertion roulette** — many asserts with no messages; when one fails you can't tell which. Fix: one concept per test, or descriptive assertion messages.

## 4. Making untested code testable

This is the daily reality more often than greenfield TDD. The sequence (Feathers's *Working Effectively with Legacy Code*, which Fowler and Beck both lean on):

1. **Identify the change point** — where does the behavior you need to change live?
2. **Find a test point** — somewhere nearby you can observe behavior.
3. **Break dependencies** just enough to get the code into a test harness. The common seams:
   - *Parameterize constructor* — add a constructor overload taking the dependency; keep the old one delegating with the default.
   - *Extract interface* — from the concrete dependency, so a fake can stand in.
   - *Extract and override* — pull the troublesome call into a virtual method; subclass in the test and override it.
   - *Introduce static setter / ambient context* — least preferred, but sometimes the only way to swap a global.
   - *Adapt parameter* — wrap an untestable framework type (`HttpContext`) in an interface you own.
   - *Sprout method / sprout class* — put *new* behavior in a new, tested method or class; call it from the untested old code. You don't test the old code, but the new code is clean.
   - *Wrap method* — rename the old method, create a new one with the old name that calls the renamed method plus the new behavior.
4. **Write characterization tests** — call the code with representative inputs, assert whatever it currently returns (even if it's wrong). These pin current behavior so you can refactor. Later, when you understand the code, convert them into real specification tests or delete them.
5. **Make the change**, test-driven where possible.
6. **Refactor** now that there's a net.

The key insight: the seam you introduce to get a test in place is usually the exact place a design pattern *should* have been. "I had to extract an interface to fake the payment call" and "the payment gateway should be behind an abstraction" are the same observation.

## 5. XP practices that bear on design

- **Pair programming / continuous review** — design decisions get a second opinion in real time. Catches speculative generality early ("do we actually need that interface?").
- **Continuous integration** — small, frequent integration keeps refactorings small and reversible. Big-bang merges make large refactorings terrifying, so people don't do them, so design rots.
- **Collective ownership** — anyone can refactor anything. Prevents "that's Bob's module, don't touch it" from freezing bad structure in place.
- **Coding standards** — consistency reduces reading cost; arguments about style are waste.
- **Sustainable pace** — tired people write tangled code and skip the refactor step.
- **Incremental design** — design happens continuously, driven by the current need, not up front. The system's design should be the best for *today's* requirements, improved daily. This is the philosophical basis for "don't add the pattern until the force is present."
- **YAGNI** (You Aren't Gonna Need It) — the XP slogan for not building speculative features or structure. Paired with "the cost of change can be kept low" — if refactoring is cheap (because tests + CI + small steps), you don't need to predict the future, you can respond to it.
- **Metaphor / shared vocabulary** — the team's names for things should match the domain. (DDD's "ubiquitous language" is the fuller development of this.)

## 6. Simple design: Beck's four rules

In priority order. A design is simple when it:

1. **Passes all the tests.** Correctness is non-negotiable and comes first.
2. **Reveals intention.** A reader can tell what it does and why. Names, structure, and the absence of noise.
3. **Contains no duplication.** Of knowledge, not just text. Each fact or rule lives in one place.
4. **Has the fewest elements.** Classes, methods, interfaces, parameters, lines — if removing one doesn't hurt 1–3, remove it.

Rules 2 and 3 are the ones that *introduce* structure (and patterns); rule 4 is the one that *removes* speculative structure. When evaluating whether to apply a pattern, check: does it serve rule 2 or 3? If not, rule 4 says no.

## 7. Lean: waste, flow, and deferring decisions

The Poppendiecks map lean manufacturing to software. Several ideas directly affect how to think about design patterns and architecture:

**The seven wastes of software**: partially done work (unintegrated branches, untested code); extra features (YAGNI again); relearning (lost knowledge — fix with docs and tests as executable specs); handoffs (information lost at each one); task switching; delays (waiting for approvals, builds, reviews); defects (the later found, the costlier).

Speculative architecture is *extra features* and *partially done work* at once — structure built for a need that hasn't materialized, and that must be maintained in the meantime.

**Decide as late as possible.** Keep options open until the last responsible moment — the point at which *not* deciding eliminates an option. Design implication: build the abstraction (the seam) only when the second implementation arrives, because by then you know what varies. Deciding early locks in a guess. The exception: decisions that are expensive to reverse (database choice, public API shape, language). Those deserve up-front thought; most others don't.

**Deliver as fast as possible.** Small batches, fast feedback. Design implication: structure that lets you ship a thin vertical slice (one use case end-to-end) early is more valuable than structure that requires all layers to be complete before anything works.

**Build integrity in.** *Perceived integrity* — the system does what users need, coherently. *Conceptual integrity* — the system's concepts fit together; it feels designed by one mind. Patterns and shared vocabulary serve conceptual integrity; inconsistent use of patterns (three different repository styles in one codebase) destroys it.

**See the whole.** Optimizing one component's elegance at the system's expense is a failure. A perfectly layered module nobody else can integrate with is waste.

**Amplify learning.** Short iterations, prototypes, set-based design (try two or three approaches briefly before committing) — especially for high-uncertainty design decisions.

## 8. How process shapes patterns

Pulling the threads together:

- TDD makes you *discover* patterns at the refactor step, when duplication is real, rather than *impose* them at design time, when it's imagined.
- Legacy-code seams and design patterns are the same thing seen from different sides; introducing a seam for testability is often the right moment to introduce the pattern properly.
- Lean's "last responsible moment" and XP's YAGNI are the process-level justification for the skill's core rule: name the force, then respond; don't respond to a force that isn't there.
- Cheap change (tests, CI, small steps) is what makes deferring structure *safe*. Without it, people add speculative structure out of fear. If a team is over-engineering, the fix may be in their testing and integration practice, not their pattern knowledge.
