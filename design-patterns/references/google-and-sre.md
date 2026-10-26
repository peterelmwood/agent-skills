# Engineering at Scale: Software Engineering at Google & The SRE Workbook

Read this for questions about code review practice, readability and consistency across a codebase, dependency and version management, testing at scale, and reliability patterns (retries, backoff, circuit breakers, SLOs, graceful degradation) that affect how you structure code that talks to other systems.

## Contents
1. The core distinction: programming vs. software engineering
2. Code review as a design practice
3. Readability, style, and consistency
4. Testing at scale (small/medium/large; hermeticity; flakiness)
5. Dependency management and the diamond problem
6. Large-scale changes and deprecation
7. SRE: SLOs and error budgets as design inputs
8. Reliability patterns in code
9. Release engineering and configuration
10. Where this meets design patterns

---

## 1. Programming vs. software engineering

Google's framing: software engineering is programming integrated over time. The questions that distinguish it: *how long will this code live?* *how many people will touch it?* *what will it cost to change?* Everything else in the book — review, testing, build systems, deprecation policy — follows from taking those questions seriously.

Three principles:
- **Time** — Hyrum's Law: with enough users, every observable behavior of your system will be depended upon by somebody, regardless of what the contract says. Design implication: the interface you expose *is* the behavior people can observe, not the behavior you documented. Narrow interfaces and sealed implementations reduce the surface area of accidental dependency. This is the strongest practical argument for information hiding.
- **Scale** — practices must work as the team and codebase grow. "Everyone knows Bob owns that module" doesn't scale; "that module has an OWNERS file and a design doc" does.
- **Trade-offs** — decisions should be made with evidence and stated reasoning, not by authority or precedent. "We've always done it this way" is not a reason. Write down *why*.

## 2. Code review as a design practice

Code review at Google is the primary mechanism for maintaining design quality across a large codebase. What makes it work:

