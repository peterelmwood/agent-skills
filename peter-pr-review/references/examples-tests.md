# Test review examples

Real threads showing how Peter reviews tests in pytest/Django (model_bakery) and Vitest/React Testing Library: tests that can't fail or can't observe the change, naming, missing tests, recipes/factories, mocking choices, hard-coded counts and ordering, test placement, and proving a point by breaking the test. Newest first. Identifiers have been renamed to a neutral ordering domain.

## Contents
- [Recipes: leave primitive fields without defaults](#recipes-leave-primitive-fields-without-defaults)
- [Test names should say what is asserted](#test-names-should-say-what-is-asserted)
- [Delete a setup line to prove it does nothing](#delete-a-setup-line-to-prove-it-does-nothing)
- [Prefer spyOn over module mocks](#prefer-spyon-over-module-mocks)
- [Explain hard-coded counts](#explain-hard-coded-counts)
- [Factor repeated test fixtures into a factory](#factor-repeated-test-fixtures-into-a-factory)
- [Enumerate the missing test cases](#enumerate-the-missing-test-cases)
- [A test must do what its name says](#a-test-must-do-what-its-name-says)
- [Set up a starting state the change must alter](#set-up-a-starting-state-the-change-must-alter)
- [Don't index into unordered querysets](#dont-index-into-unordered-querysets)
- [Put tests where the existing suite lives](#put-tests-where-the-existing-suite-lives)
- [Break the test to show it can't fail](#break-the-test-to-show-it-cant-fail)

## Recipes: leave primitive fields without defaults
**When:** 2025 · `orders/baker_recipes.py`
**Lesson:** Praise the use of model_bakery recipes, then ask that string/number fields be left to baker so uniqueness constraints don't trip up callers who need several instances; foreign keys can stay wired.

```py
 invoice_line_recipe = Recipe(
     "orders.InvoiceLine",
     invoice=foreign_key(invoice_recipe),
-)
\ No newline at end of file
+)
+
+shipping_label_recipe = Recipe(
```

> **Peter:** I love this, thank you for leveraging recipes!

> **Peter:** One thought about some of the recipes: please consider leaving no defaults wherever it makes sense. I understand supplying the `foreign_key`-wrapped arguments, but for those with a string or number value, I'd recommend leaving that to the recipe. I say that assuming that some of them might have uniqueness requirements that would trip up future developers if they require multiple instances of those objects.

Same PR, `shipments/baker_recipes.py`:

```py
+packed_shipment_recipe = Recipe(
```

> **Peter:** Once again, awesome that you used recipes!
>
> Also once again, please consider leaving primitive values without defaults.

**Outcome:** Both threads resolved.

## Test names should say what is asserted
**When:** 2025 · `orders/tests/test_order_item_view_set.py`
**Lesson:** When a test name only names the action, ask which outcome it asserts — permission to act, or a state after acting.

```py
+    detail_url = "/api/orders/items/1/"
+    test_model = OrderItem
+
+    def setUp(self):
+        super().setUp()
+        self.login_user()
+
+    def test__delete_order_item(self):
```

> **Peter:** This test name is not very instructive about what it tests:
>
> - is it that a user *can* delete an order item?
> - is it that a specific condition exists *after* deleting an order item?

**Outcome:** Resolved.

## Delete a setup line to prove it does nothing
**When:** 2025 · `orders/tests/models/test_order.py`
**Lesson:** Remove a suspicious arrange line and rerun; if the test still passes, report that as a question rather than a directive.

```py
+            "query_string": "",
+            "start_index": discount.start_index,
+            "end_index": discount.end_index,
+        }
+        inputs_dict = {
+            price_rule.id: "test_value",
+        }
+        product_option_recipe.make()
```

> **Peter:** Removing this line (`product_option_recipe.make()`) does not affect the outcome of the test. Thoughts?

## Prefer spyOn over module mocks
**When:** 2025 · `src/Containers/Store/CartDetails/Tabs/CartProductsTable/CartProductsTable.test.tsx`
**Lesson:** Suggest `vi.spyOn(module, 'fn').mockReturnValue(...)` over `vi.mock` because the return value is type-checked — and point out the wrong property the type check would have caught.

```tsx
   beforeEach(() => {
+    vi.mock('@/Routing/Routes/storeRoutes', () => ({
+      useCartContext: vi.fn(() => ({
+        items: [],
+        setCartItems: vi.fn(),
+      })),
+    }));
```

> **Peter:** An alternative to `vi.mock(...)` is to use `vi.spyOn(...)`. It has the added benefit that it will determine the types of the properties you must return in order to appropriately mock the object:
>
> ```tsx
>     import * as StoreRoutesModule from '@/Routing/Routes/storeRoutes';
>
>     ...
>
>     const useCartContextSpy = vi.spyOn(StoreRoutesModule, 'useCartContext').mockReturnValue({
>       items: [], // ! NOTE THAT THIS WILL COMPLAIN (AS IT SHOULD) BECAUSE `items` IS NOT A PROPERTY OF THE RETURNED OBJECT WHEN `useCartContext` IS CALLED
>       setCartItems: vi.fn(),
>     });
> ```

Same pattern in a sibling test file, `CartDetails.test.tsx`:

```tsx
+  beforeEach(() => {
+    vi.mock('@/Routing/Routes/storeRoutes', () => ({
```

> **Peter:** Two comments:
> 1. `vi.mock` gets hoisted, so putting it in `beforeEach` *shouldn't* do anything (although I'm curious because it's in a `beforeEach`)
> 2. Consider my comment in the other test file about using `spyOn` instead, since it has the type inference built in.

**Outcome:** Resolved; a later revision of a sibling test in the PR uses `vi.spyOn(CartContext, 'useCartContext').mockReturnValue({ cartItems: mockProducts, ... })` (see next example).

## Explain hard-coded counts
**When:** 2025 · `src/Containers/Store/CartDetails/ProductCheckboxAccordionList.test.tsx`
**Lesson:** When an assertion uses a magic number, ask how it derives from the fixture; then check the arithmetic of the explanation against the factory call.

```tsx
+        selectedProductIds={[]}
+        setSelectedProductIds={vi.fn()}
+      />
+    );
+
+    // Check if the component renders the correct number of products
+    const checkboxes = screen.getAllByRole('checkbox');
+    expect(checkboxes).toHaveLength(6);
```

> **Peter:** How does the length of the checkboxes array relate to the correct number of products?
>
> If there is a simple answer, could you please include the reasoning in a comment or in the code itself?
>
> If there is not a simple answer, could you please indicate the purpose of the steps of the test at the beginning of its body, to clarify to the next reader?

> **The author:** Changed the name of the test to reflect what it was doing more accurately

Next revision, two days later:

```tsx
+  const mockProducts = CartProductFactory.buildList(4);
+
+  vi.spyOn(CartContext, 'useCartContext').mockReturnValue({
+    cartItems: mockProducts,
+    setCartItems: vi.fn(),
+  });
+
+  it('should render the component with the correct number of checkboxes (including a check all and a check for each type)', () => {
```

> **Peter:** > including a check all and a check for each type
>
> Doesn't this amount to 5?
>
> > ```tsx
> >   const mockProducts = CartProductFactory.buildList(4);
> > ```
>
> I guess I'm missing the last 1? Or I've totally missed the origin of the checkboxes?

> **The author:** So you have the following:
>
> 1. Checkbox for 'select all'
> 2. Checkbox for 'select of type'
> 3. 4 checkboxes for each product.

**Outcome:** Resolved after the author explained the 1 + 1 + 4 breakdown — the kind of reasoning Peter wanted in the test itself.

## Factor repeated test fixtures into a factory
**When:** 2025 · `src/Components/OrderForm/OrderForm.test.tsx`
**Lesson:** When the same mock object is hand-edited across several test files, count them and propose a `factory.ts` factory so the next interface change touches one place.

```tsx
@@ -48,6 +48,9 @@ describe('OrderForm', () => {
     setMappedItemProperties: vi.fn(),
     highlightedItems: [],
     setHighlightedItems: vi.fn(),
+    itemPropertiesToUpdate: [],
```

> **Peter:** Since you've gone through the trouble of adding these properties in five files, by my count, why not define and use a `OrderWizardOutletContextFactory` which relieves any future need to do so?
>
> Consider:
>
> ```ts
> // 3rd party
> import Factory from 'factory.ts';
>
> // Local
> import { CustomerFactory } from '@/Interfaces/Models/Customer.mock';
> import { HistoricalUserFactory } from '@/Interfaces/Models/IHistoricalUser';
> import { ReadOrderFactory } from '@/Interfaces/Models/Order';
> import { OrderWizardOutletContext } from './OrderWizard';
>
> export const OrderWizardOutletContextFactory: Factory.Sync.Factory<OrderWizardOutletContext> =
>   Factory.Sync.makeFactory<OrderWizardOutletContext>({
>     setModalTrigger: vi.fn(),
>     customerList: CustomerFactory.buildList(1),
>     users: HistoricalUserFactory.buildList(1),
>     orderInstance: ReadOrderFactory.build(),
>     refreshOrderInstance: async () => {},
>     …
>     highlightedItems: [],
>     setHighlightedItems: vi.fn(),
>     itemPropertiesToUpdate: [],
>     setItemPropertiesToUpdate: vi.fn(),
>     PROPERTY_MAPPINGS_TO_VIEWER: { string: { name: 'itemName', isNameProperty: true } },
>   });
> ```

**Outcome:** Resolved.

## Enumerate the missing test cases
**When:** 2025 · `src/Components/Modals/ConfirmationModal/ConfirmationModal.tsx`
**Lesson:** When a shared component gains behavior without tests, list the concrete cases (render/not render, click effects, prop called, text shown) — and ask whether the API should prevent misuse.

```tsx
@@ -130,6 +134,25 @@ export default function ConfirmationModal({
           >
             {confirmActionText}
           </Button>
+          {/* Additional action button */}
```

> **Peter:** Please add some tests that cover the new functionality of this component:
> - shouldn't render additional action button when additionalActionText is not provided (presumably use a `data-testid` to determine if it renders)
> - should close modal when additional action button is defined and it is clicked
> - should call additionalAction prop/function when additional action button is clicked
> - should render additionalActionText when additional action button is visible
>
> Additionally, should the `additionalAction === undefined` be required whenever `additionalActionText === undefined`? This would address improper usage on the developer's part.

**Outcome:** Resolved.

## A test must do what its name says
**When:** 2025 · `src/Containers/Orders/OrderBuilder/ProductsPanel/ProductsAndOptions/ProductsAndOptions.test.tsx`
**Lesson:** Check that a test's body performs the action its name claims, and that it asserts the mocked API was called with the expected parameters.

```tsx
+    (useOutletContext as Mock).mockReturnValue(mockOutletContext);
+    //Act
+    render(<ProductsAndOptionsComponent {...mockProps} />);
+    //Assert
+    expect(screen.getByText(/product options/i)).toBeInTheDocument();
+  });
+  //Add a product
+  it('adds a product', async () => {
```

> **Peter:** This test does not appear to add a product. Additionally, please assert that the mocked API request is called, preferably with the expected parameters.

**Outcome:** Resolved.

## Set up a starting state the change must alter
**When:** 2025 · `orders/tests/test_order_item_api.py`
**Lesson:** If the fixture's default already equals the value the update writes, the test can't observe the update; seed a different value first, `refresh_from_db()`, then assert.

```py
+        # ACT
+        response = self.client.post(reverse(self.reverse_list_name), data=data)
+
+        # ASSERT
+        self.assertEqual(response.status_code, 201)
+        self.assertEqual(2, len(OrderItem.objects.all()))
+
+    def test__update_order_item(self):
```

> **Peter:** The test as written hides whether or not the `warehouse_ref` gets updated, since by default the `warehouse_ref` is `None` and then it gets set to `None`. Rewriting it like the below will force the test to assess that change.
>
> ```py
> def test__update_order_item(self):
>     # ASSIGN
>     self.order_item.warehouse_ref = uuid.uuid4()
>     self.order_item.save()
>     data = {
>         "warehouse_ref": None,
>         "product": self.product.pk,
>         "order": self.order.pk,
>     }
>
>     # ACT
>     response = self.client.put(
>         reverse(self.reverse_detail_name, kwargs={"pk": self.order_item.pk}), data=data
>     )
>
>     self.order_item.refresh_from_db()
>
>     # ASSERT
>     self.assertEqual(response.status_code, 200)
>     self.assertEqual(None, self.order_item.warehouse_ref)
> ```

**Outcome:** Resolved. (In the same file he also asked for counts relative to a `starting_count` captured before the ACT step, rather than the hard-coded `2` above.)

## Don't index into unordered querysets
**When:** 2025 · `orders/tests/test_order_api.py`
**Lesson:** Flag `response.data[0]` on an unordered queryset — require `order_by` or an explicit lookup — and hold the line under pushback with first-hand evidence of local/CI flakiness.

```py
+        gift_wrap_item = baker.make(
+            OrderItem, product=gift_wrap_product, order=self.order
+        )
+
+        # ACT
+        response = self.client.get(self.list_url + f"by-customer/?customer={self.customer.pk}")
+        response_data = response.data
+        order = response_data[0]
```

> **Peter:** The queryset does not impose and ordering on this data, nor on the nested `order_items` data. Please either apply `order_by` on the QS or ensure you have the expected Order and OrderItem when accessing them by index.

> **The author:** I believe that since the OrderItems made in the test all reference the same order, it doesn't matter what the order is.

> **Peter:** Unfortunately, that is incorrect. Without a defined order, the DB will send back results in any order. This has previously resulted in tests which pass locally failing on the server. I have witnessed it multiple times, much to my dismay.

> **The author:** I understand the database not ordering things unless it's specified. I guess I just wonder why that's your concern when all of the orders in the test are the exact same? …

**Outcome:** Resolved.

## Put tests where the existing suite lives
**When:** 2025 · `customers/tests/models/test_price_rule.py`
**Lesson:** A new test file that duplicates an existing model-test module splits coverage; name the file the test should move to.

```py
+# local
+from shop.apps.customers.models import Customer
+from shop.apps.core.tests.base import BaseTestCases
+from shop.apps.catalog.baker_recipes import catalog_recipe
+
+
+class PriceRuleTestCase(BaseTestCases.SimpleTest):
```

> **Peter:** I didn't think there was a test for this because the other file for testing model methods did not contain it.
>
> This file is redundant to that one. Please move the test to the other file: shop/apps/customers/models/pricing/test_invoice.py

> **The author:** done

## Break the test to show it can't fail
**When:** 2024 · `src/Containers/CatalogDashboard/Tabs/Products/CatalogDashboardProducts.test.tsx`
**Lesson:** Prove a test is vacuous by replacing its body with a `throw`; assertions inside an `async` `forEach` callback are never awaited, so use a `for…of` loop.

```tsx
+    await act(async () => {
+      render(<CatalogDashboardProducts />);
+    });
+
+    Object.values(ProductType).forEach(async (productType) => {
+      expect(await screen.findByTestId(`${productType.toLowerCase().replace(' ', '-')}-actions`)).toBeInTheDocument();
+    });
+  });
```

> **Peter:** this does not fail if I change it to:
> ```ts
> Object.values(ProductType).forEach(async (productType) => {
>     throw new Error('no pass');
> });
> ```
> but does if I change it to
> ```ts
> let productTypes = Object.values(ProductType);
> for (let productType of productTypes) {
>     throw new Error('no pass');
>     // expect(await screen.findByText(productType)).toBeInTheDocument();
> }
> ```
> I recommend avoiding `forEach`es that have assertions in them, as is done here, because they seem to fail silently.

**Outcome:** Resolved.
