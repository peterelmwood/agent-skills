# SICP — Abstraction, Composition, and the Functional Lens

Read this when the question is about *how to abstract* — data abstraction, abstraction barriers, higher-order composition, closures — or when a functional structure might serve better than an object-oriented pattern. SICP's ideas predate the GoF and explain *why* many patterns work; several GoF patterns are OO encodings of techniques SICP presents directly.

## Contents
1. The three mechanisms: primitives, combination, abstraction
2. Procedural abstraction and higher-order procedures
3. Data abstraction and abstraction barriers
4. Closures and the closure property
5. Message passing, data-directed programming, and dispatch
6. State, assignment, and why mutability is expensive
7. Streams and lazy evaluation
8. Mapping SICP ideas to GoF patterns
9. When to choose the functional structure

---

## 1. The three mechanisms

Every language gives you *primitive expressions*, *means of combination* (build compound things from simpler ones), and *means of abstraction* (name compound things and treat them as units). Design is mostly the choice of what to abstract and where to draw the lines.

The guiding question SICP keeps asking: **what is the interface, and what can change behind it without the client noticing?** That's the same question information hiding (Parnas), the dependency rule (Martin), and "program to an interface" (GoF) are asking.

## 2. Procedural abstraction and higher-order procedures

A procedure (function) abstracts a *pattern of computation*. Once named, callers can use it without knowing how it works — the "black box" abstraction. `square(x)` hides whether it's `x*x` or `exp(2*log(x))`.

**Higher-order procedures** — functions that take or return functions — abstract *patterns of patterns*. The classic SICP sequence: `sum_integers`, `sum_cubes`, `sum_pi_series` all share a shape; `sum(term, a, next, b)` captures it once. Then `sum` itself is a special case of `accumulate(combiner, null_value, term, a, next, b)`.

Design lessons:
- When several functions share a skeleton with varying steps, extract the skeleton as a higher-order function and pass the steps. **This is Template Method and Strategy without classes.**
- `map`, `filter`, `reduce`/`fold` are the universal higher-order vocabulary. Most loops over collections are one of these or a composition. Expressing them that way reveals intent and removes index bugs. In C#: LINQ. In Python: comprehensions, `map`/`filter`, `functools.reduce`, itertools.
- Functions returning functions (`make_adder(n)`, `compose(f, g)`) let you build specialized behavior at runtime without a class per variant. **A factory for Strategy is often just a function returning a lambda.**

## 3. Data abstraction and abstraction barriers

A compound data object should be defined by its *operations*, not its *representation*. The rational-number example: `make_rat`, `numer`, `denom` are the interface; whether a rational is a pair, a struct, or a normalized pair is hidden. Everything above the barrier uses only the constructors and selectors.

**Abstraction barriers**: horizontal lines in the program. Code above a barrier uses only the operations the barrier exposes. The representation below can change — add normalization, change storage, cache — and nothing above knows.

Consequences for design:
- **Represent domain concepts as types with operations**, not as raw primitives or dictionaries passed around. This is Fowler's Replace Primitive with Object and Martin's value objects, with a clearer argument for *why*: the barrier lets you change representation.
- **Constructors and selectors are the minimal interface.** Anything else is a convenience that should be implemented in terms of them (so it stays correct when the representation changes).
- **"Data" is whatever satisfies the contract.** SICP shows a pair implemented purely as a procedure (`cons` returns a closure that dispatches on `car`/`cdr`). The lesson: the distinction between data and procedure is a design choice, not a fact. An object with one method is a function; a function with captured state is an object.
- **Where to put a barrier** is the same question as where to put a Clean Architecture boundary or a module interface. The answer: at the points where you want to be free to change representation.

Violations to watch for: code that reaches through a barrier (`customer.address.lines[0]`); representations leaking into signatures (a method returning the raw internal list); clients that depend on an unstated invariant of the representation.

## 4. Closures and the closure property

Two meanings, both important.

**Closure property of combination**: when combining things produces something of the same type, you can nest arbitrarily (pairs of pairs; lists of lists; Composite). This is what makes hierarchical structures possible and is the formal reason **Composite** works: operations defined on the interface apply uniformly at every level.

**Closures as captured environment**: a procedure that remembers the bindings in scope when it was created. `make_account(balance)` returns `withdraw`/`deposit` procedures that share and mutate `balance`. That's an object — state plus behavior — with no class declaration.

Design lessons:
- Closures implement **Command** (captured parameters + deferred execution), **Strategy** (a configured policy), **Memento** (capture state), and simple **Observer** callbacks with less ceremony than classes. Use the class when you need multiple methods on the same state, a type for the compiler to check, or the ability to enumerate/inspect; otherwise a closure is fine.
- Closures over *mutable* state are objects and inherit objects' problems (see §6). Closures over *immutable* captured values are safe to share, cache, and reason about.

## 5. Message passing, data-directed programming, and dispatch

SICP presents three ways to make operations work across multiple representations (the complex-number example: rectangular vs. polar):

1. **Tagged data + explicit dispatch** — each operation checks the tag and branches. Simple; but every new type touches every operation (the Switch Statements smell).
2. **Data-directed programming** — a table keyed by `(operation, type)` holding the implementation; `apply_generic` looks it up. Adding a type = adding a column; adding an operation = adding a row. Neither touches existing code. **This is a cleaner formulation of what Visitor and Strategy registries do**, and it generalizes to multiple dispatch directly.
3. **Message passing** — each data object is a procedure that takes an operation name and dispatches internally. Adding a type is trivial; adding an operation touches every type. **This is ordinary OO polymorphism.**

