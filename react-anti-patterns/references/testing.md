# Testing React with Vitest: mocks as a design signal, MSW only when necessary

Testing Library's guiding principle — *the more your tests resemble the way your software is used,
the more confidence they give* — plus Kent C. Dodds' *Testing Implementation Details* cover the
philosophy. This file is about the mechanical choices, and one idea in particular:

> **A mock is a dependency your code reached out and grabbed instead of being handed. Count them.
> More than one to render a component means the component is doing more than one job.**

Mocks aren't bad; they're *diagnostic*. The fix for a test with four `vi.mock`s is almost never
"write the mocks better." It's `component-responsibilities.md`.

## §1 The test pyramid for a Query/Router app

| Layer | What | Mocks needed |
|---|---|---|
| **Pure functions** (domain rules, formatters, reducers, Zod schemas) | `expect(calculateTotal(items)).toEqual(...)` | None. This should be most of your tests. |
| **API client functions** (`getUser`) | Real `fetch` against **MSW** handlers; assert the parsed, typed result and that bad payloads throw `ZodError` | MSW (it's the layer that owns HTTP) |
| **Presentational components** (props in, callbacks out) | `render(<Row item={item} onSelect={fn} />)`, `userEvent`, assert on the screen | None — maybe a `vi.fn()` for a callback, which is a stub, not a mock of a module |
| **Hooks with Query** (`useUser`) | `renderHook` wrapped in a fresh `QueryClientProvider`; MSW serves the data | MSW + a real provider |
| **Page / integration** | `render(<OrderPage />)` inside real `QueryClientProvider` + router (memory history); MSW; assert what the user sees after interactions | MSW + real providers. Still **zero `vi.mock`**. |
| **E2E** (Playwright) | A handful of critical flows against a real backend or MSW in the browser | — |

If a layer needs something not in its "mocks needed" cell, the code is in the wrong layer.

## §2 Anti-pattern: `vi.mock` to render a component

```ts
// ❌ The component imports useQuery, the router, an analytics module and a feature-flag hook
vi.mock('@tanstack/react-query');
vi.mock('@tanstack/react-router');
vi.mock('@/lib/analytics');
vi.mock('@/hooks/useFlag', () => ({ useFlag: () => true }));
render(<OrderPage />);
```

Each line is a responsibility to extract:

| Mocked thing | What it reveals | Fix |
|---|---|---|
| `react-query` | Component fetches inline | Move to a feature hook; test the page with a real `QueryClient` + MSW |
| `react-router` | Component reads route state deep in the tree | Pass `orderId` as a prop to the inner component; only the route component touches the router; test it with `createMemoryHistory` |
| `analytics` | Side effect in render/handler | Move to mutation `onSuccess`; or inject via a tiny context/prop so tests pass a `vi.fn()` |
| `useFlag` | Hidden global input | Pass the flag as a prop, or provide via its real provider with a test value |

Module mocks also break under the React Compiler and ESM hoisting in ways that cost hours. Treat
`vi.mock` as a last resort for *third-party modules with no test surface* (a `window.matchMedia`
polyfill, a heavy chart lib that doesn't render in jsdom).

## §3 Anti-pattern: mocking `fetch` (or axios) directly

```ts
// ❌ Brittle: asserts on URL strings, misses headers/serialization/error handling
global.fetch = vi.fn().mockResolvedValue({ json: () => ({ id: '1' }) });
```

Kent's *Stop Mocking Fetch* argument: mocking `fetch` tests your mock, not your client. MSW
intercepts at the network layer, so the real `fetch`, real headers, real JSON parsing, real
`res.ok` handling, and your real Zod parse all run.

```ts
// ✅ MSW 2 — handlers describe the server, tests describe the user
// test/handlers.ts
export const handlers = [
  http.get('/api/users/:id', ({ params }) => HttpResponse.json(userFixture({ id: params.id }))),
];
// test/setup.ts
export const server = setupServer(...handlers);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
// in a test: override for one case
server.use(http.get('/api/users/:id', () => HttpResponse.json({ message: 'nope' }, { status: 500 })));
```

`onUnhandledRequest: 'error'` is the important bit: an unexpected request fails the test instead of
silently hanging.

## §4 When MSW is *not* necessary

The user asked for this emphasis, and it's right: MSW is for code that **owns an HTTP call**.
Reaching for it elsewhere means the test is at the wrong layer.

| You're testing… | MSW? | Instead |
|---|---|---|
| A pure function | No | Call it |
| A component that receives data via props | No | Pass props |
| A reducer / Zod schema / `select` function | No | Call it |
| A form component's validation UX | No | Render it with a `vi.fn()` `onSubmit`; type; assert error text |
| A component that calls `useQuery` directly (and you've decided it's the right layer) | Yes | Real `QueryClientProvider` with `retry: false`, MSW |
| The API client | Yes | — |
| A route with a loader | Yes | Memory router + MSW |

Also skip MSW when the data source is injectable: if `useUsers` accepts a `fetcher` or your API
client is provided via context, hand it a fake in-memory implementation. That's dependency
injection, which is faster and clearer than network interception for unit-level tests — reserve
MSW for the integration tier where you want the *real* client in the loop.

## §5 Anti-pattern: testing implementation details

```ts
// ❌ Breaks on any refactor; tells you nothing about the user's experience
expect(result.current.isOpen).toBe(true);
expect(mockSetState).toHaveBeenCalledWith('x');
expect(container.querySelector('.modal--open')).toBeTruthy();
```

```ts
// ✅ Query by role/label the way a user (or screen reader) would
await user.click(screen.getByRole('button', { name: /open settings/i }));
expect(screen.getByRole('dialog', { name: /settings/i })).toBeVisible();
```

Priorities: `getByRole` > `getByLabelText` > `getByText` > `getByTestId`. If you need a test ID,
ask whether the element is missing an accessible name — fixing that improves the product too.

Use `@testing-library/user-event` (`userEvent.setup()`), not `fireEvent`: it fires the full
sequence (pointerdown, focus, keydown…) a real browser would.

## §6 Testing hooks and Query specifically

```ts
// ✅ Fresh client per test — never share cache between tests
function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}
const { result } = renderHook(() => useUser('1'), { wrapper });
await waitFor(() => expect(result.current.isSuccess).toBe(true));
expect(result.current.data?.email).toBe('a@b.c');
```

`retry: false` so error tests don't wait through backoff. For suspense queries, wrap in
`<Suspense>` and `await screen.findByText(...)`. Don't `vi.mock('@tanstack/react-query')` — ever.
TkDodo's *Testing React Query* is the reference.

## §7 Vitest specifics worth knowing

- **`vi.fn()` for callbacks is a stub, not a smell.** `onSubmit={vi.fn()}` is the correct way to
  observe output from a presentational component.
- **Fake timers:** `vi.useFakeTimers()` + `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })`
  or the async user-event breaks. Prefer testing debounced behavior through MSW request counts
  over asserting timer internals.
- **`vi.mock` is hoisted** — factory functions can't reference variables declared above them
  without `vi.hoisted`. If you're fighting this, you're mocking too much.
- **Environment:** `environment: 'jsdom'` (or `happy-dom`) in `vitest.config.ts`;
  `@testing-library/jest-dom/vitest` for `toBeVisible`/`toHaveTextContent`. Vitest 4+ also ships
  **browser mode** — real Chromium via Playwright — which is the right choice when jsdom's layout
  gaps (no `getBoundingClientRect`, no real CSS) make component tests lie.
- **`vi.spyOn` on a module export** only works for ESM if the module is mocked; prefer injecting.
- **Snapshots:** fine for serialized data (a Zod error, a reducer output); a smell for DOM
  (they assert everything and therefore nothing).

## §8 The review question

When a PR adds a test, read the imports and `vi.mock` lines before the assertions. Then ask:

1. Could this test exist with zero mocks if the component took its data as props?
2. Does MSW appear only where a real HTTP call happens?
3. Would a user recognize what the assertions check?

If any answer is no, the feedback is about the component, not the test.
