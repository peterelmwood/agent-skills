# SQL Antipatterns (Karwin) — Relational Design Patterns

Read this for schema design, key choices, hierarchical data, query shape, and application-side database access. Karwin's book is organized as antipattern → why people do it → how to recognize it → legitimate uses → solution. That last section matters: several "antipatterns" are the right call in specific circumstances, and the skill should say so rather than reflexively flagging them.

## Contents
1. Logical database design antipatterns
2. Physical database design antipatterns
3. Query antipatterns
4. Application development antipatterns
5. Hierarchical data: the four solutions compared
6. Quick diagnostic checklist

---

## 1. Logical database design antipatterns

### Jaywalking — comma-separated lists in a column
**Looks like**: `tags VARCHAR(255)` holding `'red,large,sale'`. Or a `product_ids` column with `'12,34,56'`.
**Why it's done**: avoiding an intersection table feels simpler.
**Why it hurts**: can't index, can't enforce referential integrity, can't query individual values efficiently, `LIKE '%,34,%'` is both slow and wrong (matches 134), updates require string surgery, length limits are arbitrary.
**Legitimate**: you only ever store and retrieve the whole list, never query by element, and it's genuinely opaque to the DB (a denormalized cache; a serialized settings blob). Even then, a JSON column with native indexing is usually better than CSV.
**Solution**: an intersection table (`product_tags(product_id, tag_id)`) with a composite primary key.

### Naive Trees — adjacency list with recursive queries nobody can write
**Looks like**: `parent_id` self-reference, and then application code doing N queries to walk the tree.
**Why it hurts**: fetching a subtree or ancestors requires recursion; deleting a subtree is multi-step; depth queries are awkward.
**Legitimate**: the adjacency list is *fine* when the DB supports recursive CTEs (`WITH RECURSIVE`), which every major DB now does, and the trees are modest. Karwin's point is that it's naive when you don't know the alternatives, not that it's always wrong.
**Solutions**: see §5 for Path Enumeration, Nested Sets, Closure Table, and how to choose.

### ID Required — a surrogate `id` on every table reflexively
**Looks like**: every table has `id INT AUTO_INCREMENT PRIMARY KEY`, including intersection tables that then also need a `UNIQUE(a_id, b_id)` to prevent duplicates — and often don't have it.
**Why it hurts**: redundant keys; duplicate rows in intersection tables; `id` is a meaningless name when the table has a natural identity; `USING (id)` joins become impossible when every table's key is named the same thing.
**Legitimate**: surrogate keys are *usually* right for entity tables (stable, compact, ORM-friendly). The antipattern is applying them *without thought*, especially to intersection tables.
**Solution**: name keys descriptively (`bug_id`, not `id`); on intersection tables use the composite natural key as the primary key; add a surrogate only when something else must reference the row.

### Keyless Entry — no foreign key constraints
**Looks like**: "we handle integrity in the application" or "FKs slow down inserts."
**Why it hurts**: orphaned rows, dangling references, every integrity bug becomes a data-cleanup project. Application-level checks have race conditions the DB's don't.
**Legitimate**: very high-volume append-only logging where the referenced data is guaranteed by the pipeline; some sharded setups where cross-shard FKs are impossible. Rare.
**Solution**: declare the constraints. Use `ON DELETE/UPDATE CASCADE`/`SET NULL`/`RESTRICT` deliberately — they're a declarative Observer for cleanup.

### Entity-Attribute-Value — a generic `(entity_id, attribute, value)` table
**Looks like**: "we need flexible attributes so we store everything as name/value rows."
**Why it hurts**: no data types (everything is a string), no NOT NULL, no FK on values, reconstructing a row needs a self-join per attribute, aggregate queries are nightmares, no constraints on which attributes are valid.
**Legitimate**: truly sparse, truly dynamic, user-defined attributes with no query requirements — and even then, consider a JSON/document column or a document store instead.
**Solutions**, in increasing flexibility:
- **Single Table Inheritance**: one table, all attributes as nullable columns, a `type` column. Fine for few subtypes with few differing columns.
- **Concrete Table Inheritance**: one table per subtype with all columns. No nulls; but shared queries need `UNION`.
- **Class Table Inheritance**: a base table with common columns, one table per subtype with its own columns, joined on the shared key. The relational version of OO inheritance.
- **Semi-structured**: a JSON column for the variable part; indexed where the DB supports it.
These map directly onto Fowler's ORM patterns of the same names.

