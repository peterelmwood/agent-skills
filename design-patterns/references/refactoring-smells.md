# Refactoring: Smells → Moves (Fowler)

Read this when you have existing code and need to diagnose what's wrong and decide which refactoring to apply, in what order.

## Contents
1. The method: how to refactor safely
2. Smell catalog with the usual treatments
3. Refactoring catalog (the moves), grouped by purpose
4. Ordering: which refactorings unlock others
5. When *not* to refactor

---

## 1. The method

Refactoring is a change to internal structure that does not change observable behavior. Three consequences follow:

- **You need a way to know behavior didn't change.** That's tests. If there are none, write characterization tests first (see `process-and-testing.md`): call the code, record what it does, assert that. They're ugly and that's fine — they're scaffolding.
- **Small steps.** Each move should be reversible and leave the code compiling and tests passing. The "two hats" rule: you're either adding behavior or refactoring, never both in one step. Switch hats consciously.
- **Refactor opportunistically, not as a project.** The "boy scout rule" (leave it cleaner than you found it) and "preparatory refactoring" (make the change easy, then make the easy change) beat scheduled refactoring sprints, which tend to get cancelled.

The feedback loop: smell → pick a move → apply → test → commit (or at least a checkpoint) → re-smell.

---

## 2. Smell catalog

Each smell: what it looks like, why it hurts, the usual moves.

### Bloaters

**Long Method / Long Function.** A method a reader can't take in at once. The threshold isn't a line count; it's "do I need to scroll or hold multiple ideas to understand this?" Comments inside a method that label sections are a strong tell — each comment is a method name waiting to be extracted.
→ Extract Method (by far the most common). Replace Temp with Query. Introduce Parameter Object. Decompose Conditional. Replace Method with Method Object (when there are too many locals to extract cleanly).

**Large Class.** Too many fields, too many methods, often a name with "Manager" or "Service" that could mean anything.
→ Extract Class (group fields that change together). Extract Subclass/Interface. Look for the two or three responsibilities hiding inside and name them.

**Primitive Obsession.** Strings for emails, decimals for money, ints for IDs, tuples for coordinates. The rules about those values are scattered or missing.
→ Replace Primitive with Object (a `Money`, `EmailAddress`, `CustomerId` type). Replace Type Code with Class/Subclasses/Polymorphism. Introduce Parameter Object. In C#, records make this nearly free.

**Long Parameter List.** More than three or four parameters; parameters that always travel together.
→ Introduce Parameter Object. Preserve Whole Object (pass the object instead of three of its fields). Replace Parameter with Method Call (if the callee can compute it).

**Data Clumps.** The same group of fields appearing in multiple classes or parameter lists (start+end dates, host+port+credentials).
→ Extract Class into a value object; then the clump has a name and a home for its rules.

### Object-orientation abusers