The design insight SICP draws out — and that the GoF chapter on Visitor restates — is the **expression problem**: you can make it easy to add types or easy to add operations, not both, without changing the language's facilities. Choose based on which axis actually grows:

| Grows more | Prefer |
|---|---|
| Types (new payment methods, new shapes) | Message passing / OO polymorphism / methods on the type |
| Operations (new exporters, new analyses over a fixed AST) | Data-directed table / Visitor / pattern matching over sealed types |
| Both, frequently | Reconsider the decomposition; or accept a table and some ceremony |

Modern languages give data-directed programming cheaply: a `Dictionary<(Type, string), Func<...>>`, Python's `functools.singledispatch`, type-class–style patterns. Exhaustive pattern matching over a sealed hierarchy gives the operation-centric view with compiler support.

## 6. State, assignment, and why mutability is expensive

SICP introduces assignment (`set!`) late and deliberately, and spends a chapter on what it costs:

- With assignment, the **substitution model breaks**: you can no longer understand an expression by replacing names with values, because the value depends on *when*. You need the environment model — time enters the program.
- **Referential transparency is lost**: two calls to the same function with the same arguments can differ. Equality becomes subtle (same object? same contents? same at what time?).
- **Aliasing**: two names for the same mutable object means a change through one is visible through the other, often surprisingly. This is the root of a huge class of bugs.
- **Order of evaluation matters**, so concurrency becomes hard: the whole chapter on serializers and deadlock exists because state exists.

But state also *buys* something: modularity. An object with local state can model a thing in the world that changes (an account, a queue, a random-number generator) without threading its history through every call. The design principle that emerges: **confine state; make most of the program stateless functions over immutable data; put the mutable parts behind narrow interfaces.**

This is the intellectual basis for:
- Functional core / imperative shell (business logic as pure functions, I/O and state at the edges).
- Immutable value objects (Fowler, Martin, DDD).
- "Prefer composition of pure functions" as the first response to variation, before Strategy classes.
- Command–Query Separation: a function either computes (stateless, cacheable, testable) or changes state (do it in one obvious place).

## 7. Streams and lazy evaluation

A stream is a sequence whose tail is computed on demand. SICP uses it to show that **infinite sequences, pipelines, and "generate then filter" formulations become expressible** when evaluation is deferred — `integers` as an infinite stream; primes via a sieve over it; signal processing as stream transformations.

Design lessons:
- **Pipelines over loops.** `source |> filter |> map |> take(n)` describes *what*, not *how*, and composes. LINQ with deferred execution, Python generators and itertools, Java streams, Rx observables are all this.
- **Separate generation from consumption.** A generator that yields items decouples "how to produce" from "how many to consume" — the **Iterator** pattern's real payoff, delivered by `yield`.
- **Laziness as a design tool**: deferring expensive computation until needed (virtual **Proxy**), memoizing (`memo_proc` in SICP is exactly a lazy singleton), avoiding building intermediate collections.
- **The cost**: laziness makes timing and side effects harder to reason about (the same lesson as §6 from the other side). Keep lazy pipelines pure; do side effects at the terminal operation.

## 8. Mapping SICP ideas to GoF patterns

| SICP concept | GoF pattern it underlies | What SICP adds |
|---|---|---|
| Higher-order procedure with step parameters | Template Method, Strategy | No class hierarchy needed |
| Procedure returning a procedure | Factory Method for strategies, Command | Captured parameters replace fields |
| Closure over state | Object; Command with undo; Memento | Shows data/procedure duality |
| Closure property of combination | Composite | Explains *why* uniform recursion works |
| Message passing | OO polymorphism | Frames it as one of three dispatch choices |
| Data-directed programming | Visitor; strategy registries | Generalizes to N-ary dispatch; adding types *and* operations is additive |
| Abstraction barrier | Facade; Clean Architecture boundary; module interface | Gives the test: what can change below without changing above? |
| Streams / delayed evaluation | Iterator, virtual Proxy, Observer (reactive) | Makes "pipeline" the primary structure |
| Serializers / mutex | — | Why shared mutable state + concurrency needs explicit protocol |
| Metacircular evaluator / register machine | Interpreter | The pattern at its most serious |

## 9. When to choose the functional structure

Prefer functions and immutable data over an OO pattern when:
- The variation is a **single operation** (Strategy with one method → pass a function).
- You're **transforming data** through stages (pipeline, not a chain of objects).
- The behavior **doesn't need identity** — two instances configured the same way are interchangeable.
- You want **easy testing** — pure functions need no setup, no mocks, no teardown.
- **Concurrency** is in play — immutable data and pure functions compose safely.

Prefer objects when:
- Multiple operations share **the same state** and must stay consistent (an account with `deposit`/`withdraw`/`balance`).
- You need **identity** — this *particular* order, not any order with these fields.
- The type system should **enforce** that only valid combinations are possible (a `Money` that can't be added to a `Distance`).
- You need to **enumerate or inspect** the variants (list the available strategies; serialize them).
- The language or framework **expects** objects at that boundary (controllers, entities, DI registrations).

Most real code is a mix: objects at the boundaries and for stateful domain concepts; functions for the logic between. SICP's lasting contribution is making it clear that these are *choices of representation behind an abstraction barrier*, not fundamentally different kinds of program.
