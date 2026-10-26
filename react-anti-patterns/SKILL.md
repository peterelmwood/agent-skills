---
name: react-anti-patterns
description: Catalog of React anti-patterns and the patterns that replace them, with guidance on WHICH replacement fits WHEN. Use this skill whenever writing, reviewing, refactoring, or debugging React/TypeScript code — including any mention of useEffect, re-renders, prop drilling, "state out of sync", derived state, forms, validation, data fetching, tables, routing, or testing React components. Also use it when someone asks "is this good React?", "how should I structure this component?", or when a component is hard to test. Covers TanStack (Query, Router, Table, Form), Zod, MSW, Vitest, and React 19 features (useEffectEvent, React Compiler, Actions).
---

# React Anti-Patterns → Patterns

This skill exists because most React bugs are not React bugs. They are *modeling* bugs: state that
shouldn't exist, effects that are really event handlers, components doing three jobs, and
validation that trusts the shape of data nobody checked. The fix is almost never "add another
hook" — it is to put the responsibility where it belongs. This file tells you how to recognize the
smell and pick the right replacement; the `references/` files go deep on each family.

## How to use this skill

1. **Identify the family** using the smell table below. Most real code has 2–3 overlapping smells
   (an effect that syncs derived state *because* of prop drilling, say). Name all of them.
2. **Read the matching reference file** before proposing a fix. Each file has a decision table for
   choosing between alternatives — there is rarely one right answer, and the point is to say *why*
   this one fits here.
3. **Prefer deletion over addition.** The best refactor usually removes a `useState`, a `useEffect`,
   or a mock. If your fix adds more hooks than it removes, re-read the reference.
4. **When reviewing**, lead with the anti-pattern name, the concrete bug or cost it causes *in this
   code* (not in theory), then the replacement and why that replacement over the others.

## Smell table

| You see… | Family | Read |
|---|---|---|
| `useEffect` that calls `setState` from props/state; effect that fetches with `useState` + `isLoading`; effect that runs "on mount" to kick off logic; effect reacting to a value to call a callback; `eslint-disable react-hooks/exhaustive-deps` | **Effects** | `references/effects.md` |
| `useState` initialized from a prop; state that could be computed from other state; `useMemo` everywhere; "the list and the filtered list are both in state"; `useState` for data the server owns | **State & derived state** | `references/state.md` |
| A prop passed through 3+ components untouched; `...rest` spread through layers; a `config`/`handlers` object threaded everywhere; context used for everything | **Prop drilling & data flow** | `references/prop-drilling.md` |
| A component that fetches, transforms, validates, and renders; 300+ line component; 8+ `useState`s; a test file that mocks 4 modules to render one component | **Mixed responsibilities** | `references/component-responsibilities.md` |
| `if (!email.includes('@'))`; hand-written `isValid` functions; `as User` casts on `fetch` results; TypeScript interfaces that duplicate a Zod schema; untyped `useSearchParams` | **Validation** | `references/validation.md` |
| `useEffect` + `fetch`; `useState` for server data; manual `isLoading`/`error` state; refetch-on-focus reimplemented; cache invalidation via global event bus; `queryKey: ['data']` | **Data fetching** | `references/data-fetching.md` |
| Hand-rolled sort/filter/paginate in a component; `<table>` logic coupled to one UI | **Tables** | `references/tanstack-table.md` |
| `vi.mock` of hooks/modules to render a component; mocking `fetch` globally in every test; testing `state` values instead of what the user sees; MSW used for a pure function | **Testing & mocking** | `references/testing.md` |

## The five principles behind every reference file

These are the lenses. If a piece of code violates one, you will find its anti-pattern below.

1. **Render is a pure function of props and state.** Anything you can compute during render, compute
   during render. The React Compiler (stable since 1.0) makes manual memoization mostly unnecessary,
   so "but it would recompute every render" is no longer an excuse to cache in state.
2. **Effects synchronize with external systems; events respond to user actions.** If the trigger is
   "the user did X", it belongs in a handler. If the trigger is "this value changed and I need the
   DOM / a socket / a subscription to match", it is an effect. If the trigger is "data arrived from
   the server", that's TanStack Query's job, not yours.
