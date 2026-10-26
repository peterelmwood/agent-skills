# Effects: when `useEffect` is the wrong tool

Start from the React team's own framing: **an Effect synchronizes your component with an external
system.** The DOM (beyond what JSX renders), a WebSocket, a timer, a third-party widget, a browser
API. If there is no external system, there is no Effect — there is a calculation, an event handler,
or a data-fetching library's job.

The reason this matters: an effect runs *after* render, so any state it sets causes a second render
with intermediate, inconsistent UI in between. In StrictMode (dev) it runs twice. Under the React
Compiler, effects are the one place the compiler cannot help you, because it can't know what the
external system needs. Every unnecessary effect is a place where your UI is briefly wrong and your
dependency array is a bug waiting to happen.

## Decision tree

```
What triggers this code?
├─ "This value can be computed from props/state"       → calculate during render (§1)
├─ "The user clicked / typed / submitted"              → event handler (§2)
├─ "A prop changed and I need to reset/adjust state"   → key prop (§3a) or set-during-render (§3b)
├─ "I need data from the server"                       → TanStack Query (§4)
├─ "I need to notify the parent"                       → call the callback from the event (§5)
├─ "Something external changed and I need to re-read"  → useSyncExternalStore (§6)
├─ "I need to run once at app start"                   → module scope / main.tsx (§7)
└─ "I need the DOM / socket / timer / widget to match
    this value"                                        → useEffect — a real one (§8)
```

## §1 Anti-pattern: effect to derive state

```tsx
// ❌ Two renders, stale between them, extra state to keep in sync
const [items, setItems] = useState<Item[]>([]);
const [total, setTotal] = useState(0);
useEffect(() => { setTotal(items.reduce((s, i) => s + i.price, 0)); }, [items]);
```

```tsx
// ✅ It's just a value
const total = items.reduce((s, i) => s + i.price, 0);
```

**When to add `useMemo`:** only if the calculation is measurably expensive (profile it — thousands of
items, nested loops) *and* the React Compiler is not enabled. With the compiler on, write the plain
version; it memoizes for you. See `state.md` for the full treatment of derived state.

## §2 Anti-pattern: effect as event handler

```tsx
// ❌ "When submitted becomes true, send the analytics event"
const [submitted, setSubmitted] = useState(false);
useEffect(() => { if (submitted) track('form_submitted', { plan }); }, [submitted, plan]);
```

This fires again if `plan` changes after submission, fires twice in StrictMode, and models a
one-time action as a persistent state. The trigger is a *user action*, so:

```tsx
// ✅ The action lives where it happens
function handleSubmit() {
  track('form_submitted', { plan });
  submit();
}
```

**Rule of thumb from the docs:** if the code should run because *the user did something specific*,
it's an event handler. If it should run because *the component is on screen*, it's an effect.

## §3 Anti-pattern: effect to sync props into state

```tsx
// ❌ "Reset the draft when the user changes"
function Editor({ user }) {
  const [draft, setDraft] = useState(user.bio);
  useEffect(() => { setDraft(user.bio); }, [user.bio]);
}
```

Renders with the old draft first, then flashes to the new one. Two replacements — choose by scope:

### §3a Reset *everything* when an identity changes → `key`

```tsx
// ✅ A different user is a different component instance
<Editor key={user.id} user={user} />
```

Use this when the whole subtree should start fresh (forms, editors, wizards keyed by the thing they
edit). It is the cheapest and most obviously-correct option. Prefer it.

### §3b Adjust *one piece* of state when a prop changes → set state during render

```tsx
// ✅ React re-renders immediately with the new state, no intermediate frame
function List({ items }) {
  const [selection, setSelection] = useState<Item | null>(null);
  const [prevItems, setPrevItems] = useState(items);
  if (items !== prevItems) {
    setPrevItems(items);
    setSelection(null);
  }
}
```

Use only when `key` would throw away state you need to keep. It reads oddly — comment it. And ask
first whether you can **store the ID instead of the object** (`selectedId`) and derive the selection:
`const selection = items.find(i => i.id === selectedId) ?? null`. That usually removes the problem
entirely (see `state.md` §2).

## §4 Anti-pattern: effect to fetch data

```tsx
// ❌ The 2019 pattern. Race conditions, no cache, no dedupe, refetches on every mount,
//    no retry, loading/error state hand-rolled, cancelled requests ignored.
useEffect(() => {
  let cancelled = false;
  setLoading(true);
  fetch(`/api/users/${id}`).then(r => r.json()).then(data => {
    if (!cancelled) { setUser(data); setLoading(false); }
  });
  return () => { cancelled = true; };
}, [id]);
```

```tsx
// ✅ TanStack Query owns the lifecycle
const { data: user, isPending, error } = useQuery({
  queryKey: ['users', id],
  queryFn: ({ signal }) => fetchUser(id, { signal }),   // signal → real cancellation
});
```

