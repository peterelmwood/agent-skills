# Validation: Zod at the boundary, forms via a form library

TypeScript types are erased at runtime. Every `as User` on a `fetch` result, every
`JSON.parse(localStorage.getItem(...))`, every `searchParams.get('page')` is a place where the
runtime shape is *unknown* and your types are lying. The pattern is **parse, don't validate**
(Alexis King): convert unknown input into a typed value *once*, at the boundary, and never check
again inside.

Zod 4 is the default because it implements Standard Schema (so TanStack Form, TanStack Router, RHF,
tRPC, and others accept a Zod schema directly), infers types, and now includes codecs for
bidirectional transforms. Valibot and ArkType are fine substitutes with the same interface.

## §1 Anti-pattern: hand-rolled validation

```tsx
// ❌ Incomplete, untyped, duplicated across client/server, no error structure
function isValidSignup(f: any) {
  if (!f.email || !f.email.includes('@')) return false;
  if (f.password.length < 8) return false;
  if (f.age && isNaN(Number(f.age))) return false;
  return true;
}
```

```ts
// ✅ One schema → types, messages, per-field errors, reusable on the server
export const Signup = z.object({
  email: z.email(),                                   // Zod 4: top-level formats
  password: z.string().min(8, 'At least 8 characters'),
  confirm: z.string(),
  age: z.coerce.number().int().min(13).optional(),    // "17" → 17
}).refine((v) => v.password === v.confirm, { path: ['confirm'], message: 'Passwords must match' });
export type Signup = z.infer<typeof Signup>;
```

**When hand-written logic is still right:** a check that depends on runtime context Zod can't see
(availability of a username → async `refine`, or a mutation that returns the error), or a truly
one-off `if (x > max)` next to its use. Even then, express it as `.refine()`/`.superRefine()` on
the schema when it's about the data's *shape or invariants*, so the form library can surface it.

## §2 Anti-pattern: the TS interface that duplicates the schema

```ts
// ❌ Two sources of truth; they will diverge
interface User { id: string; email: string; role: 'admin' | 'user' }
const UserSchema = z.object({ id: z.string(), email: z.string(), role: z.enum(['admin', 'user']) });
```

```ts
// ✅ Schema is the source; type is derived
export const User = z.object({ id: z.string(), email: z.email(), role: z.enum(['admin', 'user']) });
export type User = z.infer<typeof User>;
// When input ≠ output (coerce/transform/default): z.input<typeof S> and z.output<typeof S>
```

Naming the schema and type the same (`User`) is a widely used convention: value space and type
space don't collide, and imports stay clean.

## §3 Anti-pattern: trusting the network

```ts
// ❌ "as" is a promise you can't keep
const user = (await res.json()) as User;
```

```ts
// ✅ Parse in the API client — the one place every response passes through
export async function getUser(id: string, signal?: AbortSignal): Promise<User> {
  const res = await fetch(`/api/users/${id}`, { signal });
  if (!res.ok) throw new ApiError(res.status);
  return User.parse(await res.json());
}
```

Choose `parse` vs `safeParse` by what the caller can do:

| | Use |
|---|---|
| API response (a mismatch is a bug or an outage; nothing to recover) | `.parse()` — throw, let the error boundary / Query's `error` state show it, and Sentry gets a precise `ZodError` instead of a `TypeError` three components later |
| User input, URL, localStorage (expected to be wrong sometimes) | `.safeParse()` and branch on `success`, or `.catch(default)` per field |
| A field that should degrade, not fail | `.catch(fallback)` |

For large payloads where parsing cost matters, parse the *envelope* and the fields you read; use
`z.looseObject()` / `.passthrough()` for the rest. Don't skip parsing — skip *depth*.

## §4 Anti-pattern: untyped URL state

```tsx
// ❌ page is a string|null; "abc" crashes the pagination
const page = Number(searchParams.get('page'));
```

