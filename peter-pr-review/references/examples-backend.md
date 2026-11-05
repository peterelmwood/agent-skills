# Backend review examples (Django/DRF)

Real Django/DRF review threads showing what Peter flags on the backend (query count, serializers, QuerySet placement, extraction, REST semantics, migrations, documentation of intent) and how he phrases it, proves it, and handles replies. Newest first.

## Contents
- [Data migration: module docstring and type hints](#data-migration-module-docstring-and-type-hints)
- [Fail fast, but count the queries](#fail-fast-but-count-the-queries)
- [Extract transforms, with reasoning](#extract-transforms-with-reasoning)
- [Out of scope? File an issue](#out-of-scope-file-an-issue)
- [Custom QuerySet needs tests and a Manager](#custom-queryset-needs-tests-and-a-manager)
- [Prove an override is redundant with framework source](#prove-an-override-is-redundant-with-framework-source)
- [Model serializer for output; drop the proxy query](#model-serializer-for-output-drop-the-proxy-query)
- [Model docstrings that explain why](#model-docstrings-that-explain-why)
- [Composition over type branching](#composition-over-type-branching)
- [Ask for the query upper bound](#ask-for-the-query-upper-bound)
- [Verify a documented serializer shape](#verify-a-documented-serializer-shape)
- [200 with an empty list, not 204](#200-with-an-empty-list-not-204)
- [Validation belongs in a serializer](#validation-belongs-in-a-serializer)
- [Minimal parameters and bulk creation](#minimal-parameters-and-bulk-creation)
- [Design objection: keep transport out of the model](#design-objection-keep-transport-out-of-the-model)
- [Migrations use historical models](#migrations-use-historical-models)

## Data migration: module docstring and type hints
**When:** 2025
**Lesson:** Give data migrations a module docstring stating their objective, and type-hint `forwards` with `StateApps`/`BaseDatabaseSchemaEditor`, using `_` for the unused editor.

```py
+    "APPAREL",
+    "ELECTRONICS",
+    "FURNITURE",
+]
+gift_wrap_option = {"x": -20, "y": 20, "text": "GW", "fill": "black", "id": "gift-wrap", "data-allow-rotation": False}
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

> **Peter:** Could you please add a docstring at the top of this file (preferably surrounded by triple quotes: `"""`) that describes what objective this migration achieves? It can go a long way toward helping someone to determine the purpose it serves when reading it later on.

**Outcome:** Resolved.

## Fail fast, but count the queries
**When:** 2025
**Lesson:** Praise fail-fast assertions, then point out when `.exists()`/`.count()`/`.get()` checks could collapse into one query because `.get()` already raises unless exactly one row matches.

```py
+        assert shipping_label is not None, f"No shipping labels found for customer {customer.name}"
+
+        historical_shipping_label = shipping_label.history.first()
+
+        horizontal_label_query = ShippingLabelTemplate.objects.filter(
+            shipping_label=historical_shipping_label, orientation="Horizontal"
+        )
+        assert horizontal_label_query.exists(), f"No horizontal shipping label found for customer {customer.name}"
```

> **Peter:** I appreciate the fail fast approach in this area!

> **Peter:** One thought, though, is that the `.exists()`, `.count()`, and `get()` might be three queries where only one is necessary. The `.get()` alone can tell you if you got a single result, as it will throw if the `count != 1`.
>
> (I'm not 100% certain about the number of queries here, but I think that is correct.)

**Outcome:** Resolved.

## Extract transforms, with reasoning
**When:** 2025
**Lesson:** When asking for an extraction, show the target shape and give a "Reasoning:" list: separation of concerns, testability, future-proofing.

```py
     def attach_shipping_labels_and_packing_slips(self):
-        raise NotImplementedError("attach_shipping_labels method not implemented")
+        # build connection object for the invoice
+        # call PDF renderer function(s)
+        invoice_b64_string = BytesCodec.encode_bytes_to_b64_bytes(self.file.read()).decode("utf-8")
```

> **Peter:** Consider moving these lengthy transforms to a method or separate service:
>
> ```py
>   invoice_b64_string = BytesCodec.encode_bytes_to_b64_bytes(self.file.read()).decode("utf-8")
> ```
>
> would be:
>
> ```suggestion
> class SomeService:
>     @staticmethod
>     def get_b64_bytes_from_bytes(value: bytes) -> bytes:
>         ...
>
> class InvoiceDocumentHelper:
>     def attach_shipping_labels_and_packing_slips(self) -> InvoiceDocumentHelper:
>
>         ...
>
>         invoice_b64_string = SomeService.get_b64_bytes_from_bytes(self.file.read())
> ```
>
> Reasoning:
> - separation of concerns - the name of this method does not indicate it would be doing the work it currently is; I would argue that's because it shouldn't
> - testability - the second code block is some significant bit easier to test, I would wager
> - future-proofing - moving the action to a separate method means that to change the implementation, *all you gotta do* is change the content of that method

**Outcome:** Resolved.

## Out of scope? File an issue
**When:** 2025
**Lesson:** When an author defers a valid design concern (here: messy exception-driven work inside `__init__`), don't drop it: file an issue and link it in the thread.

```py
-        else:
-            self.result = self.bucket.get_object_from_key(invoice.file_key)
+            self.file = result
+        except (AssertionError, ValueError) as ex:
+            logger.info(f"Error initializing InvoiceDocumentHelper: {ex}")
+            # fetch the invoice from s3
+            self.file = self.bucket.get_object_from_key(invoice.file_key)
```

> **Peter:** This section of code seems, to me, to want to live somewhere else. It is trying to make heads or tails of the provided `result`, but there are a number of scenarios it has to wade through. And even after that, it still might have an issue (like a thrown exception in `self.bucket.get_object_from_key`) that derails the instantiation process. All of that could be done before this object's initialization starts, so that it would be a simple matter of assignment.

> **The author:** will come back to this later if time permits
>
> going to focus instead on a stress test that does a large find and replace

> **Peter:** Referenced this in a new issue: <link to the new issue>

**Outcome:** Deferred to a tracked issue; thread resolved.

## Custom QuerySet needs tests and a Manager
**When:** 2025
**Lesson:** Welcome a custom QuerySet, then ask for targeted tests of its methods and a custom Manager (IDE hints, explicit creation methods); acknowledge when you find you missed something.

```py
 from django.db import models
 
 
+class ShipmentQuerySet(models.QuerySet):
```

> **Peter:** I like the use of the custom QuerySet, thanks for doing that!
>
> I might be overlooking it, but is there a test suite to cover the methods defined here?
>
> Lastly, consider adding a custom manager as part and parcel to creating a custom queryset. They are often a good means of getting IDE hints, and they allow someone to drop in explicit creation methods (similar to what `User.objects.create_user(*args)` does).

> **Peter:** I just noticed the test suite - thanks!

**Outcome:** Tests already existed; he followed up on the `objects = ShipmentQuerySet.as_manager()` line: "As mentioned before, setting up a custom manager to go with the QuerySet can add some typing benefits, as well as alleviate subsequent devs from having to supply it."

## Prove an override is redundant with framework source
**When:** 2025
**Lesson:** Ask whether a hand-written viewset method duplicates DRF's built-in behavior, and back the question with the framework's own source.

```py
+        shipment.is_valid(raise_exception=True)
+        shipment.save()
+
+        return Response(shipment.data, status=201)
+    
+    def partial_update(self, request, *args, **kwargs):
```

> **Peter:** Is this method definition necessary? Doesn't the model viewset already do all of this? I'm asking because I'm not 100% sure, but I believe that's the case.

> **Peter:** As a follow-up, here is the built-in `partial_update` method, and the method it calls (`UpdateModelMixin` is integrated into `ModelViewSet`):
>
> ```py
> …
>
> # viewsets.py
> class ModelViewSet(mixins.CreateModelMixin,
>                    mixins.RetrieveModelMixin,
>                    mixins.UpdateModelMixin,
>                    mixins.DestroyModelMixin,
>                    mixins.ListModelMixin,
>                    GenericViewSet):
>     …
>
> # mixins.py
> class UpdateModelMixin:
>     def update(self, request, *args, **kwargs):
>         partial = kwargs.pop('partial', False)
>         instance = self.get_object()
>         serializer = self.get_serializer(instance, data=request.data, partial=partial)
>         serializer.is_valid(raise_exception=True)
>         self.perform_update(serializer)
>         …
>         return Response(serializer.data)
>
>     def partial_update(self, request, *args, **kwargs):
>         kwargs['partial'] = True
>         return self.update(request, *args, **kwargs)
> ```

**Outcome:** Resolved.

## Model serializer for output; drop the proxy query
**When:** 2025
**Lesson:** Prefer a serializer over `.values(...)` so the response shape is explicit, and avoid `get_object()` when the object is only a stepping stone to another query.

```py
+    @action(detail=True, methods=["GET"], url_path="shipping-rates", url_name="shipping-rates")
+    def get_shipping_rates(self, request, *args, **kwargs):
+        """
+        Gets the Shipping Rates for a specific Customer.
+        """
+        customer = self.get_object()
+        shipping_rates = ShippingRate.objects.filter(tier=customer.shipping_tier).values('zone','base_rate','surcharge_1', 'surcharge_2')
```

> **Peter:** Recommend using a model serializer here, as it will be instructive to the reader exactly what is coming down the pipeline, in addition to other benefits like separation of concerns (akin to ModelView vs View).
>
> Separately, we make one more query here than we need to, by performing a `self.get_object()` call. Since the `customer` object is thrown away, I'd recommend restructuring the query statement so that the `get_object` call is not necessary.

> **The author:** The customer query is be used by `tier=customer.shipping_tier` . Values is used here so I don't have to create a separate serializer just to retrieve these 4 fields.

> **A co-reviewer:** Done

**Outcome:** Changed after initial pushback; resolved.

## Model docstrings that explain why
**When:** 2025
**Lesson:** Ask new models for a docstring covering purpose, each field's use, inherited fields, and reverse `related_name`s, even when that isn't yet team practice.

```py
+# django
+from django.db import models
+
+# local
+from core.models import AuditModel
+
+
+class ShipmentPackage(AuditModel):
```

> **Peter:** I realize this isn't our SOP, but articulating in a docstring the following could go a long way to helping ourselves look back and understand what and (more importantly) why the model exists and the same for its fields:
>
> - purpose/use of model: how is this model used and what does it represent?
> - purpose/use of each field: how are the fields used and what do they represent?
> - what fields does this model inherit?
> - are there any models which foreign key back to this one?
>   - (if so) what is the `related_name` that allows querying from this model?

**Outcome:** Resolved.

## Composition over type branching
**When:** 2025
**Lesson:** When code meant for one type is stretched to handle another, ask for a real separation, such as a class attribute that captures the difference in the `rest_framework` style, rather than renaming or adding `if` checks.

```py
@@ -130,7 +136,7 @@ def perform_price_recalculation(
         wholesale_items_skus_and_names: dict[int, dict[str, str]],
```

> **Peter:** Since a lot of this is labeled `wholesale_[object]`, repurposing it to be more generic without restructuring will cause a lot of confusion (including, presently, my own).
>
> The paths that the code takes seem divergent enough that a substantial separation should be made. This could manifest as an attribute on the class (à la `rest_framework` style, seen in ViewSet, Serializer, etc.) that gets used to handle the differences between the `RetailOrder` and the `WholesaleOrder`, for example.

## Ask for the query upper bound
**When:** 2025
**Lesson:** For nested query logic, ask for the upper bound on DB hits and for the logic to be put in its own function so later optimizations stay local.

```py
+    # get the mapping of attributes to products
+    product_attribute_mappings = get_product_attribute_mapping(order_item_ids)
+
+    # return for each order item, the set of attributes and whether they are required
+    result = []
```

> **Peter:** What does the upper bound on the number of db hits look like for this nested query? Could it be made into a single query?

> **Peter:** Related: could you break this out into its own method/function, to allow any future improvement in implementation to affect the body of the function less?

> **The author:** broke it out, and reduced the query size from ~50 in my testing down to 9. Possible there can be further work done, but stopping here for now.

**Outcome:** Extracted; queries cut from ~50 to 9.

## Verify a documented serializer shape
**When:** 2025
**Lesson:** Check a serializer's documented shape against what the serializer actually produces, list the mismatches, and give the command that prints it.

```py
+class InvoiceRunSerializer(AuditSerializer):
+    """
+    Serializer shape:
+        Read-only:
```

> **Peter:** Missing fields:
> - order
> - task
>
> The following field does not appear to be part of this serializer's definition:
> - status
>
> Please confer with this printout:
>
> ```bash
> python manage.py shell_plus -c "from orders.serializers.invoice_run_serializer import InvoiceRunSerializer; print(InvoiceRunSerializer())" 2>&1 # redirect to a file with: > invoicerunserializer.txt
> ```

## 200 with an empty list, not 204
**When:** 2025
**Lesson:** For a "list what's missing" endpoint, an empty list with 200 answers the question; 204 does not. Frame it as a client/server conversation.

```py
+        order = self.get_object()
+        missing_order_item_data, missing_shipping_data = order.get_missing_order_data()
+
+        if not missing_order_item_data and not missing_shipping_data:
+            return Response(status=status.HTTP_204_NO_CONTENT)
```

> **Peter:** This [204](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/204) usage seems... uncommon. I see what you're saying, but isn't an empty array and a [200](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/200) more conventional and more like a conversation?
>
> ```
> CLIENT: "What are my missing inputs?"
> SERVER: "Here is the list of your missing inputs: []"
> ```
>
> vs.
>
> ```
> CLIENT: "What are my missing inputs?"
> SERVER: "No data, but no error either"
> ```

## Validation belongs in a serializer
**When:** 2025
**Lesson:** Replace `request.data.get(...)` and manual checks with a serializer (`PrimaryKeyRelatedField`, `validate_<field>`), then call `is_valid(raise_exception=True)` and let DRF return the 400.

```py
@@ -32,6 +32,9 @@ def post(self, request, *args, **kwargs):
 
+        # check if the request contains order_item_ids array
+        order_item_ids: list[int] | None = request.data.get("order_item_ids", None)
```

> **Peter:** This is what we were talking about at the end of Thursday.
>
> Adding a serializer to ensure we are getting valid data (here with `order_item_ids` and below with `id`) would be a simple way to do so. I imagine it would look something like this:
>
> ```py
> class BulkOrderRunStartSerializer(serializers.Serializer):
>     id = serializers.PrimaryKeyRelatedField(queryset=BulkOrder.objects.all(), write_only=True)
>     order_item_ids = serializers.ListSerializer(
>         child=serializers.IntegerField(min_value=1), required=False, allow_empty=True, write_only=True
>     )
>
>     def validate_order_item_ids(self, value: list[int]) -> list[int]:
>         """Ensure that the provided order items are valid for the given bulk order."""
>         # when order_item_ids have not been provided,
>         # we assume that the user wants to run the order with all items
>         if value is None or len(value) == 0:
>             return value
>         bulk_order_id: int = self.initial_data["id"]
>         provided_items_count = len(value)
>         matched_items_count = OrderItem.objects.filter(id__in=value, bulk_order=bulk_order_id).count()
>
>         # if the number of order items is not equal to the number of provided ids,
>         # it means that one or more items are not associated with the order
>         if provided_items_count != matched_items_count:
>             raise serializers.ValidationError("One or more order items are not associated with this order.")
>
>         return value
> ```

On the revised code, where the author had added the serializer:

```py
+        # Validate the request data
+        bulk_order_run_serializer = BulkOrderRunStartSerializer(data=request.data)
```

> **Peter:** This can actually just be:
>
> ```py
> bulk_order_run_serializer = BulkOrderRunStartSerializer(data=request.data)
> bulk_order_run_serializer.is_valid(raise_exception=True)
> ```
>
> and if the exception gets raised, the View will take over handling the 400 message and all that joy.

**Outcome:** Serializer adopted; both threads resolved.

## Minimal parameters and bulk creation
**When:** 2025
**Lesson:** Pass helpers only the ids they use, not the request or whole objects, and build related rows in memory for a single `bulk_create`.

```py
@@ -138,6 +145,20 @@ def reorder_products(self, *args, **kwargs):
 
         return Response(data=response_data)
 
+    def _create_order_reservations(self, request, product):
```

> **Peter:** Please use simpler parameters, since the objects passed here are complex but the values used from them are simple.
>
> E.g.,
>
> ```py
> def _create_order_reservations(self, catalog_id, product_id):  # note the reduced parameter complexity
>     orders = Order.objects.filter(catalog=catalog_id)
>
>     reservations = []
>     for order in orders:
>         reservation = Reservation(
>             order=order,
>             product_id=product_id,
>         )
>         reservations.append(reservation)
>     Reservation.objects.bulk_create(reservations)
> ```

**Outcome:** Resolved.

## Design objection: keep transport out of the model
**When:** 2024
**Lesson:** Object when a model takes on infrastructure concerns such as channel layers; the model should notify, not orchestrate. If the author pushes back, restate the point plainly and offer to talk.

```py
     @pre_refresh_and_post_save
     def set_pdf_status_finished(self) -> None:
         """Convenience method to set finished."""
         self.pdf_generation_status = Invoice.StatusOptions.FINISHED
+        self._send_websocket_update()
+
+    def _send_websocket_update(self):
```

> **Peter:** From the point of view of the model, I think this method belongs elsewhere. I don't believe the model should know anything about the fact that there are channel layers, or that the `group_send` method needs to be converted to synchronous code, or anything of that nature. There should be a way for the invoice to "notify" a service that there is an update to the model, but not get as involved in the update process.

> **The author:** So you're just asking for some more encapsulation perhaps? In case you're not aware, because of Celery, we have to manually call the update here bc channels does not recognize the model has changed even after the save call.

> **Peter:** Please reread what I wrote above. The model shouldn't know anything about getting a channel layer. If you want to call it encapsulation, that's fine.
>
> If we're trying to set up certain scenarios where a model update should call for a websocket update, that is outside the realm of this file.
>
> If you're still unsure about what I mean, reach out.

**Outcome:** Unresolved in the thread; the author maintained the call had to happen there.

## Migrations use historical models
**When:** 2024
**Lesson:** Data migrations must use `apps.get_model()` (the model as it was at that point), never import current models or helpers that do; inline single-use helpers into the migration.

```py
+# local
+from catalog.models import Product, ProductAttribute, CatalogAttribute
+from catalog.utils.product_attribute_initialization import InitializeProductAttribute
+
+
+def create_and_relate_product_attribute(apps, schema_editor):
+    InitializeProductAttribute().initialize_product_attribute()
```

> **Peter:** The big problem here is that this initialize script calls the "current" state of the models it is creating, instead of the "at the time" state of the models it is creating. This can cause issues if any fields change in the future. Recommend writing this to utilize `apps.get_model()` here as well as below. Additionally, if `InitializeProductAttribute` is only used once, I'd recommend moving it into this migration rather than as an external "dependency", if you will.
>
> For the other `apps.get_model` call, please see the comment below.

**Outcome:** Resolved.
