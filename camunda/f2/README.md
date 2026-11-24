# F2 - executable inventory process with producer Tasklist forms

Owner: Omar Fathy (M4). Operational design: Zain-Eldin Sharaf (M3).

[Corrected Camunda project](https://hub.camunda.io/workspaces/92fa97e5-a7b4-4f61-8f95-8e16edc03f4c/projects/2564c9ce-cd79-4e20-aad5-bc07b1f28945).

This replaces the rejected 22 November draft. Scanner tasks, wrapper subprocesses, recurring checks and the correction helper were removed. The rejected Camunda project was moved to Recently deleted. F1 and main remain unchanged.

## Original design preserved

**Tasklist refinement, 24 November:** the executable now has a none start, catalogue-loading service task and producer stock-update user task. The former correction message catch is a native correction user task. The detailed [operational-to-executable mapping](../../docs/f2-tasklist-refinement.md) supersedes the exact graph/layout preservation claims below. Original operational files remain unchanged, existing business sequence-flow endpoints are preserved, and an executable interaction row is added. New Tasklist execution has not yet been verified live.

Both executable BPMN files are generated from the untouched sources in `models/operational-bpmn/functionality-2/`. The main source blob is `4ba83ea042c09a4b9493e1c21a3226e80b444b69`.

Automated comparison checks the original business node IDs and sequence-flow endpoints, with explicit allowances for the documented producer entry path and correction event-to-task refinement. The executable layout is extended; it is no longer identical to the operational diagram. The original generic "Keep product unavailable" task still receives a service-task implementation.

Added execution settings: executable flag; worker types; FEEL conditions/default paths; message definitions and correlation; administrator form reference; literal called process ID and returned variables; timer values. Target: Camunda 8.9.

## Contents

| File | Purpose |
|---|---|
| processes/inventory-seasonal-availability.bpmn | Full original operational F2 workflow with execution properties |
| processes/check-product-stock-status.bpmn | Original reusable stock-check workflow with a worker type |
| forms/f2-inventory-review.form | Linked to the original administrator task |
| forms/f2-stock-update.form | Linked native producer task with catalogue product dropdown and stock/date fields |
| forms/f2-stock-correction.form | Linked native correction task showing validation errors and previous values |

The original producer remains a black-box participant in the operational source. The executable hosts producer interaction through Tasklist, as F1 does. Start a new instance using the none start; the worker prepares product choices and an updateId, then Tasklist presents the submission form. Invalid submissions open the correction form in the same instance. No separate helper process is added.

## Explicit seasonal timer demo configuration

**Update:** the inventory service now also has a persistent per-product scheduler. It replaces schedules when dates change, rechecks current dates/stock and recovers missed actions after restart. See [scheduler behaviour and BPMN integration boundary](../../docs/f2-season-scheduler.md). It updates the service catalogue directly; it does not trigger Zain's seasonal BPMN routes. Those original fixed timer starts remain the separate single-product demonstration described below. They have not been silently replaced or described as dynamically rescheduled.

A timer start creates a fresh instance without product variables from earlier updates. To preserve the original graph, these routes are configured for ONE demonstration product. Timer dates come from `services/inventory-service/demo-product.json`: season start at UTC midnight on availableFrom; season end at UTC midnight on the day after inclusive availableUntil.

Set `F2_TIMER_PRODUCT_ID=P1` in the worker. Change the product/date configuration and rebuild/redeploy for a different demonstration. Updating dates in an instance does not reschedule deployment-level timers. Past timer dates may fire immediately on deployment. There is no recurring timer or catalogue scanner. Current catalogue dates are rechecked so stale timers cannot enable an out-of-season product. This is a limited timer demonstration, not a complete multi-product scheduler.

## Run and deploy

Python 3.12+, standard library only. Use one worker and one SQLite demo catalogue.

1. Seed: `python services/inventory-service/worker.py --seed services/inventory-service/demo-product.json`.
2. Set CAMUNDA_REST_ADDRESS, an existing authorized CAMUNDA_ACCESS_TOKEN for SaaS (or local CAMUNDA_USERNAME/CAMUNDA_PASSWORD), and F2_TIMER_PRODUCT_ID. Never commit credentials.
3. Run `python services/inventory-service/worker.py` from the seed directory, or use the same explicit --db path for both commands.
4. Deploy the two processes and administrator form together; the standalone producer form may also be included. The original timer starts activate on deployment.

F1 publication and F2 now share the worker and catalogue. The connected F1 resources are in `camunda/f1`; publication uses job type `f1-publish-product` and completes only after SQLite commits. See [integration contract](../../docs/f1-f2-integration.md) and [24 November verification](../../docs/task1-completion-review-2026-11-24.md). Notifications/correction requests are recorded in SQLite; no real email/SMS is sent. Overselling fails without reducing stock below zero; duplicate orderId does not decrement twice.

For the existing UWE cluster, run `services/inventory-service/start-f2.cmd` and leave its terminal open after CONNECTED. This launcher uses a consistent database path beside the worker and existing credentials outside the repository. Do not run a second worker or the seed command over an existing product. The generic instructions above are for a separately configured environment.

## Messages

Publish through `/v2/messages/publication` with unique messageId, correlationKey and TTL. Update variables: productId, updateId, nonnegative integer quantity, availableFrom and availableUntil (YYYY-MM-DD). Paid-order variables: productId, orderId and positive integer purchasedQuantity.

| Message | Purpose | Correlation key |
|---|---|---|
| f2-stock-update | Start original update route | productId |
| f2-stock-corrected | Legacy version only; refined deployments use the Tasklist correction form | updateId of an old waiting instance |
| f2-order-paid | Start original stock-reduction route | productId |

Legacy correction (existing instances on the old deployed version only):

```json
{"name":"f2-stock-corrected","correlationKey":"U1","messageId":"U1-correction-1","timeToLive":60000,"variables":{"quantity":12,"availableFrom":"2026-11-01","availableUntil":"2026-12-31"}}
```

Three invalid attempts route to administrator review; allowAnotherCorrection=true returns to corrections, false rejects. Original interrupting deadline: PT48H. Low stock: `0 < quantity < lowStockThreshold` (default 5); zero-stock notification is separate.

## Validation

`python -m unittest discover -s tests -p 'test_*.py' -v`: 35 checks passed on 24 November, covering the documented executable refinements, form output contracts, catalogue choices and retry-stable update IDs, scheduler behaviour, connection handling and shared F1/F2 persistence.

The existing Maven parser/schema validation and engine route tests are separate from Python worker tests. Engine route tests were previously blocked by local socket restrictions; do not count them as passed. Live F2 results are recorded in [23 November evidence](../../docs/f2-live-validation-2026-11-23.md) and the 24 November review above. The seasonal BPMN starts and 48-hour review timeout still need successful execution evidence.

Rebuild execution settings with `python scripts/build_f2.py`.