- **Small changes.** Reviews of a few hundred lines get real scrutiny; reviews of thousands get rubber-stamped. Design implication: structure work so each change is independently reviewable — which usually means separating refactors from feature changes (Fowler's two hats, enforced by process).
- **Review for design first.** Is this the right approach? Does it belong here? Does it duplicate something? Then correctness, then tests, then style. Style comments should be rare because the style guide and formatter handle them.
- **Readability approval.** A separate approval from someone certified in the language's idioms. Enforces consistency across teams and spreads knowledge of language-specific best practices — including which GoF patterns the language has absorbed into features.
- **Ownership.** Every directory has owners who must approve. Keeps domain knowledge in the loop.
- **Comments are about the code, not the author.** Blameless, specific, actionable. Suggest, don't demand, unless it's a correctness issue.

When using this skill to review code, follow this order: design/approach → correctness → tests → naming/readability → style. Leading with style comments buries the important feedback.

## 3. Readability, style, and consistency

- **Optimize for the reader, not the writer.** Code is read far more than written. A clever one-liner costs every future reader; a clear three-liner costs the writer once.
- **Be consistent.** When there are two acceptable ways, the codebase should pick one. Consistency lets readers pattern-match and lets tools work. This is why mixing three repository styles or two error-handling conventions in one codebase is a real defect even if each is fine in isolation.
- **Rules should be enforceable by tools where possible.** Formatters eliminate style debates; linters catch mechanical issues; this frees human review for design.
- **Avoid error-prone and surprising constructs**, even when the language allows them. The style guide's job is to say "we don't use that here" for features with bad risk/benefit.
- **Concede to practicality when necessary.** Rules have exceptions; document them.

Design implication for patterns: a team should agree on *how* a given pattern looks in their codebase (how repositories are named and shaped, how DI is configured, how errors are modeled) and then apply it uniformly. Half the value of a pattern is the shared vocabulary; that value is lost if each instance is bespoke.

## 4. Testing at scale

Google replaces "unit/integration/e2e" with **size** classes, which are about resource constraints and determinism rather than scope:

- **Small**: single process, single thread, no I/O, no sleeping. Must be fast and deterministic.
- **Medium**: single machine; may use localhost network, DB, multiple threads.
- **Large**: anything else — multi-machine, external services.

Target mix: ~80% small, ~15% medium, ~5% large (the pyramid again). Small tests are the ones that enable refactoring; large tests are the ones that catch integration bugs. Both needed; proportions matter.

**Hermetic tests**: a test should contain everything it needs and be unaffected by the environment. No shared databases, no real clocks, no network. Fakes for external services are the key enabler, and a *fake* (a working lightweight implementation) is preferred over a *mock* (expectation-based) because fakes test behavior and survive refactors. Teams that own a service should ship a fake of it.

**Test scope**: unit tests should test the public API of a unit, not its internals. Changing internals shouldn't break tests ("test behavior, not implementation" — the same lesson as Beck). If you need to test a private method, it's a sign a class is hiding inside the one you're testing — extract it.

**Flaky tests** are treated as bugs with high priority: a suite with 1% flakiness run 1,000 times a day produces 10 false alarms, and people stop trusting it. Causes and fixes match the test-smells list in `process-and-testing.md`.

**Test doubles and seams**: Google's guidance is to prefer *real implementations* when they're fast, deterministic, and simple to construct; then fakes; then stubs; mocks last. This is a useful corrective to over-mocking.

**Larger testing**: integration with real dependencies in staging; A/B diffs of outputs between versions; probers and canaries in production. These are the tests that validate the architecture, not the code.

## 5. Dependency management and the diamond problem

- **Semantic versioning is a promise about compatibility**, and it's a weak one (Hyrum's Law again). Major version bumps are where the ecosystem breaks.
- **The diamond dependency problem**: A depends on B and C; B needs D v1, C needs D v2; no single version of D works. Solutions: (a) one version policy — the whole repo uses one version of each dependency (monorepo discipline); (b) shading/vendoring; (c) refusing to depend on things with unstable APIs.
- **Prefer the smallest dependency surface.** Every external dependency is a maintenance commitment and a security surface. Wrap third-party libraries behind an interface you own (Adapter) when the library is likely to be swapped or has a wide API you only partly use.
- **Live at head**: continuously update to the latest version of dependencies in small steps rather than batching updates into painful upgrades. Requires good tests.

## 6. Large-scale changes and deprecation

- **Large-scale changes** (LSCs) — a refactor touching hundreds or thousands of files — are made feasible by: tooling (automated refactoring, codemods), a culture that permits touching code you don't own, and splitting the change into many small independently-reviewable commits (shard by directory).
- **Deprecation is a process, not an announcement.** Steps: provide the replacement; migrate callers (often with LSC tooling); add warnings/linter errors for new uses; remove when usage is zero. "Advisory deprecation" (please stop) rarely works; "compulsory deprecation" (with a deadline and owner) does.
- **Design for deprecation**: narrow interfaces, clear ownership, and no reach-through dependencies make things removable. A class that 400 callers reach into via a static method is nearly undeletable. This is the long-term cost of Singletons, globals, and leaky abstractions.

## 7. SRE: SLOs and error budgets as design inputs

- **SLI** (indicator): a measurement — request latency, error rate, availability. **SLO** (objective): the target for an SLI (99.9% of requests under 300 ms). **SLA**: the SLO with consequences, usually contractual.
- **Error budget**: 100% minus the SLO is how much unreliability you're *allowed*. If the SLO is 99.9%, you may be down ~43 minutes a month. Spend the budget on releases and experiments; when it's exhausted, freeze features and work on reliability.
- **Why this matters for design**: the SLO tells you *how much* reliability engineering a component needs. A 99% internal reporting tool doesn't need circuit breakers and multi-region failover; a 99.99% payment path does. Over-engineering reliability has the same costs as over-engineering abstraction. Pick the SLO first; design to it.
- **Toil**: manual, repetitive, automatable, tactical work with no lasting value. SRE's target: keep it under 50% of time. Design implication: anything an operator does by hand repeatedly should become code — a runbook that's a script, a dashboard that's checked in.

