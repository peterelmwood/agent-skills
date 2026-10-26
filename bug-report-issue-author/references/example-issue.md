# Example bug report issue

This example shows the target tone, specificity, and depth for a **medium-sized** bug. It uses the full ten-section structure. For a small, contained bug, sections 6–10 would collapse into one short "Risks, testing & rollout" section. Paths and names are illustrative.

---

**Title:** `Bug: Checkout applies discount twice when promo code is re-entered (duplicate apply in cart reducer)`

**Labels:** `bug`, `severity:high`, `checkout`

### 1) Bug summary (observed vs. expected)
**Observed:** If a shopper applies a promo code, removes it, and applies it again, the order total reflects the discount twice (a 10% code yields 20% off). The charged amount matches the incorrect total.

**Expected:** Re-applying a code yields a single discount, identical to applying it once.

Steps to reproduce (reproduced locally on `main` @ `a1b2c3d`):
1. Add any item to the cart and go to checkout.
2. Apply code `SAVE10`, then click "Remove".
3. Apply `SAVE10` again.
4. Total shows 20% off.

### 2) Impact & severity
Any shopper can trigger this; it causes direct revenue loss on every affected order. **High** — financial impact, trivially reproducible, already occurring in production per the support report.

### 3) Root-cause analysis / code research
- `src/cart/cartReducer.ts` L88–97 — `REMOVE_PROMO` clears `state.promoCode` but leaves the entry in `state.appliedDiscounts`:
  ```ts
  case 'REMOVE_PROMO':
    return { ...state, promoCode: null }; // appliedDiscounts not cleared
  ```
- `src/cart/cartReducer.ts` L71–86 — `APPLY_PROMO` pushes onto `appliedDiscounts` without checking for an existing entry with the same code.
- `src/cart/totals.ts` L30–44 — `computeTotal()` sums every entry in `appliedDiscounts`, so the stale entry is counted again.

Mechanism: removal only clears the display field, and apply is not idempotent, so the same discount accumulates.

### 4) Preliminary fix approach & pragmatic patterns
- Make `appliedDiscounts` the single source of truth: `REMOVE_PROMO` filters out the entry by code, and `promoCode` is derived from it rather than stored separately.
- Make `APPLY_PROMO` idempotent by replacing any existing entry with the same code.
- Alternative considered: de-duplicating inside `computeTotal()`. Rejected because it hides inconsistent state that other consumers (the order summary) also read.

### 5) Where to start (smallest slice)
Fix `REMOVE_PROMO` and add a reducer test for apply → remove → apply; then make `APPLY_PROMO` idempotent and derive `promoCode`.

### 6) Dangers / pitfalls & regression risks
- Stacking of *different* codes, which the business allows, must keep working.
- Carts persisted in local storage may already contain duplicate entries; loading must normalize them.
- Server-side total recalculation (`src/api/orders/price.ts`, likely — not verified) may have its own copy of this logic and needs the same check.

### 7) End-user impact
- **Good:** totals are correct and consistent between cart and receipt.
- **Tradeoff:** shoppers with a stale duplicated discount in a saved cart will see their total go up on next visit.

### 8) Testing changes
- Reducer unit tests: apply/remove/apply, apply twice, and two different codes stacking.
- Regression test for `computeTotal()` with a single discount.
- End-to-end checkout test asserting the charged amount matches the displayed total.

### 9) Packaging / deployment changes
Code-only, no schema change. Ship as a hotfix; monitor average discount per order for a drop back to baseline. Finance should review orders since the promo launch for over-discounting; no automatic backfill.

### 10) Additional concerns
- Possibly a regression of #287 (closed), which fixed a similar double-apply on page refresh.
- Consider a server-side guard that rejects totals whose discount exceeds the promo's configured maximum.