3. **Server state is not client state.** Data the server owns (users, orders, search results) has a
   lifecycle — stale, refetching, invalidated — that `useState` cannot model. Use TanStack Query for
   it and keep `useState` for things that exist *only* in the browser (open/closed, draft input,
   selected tab).
4. **Validate at the boundary, trust inside.** Every place data crosses from "unknown" to "known"
   (network response, URL, form input, localStorage, `postMessage`) gets a Zod schema. Inside that
   boundary, use the inferred type and stop checking. Hand-written validation is a boundary you
   forgot to name.
5. **The mock count is a design metric.** If a component test needs more than one mock to render,
   the component has more than one responsibility. Fix the component, not the test.

## Replacement library quick-reference

Use these as the default answer; the reference files explain the exceptions.

| Concern | Default | When something else fits |
|---|---|---|
| Fetching, caching, mutations | **TanStack Query v5** | Real-time streams → `useSyncExternalStore` or Query + WebSocket invalidation; framework with RSC/loaders → still use Query for client cache, hydrate from loader |
| Routing, URL state, route-level data | **TanStack Router** | Next.js/Remix app → use that router, but keep URL-as-state and `validateSearch`-style Zod parsing |
| Headless tables | **TanStack Table v8** | Tiny static list (< 1 screen, no sort/filter) → plain `.map()` |
| Forms | **TanStack Form v1** (Standard Schema → Zod directly, no adapter) | Existing React Hook Form codebase → keep RHF with `zodResolver`; a single input with no cross-field rules → controlled `useState` + Zod on submit |
| Schema + types | **Zod 4** (`z.infer`, `z.email()`, discriminated unions, codecs) | Valibot/ArkType if bundle size is the constraint — same Standard Schema interface |
| API mocking in tests | **MSW 2** — *only* for integration-level tests of components that own a fetch | Unit test of a hook/component that takes data as props → no MSW, just props |
| Test runner | **Vitest** + Testing Library + `user-event` | — |
| Client-only global state | React context for low-frequency values; **Zustand/Jotai** for high-frequency or cross-tree | Most "global state" is actually server state (→ Query) or URL state (→ Router) |

## Review checklist (copy into PR comments)

- [ ] Every `useEffect`: name the external system it syncs with. If you can't, it's not an effect.
- [ ] Every `useState`: can it be derived? Is it server data? Does it belong in the URL?
- [ ] Every prop passed through an intermediate component: could composition (`children`) remove the hop?
- [ ] Every component: one sentence describing what it does. If the sentence has "and", split.
- [ ] Every `fetch`/axios call: is the response parsed with a Zod schema? Is the request through `useQuery`/`useMutation`?
- [ ] Every form: is validation a schema the server could also run?
- [ ] Every test: count the mocks. More than one → the component under test is doing too much.
- [ ] Every `useMemo`/`useCallback`: is the compiler on? If yes, delete unless a dependency identity is *required* (e.g., passed to an effect).

## Sources this skill draws on

- React docs: *You Might Not Need an Effect*, *Separating Events from Effects*, *Choosing the State Structure*, *Passing Data Deeply with Context*, React 19.2 release notes (`useEffectEvent`, `<Activity>`, Actions), React Compiler 1.0 docs.
- TanStack docs: Query v5 (query keys, `select`, invalidation, `useSuspenseQuery`), Router (`validateSearch`, loaders + Query integration), Table v8 (headless model), Form v1 (Standard Schema).
- Dominik Dorfmeister (TkDodo), *Practical React Query* series — especially "Effective React Query Keys", "React Query as a State Manager", "Why You Want React Query", "Testing React Query".
- Kent C. Dodds — *Application State Management with React*, *Prop Drilling*, *Testing Implementation Details*, *Stop Mocking Fetch*, *State Colocation*.
- Dan Abramov — *A Complete Guide to useEffect*, *Writing Resilient Components*.
- Zod 4 release notes (Standard Schema, `z.codec`, top-level string formats); MSW 2 docs ("Why mock at the network level").
- Testing Library guiding principle: *the more your tests resemble the way your software is used, the more confidence they can give you.*