### Polymorphic Associations — a FK that can point to multiple tables
**Looks like**: `comments(commentable_type, commentable_id)` where `commentable_id` refers to `posts.id` *or* `photos.id` depending on the type column.
**Why it hurts**: no real foreign key possible; joins require `CASE` or multiple `LEFT JOIN`s with the type check; integrity is unenforceable. Common in Rails/Django ORMs (GenericForeignKey) because the ORM makes it look easy.
**Legitimate**: ORM convenience when integrity is genuinely low-stakes. Honestly rare.
**Solutions**: *reverse the reference* — one intersection table per parent type (`post_comments`, `photo_comments`), each with real FKs; or *common super-table* — a `commentable` base table that `posts` and `photos` both reference, and comments reference it. The second is Class Table Inheritance again.

### Multicolumn Attributes — `tag1, tag2, tag3` columns
**Looks like**: a fixed number of repeated columns for a multi-valued attribute.
**Why it hurts**: searching needs `OR` across all columns; adding/removing a value means finding which slot; the limit is arbitrary; uniqueness across columns can't be constrained.
**Legitimate**: the number is genuinely fixed by the domain and the values are positional (`address_line_1`, `address_line_2`; `home_phone`, `mobile_phone` — these are *different attributes*, not a list).
**Solution**: a dependent table, one row per value.

### Metadata Tribbles — tables or columns cloned by year/region/etc.
**Looks like**: `sales_2023`, `sales_2024`, `sales_2025` or `revenue_q1, revenue_q2, ...`.
**Why it hurts**: queries across the split need `UNION`; schema changes must be applied N times; referential integrity to the split tables is impossible; new periods require DDL.
**Legitimate**: archiving genuinely cold data; manual sharding before the DB offered partitioning.
**Solution**: one table with a discriminating column; use the database's **partitioning** for the physical split if volume demands it. For column-tribbles, a dependent table (one row per period).

## 2. Physical database design antipatterns

### Rounding Errors — `FLOAT` for money
**Why it hurts**: binary floating point can't represent most decimal fractions; sums drift; equality fails.
**Solution**: `NUMERIC`/`DECIMAL` with explicit precision and scale for money and anything requiring exact decimal arithmetic. `FLOAT` only for genuinely approximate scientific quantities.

### 31 Flavors — `ENUM` or `CHECK (status IN ('new','open','closed'))` for a changing set
**Why it hurts**: changing the set is DDL; the values aren't queryable as data (can't list them with `SELECT`); ordering is by definition order; portability varies.
**Legitimate**: a set that genuinely never changes (`('left','right')`, days of the week).
**Solution**: a lookup table with a FK. The valid set becomes data, can be queried, can carry extra attributes (display name, sort order, active flag), and changes without DDL.

### Phantom Files — storing file *paths* in the DB with files on disk
**Why it hurts**: no transactional integrity (DB row deleted, file remains, or vice versa); backups are two separate problems; access control is split; the path format couples the DB to a filesystem layout.
**Legitimate**: very large files where DB storage is impractical; CDN/object-storage architectures where the external system has its own integrity model. Common and often correct in modern systems — but be explicit about the compensating mechanisms (cleanup jobs, orphan detection).
**Solution**: `BLOB` for small/medium files when transactional integrity matters; otherwise object storage with a reconciliation strategy.

### Index Shotgun — no indexes, or indexes on everything
**Why it hurts**: missing indexes → slow reads; indiscriminate indexes → slow writes, wasted space, and the optimizer still picks wrong.
**Solution**: Karwin's **MENTOR**: *Measure* (slow query log, profiler), *Explain* (read the plan), *Nominate* (which queries need help), *Test*, *Optimize* (cache, configure), *Rebuild* (maintain statistics). Index for actual queries. Composite indexes follow the leftmost-prefix rule, so column order matters; covering indexes avoid the table lookup.