```ts
// ✅ TanStack Router — validateSearch accepts a Standard Schema directly
export const Route = createFileRoute('/products')({
  validateSearch: z.object({
    page: z.number().int().positive().catch(1),
    q: z.string().trim().catch(''),
    sort: z.enum(['price', 'name']).catch('name'),
  }),
  loaderDeps: ({ search }) => search,
  loader: ({ context: { queryClient }, deps }) => queryClient.ensureQueryData(productsQuery(deps)),
});
```

`Route.useSearch()` is now fully typed and already-coerced. `.catch()` per field = a bad param
falls back instead of 404ing the page. In Next.js, do the same in a tiny `useTypedSearchParams(schema)`
hook.

## §5 Anti-pattern: forms modeled by hand

```tsx
// ❌ Every field: a useState, an error useState, a touched flag, an onBlur, a handler
const [email, setEmail] = useState(''); const [emailErr, setEmailErr] = useState('');
const [emailTouched, setEmailTouched] = useState(false);
// × 8 fields, then a 40-line handleSubmit
```

A form is: values, per-field errors, touched/dirty, submission state, and validation timing. That
is a solved problem. Pick the library by context:

| Context | Use |
|---|---|
| New code, TanStack already in the stack | **TanStack Form v1** — `validators: { onChange: Signup }` takes the Zod schema directly (Standard Schema, no adapter package) |
| Existing React Hook Form codebase | Keep **RHF** + `zodResolver(Signup)` (`@hookform/resolvers`); don't churn for its own sake |
| Server-centric app (RSC / Server Actions / Router server functions) | React 19 **Actions** + `useActionState`, schema parsed on the server; the same Zod schema runs client-side for instant feedback |
| One field, no cross-field rules, no async | Controlled `useState` + `schema.safeParse` on submit — a library would be ceremony |

```tsx
// ✅ TanStack Form + Zod 4
const form = useForm({
  defaultValues: { email: '', password: '', confirm: '' } satisfies z.input<typeof Signup>,
  validators: { onChange: Signup },
  onSubmit: async ({ value }) => { await signup.mutateAsync(value); },
});
<form.Field name="email">
  {(field) => (
    <>
      <input value={field.state.value} onBlur={field.handleBlur}
             onChange={(e) => field.handleChange(e.target.value)} />
      {field.state.meta.errors.map((e) => <p key={e?.message}>{e?.message}</p>)}
    </>
  )}
</form.Field>
```

**Timing:** validate `onChange` for format errors the user can fix as they type, `onBlur` for
things that are annoying mid-typing (email), `onSubmit` for everything, and async validators
(`onChangeAsync` with `asyncDebounceMs`) for server checks. The schema is the same in every slot.

## §6 Server ↔ client: one schema, both sides

```ts
// shared/schemas/order.ts — imported by the API handler AND the form
export const CreateOrder = z.object({ ... });
```

If the backend isn't TypeScript, generate: OpenAPI → Zod (`openapi-zod-client`, `orval`) so the
client schema is derived from the server contract, not hand-copied.

For transforms that must run both directions (ISO string ↔ `Date`, cents ↔ `Money`), Zod 4.1's
**codecs** replace the old pattern of a parse schema plus a separate serializer:

```ts
const IsoDate = z.codec(z.iso.datetime(), z.date(), {
  decode: (s) => new Date(s), encode: (d) => d.toISOString(),
});
// z.decode(IsoDate, '2026-10-26T18:21:00Z') → Date;  z.encode(IsoDate, date) → string
```

## §7 Validation anti-patterns checklist

- `as T` on anything that came from outside the process.
- `JSON.parse` without a schema.
- A regex for email/URL/UUID — use `z.email()`, `z.url()`, `z.uuid()`.
- `Number(x)` / `parseInt` on input — `z.coerce.number()` with `.int()`/`.min()`.
- `if (!x.foo) throw new Error('foo required')` chains — that's a schema.
- An `isValid` boolean with no error detail — the user needs to know *which* field.
- The same rule in a form handler *and* an API route, written twice.
- Validation that lives in a component instead of next to the type it validates.
