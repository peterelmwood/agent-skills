# Clean Code & Clean Architecture (Robert C. Martin)

Read this for questions about naming, function and class design, SOLID, and where responsibilities and dependencies should live at the module/layer level.

## Contents
1. Naming
2. Functions
3. Classes and SOLID
4. Error handling and boundaries
5. Comments and formatting (briefly)
6. Clean Architecture: the dependency rule
7. Applying Clean Architecture proportionately
8. Common misreadings

---

## 1. Naming

Names are the primary documentation. Most "needs a comment" code actually needs a rename.

- **Intention-revealing.** `elapsedDays`, not `d`. `activeAccounts`, not `list1`. If you need a comment to explain what a name means, change the name.
- **Avoid disinformation.** Don't call something a `List` if it isn't one. Don't use `accountGroup` for a single account. Avoid names differing only subtly (`XYZControllerForEfficientHandlingOfStrings` vs. `...StorageOfStrings`).
- **Meaningful distinctions.** `source`/`destination`, not `a1`/`a2`. Noise words (`Info`, `Data`, `Manager`, `Processor`, `Object`) add nothing; `ProductInfo` vs. `ProductData` tells the reader nothing.
- **Pronounceable and searchable.** Single-letter names are fine for tiny scopes (loop indices, lambda params) and nowhere else. Constants should be named so they can be grepped: `MAX_RETRY_COUNT`, not `7`.
- **Classes are nouns, methods are verbs.** `Customer`, `WikiPage`, `AddressParser`. `postPayment`, `deletePage`, `save`. Accessors/mutators/predicates: `get`/`set`/`is` (or language convention — C# properties, Python plain attributes).
- **One word per concept.** Don't have `fetch`, `retrieve`, and `get` all meaning the same thing across the codebase. Conversely, don't reuse `add` for both "append to list" and "sum two numbers."
- **Solution-domain names where the reader is a programmer** (`JobQueue`, `AccountVisitor` if it's really a Visitor); **problem-domain names otherwise** (`Invoice`, `RateSchedule`). The latter should dominate in business logic.
- **Context.** `state` in `Address` is clear; `state` alone in a 20-field method is not. Add context by moving the variable into a class, not by prefixing everything (`addrState`).

## 2. Functions

- **Small.** Then smaller. The aim is a function that does one thing, where "one thing" means: all statements are at the same level of abstraction, one level below the function's name. If you can extract another function with a name that isn't a restatement of the original, it was doing more than one thing.
- **One level of abstraction per function.** Don't mix `getHtml()` with `.append("\n")` in the same body. The "stepdown rule": reading top to bottom, each function is followed by those at the next level down.
- **Few arguments.** Zero is ideal, one or two fine, three needs justification, more is a smell (see Fowler's Introduce Parameter Object). Boolean flag arguments are a strong smell — they announce the function does two things. Split it.
- **No side effects.** A function named `checkPassword` that also initializes a session is lying. If it must do both, name it `checkPasswordAndInitializeSession` — and then notice that's two functions.
- **Command–Query Separation.** Either change state or return information; not both. `if (set("username", "bob"))` is confusing because `set` is doing both.
- **Prefer exceptions to error codes**, and extract try/catch bodies into their own functions so error handling is one thing and the happy path is another.
- **DRY, within reason.** Duplication is the root of a lot of evil, but see the rule of three and "different reasons to change" in the refactoring reference.
- **Output arguments are confusing.** `appendFooter(report)` — is report input or output? If a function must change something, change the state of its owning object.

## 3. Classes and SOLID

Classes should be small too, measured in *responsibilities*, not lines. A class with five public methods and one reason to change is fine; one with two methods and three reasons to change is not.

**S — Single Responsibility.** A class should have one reason to change. "Reason" means a stakeholder or axis of change: reporting format, data source, business rule, UI. If you can describe the class only with "and," split it. Divergent Change is the smell.

**O — Open/Closed.** Open for extension, closed for modification: you should be able to add behavior (a new payment provider, a new report) without editing existing, tested code. Achieved through abstraction at the points of expected variation — and *only* there. Trying to be open to every possible change is Speculative Generality. Pick the axes that have actually varied or are concretely planned.

**L — Liskov Substitution.** Subtypes must be usable wherever the base type is, without the caller knowing. Violations: overriding a method to throw `NotSupportedException`; subclasses that strengthen preconditions or weaken postconditions; the Square-extends-Rectangle problem. Refused Bequest is the smell. Fix: Replace Inheritance with Delegation, or redraw the hierarchy around behavior rather than real-world taxonomy.

**I — Interface Segregation.** Clients shouldn't depend on methods they don't use. Fat interfaces force implementors to stub things and force clients to be coupled to changes they don't care about. Split by client need: `IReadRepository<T>` and `IWriteRepository<T>` rather than one `IRepository<T>` with 15 methods. Decorators and test doubles get much easier.

**D — Dependency Inversion.** High-level policy should not depend on low-level detail; both should depend on abstractions, and the abstractions should be owned by the high-level side. Concretely: `OrderService` depends on `IOrderRepository` *defined in the same module as `OrderService`*; `SqlOrderRepository` in the infrastructure module implements it. The dependency arrow points inward. This is what makes the business logic testable without a database, and it's the mechanism behind Clean Architecture.

**Cohesion.** Methods should use most of the class's fields. If a class has two groups of methods each using a disjoint group of fields, that's two classes.

**Tell, Don't Ask.** Instead of asking an object for data and deciding what to do, tell the object what you want done. `account.Withdraw(amount)` rather than `if (account.Balance >= amount) account.Balance -= amount`. Keeps the rule with the data (fixes Feature Envy and Data Class).

**Law of Demeter.** A method should only call methods on: itself, its parameters, objects it creates, its direct fields. Not on objects returned by those (`a.B().C().Do()`). Applied too rigidly it produces Middle Man; applied to data structures (DTOs, records) it's irrelevant. It matters for *objects with behavior* whose internal structure might change.

## 4. Error handling and boundaries

- **Use exceptions, not return codes**, for exceptional conditions. Provide context in the message (what operation, what input).
- **Define exceptions by caller need.** If callers would handle five vendor exceptions identically, wrap the vendor call and throw one of your own. This is Adapter applied to failure modes.
- **Don't return null; don't pass null.** Return empty collections, Null Objects, or `Optional`/nullable-annotated types the compiler can check. Every `null` return creates a check at every call site, and the one you forget is the production bug.
- **Wrap third-party APIs.** Learning tests (write tests against the vendor API to learn it) and a thin adapter of your own give you one place to absorb vendor changes and one place to mock. Especially worthwhile for payment gateways, external SDKs, and anything with its own exception hierarchy.
- **The "special case" pattern.** When an exception would be thrown for a non-exceptional situation (no meal expenses today), return an object that handles the special case (`PerDiemMealExpenses` returning the default) rather than throwing and catching.

## 5. Comments and formatting (briefly)

- Comments compensate for failure to express in code. Before writing one, try to rename or extract instead.
- Good comments: legal headers, explanation of *intent* or *why* this non-obvious approach, warnings of consequences, TODOs with owners, amplification of something that looks unimportant but isn't, public API docs.
- Bad comments: restating the code, journal/changelog comments (that's version control), commented-out code (delete it), position markers, closing-brace comments, attributions.
- Formatting: vertical density — related things close together, concepts separated by blank lines; variables declared near use; caller above callee (the newspaper metaphor — headline, then detail). Follow the team's style; consistency beats any particular rule.

## 6. Clean Architecture: the dependency rule

The single rule: **source code dependencies point inward, toward higher-level policy.** Nothing in an inner circle knows anything about an outer circle.

Concentric layers, inside out:
1. **Entities** — enterprise-wide business rules; objects/data structures with methods that embody rules. Change least.
2. **Use Cases** — application-specific rules; orchestrate entities to accomplish a user goal. Know nothing about UI, database, or frameworks.
3. **Interface Adapters** — controllers, presenters, gateways; convert data between the use-case format and the external format (web request, DB row, view model).
4. **Frameworks & Drivers** — web framework, DB, UI, devices. Glue code only.

Crossing boundaries: when a use case needs the database, it calls an interface (`IOrderRepository`) *defined in the use-case layer*; the implementation lives outside and is injected. Data crossing a boundary should be simple structures (DTOs), not framework types (no `HttpRequest` or EF entity passed into a use case).

**Why**: the business rules become testable in isolation, the database and framework become replaceable details, and the system's structure screams what it does ("this is an invoicing system") rather than what it's built with ("this is an ASP.NET app").

**Related architectures that implement the same rule**: Hexagonal / Ports & Adapters (Cockburn), Onion (Palermo), BCE. The vocabulary differs; the dependency direction is the same.

## 7. Applying Clean Architecture proportionately

The full four-ring structure with separate projects per ring is appropriate for systems that will live for years, have real business rules, and are likely to swap infrastructure or UI. It is not appropriate for everything. Apply the *rule*, scale the *ceremony*:

- **Script or small tool**: pure functions for logic, I/O at the top. No layers needed; the dependency rule is satisfied by "logic doesn't `import` the HTTP client."
- **Small app / internal service**: two folders — `Domain` (entities, rules, interfaces) and everything else. Inject implementations. That's 80% of the benefit.
- **Long-lived product with multiple adapters** (web + API + batch; multiple DBs): the full layering, with the inner layers in projects that *cannot* reference the outer ones (enforce via project references / import linting).

Signs you've over-applied it: DTOs that mirror entities field-for-field with no transformation; interfaces with one implementation that only exist to satisfy the layering; use cases that are one line calling the repository. Signs you've under-applied it: business rules in controllers; entities decorated with ORM attributes and JSON attributes and validation attributes all at once; tests that need a database to check a discount calculation.

**Framework-specific notes**:
- *ASP.NET Core / EF Core*: controllers in the adapter ring; EF `DbContext` behind a repository or directly in a gateway implementation; domain entities separate from EF entities when the mapping is non-trivial, shared when it's trivial (be pragmatic — the dual-model tax is real).
- *Django*: models are both entity and ORM record; that's a known compromise. Keep rules in model methods or a `services`/`domain` module, keep views thin, keep business logic out of views and templates. Don't fight the framework's model layer unless the domain rules are genuinely complex.
- *Power Apps / low-code*: the dependency rule still applies conceptually — keep formula logic in reusable components or named formulas, not duplicated per screen; treat data sources as replaceable details behind collections.

## 8. Common misreadings

- "Functions should be under N lines." The point is one level of abstraction, not a count. A 25-line function that reads linearly at one level is fine; a 10-line one mixing levels isn't.
- "Every class needs an interface." No — interfaces at the points where the *dependency rule* requires them (inner layer calling outer) and where test doubles are needed. Not on value objects, DTOs, or leaf utilities.
- "Clean Architecture means many projects." It means dependency direction. One project with disciplined namespaces and an import-lint rule is Clean Architecture; six projects with the domain referencing EF Core is not.
- "No comments ever." No *redundant* comments. Why-comments and API docs remain valuable.
- "DRY means no duplication anywhere." It means no duplication of *knowledge*. Two similar-looking functions that encode different business rules are not duplicates.