**Switch Statements (on type).** The same `switch`/`if-else` on a type code appears in multiple places. Adding a new case means finding all of them.
→ Replace Conditional with Polymorphism. But: a *single* switch over a *closed* set (an enum that won't grow) is fine, and in languages with exhaustive pattern matching it's often the clearest choice. The smell is the *duplication* of the switch, not its existence.

**Refused Bequest.** A subclass inherits methods it doesn't want or overrides them to throw.
→ Replace Inheritance with Delegation. Push Down Method/Field. Reconsider whether the hierarchy models an is-a relationship at all.

**Temporary Field.** A field that's only set in certain circumstances; readers can't tell when it's valid.
→ Extract Class for the circumstance it supports. Introduce Null Object.

**Alternative Classes with Different Interfaces.** Two classes do similar things with differently named methods.
→ Rename Method, Move Method, until they share an interface; then Extract Superclass or Interface.

### Change preventers

**Divergent Change.** One class gets changed for many unrelated reasons (every new report format *and* every new data source touches `ReportService`).
→ Extract Class per reason-for-change. This is SRP as a smell.

**Shotgun Surgery.** The inverse: one logical change requires edits in many classes.
→ Move Method/Field to bring the scattered pieces together. Inline Class if the pieces are tiny.

**Parallel Inheritance Hierarchies.** Adding a subclass in one hierarchy forces a subclass in another.
→ Move Method/Field so one hierarchy references the other; eliminate one.

### Dispensables

**Comments (as deodorant).** Comments that explain *what* confusing code does, rather than *why*.
→ Extract Method and name it what the comment said. Rename Variable. Introduce Assertion. Keep comments that explain intent, constraints, or non-obvious decisions.

**Duplicate Code.** Same expression in two places.
→ Extract Method. Pull Up Method (in siblings). Form Template Method (similar but not identical). Substitute Algorithm. Note: not all duplication is bad; two things that look the same but will change for different reasons should stay separate (the "rule of three" — wait for the third occurrence before abstracting, unless the duplication is already causing bugs).

**Lazy Class.** A class that doesn't do enough to justify existing.
→ Inline Class. Collapse Hierarchy.

**Dead Code.** Unreachable or unused.
→ Delete it. Version control remembers.

**Speculative Generality.** Abstract classes with one subclass, parameters that are always the same value, hooks nobody calls, "just in case" interfaces.
→ Collapse Hierarchy. Inline Class. Remove Parameter. Rename to something concrete. This is the smell most often introduced by over-eager pattern application; audit your own designs for it.

**Data Class.** A class with fields and getters/setters and no behavior; the behavior lives elsewhere, usually in a class that envies it.
→ Move Method into the data class. Encapsulate Collection. Remove Setting Method for things that shouldn't change. (Note: DTOs at boundaries are supposed to be data classes; the smell is when domain objects are.)

### Couplers

**Feature Envy.** A method is more interested in another class's data than its own — lots of `other.GetX()`, `other.GetY()`.
→ Move Method to where the data is. Extract Method first if only part of the method envies.

**Inappropriate Intimacy.** Two classes reach into each other's private parts.
→ Move Method/Field. Change Bidirectional Association to Unidirectional. Extract Class for the shared bit. Hide Delegate.

**Message Chains.** `a.GetB().GetC().GetD().DoThing()`. Any change to the intermediate structure breaks the client (Law of Demeter).
→ Hide Delegate (give `a` a method that does the navigation). Extract Method for the chain and Move it closer to the data. Don't over-apply: chains over immutable value objects or fluent builders are fine.

**Middle Man.** A class that does nothing but delegate.
→ Remove Middle Man. Inline Method. (Often the result of over-applying Hide Delegate.)

---

## 3. Refactoring catalog (the moves)

Grouped by what you're trying to accomplish. Each move's safety trick is noted where it isn't obvious.

### Composing methods
- **Extract Method** — the workhorse. Safety: identify locals used before/after; those become parameters/returns. If too many, see Replace Method with Method Object.
- **Inline Method** — when the body is as clear as the name, or as prep for a larger extraction.
- **Extract Variable / Inline Variable** — name a sub-expression (or un-name a pointless one).
- **Replace Temp with Query** — turn a local computed once into a method so other methods can use it. Prerequisite for many extractions.
- **Split Variable** — one local used for two purposes; give each its own.
- **Replace Method with Method Object** — a long method with many locals becomes a class whose fields are the locals; then extract freely.
- **Substitute Algorithm** — replace the body wholesale with a clearer approach.
- **Decompose Conditional** — extract the condition, the then-branch, and the else-branch into named methods.
- **Replace Nested Conditional with Guard Clauses** — early returns for the unusual cases; the main path reads linearly.
- **Consolidate Conditional Expression** — several conditions with the same result → one named condition.
- **Introduce Assertion** — make an assumption explicit.

### Moving features between objects
- **Move Method / Move Field** — to the class that uses it most. Safety: leave a delegating stub, then remove callers one by one.
- **Extract Class / Inline Class** — split or merge responsibilities.
- **Hide Delegate / Remove Middle Man** — the Law of Demeter dial; turn it toward Hide when clients are coupled to structure, toward Remove when the middle man is pure noise.
- **Introduce Foreign Method / Introduce Local Extension** — add behavior to a class you can't modify (extension methods in C# are the first; a subclass or wrapper the second).

### Organizing data
- **Replace Primitive with Object** (Replace Data Value with Object) — see Primitive Obsession.
- **Encapsulate Field / Encapsulate Collection** — expose a read-only view and add/remove methods, not the raw list.
- **Replace Magic Number with Symbolic Constant.**
- **Replace Type Code with Class / Subclasses / State-Strategy** — escalating responses to type codes, by how much behavior varies.
- **Change Value to Reference / Reference to Value** — decide identity semantics explicitly. Value objects should be immutable.
- **Replace Array with Object** — when array positions have meaning.
- **Change Unidirectional to Bidirectional Association** (and back) — add back-references only when genuinely needed; they complicate invariants.
- **Replace Record with Data Class** — the first step toward giving data behavior.

### Simplifying method calls
- **Rename Method** — most valuable refactoring per keystroke. Safety: IDE rename handles it; otherwise add new, delegate from old, migrate, delete old.
- **Add / Remove Parameter.**
- **Separate Query from Modifier** — a method should return data or change state, not both (Command-Query Separation).
- **Parameterize Method** — two methods differing only by a constant → one with a parameter.
- **Replace Parameter with Explicit Methods** — the reverse, when the parameter selects wildly different behavior.
- **Preserve Whole Object** / **Replace Parameter with Method Call** — see Long Parameter List.
- **Introduce Parameter Object.**
- **Remove Setting Method** — for fields set once at construction.
- **Hide Method** — tighten visibility.
- **Replace Constructor with Factory Method** — when construction needs logic or should return a subtype.
- **Replace Error Code with Exception** / **Replace Exception with Test** — exceptions for exceptional conditions; a pre-check for expected ones.

### Dealing with generalization
- **Pull Up / Push Down Field, Method, Constructor Body.**
- **Extract Subclass / Superclass / Interface.**
- **Collapse Hierarchy** — when subclass and superclass aren't different enough.
- **Form Template Method** — similar methods in siblings with the same steps in the same order.
- **Replace Inheritance with Delegation** — the escape hatch from a bad hierarchy.
- **Replace Delegation with Inheritance** — rare; only when you delegate *everything*.

### Big refactorings (multi-session)
- **Tease Apart Inheritance** — a hierarchy doing two jobs → two hierarchies, one referencing the other.
- **Convert Procedural Design to Objects.**
- **Separate Domain from Presentation.**
- **Extract Hierarchy** — one class with many conditionals on type → a hierarchy.

---

## 4. Ordering: which refactorings unlock others

Refactorings have prerequisites. A typical productive sequence on a long, tangled method:

1. **Rename** anything misleading, so you can think about it.
2. **Split Variable** / **Replace Temp with Query** to untangle locals.
3. **Replace Nested Conditional with Guard Clauses** to flatten.
4. **Extract Method** repeatedly, naming each chunk by what the comment (or your understanding) said it does.
5. Now that methods are small, **Feature Envy** becomes visible → **Move Method**.
6. Clusters of moved methods + fields → **Extract Class**.
7. Repeated type switches across the new classes → **Replace Conditional with Polymorphism**.

Each step leaves tests green. Don't attempt step 7 first; you can't see the polymorphism until the methods are small enough to compare.

---

## 5. When not to refactor

- The code works, is never touched, and you can't test it. Leave it. Wrap it (Facade) if you must integrate with it.
- Rewriting would be cheaper. Small, isolated, badly broken modules are sometimes better replaced than refactored — but be honest about "small" and "isolated."
- The deadline is real and the refactor isn't on the critical path. Note the smell; do it in the next preparatory refactoring.
- The "smell" is a style preference, not a maintenance cost. Refactoring is justified by making a future change easier, not by taste.
