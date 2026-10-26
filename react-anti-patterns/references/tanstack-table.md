# Tables: hand-rolled vs. TanStack Table

A data table is a bundle of state (sorting, filtering, pagination, selection, column visibility,
grouping) plus the logic that applies it. Rolling it by hand means re-deriving all of it per table,
coupling it to one markup, and re-testing it each time. TanStack Table v8 is **headless**: it owns
the state model and the row model computation and renders nothing. You keep full control of markup
and styling.

## When to use what

| Situation | Use |
|---|---|
| Static list, no sort/filter/paginate, fits on one screen | `.map()` over `<tr>`. Don't add a library for nothing. |
| Any interactive column behavior, selection, or >1 table with the same features | **TanStack Table** |
| Server-side sort/filter/paginate (large datasets) | TanStack Table in **manual** mode (`manualSorting`, `manualPagination`, …) with the table state as the query key for TanStack Query |
| Tens of thousands of rows rendered client-side | TanStack Table + **TanStack Virtual** for row virtualization |
| A design system already ships a table component built on TanStack Table (shadcn `DataTable`, MUI X, AG Grid for spreadsheet-like needs) | Use that; don't rebuild it |

## Anti-pattern: table logic in the component

```tsx
// ❌ Sort state, comparator, filter, pagination math, and selection all inline — and all in useState
const [sortKey, setSortKey] = useState<keyof Row>('name');
const [dir, setDir] = useState<'asc' | 'desc'>('asc');
const [page, setPage] = useState(0);
const [selected, setSelected] = useState<Set<string>>(new Set());
const sorted = [...rows].sort((a, b) => /* type-specific comparator */);
const visible = sorted.slice(page * 20, page * 20 + 20);
```

```tsx
// ✅ Declarative column defs; the table instance computes row models
const columnHelper = createColumnHelper<User>();
const columns = [
  columnHelper.accessor('name', { header: 'Name' }),
  columnHelper.accessor('email', { header: 'Email', enableSorting: false }),
  columnHelper.accessor((row) => row.createdAt, { id: 'created', header: 'Joined', cell: (c) => format(c.getValue()) }),
  columnHelper.display({ id: 'actions', cell: ({ row }) => <RowActions id={row.original.id} /> }),
];

function UsersTable({ data }: { data: User[] }) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const table = useReactTable({
    data, columns,
    state: { sorting }, onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });
  return (
    <table>
      <thead>{table.getHeaderGroups().map((hg) => (
        <tr key={hg.id}>{hg.headers.map((h) => (
          <th key={h.id} onClick={h.column.getToggleSortingHandler()}>
            {flexRender(h.column.columnDef.header, h.getContext())}
          </th>))}</tr>))}</thead>
      <tbody>{table.getRowModel().rows.map((r) => (
        <tr key={r.id}>{r.getVisibleCells().map((c) => (
          <td key={c.id}>{flexRender(c.column.columnDef.cell, c.getContext())}</td>))}</tr>))}</tbody>
    </table>
  );
}
```

## Patterns that keep tables honest

- **Define `columns` at module scope** (or `useMemo` without the compiler). A new array each render
  resets internal state. With the compiler on, an inline array is memoized — still prefer module
  scope for readability.
- **Table state that users share → URL.** Sorting and page number belong in search params
  (`state.md` §5); pass `Route.useSearch()` in as `state` and `navigate` in the `on…Change`
  handlers. Column visibility/order → `localStorage` via `useSyncExternalStore`.
- **Server-side mode:** the table's `sorting`/`pagination`/`columnFilters` state *is* the query
  key: `useQuery({ queryKey: userKeys.list({ sorting, pagination }), ... })`, and
  `manualSorting: true`, `rowCount: data.total`. The table never sorts; it just reports intent.
- **Row identity:** set `getRowId: (row) => row.id`. Index-based IDs break selection when data
  refetches (`state.md` §2 again).
- **Separate the generic `<DataTable>` from the feature:** `UsersTable` = columns + data source;
  `DataTable<T>` = markup + `useReactTable` wiring. The generic one is written once and tested once.

## Testing tables

The table logic is TanStack's; don't re-test sorting. Test *your* parts: column `cell` renderers
as plain functions or small components, and one integration test that a click on a header changes
row order (or, in manual mode, changes the query key / URL).
