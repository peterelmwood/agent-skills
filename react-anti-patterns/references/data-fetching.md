# Data fetching: TanStack Query, and the anti-patterns inside it

Assumed baseline: server data goes through `useQuery` / `useSuspenseQuery` / `useMutation`
(`effects.md` §4, `state.md` §4). This file covers the mistakes people make *after* adopting Query,
and how routing changes the picture. Much of it is distilled from TkDodo's *Practical React Query*
series, which remains the best long-form source.

## §1 Anti-pattern: unstructured query keys

```ts
// ❌ Collisions, impossible to invalidate precisely, typos everywhere
useQuery({ queryKey: ['users'], ... });
useQuery({ queryKey: ['user', id], ... });
useQuery({ queryKey: ['users-list', filters], ... });
```

```ts
// ✅ Key factory + queryOptions: one place keys live, typed data everywhere
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: UserFilters) => [...userKeys.lists(), filters] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};
export const userQuery = (id: string) => queryOptions({
  queryKey: userKeys.detail(id),
  queryFn: ({ signal }) => getUser(id, signal),
});
```

Keys are hierarchical so `invalidateQueries({ queryKey: userKeys.all })` hits everything, and
`userKeys.lists()` hits only lists. **Everything the `queryFn` depends on goes in the key** — the
eslint plugin (`@tanstack/eslint-plugin-query`) enforces this; enable it.

`queryOptions()` is the v5 way: it gives `useQuery`, `useSuspenseQuery`, `prefetchQuery`,
`ensureQueryData`, and `getQueryData` the same typed object, so `queryClient.getQueryData(userQuery(id).queryKey)`
is typed as `User | undefined`.

## §2 Anti-pattern: `enabled` as control flow, or `useQuery` in a handler

```tsx
// ❌ Trying to fetch on click with a query
const [go, setGo] = useState(false);
useQuery({ queryKey: ['search', q], queryFn: ..., enabled: go });
```

Queries describe *what data this screen needs*; they are declarative. A click that performs an
action is a **mutation**, even if it "reads" — or it is a change of *state the query depends on*:

