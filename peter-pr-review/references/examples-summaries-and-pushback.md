# Review summaries and handling pushback

Real review summaries (what Peter writes in the top-level review body, from one-liners to themed bullet lists and closing notes) and inline threads showing how he handles authors who push back: conceding, holding firm, offering a call, letting a good reason stand, chasing silent resolutions, and calling out tone. Each section is newest-first.

## Contents
**Review summaries**
- [One-line request: just a test](#one-line-request-just-a-test)
- [Point at the comment that matters most](#point-at-the-comment-that-matters-most)
- [Multi-part review of a big PR](#multi-part-review-of-a-big-pr)
- [Large PR: themed bullets for recurring issues](#large-pr-themed-bullets-for-recurring-issues)
- [Closing a stale PR with reasons](#closing-a-stale-pr-with-reasons)
- [State your review assumptions, then check viability](#state-your-review-assumptions-then-check-viability)
- [Approve with praise after a long exchange](#approve-with-praise-after-a-long-exchange)
- [Diff does not match the ticket](#diff-does-not-match-the-ticket)
- [Approve with a side note](#approve-with-a-side-note)
- [Missing tests are a blocker, and why](#missing-tests-are-a-blocker-and-why)

**Handling pushback**
- [Concede quickly when the author is right](#concede-quickly-when-the-author-is-right)
- [Re-open a thread resolved without action](#re-open-a-thread-resolved-without-action)
- [Accept a good reason and let it go](#accept-a-good-reason-and-let-it-go)
- [Hold firm with evidence](#hold-firm-with-evidence)
- [Still confused after a reply: offer a call](#still-confused-after-a-reply-offer-a-call)
- [Flag a dismissive tone](#flag-a-dismissive-tone)

---

# Review summaries

## One-line request: just a test
**When:** 2025 · small bug fix (+31/-4, 2 files)
**Lesson:** On a small bug fix, a single-sentence summary that names the one thing needed (a test) is enough; approve briefly once it lands.

> **Peter (Request changes):** Just requesting a test for this change.

> **Peter (Approve, next day):** Looks good, nice work!

**Outcome:** Test added; approved and merged the next day.

## Point at the comment that matters most
**When:** 2025 · (+62/-0, 1 file)
**Lesson:** When a review mixes nitpicks with one real problem, say which comment carries the weight.

> **Peter (Request changes):** Looks good! Some of my comments are probably nitpicky, but the N+1 comment is the one I'd pay most attention to.

> **Peter (Approve):** Looks good!

**Outcome:** Approved the same day after fixes; merged.

## Multi-part review of a big PR
**When:** 2025 · (+1078/-36, 23 files)
**Lesson:** For a very large PR, submit the review in passes and label each so the author can start on the first half while you finish.

> **Peter (Comment, day 1):** Backend review part 1 (halfway there)

> **Peter (Comment, day 3):** Review part 2

**Outcome:** 48 inline comments across the passes; several deferred items were turned into tech-debt tickets/issues; merged the next day.

## Large PR: themed bullets for recurring issues
**When:** 2025 · (+4464/-1009, 80 files)
**Lesson:** On a large PR, group the inline comments into a few recurring themes so the author can fix patterns instead of chasing individual comments; include the exact command for mechanical fixes.

> **Peter (Request changes):** There are some recurring themes in my comments, including:
>
> - pre-commit formatting: please install/apply the formatters. this can be done like:
>     ```sh
>     login-pip
>     login-npm
>     pip install pre-commit  # should be run from within venv
>     pre-commit run --from-ref $(git rev-parse feature/shipment-scheduler) --to-ref $(git rev-parse HEAD)
>     ```
> - function/class extraction: there are a lot of opportunities to slim down functions so that the context they present to the user is not as deep and/or wide
> - separation of concerns: there are a number of places where the order type separation is good, but there are also a number of places where the order type separation is muddled by if checks, rather than handling them in a compositional way (e.g., the `rest_framework` way of using an attribute to handle the differences between objects)
> - class definition placement: some classes seem like they do not belong in the file, or even the Django application, in which they are defined. Please consider moving those items into places which are more neutral or `core`.

## Closing a stale PR with reasons
**When:** 2025 · (+438/-218, 50 files)
**Lesson:** When closing a PR that stalled after changes were requested, list each reason as a labeled bullet and tell the author the path to reopen it.

> **Peter (PR comment, then closed):** Closing this PR for a few reasons:
>
> - out of date - updating/merging with develop would be difficult
> - incomplete - some of the models' docstrings have not been annotated
> - inconsistent - the terminology, format, and content of the added/modified content varies, to some degree, across models and does not maintain a consistent format
> - extraneous - unnecessary comments have been added; some of the docstrings have had the names of the fields _on the selfsame model_ added, which adds clutter since they are defined immediately below. Please put that type of information near or on the fields themselves.
> - failing unit tests - it may not have been related to the content, but the latest commit shows failing unit tests
>
> If you feel this PR should not be closed, please submit a new PR for this branch where it has been updated with `origin/develop`.

**Outcome:** Closed four and a half months after the "doesn't match the ticket" review below went unaddressed. For a PR with nothing to explain, he keeps it to one line: "Closing since this is far behind HEAD and because there has been no activity in quite some time." (2025)

## State your review assumptions, then check viability
**When:** 2025 · (+193/-56, 7 files)
**Lesson:** If you skimmed files you believe are formatting-only, say so in the summary and invite correction; if the PR then goes quiet, ask whether it is still viable.

> **Peter (Request changes):** I assumed test_order_items.py and order_items.py were not material changes, but formatting.
>
> Please inform me if this assumption is incorrect so I can go over the files in more detail.

> **Peter (Comment, three weeks later):** Is this PR still viable?

**Outcome:** PR closed unmerged a few days later.

## Approve with praise after a long exchange
**When:** 2025 · (+576/-10, 12 files)
**Lesson:** Open a changes-requested review by naming the themes as open questions, and close the approval by thanking the author for the discussion, not just the code.

> **Peter (Request changes, day 1):** Looking good, generally! I'm seeing some areas where I'm not sure I understand the basis for using certain React utilities (most notably, `useMemo`), and I think I see some opportunities to select more advantageous data structures.
>
> Let me know if you have any questions, and I'll try to supply the answers ASAP!

> **Peter (Approve, day 2):** Thanks for all the effort and for the great exchange of ideas!

**Outcome:** About 50 inline comments over two days; approved and merged.

## Diff does not match the ticket
**When:** 2025 · (+438/-218, 50 files)
**Lesson:** When a PR misses the ticket's intent, restate what the ticket asks for, name what is unconventional, point to the existing convention, and offer examples.

> **Peter (Request changes):** These changes do not reflect the ticket's purpose/request.
>
> Carrying out the ticket should mean that the app's models' docstrings would each have the relevant related_names added. An addendum might be that those which already had related_names would be checked to ensure the listed reverse relations are accurate.
>
> However, providing the list of fields on the models is not conventional as far as the app goes, and I would recommend against it.
>
> Additionally, where reverse relations are provided, they do not match the format which already exists in other docstrings.
>
> Please revise the PR in accordance with these facts, and follow the established convention for the related names. If you require some examples, I can provide them.

**Outcome:** Not revised; later closed as stale (see above).

## Approve with a side note
**When:** 2025 · (+1/-20, 2 files)
**Lesson:** Approve a small cleanup with thanks, and put any follow-up idea in a clearly marked side note that does not block the merge.

> **Peter (Approve):** Looks good, thanks for doing that!
>
> Side note, do you know if this can/should be done in the backend? I'll try to look into it, but feel free to take that task on if you are available.

## Missing tests are a blocker, and why
**When:** 2025 · (+420/-110, 9 files)
**Lesson:** Say plainly that missing tests block the PR; when the author adds them, approve, let a smaller request go, and explain why tests matter in code that will keep changing.

> **Peter (Request changes):** My biggest concern, when it comes to the code, is the lack of tests covering the new functionality. For me, that is a blocker. Please add suitable tests for that purpose.
>
> I haven't hit on all of the functionality defined by the ticket yet, but so far it looks good!

> **The author:** I can definitely add a suite of tests, they would cover that when I click the left button, the collapse api is called. … I will say if this proves difficult to test, I'm going to time box the tests to half a day. … **UPDATE**: Added in tests based on above comment.

> **Peter (PR comment, next day):** Thanks, that and the other changes look good to me!
>
> We can leave the context addition request alone, but we ought to be refactoring as we go, along with adding the new changes. Waiting for something to become a problem rather than being proactive is my big concern here, since we are working heavily in this area.
>
> It's a guarantee that the way something gets written the first time won't account for some types of changes that will come along. Whether it's a PR for a dark task or a story, adding changes that we don't protect with tests leaves us more vulnerable to regressions. This is additionally why I want tests here: we are guaranteed to make changes in this part of the code, and we need to be able to recognize when something we did later breaks all the hard work you did today.
>
> All that said, this PR looks good to me. Once I run through a little more of the functionality, I'll be ready to merge. Nice work!

---

# Handling pushback

## Concede quickly when the author is right
**When:** 2025
**Lesson:** If the author's objection checks out, look it up and say so plainly; don't let them make a change you were wrong about.

```tsx
+      <Typography variant='body2' sx={{ color: 'gray', marginTop: '10px' }}>
+        Note: If you do not select any warehouses, all warehouses will be used by default.
```

> **Peter:** Please remove the capital `I` on `If`

> **The author:** I don't think that is right.. From what I remember after a ':' that indicates a new sentence, the 'I' should be capitalized because of that.
>
> However -- it doesn't really matter to me, so I'll change this. (Just wanted to note it.)

> **Peter:** I got to tell you that I think you're right! Sorry for my error in judgment; I had to look it up, and it seems that it's typically done your way - my bad!

**Outcome:** Resolved; capitalization kept.

## Re-open a thread resolved without action
**When:** 2025
**Lesson:** A reaction or a resolved checkbox is not a fix; when the code hasn't changed, say so in the thread.

```tsx
+  // Handler for "Select All" checkbox (selects only visible warehouses)
+  const handleSelectAllChange = (e: React.ChangeEvent<HTMLInputElement>) => {
```

> **Peter:** Same comment as on the other `ChangeEvent` regarding the lack of need for the entire `e` object.

> **Peter (next day):** ??? thumbs up but no change?

> **The author:** Oops, just pushed up!

**Outcome:** Fixed. A longer variant when he also restates the ask: "This was marked as resolved but I don't see acknowledgement or action taken. Please note that this validation could be moved outside of the `OrderForm`. Otherwise, this function gets created each time the component renders." (2024)

## Accept a good reason and let it go
**When:** 2025
**Lesson:** Ask "why both?" as a genuine question that assumes a reason exists; if the answer explains it, resolve without arguing further.

```tsx
+            if (orderEditor.current) {
+              const editorExport = orderEditor.current.Export();
+              const currentEditorState = editorExport;
+              if (_.isEqual(currentEditorState, initialEditorState)) {
+                dirtyRef.current = false;
```

> **Peter:** I'm sure there's a simple reason, but why do you have to update both the `dirtyRef.current` and the form's `dirty` state?
>
> Could one or the other suffice?

> **The author:** dirtyRef tells the stepper/nav whether to interrupt the flow or not. form.change() tells the "Save" button on the local form that it is changed and may be submitted. With the current approach, both are necessary :)

**Outcome:** Resolved with no further reply; code unchanged.

## Hold firm with evidence
**When:** 2025
**Lesson:** Back a pattern request with links to an existing implementation, its use, and its test; if the author objects on principle, restate the concrete benefit and ask them to try it.

```tsx
 const OrderItems = () => {
   // React Router Loader
-  const { orderId, items } = useLoaderData() as IOrderItems;
+  const { customerId, orderId, items, products, shipments } = useLoaderData() as IOrderItems;
```

> **Peter:** Please revise this approach to use a more abstract pattern:
>
> In this file:
> ```ts
> const { customerId, orderId, items, products, shipments } = orderItemsData();
> ```
>
> and in the `@/Routes/Loaders/Orders/orderItemsLoader` file:
> ```ts
> export const orderItemsData = (): IOrderItems => useLoaderData() as IOrderItems;
> ```
>
> This takes dependency on React Router out of this file, and allows you to simply mock or `vi.spyOn` the `orderItemsData` function. See the OrderItems.test.tsx file for more on this.
>
> Also, as an example, please see this implementation, use, and test.

> **The author:** I don't agree with moving the useLoaderData() outside the component for the sake of testing. React Router intended the useLoaderData() to be used as a hook on the component.

> **Peter (review summary, four days later):** > I don't agree with moving the useLoaderData() outside the component for the sake of testing. React Router intended the useLoaderData() to be used as a hook on the component.
>
> Please give the pattern a try. This simplifies multiple aspects of the code while making the tests easier to write and cleaner to read.

**Outcome:** He held the request in the summary rather than re-arguing inline; the thread was later resolved.

## Still confused after a reply: offer a call
**When:** 2025
**Lesson:** Ask about a model's relationships as questions; if the author's answer doesn't clear it up, stop going back and forth in text and ask to talk.

```py
+    class Meta:
+        unique_together = ("order", "order_item")
+
+    # relational fields
+    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="shipment_lines")
```

> **Peter:** Do we need an FK to order? Doesn't the OI get us that relationship? Or are we considering Customer Items here, too?

> **Peter:** Separate question/concern: is the number of FKs in here necessary? Something feels off about it, but I haven't narrowed it down yet.

> **The author:** The order here is for the customer items. If two lines were to reference the same handles referenced by there assigned they would have issues overwriting each other. For the number of foreign we need to assign an order item to product attribute for a particular shipment

> **Peter:** I'm still a little confused here. Can we chat about it shortly?

> **The author:** done

**Outcome:** Settled on a call; thread resolved.

## Flag a dismissive tone
**When:** 2024
**Lesson:** If a reply dismisses a suggestion without reasons, ask briefly and directly for reasoning and considerate language, without re-arguing the code. (2024; no 2025 equivalent.)

```tsx
+  function getDialogTitle() {
+    const verb = initialData === undefined ? 'Create' : 'Edit';
```

> **Peter:** Consider, in the future, creating one or more classes that handle these sort of behaviors:
>
> ```ts
> class CreateUpdateThing {
>   private _initialData: Partial<CustomerOrderStage> | undefined;
>
>   constructor(initialData: Partial<CustomerOrderStage> | undefined) {
>     this._initialData = initialData;
>   }
>
>   get initialData() {
>     return this._initialData;
>   }
>
>   get presentTenseVerb() {
>     return this._initialData === undefined ? "Create" : "Edit";
>   }
>
>   get pastTenseVerb() {
>     return this._initialData === undefined ? "Created" : "Edited";
>   }
> }
> ```

> **The author:** This seems like an insane amount of overhead for doing a ternary

> **Peter:** Please use a reasoned response rather than rejecting something out of hand. And please use more considerate language.

> **A co-reviewer:** Just as an aside on this, I _think_ what the reviewer is suggesting here is that a class could be created and then utilized in **every** place that that we do these types of ternary button things.
>
> However, in this situation I do agree that a class is a tad heavy-handed for a ternary refactor. Dealers choice imo

**Outcome:** The suggestion was explicitly "in the future", so it was optional; thread resolved and the PR merged.
