# Gang of Four Patterns — by Force, with Modern Substitutes

Read this when you've identified a force (variation, construction, coupling, state, cross-cutting) and need to pick or rule out a named OO structure.

## Contents
1. The forces → pattern map
2. Creational patterns
3. Structural patterns
4. Behavioral patterns
5. Patterns that are frequently confused
6. Modern-language substitutes (quick table)
7. Pattern smells: signs a pattern is misapplied

---

## 1. Forces → pattern map

Start here. Find the force; the candidates are listed cheapest-first.

| Force | First try | Then consider |
|---|---|---|
| Algorithm/policy varies; caller shouldn't care which | Pass a function | **Strategy** (if the policy has state or several methods) |
| Behavior depends on internal state with rules about transitions | Enum + switch / transition table | **State** (if each state has substantial behavior) |
| Need to add responsibilities to objects without subclassing explosion | Composition | **Decorator** |
| Object creation is complex, conditional, or must be deferred | Constructor / static factory method | **Factory Method**, **Abstract Factory**, **Builder** |
| Many objects must react when one changes | Language events / `IObservable` / pub-sub | **Observer** (hand-rolled only without framework support) |
| Need to treat single objects and groups uniformly | — | **Composite** |
| An interface doesn't match what a client expects | Wrapper function | **Adapter** |
| Want to control access, add laziness, caching, or remote transparency | — | **Proxy** |
| Want to represent operations as objects (undo, queue, log, retry) | Closures | **Command** |
| A request should be handled by one of several handlers in sequence | Middleware pipeline (framework) | **Chain of Responsibility** |
| Need to perform operations across a heterogeneous object structure | Pattern matching over a sealed hierarchy | **Visitor** (only if the operation set grows faster than the type set) |
| Want an algorithm skeleton with pluggable steps | Pass functions for the steps | **Template Method** |
| Need to traverse without exposing internals | `yield`/iterators | **Iterator** (hand-rolled only when the language has none) |
| A subsystem is too complex for most callers | — | **Facade** |
| Too many fine-grained objects consuming memory | Interning, caching | **Flyweight** |
| Many objects communicating in a tangle | — | **Mediator** |
| Need to snapshot and restore state | Immutable records + history list | **Memento** |
| Create copies of complex configured objects | Record `with` expressions / copy constructor | **Prototype** |
| Exactly one instance must exist | DI container singleton lifetime | **Singleton** (rarely; see §7) |
| Need to define a language's grammar and evaluate it | Parser library | **Interpreter** |
| Need to separate abstraction from implementation so both vary | — | **Bridge** |

---

## 2. Creational patterns

### Factory Method
**Problem**: a class must create objects but shouldn't know their concrete type, or subclasses should decide what gets created.
**Shape**: a method whose job is to return an instance of an interface; subclasses or configuration override what it returns.
**Use when**: the creation decision belongs to a different place than the use.
**Don't use when**: there's one concrete type. A constructor is a factory method with no variation.
**Modern note**: in C#/Java/Python, a static method on the interface or a simple function is usually enough. A full subclass-per-product hierarchy is rarely warranted.

### Abstract Factory
**Problem**: you need to create *families* of related objects that must be used together (a UI toolkit's Button+Checkbox+Window for Windows vs. Mac; a data layer's Connection+Command+Reader for SQL Server vs. Postgres).
**Shape**: an interface with one creation method per product; one implementation per family.
**Use when**: consistency across the family is a correctness requirement.
**Don't use when**: only one product varies — that's Factory Method. Abstract Factory is the heavier pattern; the family constraint is what justifies it.

### Builder
**Problem**: constructing an object requires many steps, optional parts, or validation across parts; telescoping constructors are getting ugly.
**Shape**: a separate object that accumulates configuration and then produces the result.
**Use when**: construction is genuinely multi-step or the product is immutable and has many optional fields.
**Don't use when**: named/optional parameters or an init-only record would do. In C#, `new Options { A = 1, B = 2 }` with `init` setters and a validating constructor covers most cases. Builders earn their keep when there's *logic* in assembly (e.g., building a SQL query, an HTTP request, a test fixture with sensible defaults).

