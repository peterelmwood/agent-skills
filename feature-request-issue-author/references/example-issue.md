# Example feature request issue

This example shows the target tone, specificity, and depth for a **medium-sized** feature. It uses the full ten-section structure. For a small change, sections 6–10 would collapse into one short "Risks, testing & rollout" section. Paths and names are illustrative.

---

**Title:** `Feature: Export filtered order history to CSV for store managers`

**Labels:** `enhancement`, `reporting`

### 1) Problem statement
Store managers can filter order history in the admin dashboard (date range, status, location) but cannot export the result. Today they screenshot pages or ask support to run a database query, which generates about 15 support tickets a month and delays month-end reconciliation.

### 2) Goal / outcome
Managers can download exactly the orders they are currently viewing as a CSV.

Acceptance criteria:
- An "Export CSV" button appears on the order history page for users with the `manager` role.
- The export honors all active filters and sort order.
- Exports of up to 50,000 rows complete in under 10 seconds.
- Currency and dates use the store's configured locale.

Out of scope: scheduled/emailed exports, Excel format, exporting line-item detail.

### 3) Preliminary code research
- `src/admin/orders/OrderHistoryView.tsx` (L40–118) — renders the filter bar and table; the export button goes next to the filter controls. Small change.
- `src/api/orders/list.ts` (L22–71) — `listOrders()` already builds the filtered query; extract the query builder so export and list share it. Medium change.
- `src/api/reports/` — existing `csvStream()` helper in `csv.ts` (L5–39) streams rows; reuse it. No change.
- `src/auth/roles.ts` (L12) — `requireRole()` guard to reuse for the new endpoint.
- New endpoint location, likely `src/api/orders/export.ts` (likely — not verified against routing conventions in `src/api/index.ts`).

### 4) Pragmatic design patterns
- Extract the filter-to-query logic from `listOrders()` into `buildOrderQuery(filters)` so list and export can never disagree about which orders match.
- Stream the response with the existing `csvStream()` rather than building the file in memory.
- Keep column formatting (currency, dates) in one `formatOrderRow()` function, separate from the query.
- Alternative considered: generating the CSV client-side from loaded pages. Rejected because the table paginates at 50 rows and managers need full result sets.

### 5) Where to start
1. Extract `buildOrderQuery()` with unit tests proving `listOrders()` output is unchanged.
2. Add the export endpoint with a fixed column set and a role guard.
3. Add the button, then locale formatting.

### 6) Dangers / pitfalls
- List and export diverging if the query logic isn't shared.
- Large exports holding database connections too long; needs a row cap and a statement timeout.
- Leaking orders from other locations if location scoping is applied in the UI but not the query.

### 7) End-user impact (good and bad)
- **Good:** managers self-serve reconciliation data; fewer support tickets.
- **Bad/Tradeoff:** a 50,000-row cap means very large ranges must be split, and the UI must explain this clearly.

### 8) Testing changes
- Unit tests for `buildOrderQuery()` and `formatOrderRow()`, including locale cases.
- Integration test: export honors each filter and rejects non-manager roles.
- Regression test: order list results unchanged after the refactor.
- Accessibility: button is keyboard-reachable and announces download status.

### 9) Packaging/deployment changes
Code-only, no schema change. Ship behind a `orders_csv_export` flag, enable for one region first, monitor endpoint latency and error rate, and roll back by disabling the flag. Add a help-center article.

### 10) Additional concerns
- Track export count and row volume to validate adoption.
- Column headers need translation for non-English stores.
- Related: #412 (closed) asked for PDF export of individual orders.
- Open question: should cancelled orders be included by default?
