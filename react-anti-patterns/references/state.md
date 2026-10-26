# State: derived state, props-as-state, and where state should live

The React docs' *Choosing the State Structure* reduces to one test: **if you can compute it, don't
store it.** Every redundant piece of state is a second source of truth that must be kept in sync,
and the sync is always an effect, a forgotten call, or a bug.

## §1 Anti-pattern: storing what you can compute

```tsx
// ❌ fullName is redundant; it will drift
const [firstName, setFirstName] = useState('');
const [lastName, setLastName] = useState('');
const [fullName, setFullName] = useState('');
```

```tsx
// ✅
const fullName = `${firstName} ${lastName}`.trim();
```

Same for `filteredItems`, `isValid`, `totalPrice`, `hasErrors`, `sortedRows`, `selectedItem` (see
§2). The tell is a `set…` that is only ever called in an effect or immediately after another
`set…`.

**"But it's expensive."** Measure first. If it really is (profiler shows it), then:

| Situation | Do |
|---|---|
| React Compiler enabled | Write the plain expression. The compiler memoizes it. |
| No compiler, expensive, inputs are props/state | `useMemo(() => compute(a, b), [a, b])` |
| Expensive and the *inputs* are server data | Put it in TanStack Query's `select` — memoized per query, shared across consumers (`data-fetching.md` §5) |
| Expensive and shared by many components | Compute once in a parent or a custom hook, pass the result down |

Never fall back to `useState` + `useEffect` for memoization; that's §1 of `effects.md`.

## §2 Anti-pattern: storing objects when you mean identity

```tsx
// ❌ When `items` refetches, `selected` points at a stale object
const [selected, setSelected] = useState<Item | null>(null);
```

```tsx
// ✅ Store the ID; derive the object from the current list
const [selectedId, setSelectedId] = useState<string | null>(null);
const selected = items.find(i => i.id === selectedId) ?? null;
```

This single change eliminates most "sync state when the prop changes" effects (`effects.md` §3).
It also works naturally with TanStack Query: the list is cached and refetches; your selection
survives because it's a key, not a snapshot.

## §3 Anti-pattern: props copied into state ("mirroring")

```tsx
// ❌ Ignores all future updates to `color` — the classic "why doesn't it update" bug
function Swatch({ color }) {
  const [c, setC] = useState(color);
```

Ask what you actually want:

| Intent | Pattern |
|---|---|
| Just display the prop | Use the prop directly. No state. |
| Prop is an *initial* value and the component owns edits afterward | Keep the state, **name the prop `initialColor` / `defaultColor`** so the contract is explicit, and reset with `key` when the source entity changes |
| Parent owns the value, child edits it | **Controlled**: `value` + `onChange` props, no internal state |
| Component should work both ways | Controlled-or-uncontrolled: `const isControlled = value !== undefined; const current = isControlled ? value : internal;` — but reach for this only in reusable UI primitives |

The `initialX` naming convention comes straight from the React docs and is worth enforcing in
review: it turns a silent footgun into an obvious contract.

## §4 Anti-pattern: server data in `useState`

```tsx
// ❌ A copy of the server's truth, with none of its lifecycle
const [users, setUsers] = useState<User[]>([]);
useEffect(() => { api.users().then(setUsers); }, []);
```

TkDodo's framing: **TanStack Query is not a data-fetching library, it's an async state manager.**
Server state is owned by the server; your copy is a cache, and caches need staleness, invalidation,
deduplication, and background refresh. `useState` has none of that. Move it to `useQuery` and
delete the state. Client state (`useState`) is for things only the browser knows: whether a modal
is open, what's typed in a search box, which tab is active.

Decision: *Who can change this value without my component knowing?* If the answer is "the server"
or "another user", it is server state.

## §5 Anti-pattern: state that belongs in the URL

```tsx
// ❌ Lost on refresh, un-shareable, back button broken
const [page, setPage] = useState(1);
const [sort, setSort] = useState<'name' | 'date'>('name');
const [filter, setFilter] = useState('');
```

If a user would reasonably bookmark it, share it, or hit "back" to undo it, it is URL state:

```tsx
// ✅ TanStack Router: typed, validated, and the source of truth
export const Route = createFileRoute('/users')({
  validateSearch: z.object({
    page: z.number().int().positive().catch(1),
    sort: z.enum(['name', 'date']).catch('name'),
    filter: z.string().catch(''),
  }),
});

function Users() {
  const { page, sort, filter } = Route.useSearch();
  const navigate = Route.useNavigate();
  const setPage = (page: number) => navigate({ search: (prev) => ({ ...prev, page }) });
```

`.catch()` on each field means malformed URLs degrade gracefully instead of crashing. In
Next.js/Remix the mechanism differs (`useSearchParams` + a Zod parse in a small hook) but the
principle is the same.

## §6 Anti-pattern: many `useState`s that change together

```tsx
// ❌ Impossible states are representable (isLoading && error), updates can be partial
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<T | null>(null);
const [step, setStep] = useState(0);
const [canGoBack, setCanGoBack] = useState(false);
```

| Shape of the problem | Replacement |
|---|---|
| Async request status | It's server state → `useQuery` (status is modeled for you) |
| Several fields that always update together | One `useState` holding an object, or better a discriminated union: `{ status: 'idle' } \| { status: 'editing', draft } \| { status: 'saving' }` |
| Transitions with rules ("can't go back from step 0") | `useReducer` with a typed action union — the reducer is the single place rules live, and it's unit-testable without React |
| Form fields | TanStack Form / RHF — don't model forms by hand (`validation.md`) |

Make impossible states unrepresentable. If `error` and `data` can't both be set, the type
shouldn't allow it.

## §7 Anti-pattern: lifting everything to the top

The opposite failure. State that only one subtree uses, hoisted to `App` "in case" — causing whole-
app re-renders and prop drilling. Kent C. Dodds' **state colocation**: *place state as close to
where it's used as possible.* Start local; lift only when a second component actually needs it;
lift only as far as the nearest common ancestor. See `prop-drilling.md` for what to do when that
ancestor is far away.

## §8 Where does this state live? — the decision table

| Question | Yes → |
|---|---|
| Can it be computed from other state/props? | Derive it (§1) |
| Does the server own it? | TanStack Query (§4) |
| Would a user bookmark/share/back-button it? | URL via Router search params (§5) |
| Is it a form's draft values/errors? | Form library state (`validation.md`) |
| Is it only used by this component? | `useState` here (§7) |
| Used by siblings? | Lift to common parent; pass down, or compose (`prop-drilling.md`) |
| Used across distant parts of the tree, changes rarely (theme, locale, auth user)? | Context |
| Used across distant parts, changes often (cursor position, live counters, undo stack)? | External store (Zustand/Jotai) read via `useSyncExternalStore` under the hood |
| Must survive reload but isn't shareable (draft, "dismissed banner")? | `localStorage` behind `useSyncExternalStore`, parsed with Zod |

Most "global state" questions resolve to the second or third row.