### Prototype
**Problem**: creating an object is expensive or you want copies of a pre-configured instance.
**Modern note**: largely subsumed by immutable records with `with`-expressions (C# records, Python dataclasses `replace`). Hand-rolled `Clone()` hierarchies are a shallow/deep-copy bug farm; avoid unless the language lacks the feature.

### Singleton
**Problem**: exactly one instance and a global access point.
**Reality**: the "global access point" half is the problem. Singletons hide dependencies, make tests order-dependent, and prevent parallel test runs. The "exactly one instance" half is a *lifetime* concern, which DI containers handle with a singleton registration while still injecting through constructors.
**Use when**: you have no DI container and the object is stateless or truly process-global (a logger config). Even then, prefer passing it in.

---

## 3. Structural patterns

### Adapter
**Problem**: you have a class with the right behavior and the wrong interface.
**Shape**: a wrapper that implements the interface the client wants and delegates to the wrapped object.
**Use when**: integrating third-party code, or isolating the rest of your system from a vendor API shape (Worldpay triPOS, a legacy COM object, etc.). Very often correct at system boundaries.
**Note**: Adapter changes interface; Decorator keeps it and adds behavior; Proxy keeps it and controls access. If you're unsure which you're writing, ask "does the caller see a different interface afterwards?"

### Bridge
**Problem**: two dimensions of variation (e.g., Shape × RenderingAPI) would produce an N×M subclass explosion.
**Shape**: the abstraction holds a reference to an implementation interface; each varies independently.
**Use when**: you can actually name two orthogonal axes that both vary. If only one does, it's Strategy.
**Honest note**: Bridge is mostly just "prefer composition over inheritance" with a name. If you find yourself explaining Bridge, you can usually say "composition" instead.

### Composite
**Problem**: tree structures where leaves and containers should be treated the same way (file systems, UI trees, expression trees, org charts, bills of materials).
**Shape**: a common interface; containers hold children of that interface and typically forward operations to them.
**Use when**: the client genuinely wants to ignore leaf-vs-container. Composite is one of the most reliably useful GoF patterns.
**Design decision**: where do child-management methods live? On the base (uniformity, but leaves get nonsense methods) or only on containers (safety, but clients must type-check). Favor safety unless uniformity is the whole point.

### Decorator
**Problem**: add responsibilities (logging, caching, retry, auth, compression) to individual objects at runtime without a subclass per combination.
**Shape**: implements the same interface as the wrapped object; delegates, adding behavior before/after.
**Use when**: cross-cutting concerns that stack. `CachingRepository(LoggingRepository(SqlRepository))` is the canonical good use.
**Don't use when**: the behavior isn't orthogonal to the wrapped object, or there's one decorator forever (just put the behavior in the class). Also watch for interface drift: decorators must track every method of the interface, so wide interfaces make them painful — which is itself a hint the interface is too wide (ISP).
**Modern note**: in .NET, `DelegatingHandler` for HTTP and middleware pipelines are built-in Decorator/Chain structures. Python decorators (`@functools.wraps`) are the function-level version.

### Facade
**Problem**: a subsystem has many classes and most callers need a simple, high-level entry point.
**Shape**: one class with a few methods that orchestrate the subsystem.
**Use when**: reducing the surface area a client must learn. Very common and cheap. Also a good first step when wrapping a legacy module you intend to replace later (Strangler Fig).
**Don't**: let the facade become a god class that *also* contains logic. It should orchestrate, not implement.

### Flyweight
**Problem**: huge numbers of objects with shared intrinsic state (glyphs in a document, tiles in a game, particles).
**Shape**: separate intrinsic (shared, immutable) from extrinsic (per-use) state; share the intrinsic part.
**Use when**: you have measured a memory problem. This is an optimization pattern; don't apply it prophylactically.
**Modern note**: string interning, `record` structs, and caching dictionaries achieve this without ceremony.

### Proxy
**Problem**: control access to an object — lazy initialization (virtual proxy), access control (protection proxy), remote access (remote proxy), caching, or reference counting.
**Shape**: same interface as the real subject; decides whether/how to forward.
**Use when**: the decision about *whether* to call matters. Lazy-loading ORMs, RPC stubs, and permission gates are all proxies.
**vs. Decorator**: Decorator always forwards and adds; Proxy may not forward at all.

---

## 4. Behavioral patterns

### Chain of Responsibility
**Problem**: multiple handlers could process a request; the sender shouldn't know which one will.
**Shape**: handlers linked in sequence; each handles or passes along.
**Use when**: handler order and membership change at configuration time (middleware, validation pipelines, event bubbling, approval workflows).
**Don't use when**: the set of handlers is fixed and small — an `if/else` is clearer and the "which handler ran?" question is answerable by reading.
**Modern note**: ASP.NET middleware, Django middleware, and Express middleware are this pattern. Don't hand-roll it inside those frameworks.

### Command
**Problem**: represent a request as an object so it can be queued, logged, undone, retried, or composed.
**Shape**: an interface with `Execute()` (and often `Undo()`); one class per operation, carrying its parameters.
**Use when**: you actually need one of queue/log/undo/retry/macro. These are the forces; without one, a method call is better.
**Modern note**: a closure captures parameters and execution; a list of closures is a macro; undo needs an explicit object only if you must store the inverse. CQRS "commands" are a related but distinct idea (request DTOs + handlers), often served by a mediator library.

### Interpreter
**Problem**: a domain has its own small language (rules, formulas, filters) that you need to evaluate.
**Shape**: an AST where each node type knows how to evaluate itself.
**Use when**: the grammar is small and stable. Composite + a `Evaluate` method is the usual realization.
**Don't**: write a parser by hand for anything non-trivial; use a parser library or expression trees. Interpreter is one of the least-applied GoF patterns for good reason.

### Iterator
**Problem**: traverse a collection without exposing its structure.
**Modern note**: built into every mainstream language (`IEnumerable`/`yield return`, Python generators, Java `Iterable`). Hand-roll only for unusual traversals (e.g., multiple simultaneous cursors with independent state) and even then, generators usually suffice.

### Mediator
**Problem**: many objects interact in a tangle of many-to-many references.
**Shape**: a central object that coordinates; participants talk only to it.
**Use when**: the interaction logic is genuinely complex and belongs in one place (UI dialog coordination, air traffic control). The mediator becomes the one class that knows the protocol.
**Risk**: the mediator becomes a god object. If it's growing without bound, the participants are probably too dumb — push behavior back into them.
**Note**: the popular .NET "MediatR" library is a request-dispatch mechanism, closer to Command + a registry than to GoF Mediator. Don't conflate them.

### Memento
**Problem**: capture and restore an object's state without breaking encapsulation (undo, checkpoints, transactions).
**Modern note**: immutable state + a history list is simpler. If your domain objects are records, a memento is just "keep the old record."

### Observer
**Problem**: one-to-many dependency; when one object changes, dependents are notified.
**Modern note**: C# events, `IObservable`/Rx, Python signals (Django), pub/sub. Hand-roll only in the absence of language support. The real design questions are: push vs. pull (what does the notification carry?), synchronous vs. async, and how to avoid leaks from forgotten unsubscriptions (weak references, `IDisposable` subscriptions).

### State
**Problem**: an object's behavior changes with its internal state, and the number of states or transitions makes conditionals unmanageable.
**Shape**: one class per state implementing a common interface; the context delegates to the current state and states trigger transitions.
**Use when**: three or more states, each with meaningful behavior, and transitions with rules. Order lifecycles, connection states, document workflows.
**Simpler first**: an enum and a transition table (`Dictionary<(State, Event), State>`) handles the *transition* rules with far fewer classes. Reach for the full pattern when each state has substantial *behavior*, not just a name.
**vs. Strategy**: structurally identical. The difference is intent: Strategy is chosen by the client and stays put; State changes itself over time and the client doesn't choose.

### Strategy
**Problem**: a family of interchangeable algorithms; the client selects one.
**Shape**: an interface; one class per algorithm; the context holds one and delegates.
**Use when**: the algorithm has state or multiple methods, or you need to enumerate/describe available strategies (e.g., a dropdown of shipping methods).
**Simpler first**: a function parameter. `Sort(items, Comparison<T>)` is Strategy without the ceremony. Only when the strategy has multiple methods or needs its own dependencies does an interface pay off.

### Template Method
**Problem**: an algorithm's skeleton is fixed but some steps vary.
**Shape**: a base class with the skeleton; abstract/virtual hooks for the varying steps.
**Use when**: inheritance is already the chosen mechanism and the steps are few.
**Prefer**: passing the varying steps as functions (Strategy-style composition). Template Method couples variation to inheritance, which is the less flexible tool. It's fine in frameworks (ASP.NET `Controller`, Django `View`) where the base class *is* the framework; it's rarely the best choice in your own code.

### Visitor
**Problem**: perform many different operations over a fixed set of element types without polluting the element classes with every operation.
**Shape**: elements accept a visitor; the visitor has one method per element type (double dispatch).
**Use when**: the element types are stable and the operations keep growing (compilers, AST tooling, document exporters). If the *types* grow and operations are stable, Visitor is exactly wrong — every new type touches every visitor.
**Modern substitute**: pattern matching over a sealed/closed hierarchy (C# `switch` expressions on records, Python `match`) gives the same exhaustiveness check with no accept/visit plumbing.

---

## 5. Patterns that are frequently confused

| Pair | Distinguishing question |
|---|---|
| Strategy vs State | Who changes it? Client → Strategy. The object itself, over time → State. |
| Decorator vs Proxy | Does it always forward? Yes and adds → Decorator. May refuse/defer/cache → Proxy. |
| Adapter vs Facade | Same interface, different shape → Adapter. Simplified interface over many classes → Facade. |
| Factory Method vs Abstract Factory | One product → Factory Method. A family that must match → Abstract Factory. |
| Command vs Strategy | Does it represent a *request* (with parameters, possibly undoable)? → Command. A *policy* the context applies? → Strategy. |
| Mediator vs Observer | Centralized coordination with knowledge of participants → Mediator. Decoupled broadcast → Observer. |
| Composite vs Decorator | Tree with many children → Composite. Linear wrapping chain, one child each → Decorator. |
| Chain of Responsibility vs Decorator | Both wrap. Chain may *stop*; Decorator always continues. |

---

## 6. Modern-language substitutes (quick table)

| GoF pattern | C# | Python |
|---|---|---|
| Strategy (single method) | `Func<>` / delegate | function argument |
| Command | lambda, `Action` | closure |
| Iterator | `yield return`, `IEnumerable<T>` | generator |
| Observer | `event`, `IObservable<T>` | signals, callbacks |
| Visitor (closed types) | `switch` expression on sealed records | `match` on dataclasses |
| Prototype | `record` + `with` | `dataclasses.replace` |
| Singleton | DI singleton lifetime | module-level instance |
| Template Method | virtual methods *or* function parameters | same |
| Decorator (functions) | — | `@decorator` |
| Chain of Responsibility | middleware pipeline | middleware |
| Null Object | `?.` and `??`, `Option`-style types | `Optional`, sentinel objects |
| Builder (simple) | `init` properties, object initializer | keyword args, dataclass defaults |

The rule: if the language feature expresses the intent clearly, the pattern class hierarchy is noise.

---

## 7. Pattern smells: signs a pattern is misapplied

- **Interface with one implementation and no test double.** Delete the interface until a second implementor exists.
- **Factory that only ever `new`s one type.** Inline it.
- **Strategy classes that are all stateless with one method.** Replace with functions.
- **Visitor over a hierarchy that keeps gaining types.** Switch to methods on the types, or pattern matching.
- **Decorator chain where ordering is load-bearing but undocumented.** Make the composition explicit in one place and comment the order dependency.
- **Singleton holding mutable state.** This is a global variable with extra steps.
- **Mediator that's 1,500 lines.** Participants are too anemic; push behavior down.
- **Observer with no unsubscribe path.** Memory leak.
- **Abstract Factory for a single family.** Use Factory Method or direct construction.
- **Template Method with 8 hooks.** The "skeleton" has no shape; use composition.
- **Pattern name in the class name with no explanation of the force.** `PaymentStrategyFactoryBuilder` is a warning sign. Name things by domain role, not by pattern (`PaymentGateway`, `RateCalculator`), and mention the pattern in a doc comment if it aids the reader.