## 8. Reliability patterns in code

These are the "design patterns" of distributed systems. They govern how code that calls other systems should be structured.

- **Timeouts** — every external call has one. No exceptions. Choose based on the SLO of the caller, not the typical latency of the callee.
- **Retries with exponential backoff and jitter** — retry transient failures (timeouts, 503s, connection resets), not permanent ones (400s, auth failures). Back off exponentially so a struggling dependency isn't hammered; add jitter so retries from many clients don't synchronize into a thundering herd. Cap the total retry budget (e.g., retries are at most 10% of requests) so retries don't amplify an outage.
- **Idempotency** — retries are only safe if the operation can be repeated without side effects. Design write operations to be idempotent (idempotency keys; "set to X" rather than "increment"). Payment APIs are the canonical case: a retried charge must not double-charge.
- **Circuit breaker** — after N failures, stop calling the dependency for a cooling-off period and fail fast; probe occasionally to see if it's back. Protects both the caller (no waiting on a dead service) and the callee (time to recover). A State pattern instance: Closed → Open → Half-Open.
- **Bulkheads** — isolate resources (thread pools, connection pools) per dependency so one slow dependency can't exhaust everything.
- **Load shedding and graceful degradation** — when overloaded, drop low-priority work or return a degraded response (cached data, a default) rather than failing entirely. Requires the code to *know* which work is low-priority — a design decision.
- **Health checks and readiness** — distinguish "alive" from "ready to serve." Don't route traffic to an instance that's still warming up.
- **Canary and progressive rollout** — release to a small fraction, watch the SLIs, expand. Requires feature flags or routing control in the code.
- **Observability as a design requirement** — structured logs, metrics (RED: rate, errors, duration; USE: utilization, saturation, errors), traces with propagated context. If you can't tell *why* it's slow, you can't fix it. Build the instrumentation in; don't bolt it on.

In .NET these are provided by `Polly` (retry, circuit breaker, bulkhead, timeout policies) and `IHttpClientFactory` integration; in Python by `tenacity`, `pybreaker`, and the like. Use the library; don't hand-roll a circuit breaker.

## 9. Release engineering and configuration

- **Hermetic builds**: same inputs → same output, regardless of machine. Pin everything.
- **Configuration is code**: version it, review it, test it. Config errors cause a large share of outages.
- **Separate config from code in deployment, but not in review.** The Twelve-Factor "config in the environment" rule is about deployment; the config's *shape* and validation still belong in reviewed code.
- **Feature flags** decouple deploy from release. They also accumulate — schedule their removal when the feature is fully rolled out, or they become permanent conditionals nobody understands.
- **Rollback must be fast and routine.** A design that can't roll back (irreversible migrations, no backward compatibility) forces forward-fixes under pressure. Expand/contract migrations (add new column → dual-write → migrate readers → remove old) keep rollback possible.

## 10. Where this meets design patterns

- **Hyrum's Law** is why interfaces should be minimal and implementations sealed: every exposed detail becomes a dependency. It's the scale-level argument for Facade, Information Hiding, and ISP.
- **Fakes over mocks** aligns with testing behavior, which aligns with designs that have clear boundaries (Repository, Gateway) worth faking.
- **One-version policy and live-at-head** reward wrapping external dependencies behind your own interface (Adapter), because the upgrade pain is contained to one place.
- **Deprecation cost** is the long-term bill for globals, Singletons, and reach-through access; it's why the dependency rule and narrow seams pay off years later.
- **SLOs set the reliability budget**, which should set how much resilience machinery (retries, breakers, bulkheads) a component carries — the reliability analogue of "name the force before applying the pattern."
- **Circuit breaker is State**, **middleware is Chain of Responsibility**, **retry policies are Decorators** around a call. Recognizing them as such helps compose them (order matters: timeout inside retry inside circuit breaker, typically) and helps spot when a hand-rolled version should be a library.
