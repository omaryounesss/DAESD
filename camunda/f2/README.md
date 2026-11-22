# F2 - Zain's original operational BPMN made executable

Owner: Omar Fathy (M4). Operational design: Zain-Eldin Sharaf (M3).

[Corrected Camunda project](https://hub.camunda.io/workspaces/92fa97e5-a7b4-4f61-8f95-8e16edc03f4c/projects/2564c9ce-cd79-4e20-aad5-bc07b1f28945).

This replaces the rejected 22 November draft. Scanner tasks, wrapper subprocesses, recurring checks and the correction helper were removed. The rejected Camunda project was moved to Recently deleted. F1 and main remain unchanged.

## Original design preserved

Both executable BPMN files are generated from the untouched sources in `models/operational-bpmn/functionality-2/`. The main source blob is `4ba83ea042c09a4b9493e1c21a3226e80b444b69`.

Automated comparison checks all original node IDs, every sequence-flow endpoint, nesting/ownership, and the entire BPMN diagram (bounds, waypoints, labels and pools/lanes). No business nodes, routes or subprocesses are added. The original generic "Keep product unavailable" task receives a service-task implementation with its original ID, name, position and connections.

Added execution settings: executable flag; worker types; FEEL conditions/default paths; message definitions and correlation; administrator form reference; literal called process ID and returned variables; timer values. Target: Camunda 8.9.

## Contents

| File | Purpose |
|---|---|
| processes/inventory-seasonal-availability.bpmn | Full original operational F2 workflow with execution properties |
| processes/check-product-stock-status.bpmn | Original reusable stock-check workflow with a worker type |
| forms/f2-inventory-review.form | Linked to the original administrator task |
| forms/f2-stock-correction.form | Standalone producer form specification/preview; not a Tasklist task |

The original producer is a black-box pool. There is no producer user task to attach the correction form to. Corrections arrive at Zain's original message catch through an external producer UI or a demonstration message. No separate helper diagram is added.

## Explicit seasonal timer demo configuration

A timer start creates a fresh instance without product variables from earlier updates. To preserve the original graph, these routes are configured for ONE demonstration product. Timer dates come from `services/inventory-service/demo-product.json`: season start at UTC midnight on availableFrom; season end at UTC midnight on the day after inclusive availableUntil.

Set `F2_TIMER_PRODUCT_ID=P1` in the worker. Change the product/date configuration and rebuild/redeploy for a different demonstration. Updating dates in an instance does not reschedule deployment-level timers. Past timer dates may fire immediately on deployment. There is no recurring timer or catalogue scanner. Current catalogue dates are rechecked so stale timers cannot enable an out-of-season product. This is a limited timer demonstration, not a complete multi-product scheduler.

## Run and deploy

Python 3.12+, standard library only. Use one worker and one SQLite demo catalogue.

1. Seed: `python services/inventory-service/worker.py --seed services/inventory-service/demo-product.json`.
2. Set CAMUNDA_REST_ADDRESS, an existing authorized CAMUNDA_ACCESS_TOKEN for SaaS (or local CAMUNDA_USERNAME/CAMUNDA_PASSWORD), and F2_TIMER_PRODUCT_ID. Never commit credentials.
3. Run `python services/inventory-service/worker.py` from the seed directory, or use the same explicit --db path for both commands.
4. Deploy the two processes and administrator form together; the standalone producer form may also be included. The original timer starts activate on deployment.

The catalogue is a separate seeded demo stub, not an F1 integration. Notifications/correction requests are recorded in SQLite; no real email/SMS is sent. Overselling fails without reducing stock below zero; duplicate orderId does not decrement twice.

## Messages

Publish through `/v2/messages/publication` with unique messageId, correlationKey and TTL. Update variables: productId, updateId, nonnegative integer quantity, availableFrom and availableUntil (YYYY-MM-DD). Paid-order variables: productId, orderId and positive integer purchasedQuantity.

| Message | Purpose | Correlation key |
|---|---|---|
| f2-stock-update | Start original update route | productId |
| f2-stock-corrected | Resume original correction catch | updateId of waiting update |
| f2-order-paid | Start original stock-reduction route | productId |

Example correction:

```json
{"name":"f2-stock-corrected","correlationKey":"U1","messageId":"U1-correction-1","timeToLive":60000,"variables":{"quantity":12,"availableFrom":"2026-11-01","availableUntil":"2026-12-31"}}
```

Three invalid attempts route to administrator review; allowAnotherCorrection=true returns to corrections, false rejects. Original interrupting deadline: PT48H. Low stock: `0 < quantity < lowStockThreshold` (default 5); zero-stock notification is separate.

## Validation

`python -m unittest discover -s tests -p test_inventory.py -v`: 14 checks pass, including exact original graph/nesting/diagram preservation and explicit timer product configuration.

`cd tests/camunda-f2; mvn -o -Dtest=ModelValidationTest test`: Camunda parser/schema validation passes for the actual two BPMN files. The three engine route tests compile but cannot start here because local loopback sockets are blocked. No live F2 route is claimed as passed. Connect the worker and capture Tasklist/Operate evidence before claiming successful execution.

Rebuild execution settings with `python scripts/build_f2.py`.
