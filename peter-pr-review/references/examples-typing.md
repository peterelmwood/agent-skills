# Typing review examples (Python & TypeScript)

Real threads showing how Peter reviews type accuracy: hints and return types, type-checker output as evidence, nullable vs optional, `!` and `any`, interfaces that must match serializers, and narrowing to unions. Newest first; about half Python, half TypeScript. Identifiers have been renamed to a neutral ordering domain.

## Contents
- [Type-hint migration functions](#type-hint-migration-functions)
- [Paste the type-checker error as the comment](#paste-the-type-checker-error-as-the-comment)
- [Use isinstance for type checks](#use-isinstance-for-type-checks)
- [Validate untyped request data with a serializer](#validate-untyped-request-data-with-a-serializer)
- [A variable should not change type](#a-variable-should-not-change-type)
- [Type state by what is used, not by the event it came from](#type-state-by-what-is-used-not-by-the-event-it-came-from)
- [Drop optional chaining the type does not need](#drop-optional-chaining-the-type-does-not-need)
- [Interfaces must match the serializer shape](#interfaces-must-match-the-serializer-shape)
- [Empty list instead of null](#empty-list-instead-of-null)
- [A non-null assertion means the typing is wrong](#a-non-null-assertion-means-the-typing-is-wrong)
- [Constrain string sets with as const unions](#constrain-string-sets-with-as-const-unions)
- [Reduce any](#reduce-any)

## Type-hint migration functions
**When:** 2025
**Lesson:** Ask for parameter and return type hints even on migration functions, and give the exact imports to use; name unused parameters `_`.

```diff
+    "APPAREL",
+    "ELECTRONICS",
+    "FURNITURE",
+]
+new_badge = {"x": -20, "y": 20, "text": "NEW", "fill": "black", "id": "new-badge", "data-allow-rotation": False}
+
+
+def forwards(apps, schema_editor):
```

> **Peter:** Please add the following imports:
>
> ```py
> from django.db.backends.base.schema import BaseDatabaseSchemaEditor
> from django.db.migrations.state import StateApps
> ```
>
> and use them for type hints here:
>
> ```suggestion
> def forwards(apps: StateApps, _: BaseDatabaseSchemaEditor) -> None:
> ```

**Outcome:** Resolved.

## Paste the type-checker error as the comment
**When:** 2025
**Lesson:** When the code violates its own declared types, the Pylance error quoted verbatim is the whole comment; it is evidence the author can reproduce.

```diff
+                        "applied_discounts": [discount.__dict__ for discount in discounts_with_value],
+                    }
+                )
+            else:
+                results.append(
+                    {
+                        "sku": line_item["sku"],
+                        "value": updated_price,
```

> **Peter:**
> > Argument of type "dict[str, str | tuple[str, list[DiscountWithValue]] | int | None]" cannot be assigned to parameter "object" of type "PriceUpdateResult" in > function "append"
> >   Type "str | tuple[str, list[DiscountWithValue]]" is not assignable to type "str"
> >     "tuple[str, list[DiscountWithValue]]" is not assignable to "str"

## Use isinstance for type checks
**When:** 2025
**Lesson:** Narrow with `isinstance` (which type checkers understand), not `type(x) == Cls`; when comparing types themselves, use `is`.

```diff
-        shipments = Shipment.objects.completed().filter(wholesale_order=wholesale_order)
+        shipments = Shipment.objects.none()
+        shipments_by_warehouse = {}
+        product_ids_being_replaced = []
+        if type(order) == WholesaleOrder:
```

> **Peter:** Recommend using `isinstance`, which is the idiomatic way to perform an instance type check.
>
> Separately, `is` and `is not` operators should be used with type comparisons. For example:
>
> ```py
> Type1 is Type2  # compares the two types
> ```
>
> ```suggestion
>         if isinstance(order, WholesaleOrder):
> ```

## Validate untyped request data with a serializer
**When:** 2025
**Lesson:** A type annotation on `request.data.get(...)` is a wish, not a guarantee; validate the input with a serializer so the declared type is actually true.

```diff
@@ -32,6 +32,9 @@ def post(self, request, *args, **kwargs):
         """Creates a fulfillment run and kicks off the process of shipping the Order's associated items."""
 
+        # check if the request contains order_item_ids array
+        order_item_ids: list[int] | None = request.data.get("order_item_ids", None)
```

> **Peter:** This is what we were talking about at the end of Thursday.
>
> Adding a serializer to ensure we are getting valid data (here with `order_item_ids` and below with `id`) would be a simple way to do so. I imagine it would look something like this:
>
> ```py
> class FulfillmentRunStartSerializer(serializers.Serializer):
>     id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), write_only=True)
>     order_item_ids = serializers.ListSerializer(
>         child=serializers.IntegerField(min_value=1), required=False, allow_empty=True, write_only=True
>     )
>
>     def validate_order_item_ids(self, value: list[int]) -> list[int]:
>         """Ensure that the provided order items are valid for the given order."""
>         …
>         if provided_items_count != matched_items_count:
>             raise serializers.ValidationError("One or more order items are not associated with this order.")
>
>         return value
> ```

**Outcome:** Resolved.

## A variable should not change type
**When:** 2025
**Lesson:** Point out when a variable is first one type (a Manager) and later another (a QuerySet); assign it once per branch with its final type.

```diff
-        order_items = OrderItem.objects.filter(order=order_pk).values(
-            "pk", "product", "selected_warehouse"
-        )
+        qs = OrderItem.objects
```

> **Peter:** This is really a manager in its first assignent, and its type changes in line 132/134. You can actually get rid of this altogether and move the `OrderItem.objects` into those lines:
>
> ```suggestion
> if order_item_ids is not None:
>     qs = OrderItem.objects.filter(pk__in=order_item_ids)
> else:
>     qs = OrderItem.objects.filter(order=order_pk)
> ```

**Outcome:** Resolved.

## Type state by what is used, not by the event it came from
**When:** 2025
**Lesson:** Don't store a wide framework type (a whole grid event) when only two fields are used; a small explicit type says what the state is and why it exists.

```diff
   const [gridApi, setGridApi] = useState<GridApi | undefined>(undefined);
   const [filteredAttributes, setFilteredAttributes] = useState<IProductAttribute[]>([]);
+  const [showCancelModal, setShowCancelModal] = useState<boolean>(false);
+  const [updateAttrEvent, setUpdateAttrEvent] = useState<CellValueChangedEvent<IProductAttribute, any>>();
```

> **Peter:** One comment I meant to make about the `updateAttrEvent` is that its type obscures why it is relevant and what its use is.
>
> To expand on that, the only properties this object offers that are used are:
> - data
> - oldValue
>
> A simpler object would be more instructive in what it is and why it exists, for example:
>
> ```tsx
>     const [updatedAttribute, setUpdatedAttribute] = useState<{ attribute: IProductAttribute, oldValue: string } | null>(null);
>
>     ...
>     setUpdatedAttribute({ attribute: event.data, oldValue: event.oldValue });
> ```

**Outcome:** Resolved.

## Drop optional chaining the type does not need
**When:** 2025
**Lesson:** `?.` on a field the type says is always present guards an impossible state; remove it, and simplify the loop that it was cluttering.

```diff
+  const getUnavailableProducts = (): number[] => {
+    const unavailableProducts: number[] = []
+    orders.forEach((order) => {
+      order.order_items?.forEach((orderItem) => {
```

> **Peter:** This optional chaining is not necessary. Additionally, this structure may benefit from simplification like:
>
> ```ts
>   const getUnavailableProducts = (): number[] => {
>     return orders.flatMap(
>       (order) => order.order_items.map((item) => item.product)
>     );
>   };
> ```

**Outcome:** Resolved.

## Interfaces must match the serializer shape
**When:** 2025
**Lesson:** Check a frontend interface against its backend serializer; if endpoints return different shapes, define one interface per shape (with a shared base) rather than marking fields optional. He holds this position under pushback.

```diff
@@ -35,6 +35,7 @@ export interface IProduct extends AuditBase, Base {
   is_active: boolean;
   sku_suffix?: string;
   has_bulk_pricing?: boolean;
+  mapped_warehouse_location?: string;
```

> **Peter:** This does not appear to be optional in the counterpart serializer. Please correct this or me if I am mistaken.

> **The author:** Its only used on the products table in the GET. I guess the issue with making it required is all post/puts etc would require this field.

> **Peter:** Right, but the interface should reflect the shape of the data. If there are multiple shapes that could come back from different endpoints, there should be a corresponding interface for each of them. Otherwise, we are adding cognitive overhead where the dev has to understand that the interface is a guideline that is known to be erroneous in at least some situations.
>
> If this change results in that situation, I recommend defining a new interface that correctly corresponds with ProductSerializer and/or a base interface that it and other related interfaces draw from.

**Outcome:** Resolved.

## Empty list instead of null
**When:** 2024
**Lesson:** Don't make a collection field nullable when an empty collection already means "none"; two representations of the same state is an avoidable ambiguity. State your assumption and invite correction.

```diff
@@ -23,6 +24,7 @@ class Customer(models.Model):
     last_name = models.TextField()
     email = models.EmailField()
     phone_number = models.TextField(blank=True, null=True)
+    tags = ArrayField(models.CharField(max_length=255), blank=True, null=True)
```

> **Peter:** A few things I'd consider issues here:
> …
> - An ArrayField should probably not employ `blank=True`, but I believe it shouldn't employ `null=True` either. I'd assume we want an empty list to equate to "no tags", rather than a null value. This is especially true if both would mean the same thing. If my assumption is incorrect here, please inform me.
> …
>
> I'd be happy to discuss this further with you. LMK what you think.

**Outcome:** Resolved.

## A non-null assertion means the typing is wrong
**When:** 2024
**Lesson:** Reject `!` as a fix: offer conditional rendering or an earlier guard, and if "we know it's defined", treat the type that says otherwise as the bug. Hold the point, offer to pair on the root cause.

```diff
+              <Grid2 size={12}>
+                <Typography variant='h5' mt={2} mb={2}>
+                  {orderInstance!.customer_name}
```

> **Peter:** Please do not use the TypeScript `!` unless thoroughly necessary.
>
> The preferred alternative would be:
> - conditional rendering of this typography component: _IF_ the rest of the form is supposed to appear when there is no `orderInstance` defined
> - the form does not get rendered if the `orderInstance` is not defined.

> **The author:** The order instance has to be defined for this form. … However the type is 'ReadOrder | undefined', well we know that it _should_ be defined here.

> **Peter:** If we know the `orderInstance` is defined but TypeScript doesn't, that means the typing is inaccurate. I'd be happy to work with you to determine what the root cause is, but either way there is an issue here.

> **The author:** … at this point in the stepper the orderInstance is a known thing. But in the previous steps the orderInstance _could be_ undefined. … unless you think this is an absolute blocker, I wouldn't say this is a show stopper for this ticket.

> **Peter:** We can discuss more on a call... there are some simple ways to resolve this, unless I'm mistaken

**Outcome:** Taken to a call; thread resolved.

## Constrain string sets with as const unions
**When:** 2024
**Lesson:** A fixed list of names typed as `ReadonlyArray<string>` loses information; `as const` plus an indexed-access type gives a literal union that keys can be checked against. Say plainly when a suggestion is only illustrative.

```diff
+  const { catalogAccess, isAdmin } = useContext(AuthContext);
+
+  // Define the customer fields to fetch
+  const ORDER_INFO_FIELD_NAMES: ReadonlyArray<string> = [
```

> **Peter:** Consider, for the purpose of rather strict typing:
>
> ```ts
> // Define the customer fields to fetch
> const ORDER_INFO_FIELD_NAMES = [
>   'Order Type',
>   'Shipping Method',
>   …
> ] as const;
>
> type TFieldName = (typeof ORDER_INFO_FIELD_NAMES)[number];
>
> type EntryOptions = Partial<{
>   [key in TFieldName]: EntryOptionList;
> }>;
> ```

> **The author:** Confused on the ask here.

> **Peter:** I just wanted to supply an example of how the typing can be more constrained than it currently is.

## Reduce any
**When:** 2024
**Lesson:** A curried handler typed `any` at every layer gives the checker nothing to verify; ask for real types, briefly.

```diff
+  const transformedOrder = order ? transformOrderData(order) : null;
+
+  const handleAutocompleteChange = (input: any, isMultiple: boolean) => (_: any, selectedOptions: any) => {
```

> **Peter:** possible alternative:
>
> ```ts
>   const handleAutocompleteChange = (input: any, isMultiple: boolean) => (_: any, selectedOptions: any) => {
>     let changeValue: any[] | any;
>     …
>   };
> ```

> **Peter:** Please reduce `any`s

**Outcome:** Resolved.