| Intent | Pattern |
|---|---|
| "Search when the user submits" | Put `q` in state/URL on submit; the query for `['search', q]` runs because its key changed |
| "Fetch details for the row I clicked" | `setSelectedId(id)`; a query keyed on `selectedId` (with `enabled: !!selectedId` for the null case — that's the legitimate use of `enabled`) |
| "Call an endpoint that *does* something" | `useMutation` |
| "Preload before navigation" | `queryClient.prefetchQuery(userQuery(id))` on hover/focus, or Router loader |

`enabled: false` is for *dependent* queries (wait for `userId` to exist) and feature flags, not for
imperative triggering.

## §3 Anti-pattern: syncing query data into local state

```tsx
// ❌ Loses background updates; the classic "why is my list stale after a mutation"
const { data } = useQuery(usersQuery);
const [users, setUsers] = useState([]);
useEffect(() => { if (data) setUsers(data); }, [data]);
```

Reasons people do this, and what to do instead:

| "I copy it because…" | Instead |
|---|---|
| I need to edit it locally (a form) | `defaultValues` from `data` in the form library, keyed by `data.id` so it resets when the entity changes. The form owns the draft; Query owns the truth. |
| I need to transform it | `select` (§5) |
| I want it to not change under the user mid-edit | `staleTime` / `refetchOnWindowFocus: false` for that query, or snapshot into the form as above |
| I need to add client-only fields (selected, expanded) | Keep those in client state keyed by ID: `Set<string>` of expanded IDs; derive the merged view in render |

## §4 Anti-pattern: manual cache updates after every mutation

```ts
// ❌ Reimplementing the server's logic on the client to patch the cache
onSuccess: (newUser) => qc.setQueryData(userKeys.lists(), (old) => sortAndInsert(old, newUser))
```

Default to **invalidation**: `onSuccess: () => qc.invalidateQueries({ queryKey: userKeys.all })`.
The server is the source of truth; refetching costs one request and can't drift.

Use `setQueryData` only for: (a) **optimistic updates** where latency is visible, with
`onMutate` snapshot + `onError` rollback + `onSettled` invalidate (the documented recipe), or
(b) seeding a detail query from a list you already have (`initialData`/`placeholderData`).

Return `qc.invalidateQueries(...)` (a promise) from `onSuccess` if the mutation's `isPending`
should stay true until the refetch lands — it avoids a flash of stale UI.

## §5 Anti-pattern: transforming in render, or in the `queryFn`, when `select` fits

```tsx
// ❌ Transform runs every render for every consumer
const { data } = useQuery(usersQuery);
const names = data?.map(u => u.name).sort();
```

| Where to transform | When |
|---|---|
| In the **API client** (before Zod parse / as part of it) | Normalizing the wire format (snake→camel, ISO→Date via codec). Everyone wants it; cache the clean shape. |
| In **`select`** | Per-consumer derivations: `select: (users) => users.map(u => u.name)`. Memoized per query data reference; consumers re-render only when *their* selection changes. |
| In **render** | Cheap one-offs. With the compiler on, this is fine for most cases too. |

`select` with an inline arrow is re-run on every render of that component (not every consumer);
stabilize with a module-level function or `useCallback` if it's heavy. Query v5 structurally shares
results, so a `select` that returns the same shape won't cause re-renders.

## §6 Anti-pattern: `isLoading` branches in every component

```tsx
// ❌ Every leaf handles pending + error; nested spinners; inconsistent error UI
if (isPending) return <Spinner />; if (error) return <Oops />;
```

```tsx
// ✅ Route-level boundaries; leaves assume data
// router/page level:
<ErrorBoundary fallback={<RouteError />}>
  <Suspense fallback={<PageSkeleton />}>
    <OrderPage />
  </Suspense>
</ErrorBoundary>
// in OrderPage:
const { data: order } = useSuspenseQuery(orderQuery(id)); // `data` is non-optional
```

`useSuspenseQuery` removes the `undefined` branch from the type and centralizes pending/error UI.
TanStack Router has `pendingComponent` / `errorComponent` per route for exactly this. Keep
`useQuery` + `isPending` for *secondary* data where you want to render the page around a hole
(a sidebar widget, a "related items" strip) — Suspense would block the whole route for it.

`isPending` vs `isLoading` (v5): `isPending` = no data yet; `isLoading` = `isPending && isFetching`
(first load in flight). A `disabled` query is pending but not loading.

## §7 Anti-pattern: waterfalls

```tsx
// ❌ Child can't start its fetch until parent's resolves and it renders
function Order({ id }) { const { data } = useSuspenseQuery(orderQuery(id)); return <Customer id={data.customerId} />; }
```

| Fix | Use when |
|---|---|
| **Router loader + `ensureQueryData`** — both queries kicked off before render | You use TanStack Router (or any loader-based router). This is the primary answer. |
| **`useSuspenseQueries` / `useQueries`** at the parent for parallel independent data | No loader, data is independent |
| Include related data in the response (`/orders/:id?include=customer`) | You control the API and the join is cheap server-side |
| `prefetchQuery` on hover/intent | Navigations |

```ts
// ✅ Router + Query: loader starts fetches, components read from cache
export const Route = createFileRoute('/orders/$orderId')({
  loader: ({ context: { queryClient }, params }) =>
    Promise.all([
      queryClient.ensureQueryData(orderQuery(params.orderId)),
      queryClient.ensureQueryData(customerForOrderQuery(params.orderId)),
    ]),
  component: OrderPage,   // uses useSuspenseQuery(orderQuery(orderId)) — instant from cache
});
```

The loader is a *prefetch*; the component still subscribes via `useSuspenseQuery` so it gets
background updates. Don't return loader data and prop-drill it — that's `prop-drilling.md` §2
again.

## §8 `staleTime` is the most important option you're not setting

Default `staleTime: 0` means every new mount refetches. That's correct for a default (always
fresh) and wrong for most apps (chatty). Set a global default — TkDodo suggests something like
`staleTime: 60_000` — in the `QueryClient`, then tune per query: `Infinity` for config/reference
data, short for dashboards. Pair with `gcTime` only if memory matters.

## §9 Mutations: side effects go on the mutation, not in the component

```tsx
// ✅ Hook owns invalidation + toast; component just calls mutate
export function useDeleteUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteUser,
    onSuccess: (_, id) => { qc.removeQueries({ queryKey: userKeys.detail(id) });
                            return qc.invalidateQueries({ queryKey: userKeys.lists() }); },
    onError: (e) => toast.error(describe(e)),
  });
}
```

Use the per-call `mutate(vars, { onSuccess })` only for UI-local reactions (close *this* dialog,
navigate from *this* page). Note those per-call callbacks don't fire if the component unmounts
first; the hook-level ones do.

React 19 **Actions** (`useActionState`, `<form action={fn}>`) overlap with mutations for
form-submit flows. In a Router/Query app, `useMutation` stays the primary tool because it
integrates with the cache; in an RSC app, Server Actions + `revalidatePath` take that role.

## §10 Checklist

- Every `queryFn` returns Zod-parsed data; every dependency is in the key.
- Keys come from a factory; `queryOptions()` objects are shared with loaders.
- No `useState` mirrors of query data; no `useEffect(() => setX(data))`.
- `staleTime` is set globally and intentionally.
- Mutations invalidate by default; `setQueryData` only for optimistic/seed.
- Pending/error handled at route boundaries with `useSuspenseQuery`; `isPending` only for secondary data.
- Loaders start parallel fetches; components subscribe.
- `@tanstack/eslint-plugin-query` is on.