## 3. Query antipatterns

### Fear of the Unknown — mishandling `NULL`
**Looks like**: `WHERE col != 'x'` expecting NULL rows to match; `WHERE col = NULL`; concatenating with a nullable column and getting NULL; using a sentinel (`-1`, `''`, `'N/A'`) to avoid NULL.
**Why it hurts**: three-valued logic; sentinels are worse because they *look* like data and participate in arithmetic and joins.
**Solution**: NULL is for "unknown/not applicable" and that's fine. Use `IS NULL`/`IS NOT NULL`, `COALESCE`, `IS DISTINCT FROM` where available. Declare `NOT NULL` wherever a value is genuinely required so the question doesn't arise.

### Ambiguous Groups — selecting non-grouped, non-aggregated columns
**Looks like**: `SELECT product_id, MAX(date), bug_id FROM bugs GROUP BY product_id` and expecting `bug_id` to be the one from the max-date row. Some DBs reject it; MySQL historically returned an arbitrary row.
**Solution**: window functions (`ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY date DESC)` then filter to `= 1`); or a correlated subquery; or a derived table joining back on the max; or `GROUP_CONCAT`/`STRING_AGG` if you actually want all of them.

### Random Selection — `ORDER BY RAND() LIMIT 1`
**Why it hurts**: sorts the whole table to pick one row.
**Solutions**: pick a random key between min and max and take the first row ≥ it (gaps tolerated); or count, pick a random offset, `LIMIT 1 OFFSET n` (still scans n rows); or use the DB's `TABLESAMPLE`.

### Poor Man's Search Engine — `LIKE '%term%'` for text search
**Why it hurts**: can't use an index; matches substrings (`'one'` matches `'money'`); no ranking, stemming, or relevance.
**Solution**: full-text search features (PostgreSQL `tsvector`, MySQL `FULLTEXT`, SQL Server full-text indexes) or an external engine (Elasticsearch, etc.). An inverted-index table is the DIY version.

### Spaghetti Query — one enormous query doing everything
**Why it hurts**: Cartesian products inflate counts (joining to two one-to-many tables multiplies rows — `COUNT` is wrong); impossible to debug; the optimizer gives up.
**Solution**: split into several queries. Each should answer one question. Combine in the application if needed. For the Cartesian problem specifically: aggregate each one-to-many in its own subquery or CTE, then join the aggregates.

### Implicit Columns — `SELECT *` and `INSERT` without a column list
**Why it hurts**: schema changes break the application silently (column order, new columns); fetches more than needed; ambiguous names across joins.
**Legitimate**: ad-hoc exploration.
**Solution**: name the columns. Always, in application code.

## 4. Application development antipatterns

