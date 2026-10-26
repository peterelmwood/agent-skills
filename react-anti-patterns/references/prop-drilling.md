# Prop drilling and data flow

Prop drilling is passing a value through components that don't use it, only so a descendant can.
Two or three levels are fine and explicit. The anti-pattern is when intermediate components become
*coupled to data they don't care about*: renaming a prop touches six files, a `Layout` component
has twelve props it just forwards, and `...rest` spreads hide what's actually flowing.

The fix is **not** "reach for context." Context is the third option, not the first. Work down this
list and stop at the first that fits.

## Decision table

| Situation | Replacement | Why this one |
|---|---|---|
| Intermediate components only *position* the child | **Composition** (§1) | Removes the hop entirely; no new API surface |
| Several children need the same data from one parent | **Lift + pass** is fine up to ~2 levels; beyond, **composition** | Explicit data flow beats hidden |
| The data is server data | **Call `useQuery` where it's used** (§2) | The cache is already global; drilling it is redundant |
| The data is URL state | **`Route.useSearch()` / `useParams()` where it's used** (§2) | Same — the router is already global |
| Rarely-changing, tree-wide values (theme, locale, current user, feature flags) | **Context** (§3) | Correct tool for "ambient" values |
| Frequently-changing, tree-wide values; many writers | **External store** (§4) | Context re-renders every consumer on every change |
| A compound component (Tabs/Tab, Select/Option) | **Context scoped to the compound** (§5) | Internal plumbing; users never see it |

## §1 Composition: pass components, not data

The React docs' own recommendation, and the one most often skipped.

```tsx
// ❌ Layout, Sidebar and Nav all take `user` only to hand it to Avatar
<Layout user={user}>
  ...
</Layout>
function Layout({ user, children }) { return <><Sidebar user={user} />{children}</>; }
function Sidebar({ user }) { return <Nav user={user} />; }
function Nav({ user }) { return <Avatar user={user} />; }
```

```tsx
// ✅ The component that *has* `user` renders the component that *needs* it.
//    Layout/Sidebar/Nav become layout-only and know nothing about users.
<Layout sidebar={<Sidebar nav={<Nav avatar={<Avatar user={user} />} />} />}>
  ...
</Layout>
```

In practice you rarely nest that deep because the real win is in the *middle* layer:

```tsx
// ✅ `children` and named slots
function Page({ header, children }: { header: ReactNode; children: ReactNode }) {
  return <main><header>{header}</header>{children}</main>;
}
<Page header={<UserMenu user={user} />}><Dashboard user={user} /></Page>
```

**Why this is better than context:** data flow stays visible at the call site, the layout
components are reusable with *any* content, and there is no provider to forget in tests.

**When composition doesn't fit:** when the consumer is deep inside a component you don't control,
or when the value genuinely is ambient (every component in the tree might need it). Then §2–§4.

## §2 The data is already global — stop drilling it

Most drilled props are server data or URL state. Both already live in a global, keyed cache:

```tsx
// ❌ Fetched at the top, drilled down four levels
function App() { const { data: user } = useQuery(userQuery(id)); return <Shell user={user} />; }

// ✅ Fetch where you render. Query dedupes: ten components calling the same key = one request.
function Avatar({ userId }: { userId: string }) {
  const { data: user } = useQuery(userQuery(userId));
```

The thing you pass down is the **ID** (or nothing, if it's in the URL), not the object. TkDodo
calls this "React Query as a state manager": `staleTime` controls how often it refetches, and
every consumer is automatically in sync after a mutation invalidates the key.

Same for the URL: `Route.useParams()` / `Route.useSearch()` in the component that needs them.

## §3 Context: for ambient, slow-changing values

```tsx
// ✅ Theme, locale, auth session, feature flags, a DI'd API client
const ThemeContext = createContext<Theme | null>(null);
export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (ctx === null) throw new Error('useTheme must be used within <ThemeProvider>');
  return ctx;
}
```

Rules that keep context from becoming the anti-pattern:

- **Throw on missing provider.** A `null` default silently produces wrong UI; the throw turns a
  class of bugs into a stack trace.
- **Expose a hook, not the context object.** Consumers import `useTheme`, never `ThemeContext`.
- **Split state from dispatch** when both are provided: `<StateContext>` and `<DispatchContext>`.
  Components that only dispatch won't re-render when state changes.
- **Keep the value stable.** `value={{ user, setUser }}` creates a new object every render and
  re-renders every consumer. With the React Compiler on this is handled; without it, `useMemo` the
  value.
- **Scope providers tightly.** A context for a wizard goes around the wizard, not at the app root.

**When context is wrong:** the value changes many times per second (every consumer re-renders), or
only one or two components need it (composition is simpler), or you're using it to avoid
*thinking* about data flow.

## §4 External stores for high-frequency shared client state

Context re-renders every subscriber on any change. For values that change often and are read in
many places — selection in a canvas editor, an undo stack, a WebSocket's live ticker, playback
position — use a store with selector-based subscriptions:

```tsx
// ✅ Zustand: only components whose selected slice changed re-render
const useEditor = create<EditorState>((set) => ({
  selectedIds: new Set(), select: (id) => set((s) => ({ selectedIds: new Set(s.selectedIds).add(id) })),
}));
const selectedIds = useEditor((s) => s.selectedIds);
```

Jotai fits when state is naturally atomic and composed (derived atoms). Both are built on
`useSyncExternalStore` and need no provider — which is also why they're easy to test: reset the
store in `beforeEach`.

Guardrail: before adding a store, re-ask whether the value is server state (→ Query) or URL state
(→ Router). Global client stores filled with API responses are the most common misuse.

## §5 Compound components: context as internal plumbing

```tsx
// ✅ The consumer sees a clean API; context is an implementation detail
<Tabs defaultValue="a">
  <Tabs.List><Tabs.Trigger value="a">A</Tabs.Trigger></Tabs.List>
  <Tabs.Content value="a">…</Tabs.Content>
</Tabs>
```

This is the one case where context is the *first* choice: `Tabs` owns the state, `Trigger` and
`Content` read it, and the alternative (drilling `activeTab`/`setActiveTab` into every child) is
exactly the smell. Libraries like Radix and Ark UI are built this way; so should your own
primitives be.

## §6 Related smells

- **`...rest` passthrough everywhere.** Legitimate on a thin wrapper around a DOM element
  (`<Button {...rest}>`). A smell when it's hiding a drilled prop — grep where it lands.
- **A `config` / `handlers` / `callbacks` object drilled as one prop.** Drilling with extra steps.
  Usually the handlers are events that belong next to the state (lift the state, or use a reducer
  via context §3).
- **Render props to escape drilling.** Still valid for inversion of control (`<List renderItem>`),
  but if it's solely to get data to a leaf, composition with `children` is cleaner.
- **`React.memo` to "fix" re-renders caused by drilling.** Treats the symptom. Fix the data flow.