Why this is not "just another library": the fetch-in-effect pattern needs you to re-implement
caching, deduping, stale-while-revalidate, retries, cancellation, window-focus refetch, and
invalidation after mutations — and every hand-rolled version has the race condition shown above.
Full treatment, including when loaders/RSC change the answer, in `data-fetching.md`.

## §5 Anti-pattern: effect to notify the parent

```tsx
// ❌
useEffect(() => { onChange(value); }, [value, onChange]);
```

Fires on mount with the initial value (usually unwanted), fires when `onChange` identity changes,
and introduces a frame where parent and child disagree. Instead, call `onChange` **in the same
handler that calls `setValue`**. If you find you can't — because `value` is set in many places —
that's a sign the state should be lifted to the parent and passed down (controlled component), which
removes the sync entirely.

## §6 Anti-pattern: effect to subscribe to a browser/external store

```tsx
// ❌ Works, but tears under concurrent rendering and is 15 lines of boilerplate
const [online, setOnline] = useState(navigator.onLine);
useEffect(() => {
  const on = () => setOnline(true), off = () => setOnline(false);
  window.addEventListener('online', on); window.addEventListener('offline', off);
  return () => { /* remove both */ };
}, []);
```

```tsx
// ✅ Purpose-built hook; React guarantees consistency
const online = useSyncExternalStore(
  (cb) => { window.addEventListener('online', cb); window.addEventListener('offline', cb);
            return () => { window.removeEventListener('online', cb); window.removeEventListener('offline', cb); }; },
  () => navigator.onLine,
  () => true,   // server snapshot
);
```

Use `useSyncExternalStore` for anything with a subscribe/getSnapshot shape: `matchMedia`,
`localStorage` (with a `storage` listener), Zustand-style stores, a WebSocket's last message.

## §7 Anti-pattern: effect to "run once on app start"

```tsx
// ❌ Runs on every mount of this component, twice in StrictMode dev
useEffect(() => { initAnalytics(); loadFeatureFlags(); }, []);
```

If it should truly happen once per *application*, it does not belong in a component at all:

```tsx
// ✅ main.tsx / module scope
if (typeof window !== 'undefined') { initAnalytics(); }
```

Or, if it has a result the tree needs (feature flags, config), it is **data** → a `useQuery` with
`staleTime: Infinity` at the root, so every consumer reads it and it fetches exactly once.

## §8 Legitimate effects — and how to write them well

Real effects: focusing an input, attaching a non-React widget (map, chart, editor), opening a
WebSocket/EventSource, `document.title`, `IntersectionObserver`, timers whose *existence* depends on
state. For these:

**Separate reactive from non-reactive code with `useEffectEvent` (stable in React 19.2).**

```tsx
// ❌ `theme` in the deps reconnects the socket every time the user toggles dark mode
useEffect(() => {
  const conn = connect(roomId);
  conn.on('connected', () => showToast(`Connected`, theme));
  return () => conn.disconnect();
}, [roomId, theme]);
```

```tsx
// ✅ The effect depends on roomId (reactive); the toast reads latest theme without re-running it
const onConnected = useEffectEvent(() => showToast('Connected', theme));
useEffect(() => {
  const conn = connect(roomId);
  conn.on('connected', () => onConnected());
  return () => conn.disconnect();
}, [roomId]);
```

The pre-19.2 equivalent was a "latest ref" (`useRef` updated each render). Replace those with
`useEffectEvent` when you upgrade; the ESLint plugin (`eslint-plugin-react-hooks` v6+) understands
it and won't demand it in the deps.

**Never silence `exhaustive-deps`.** A disabled lint rule is an effect with a lie in it. If the
array is wrong, the *effect* is wrong: usually it's one of §1–§7 in disguise, or it needs
`useEffectEvent`, or the dependency should be a primitive (`user.id`, not `user`).

**Always return cleanup** for anything you subscribe, open, or start. StrictMode's double-invoke in
dev exists precisely to surface missing cleanups.

**`useLayoutEffect`** only for measuring layout before paint (tooltip position, scroll restoration).
It blocks painting; the default is `useEffect`.

## Quick reference: "I want to…" → use

| Intent | Use |
|---|---|
| Compute from props/state | plain expression (+ compiler) |
| React to a click/submit/keypress | event handler |
| Reset state when an entity changes | `key` |
| Adjust state when a prop changes | store an ID & derive; else set-during-render |
| Load server data | `useQuery` / route loader |
| Save/delete server data | `useMutation` / form Action |
| Tell parent about a change | call the callback in the handler |
| Read a mutable external value | `useSyncExternalStore` |
| Run once per app | module scope |
| Sync DOM/socket/timer/widget | `useEffect` + cleanup + `useEffectEvent` for the non-reactive parts |
| Measure layout before paint | `useLayoutEffect` |