### Readable Passwords — storing passwords in plain text or reversible encryption
**Solution**: salted, slow hash (bcrypt/scrypt/Argon2). Reset flows, not recovery flows. (Not a "pattern" question, but Karwin includes it because it's a schema decision.)

### SQL Injection — string-concatenated queries
**Solution**: parameterized queries, always. Whitelist for things that can't be parameterized (identifiers, `ORDER BY` column names). Don't rely on escaping.

### Pseudokey Neat-Freak — reusing or renumbering surrogate keys to fill gaps
**Why it hurts**: keys are identifiers, not row numbers; reuse breaks external references, logs, and caches.
**Solution**: gaps are fine. If you need a gapless sequence for display, compute it at query time with `ROW_NUMBER()`.

### See No Evil — ignoring return values and errors from the DB API
**Solution**: check them; log the query *and* parameters on failure; let exceptions propagate to a layer that can handle them.

### Diplomatic Immunity — treating SQL as exempt from engineering practice
**Looks like**: schema changes with no version control, no migrations, no tests, no documentation.
**Solution**: migrations in source control (Flyway, Liquibase, EF migrations, Django migrations); schema documented (ERD, comments); database code tested (integration tests against a real DB in CI). SQL is code.

### Magic Beans — the model *is* the active record
**Looks like**: every model class maps 1:1 to a table and exposes CRUD; business logic lives in controllers that call `save()` on several models.
**Why it hurts**: domain logic has no home; models are coupled to the schema; testing requires a DB; the "Data Class" smell at scale.
**Legitimate**: simple CRUD apps where the table *is* the domain.
**Solution**: a domain model layer with behavior; the ORM/Active Record as an infrastructure detail behind it (Repository, Data Mapper). This is Clean Architecture's dependency rule applied to data access, and Fowler's Domain Model vs. Active Record distinction. Django note: `Model` methods and a `services` module get you most of the way without abandoning the ORM.

## 5. Hierarchical data: the four solutions compared

The most reusable section of the book. Trees in SQL (categories, org charts, threaded comments, bill of materials, relay-protection zone hierarchies, network topologies).

| Design | Insert | Move subtree | Delete subtree | Query ancestors | Query descendants | Referential integrity | Depth known? |
|---|---|---|---|---|---|---|---|
| **Adjacency List** (`parent_id`) | Easy | Easy | Needs recursion | Recursive CTE | Recursive CTE | Yes (FK) | Via CTE |
| **Path Enumeration** (`'1/4/7/'`) | Easy | Rewrite paths | `LIKE 'path%'` | Parse the path | `LIKE 'path%'` | No (string) | Count separators |
| **Nested Sets** (`left`, `right`) | Renumber half the table | Hard | `BETWEEN left AND right` | `BETWEEN` on ancestors | `BETWEEN` | No | Hard |
| **Closure Table** (separate `(ancestor, descendant, depth)` table) | Insert O(depth) rows | Delete + insert paths | Delete descendant rows | Join on descendant | Join on ancestor | Yes (FKs) | Stored |

How to choose:
- **Adjacency List** when the DB has recursive CTEs (all modern ones do), the tree is moderate, and writes are frequent. The default.
- **Path Enumeration** for breadcrumbs and read-mostly trees where a `LIKE` prefix query is enough and you accept the integrity gap. Materialized-path ORM libraries use this.
- **Nested Sets** only for read-only or rarely-changed trees where subtree queries dominate and you need them fast without CTEs. Writes are expensive enough that it's seldom the right call today.
- **Closure Table** when you need fast ancestor *and* descendant queries, referential integrity, and reasonable writes; cost is a table with O(n·depth) rows. The most versatile; the right choice for anything with real integrity requirements. Supports multiple parents (DAGs) with minor extension.

## 6. Quick diagnostic checklist

Run through this when reviewing a schema or query:

- Any column holding a delimited list? → Jaywalking
- Any `id` on an intersection table without a unique constraint on the pair? → ID Required
- Any FK columns without a declared constraint? → Keyless Entry
- Any `(entity, attribute, value)` table? → EAV
- Any `*_type` + `*_id` pair pointing to multiple tables? → Polymorphic Association
- Any `col1, col2, col3` repetition? → Multicolumn Attributes
- Any tables or columns suffixed by period/region? → Metadata Tribbles
- Money in `FLOAT`? → Rounding Errors
- `ENUM`/`CHECK IN (...)` on a set that changes? → 31 Flavors
- `WHERE x != 'y'` on a nullable column? → Fear of the Unknown
- `GROUP BY` with ungrouped columns in `SELECT`? → Ambiguous Groups
- `ORDER BY RAND()`? → Random Selection
- `LIKE '%term%'` for search? → Poor Man's Search Engine
- One query joining to two or more one-to-many tables and aggregating? → Spaghetti Query (Cartesian inflation)
- `SELECT *` in application code? → Implicit Columns
- String-built SQL? → Injection
- No migrations in source control? → Diplomatic Immunity
- Business rules in controllers calling `model.save()`? → Magic Beans
- Tree via `parent_id` with app-side recursion? → Naive Trees; see §5
