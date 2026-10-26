# Mixed responsibilities: the god component

A component has one job: **turn some inputs into UI, and route user intent back out.** Everything
else — fetching, parsing, transforming, deciding, persisting — is a responsibility that can be
pulled out, named, and tested on its own. The test for whether a component has too many
responsibilities is not line count; it is **how many things you'd have to fake to render it**
(see `testing.md`). Each mock is a dependency the component reached out and grabbed instead of
being handed.

## Recognize it

```tsx
// ❌ One component: HTTP, parsing, business rules, form state, validation, UI, analytics
function OrderPage({ orderId }) {
  const [order, setOrder] = useState<any>(null);
  const [items, setItems] = useState([]);
  const [discount, setDiscount] = useState('');
  const [discountError, setDiscountError] = useState('');
  const [saving, setSaving] = useState(false);
  useEffect(() => { fetch(`/api/orders/${orderId}`).then(r => r.json()).then(o => { setOrder(o); setItems(o.items); }); }, [orderId]);
  const total = items.reduce(/* tax rules, rounding, currency */);
  const applyDiscount = async () => {
    if (!/^[A-Z0-9]{6}$/.test(discount)) { setDiscountError('Invalid'); return; }
    setSaving(true); await fetch(...); track('discount_applied'); setSaving(false);
  };
  return ( /* 150 lines of JSX */ );
}
```

Signals: `any`-typed state; an effect that fetches; business arithmetic inline; regex validation;
`fetch` in a handler; `track()` calls scattered through; more than ~5 `useState`s; a test that
mocks `fetch`, `track`, and the router to render it.

## The layering that replaces it

```
┌─────────────────────────────────────────────────────────────┐
│ Route / Page component       — composes; knows the URL       │
├─────────────────────────────────────────────────────────────┤
│ Feature hooks (useOrder, useApplyDiscount)                   │
│   — TanStack Query wrappers; the *only* place keys live      │
├─────────────────────────────────────────────────────────────┤
│ Domain functions (calculateTotal, discountCodeSchema)        │
│   — pure TS; zero React imports; most of your unit tests     │
├─────────────────────────────────────────────────────────────┤
│ API client (getOrder, applyDiscount)                         │
│   — fetch + Zod parse; the trust boundary                    │
├─────────────────────────────────────────────────────────────┤
│ Presentational components (OrderSummary, DiscountForm)       │
│   — props in, callbacks out; render with no providers        │
└─────────────────────────────────────────────────────────────┘
```

```tsx
// api/orders.ts — boundary
export const Order = z.object({ id: z.string(), items: z.array(LineItem), currency: z.enum(['USD','EUR']) });
export type Order = z.infer<typeof Order>;
export const getOrder = (id: string, signal?: AbortSignal) =>
  fetch(`/api/orders/${id}`, { signal }).then(r => r.json()).then(Order.parse);

// domain/pricing.ts — pure
export function calculateTotal(items: LineItem[], currency: Currency): Money { /* rules */ }

// features/orders/queries.ts — server state
export const orderQuery = (id: string) => queryOptions({ queryKey: ['orders', id], queryFn: ({ signal }) => getOrder(id, signal) });
export function useApplyDiscount(orderId: string) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (code: DiscountCode) => applyDiscount(orderId, code),
                       onSuccess: () => qc.invalidateQueries({ queryKey: ['orders', orderId] }) });
}

// features/orders/OrderPage.tsx — composition
function OrderPage() {
  const { orderId } = Route.useParams();
  const { data: order } = useSuspenseQuery(orderQuery(orderId));
  const apply = useApplyDiscount(orderId);
  return (
    <>
      <OrderSummary items={order.items} total={calculateTotal(order.items, order.currency)} />
      <DiscountForm onSubmit={(code) => apply.mutate(code)} isPending={apply.isPending} />
    </>
  );
}
```

Now: `calculateTotal` is tested with plain `expect`. `OrderSummary` and `DiscountForm` render
with props and no providers. `getOrder` is tested once with MSW (it owns the fetch). `OrderPage` is
one integration test with MSW and a `QueryClientProvider`. **No `vi.mock` anywhere.**

## Which extraction, when

| Responsibility found inline | Extract to | When *not* to extract |
|---|---|---|
| `fetch`/axios + response handling | API client function returning parsed, typed data | Never leave it inline |
| `useQuery`/`useMutation` with keys | A `queryOptions` factory + a feature hook | A key used in exactly one place can stay inline — but the factory costs one line and enables prefetch/invalidation elsewhere |
| Calculations, formatting, business rules | Pure function in `domain/` or `lib/` | A one-liner (`items.length > 0`) stays inline |
| Several related `useState` + handlers | Custom hook returning `{ state, actions }`, or `useReducer` | If the hook is only ever used by one component *and* has no logic, it's just moving lines |
| Validation | Zod schema; form library | Never hand-roll (`validation.md`) |
| Analytics / logging / toasts side effects | Call from the mutation's `onSuccess`/`onError`, or an event-handler helper | — |
| A large JSX block with its own concerns | Presentational component taking props | If the extracted component would need 10+ props, you've split in the wrong place — split by *concern*, not by screen region |
| Conditional rendering of 3+ modes | One component per mode + a small switch | — |

## The hook-extraction trap

```tsx
// ❌ Extracting the mess into a hook does not fix the mess
function useOrderPage(orderId) { /* the same 80 lines, now harder to read */ }
```

A custom hook is a refactor of *React logic* (state + effects + queries that belong together). It
is not a place to hide a fetch, a parser, and a business rule. Those should each go to their own
non-React module first; the hook composes them. Test: if the hook could be tested only by
rendering a component with providers, it still has too many responsibilities.

## Presentational vs. container, 2026 edition

Dan Abramov retired the strict container/presentational split when hooks arrived, but the
*spirit* survives as the lower layer of the diagram above: **most components should be renderable
with props alone.** The components that call hooks (`useQuery`, `useSearch`, `useForm`) are the
thin ones near the route. Error and loading UI belong to `<ErrorBoundary>` and `<Suspense>` at the
route level, not to every leaf — which is why `useSuspenseQuery` in the page and plain props in
the leaves is the default shape.

## Size heuristics (guidelines, not rules)

- A component you can't summarize in one sentence without "and".
- More than ~5 `useState`s → a reducer, a form library, or server state.
- More than one `useEffect` → check `effects.md`; most are removable.
- More than ~7 props → the component is doing several jobs or the props should be grouped into a
  typed object with a name (`<Chart series={series} />`, not eleven loose arrays).
- A test with `vi.mock` → the dependency should be a prop or a hook you can wrap with a real
  provider.
