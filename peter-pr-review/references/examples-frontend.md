# Frontend review examples (React/TypeScript)

Real review threads showing how Peter reviews React components, hooks, loaders and JSX: keep data shaping out of components, avoid state and memoization that buy nothing, keep hooks and listeners where React expects them, and back library claims with docs. Identifiers have been renamed to a neutral ordering domain. Newest first.

## Contents
- [Question useMemo when the dependencies are what change](#question-usememo-when-the-dependencies-are-what-change)
- [Suggest extracting a mapped JSX block into its own component](#suggest-extracting-a-mapped-jsx-block-into-its-own-component)
- [Keep data transformations out of components](#keep-data-transformations-out-of-components)
- [Do not keep derived values in state](#do-not-keep-derived-values-in-state)
- [Replace redundant props with a single callback](#replace-redundant-props-with-a-single-callback)
- [No hooks inside a render prop](#no-hooks-inside-a-render-prop)
- [Simplify the transform and let the child compute it](#simplify-the-transform-and-let-the-child-compute-it)
- [Do not use the index as a key](#do-not-use-the-index-as-a-key)
- [Replace chained ternaries with if-else](#replace-chained-ternaries-with-if-else)
- [Fetch in the route loader or render conditionally](#fetch-in-the-route-loader-or-render-conditionally)
- [Keep the try block to the call that can throw](#keep-the-try-block-to-the-call-that-can-throw)
- [Register window listeners in a useEffect with cleanup](#register-window-listeners-in-a-useeffect-with-cleanup)

## Question useMemo when the dependencies are what change
**When:** 2025
**Lesson:** Ask what a `useMemo` actually saves; if the re-renders that matter come from its own dependencies changing, it does little, and saying "food for thought" keeps the question non-blocking.

```tsx
+  // Search state for filtering products
+  const [searchTerm, setSearchTerm] = useState<string>('');
+
+  // Filtered products by name or category based on search
+  const filteredProductsByCategory = useMemo(() => {
```

> **Peter:** I'd imagine that `useMemo` serves little practical purpose here. Although I can see how it would save on calculations done when re-renders hit, it will only do so if the re-renders are not on account of a change in search term or products. Those seem to me to be a bigger deal.
>
> Why not cache the result of the function as a state variable instead? Just food for thought.

> **The author:** I think the useMemo actually does what I want it to here.
>
> Because if we had a state value, we would then need additional useEffect *I think* around that to trigger UI changes resulting from this. The memo also keeps unneeded re-renders from happening unless those two values are changed. …

> **Peter:** I definitely agree that an additional `useEffect` would be necessary if we took the approach I proposed above.
>
> However, I don't know that using the `useMemo` hook in this way is going to prevent a re-render in situations outside of the two dependency values changing, nor is it my understanding that the `useEffect` approach would result in more re-renders (not meaning to put words in your mouth, just saying that I don't think it is the case).
>
> My reading has brought me to believe that `useMemo`'s main use is to reduce the need for costly calculations when the parent component might undergo multiple render cycles which shouldn't affect the memoized component as frequently.
>
> Let me do a bit more digging around this question. However, I won't hold the ticket up on it!
>
> Good stuff!

**Outcome:** Left as `useMemo`; Peter explicitly did not block on it.

## Suggest extracting a mapped JSX block into its own component
**When:** 2025
**Lesson:** When a long `sx`-styled block wraps a `.map` that renders sizable JSX, suggest making the block (or the mapped item) its own component, and answer "we only use it once" with the render-cost argument.

```tsx
+          overflowY: 'auto',
+          border: '1px solid #e0e0e0',
+          borderRadius: '4px',
+          padding: '10px',
+          backgroundColor: '#fafafa',
+        }}
+      >
+        {Object.keys(filteredProductsByCategory).map((category) =>
```

> **Peter:** This section seems to want to be made into tis own component (or maybe it's everything inside this `map` call). Just more food for thought.

> **The author:** I don't think we need to extract this until we see a need for another list like it with checkbox sections and whatnot -- mainly because right now the only overhead is understanding that I have a list and I am going to iterate and gen the new JSX to match each list item.

> **Peter:** Regarding the notion of having no additional overhead: my concern is that if one of those child components has to re-render for some reason, it may force the parent to fully re-render, alongside all of its sibling components and any children that the rest have, as well.
>
> I'm not certain that it is the case here, but I would be hesitant. Consider the extreme scenario where an entire app is defined in a single component. Each time a child component has to re-render, it's bad news for the presentation.
>
> My understanding is that they may need to re-render _even if there are no data changes_. This can happen with styled components that are not memoized.
>
> Just wanted to put those thoughts out there, let's discuss more tomorrow!

**Outcome:** Moved to a conversation; Peter labelled it "food for thought", not a blocker.

## Keep data transformations out of components
**When:** 2025
**Lesson:** Ask for grouping, filtering and reshaping logic to live in a plain function or class outside the component, so it can be unit-tested without rendering React.

```tsx
+      } else {
+        setSelectedProductIds((prev) => prev.filter((pid) => pid !== id));
+      }
+    },
+    [setSelectedProductIds]
+  );
+
+  // Group products by category
```

> **Peter:** Last comment on here: it's currently a belief of mine that data mutations should be isolated from the components:
>
> Performing data mutations in a separate class or function allows us to test just the mutation. Assertions and expectations regarding the resulting data shape would be trivial to set up and maintain. Additionally, a failing test could indicate exactly where the error was without involving React. Finally, it would be far more lightweight than rendering a React component just to test a data mutation.

## Do not keep derived values in state
**When:** 2025
**Lesson:** If a value is cheap to compute from props or other state, compute it in the component body instead of storing it with a setter; also ask whether a branch that skips a call the other branches make is intentional.

```tsx
       if (
-        property.item_name === updatedProperty.item_name &&
-        property.property.id === updatedProperty.property.id
+        orderItems.find((item) => item.item_instance === updatedProperty.itemId)?.product.category
+          .name === 'BUNDLE'
       ) {
-        return updatedProperty;
+        setNumBundlesToChange(orderItems.filter((item) => item.name === event.oldValue).length);
```

> **Peter:** In this code block, there is no call to `setProperties`, but there are in the three other conditions. Is that intentional?

> **Peter:** Additionally, please remove `setNumBundlesToChange` as a state variable. When a calculation is not costly, it is best not use a state for something that is derived from another state variable or from a prop.
>
> Instead, use a temporary variable assigned in the body of the component.

> **The author:** For the first question, yes.
>
> The second comment, I need the number that is numBundlesToChange to update on the dialog.  It won't do that as a local variable, but I can probably use a ref instead of state if you prefer that?

## Replace redundant props with a single callback
**When:** 2025
**Lesson:** When a child receives a ref and a form that serve the same purpose for it, suggest one callback prop instead, which decouples the child from the caller; mark it as non-blocking.

```tsx
@@ -23,6 +26,8 @@ interface IOrderCanvasProps {
   isFullScreen: boolean;
   setFullScreen: React.Dispatch<React.SetStateAction<boolean>>;
   setCurrentOrderLayout: React.Dispatch<React.SetStateAction<IOrderLayout | undefined>>;
+  dirtyRef: React.MutableRefObject<boolean>;
```

> **Peter:** Consider that both dirty ref and form are performing the same function, at least where this component is concerned. Aside from the fact that this seems redundant, a single callback function could be provided as a prop to effect the same outcome, and to disentangle this component from the calling component.
>
> This is not a blocker, just food for thought.

> **The author:** I am pretty sure these actually control different things.
>
> … So the dirtyref controls the 'next/back' and the form is controlling the 'save'.

**Outcome:** Author kept both; the comment was non-blocking.

## No hooks inside a render prop
**When:** 2025
**Lesson:** Flag hooks called inside a library's `render` callback and fix it by moving the render body into its own component file, listing what that extraction buys.

```tsx
+    <Form
+      onSubmit={handleSubmission}
+      initialValues={{
+        dirty: 'false',
+      }}
+      render={({ handleSubmit, form, pristine, submitting }) => {
+        // every 1 second, export the order canvas json and compare with initial, and set dirty flag accordingly
+        useEffect(() => {
```

> **Peter:** A `useEffect` shouldn't really live inside the `render` function, unless I'm totally mistaken. Depending on how the `render` function is called, it may not cause problems -- I'm not really sure without digging into the `Form` component's definition. However, canonically this is not a pattern we should adopt.
>
> Instead, I would recommend moving this `render` block to its own file. This kills multiple birds with fewer stones, since then we will be able to:
>
> - test the form body on its own,
> - stub the new component when we don't want to render the whole form when rendering the OrderBuilder,
> - decrease the size of this already large file.

## Simplify the transform and let the child compute it
**When:** 2025
**Lesson:** Replace nested `forEach`/push loops with `flatMap`, drop optional chaining the types don't need, and ask why a parent computes something from data the child already receives.

```tsx
+  /**
+   * returns a list of products that are already in use
+   * @returns 
+   */
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

> **Peter:** Final question:
>
> Is there any reason this function is defined here? The only component that is receiving the result of the function (OrderItemsForm) already has the `orders` variable being passed to it, so why doesn't it handle this on its own?

> **The author:** I think i did it that way since unavailable Products doesn't change in the child, so it won't be rerun on re-renders.

## Do not use the index as a key
**When:** 2025
**Lesson:** When the author pushes back on a library or framework rule, answer with the official docs and the library's own example rather than restating the request.

```tsx
+                          <Stack paddingTop={'5px'}>
+                            <Grid container spacing={1}>
+                              {fields.map((name: any, index: number) => (
+                                <Fragment key={index}>
```

> **Peter:** Please do not use `index` as a key. Instead, use something else unique. Perhaps `name` is unique in this case?

> **The author:** the name could be undefined, I think index works fine and will always be unqiue

> **Peter:** This is an example of the pitfall outlined in the React docs [here](https://react.dev/learn/rendering-lists#why-does-react-need-keys). Please use something else to maintain distinction, especially since elements can get added and deleted, which is what the docs talk about. Please note that the final-form-array docs show a similar thing in [their example here](https://github.com/final-form/react-final-form-arrays?tab=readme-ov-file#usage), by showing `key={name}` rather than `key={index}`.

## Replace chained ternaries with if-else
**When:** 2025
**Lesson:** Offer an `if`/`else` (or an extracted function) in place of chained ternaries, and name values as nouns, not `[Verb][Noun]`; when the author is lukewarm, let it go and say it is a preference.

```tsx
@@ -205,8 +210,8 @@ export default function OrdersGrid({
     const getDataRequestStatus = loadingOrders
```

> **Peter:** While you are here, could you rename this variable? It is in the [Verb][Noun] format, which is broadly used for functions and methods.

> **Peter:** Also, regarding the logical flow here, I suggest an alternative (and took the liberty of providing a different name for the variable mentioned above):
>
> ```ts
> let dataRequestStatus: DataRequestStatus;
> if (loadingOrders) {
>     dataRequestStatus = DataRequestStatus.Requested;
> } 
> else {
>     if (gridDisplayedOrders.length > 0) {
>         dataRequestStatus = DataRequestStatus.NonEmptyData;
>     }
>     else {
>         dataRequestStatus = DataRequestStatus.EmptyData;
>     }
> }
> ```
>
> Another alternative might be to simply abstract the dataRequestStatus assignment into a function and move that logic away from here, since we don't really care about it in this specific context (the `onGridReady` function, that is).

> **The author:** I have no idea what this even is lol

> **Peter:** It's merely an extraction from a chained set of ternaries into a if/then statement. We can leave it be, just not a fan of chained ternaries, as I think they cause more cognitive overhead.

**Outcome:** Left as is at Peter's say-so.

## Fetch in the route loader or render conditionally
**When:** 2024
**Lesson:** Suggest fetching in the route loader instead of in a child's effect, unless the child is rendered conditionally; an author who checks the network tab and shows the request only fires when needed has answered it.

```ts
+export interface IOrderItems {
+  orderId: number;
+  items: IOrderItem[];
+}
+
+export const orderItemsLoader: LoaderFunction = async (props): Promise<IOrderItems> => {
```

> **Peter:** As mentioned in this file, it may be better to fetch the product categories here.

> **The author:** … it looks like you want the product categories that are loaded in the orderitemsform to be loaded in the loader which lands on the orderitems page.  If we do that then I'm potentially doing an extra call and passing it down in memory to a child component when it may not be needed. As it stands now we only perform the request when it's needed.

> **Peter:** Just as a follow-up, you'd be right if we conditionally rendered the Form, but the way it is written, it is rendered either way, just not visibly.

> **The author:** Well I actually opened my network tab and checked that the request is only sent out when the form is opened.

**Outcome:** Resolved with the fetch left in the form.

## Keep the try block to the call that can throw
**When:** 2024
**Lesson:** When a `catch` swallows one expected error, move the steps that follow out of the `try`, and walk through both paths (unexpected error re-thrown, expected error swallowed) to show why.

```tsx
+        if (
+          err.message !==
+          'Viewer error: dispose() was called before initialize() completed. Are you using React strict mode?'
+        ) {
+          throw err;
+        }
+
+        const renderViewer: Renderer.Viewer = viewerRef.current.renderViewer();
```

> **Peter:** Please move this and the rest of the statements below it outside of the try/catch. Reasoning:
>
> If the `await viewerRef.current.initialize(canvas)` command throws, we will proceed to the catch block and:
>   - if it's an unexpected error, we'll raise the error again and the stack will be traversed downwards until we reach another handler.
>   - if it's an expected error, we'll leave the catch block and continue to perform the other initialization steps.

## Register window listeners in a useEffect with cleanup
**When:** 2024
**Lesson:** A listener added in the component body is added again on every render; put it in a `useEffect` that removes it, and keep the handler reference stable.

```tsx
+    if (ev.key === 'Escape') {
+      setProductToPlace(undefined);
+      setSelectedAction(ActionType.Default);
+    }
+  };
+
+  // event listeners
+  window.addEventListener('keyup', handleHotKeyUp);
```

> **Peter:** Please place this command inside a `useEffect`. Otherwise, each render will add another `eventListener` to the page, causing the callback to get called multiple times when the event happens. Example:
>
> ```ts
> useEffect(() => {
>     window.addEventListener('keyup', handleHotKeyUp);
>     return () => window.removeEventListener<'keyup'>('keyup', handleHotKeyUp);
> }, []);
> ```
>
> Additionally, you may have to memoize the `handleHotKeyUp` with a `useCallback` or `useRef` (unsure about that last one!); this is because when the handler is going to be removed, it needs to be the same object reference as the original.

> **The author:** this was a test and you passed. I think have the `handlehotkeyup` function in the useEffect will also.

> **The author:** the canvas library actually handles this event, so i removed the above

**Outcome:** The manual listener was removed; the canvas library already handled the key event.
