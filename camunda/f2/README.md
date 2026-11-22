# F2 Inventory and Seasonal Availability Management

Owner: Omar Fathy (M4). Source model: Zain-Eldin Sharaf (M3).

This implementation refines the original operational BPMN. It does not replace it with a smaller business process. F1 is unchanged. Work is isolated on `feature/camunda-f2-inventory-seasonal`; nothing is merged into main.

## Source and execution changes

Original main model: `models/operational-bpmn/functionality-2/inventory-seasonal-availability.bpmn`, blob `4ba83ea042c09a4b9493e1c21a3226e80b444b69` from Zain's F2 commit `59f3b07fd3d9379206ef3308322140751a24468a`. The same blob was present on main at review time. The companion stock-check blob is `ffe8f6c2353ba64a687b3954a68f45df48d53166`.

The build retains every original XML ID and the business flow endpoints. Two original seasonal entry flows now originate at added inner start events because the original season routes are enclosed in per-product sequential multi-instance subprocesses. This preserves the original tasks and decisions while making the catalogue-wide timers executable.

| Original feature | Executable refinement |
|---|---|
| Stock/season update message start | `f2-stock-update` message; required productId and updateId |
| Expanded quantity and season validation | Two inventory worker jobs, errors and attempt counter |
| Correction request and message catch | Durable request message, Tasklist correction form adapter, `f2-stock-corrected` correlated by updateId |
| Three invalid attempts | Original gateway routes to administrator form |
| Administrator allows correction / rejects update | Boolean form decision; original routes retained |
| Interrupting 48-hour review boundary timer | `PT48H`; original timeout end retained |
| Stock-zero / seasonal / low-stock gateways | FEEL conditions and default paths |
| Original service and send tasks | Explicit `f2-*` job types |
| Reusable stock-status call | Literal called process ID `check_product_stock_status`; child outputs propagated |
| Season-start and season-end timer starts | One-minute catalogue reconciliation, each original branch repeated for applicable products |
| Order paid message | `f2-order-paid`, deduplicated by orderId, no negative stock |
| Product Catalogue | Separate SQLite demonstration catalogue, with atomic updates and job-response cache |
| Notification Service | Notifications recorded in SQLite; no real email or SMS is sent |

Season dates are inclusive UTC calendar dates. Season-end reconciliation makes the product unavailable on the next day, within the next polling interval while the worker is running. Reconciliation catches boundaries missed during downtime. Availability is rechecked from current catalogue state so an old timer cannot enable a product after its season has changed. The threshold rule is `0 < quantity < lowStockThreshold` (default 5).

## Files and Camunda project

Upload the three BPMN files in `processes` and the two forms in `forms` into the same project. The producer correction process is only a Tasklist adapter; the marketplace process still waits at Zain's original correction-message catch.

[Separate Camunda F2 project](https://hub.camunda.io/workspaces/92fa97e5-a7b4-4f61-8f95-8e16edc03f4c/projects/4e0530c1-1ba8-4aaa-bd15-998f31f6508b).

Deploy forms, stock-check process, correction adapter and main process together. Deploying the main process activates its one-minute timers. It needs the inventory worker; deployed service tasks will wait until that worker connects. Do not deploy Zain's design-only originals or F1 files as part of this project.

## Run the demonstration worker

Python 3.12 or newer; no third-party Python packages. Run a single worker with one SQLite catalogue. Keep the database outside git.

1. Create a demo product JSON such as `services/inventory-service/demo-product.json` and seed it:
   `python services/inventory-service/worker.py --seed services/inventory-service/demo-product.json`
2. Set `CAMUNDA_REST_ADDRESS` to the environment's REST base URL (with or without `/v2`). For SaaS, set `CAMUNDA_ACCESS_TOKEN` to an existing authorized bearer token. Refresh expired tokens outside this worker. For a local cluster, use `CAMUNDA_USERNAME` and `CAMUNDA_PASSWORD` if required. Never commit credentials.
3. Run `python services/inventory-service/worker.py` from the same directory used for seeding, or use `--db` to point both commands at the same database.

This catalogue is a demonstration stub for the existing-published-product boundary. It is not integrated with the F1 catalogue; seed the product explicitly. This keeps F1 untouched. Real notifications, producer authentication and a shared production catalogue remain integration work.

## Start an update or paid-order route

Publish messages through the Camunda REST API `/v2/messages/publication`. The worker's `request()` function provides the configured connection. Example bodies:

```json
{"name":"f2-stock-update","correlationKey":"P1","messageId":"update-U1","timeToLive":60000,"variables":{"productId":"P1","updateId":"U1","quantity":12,"availableFrom":"2026-11-01","availableUntil":"2026-12-31"}}
```

```json
{"name":"f2-order-paid","correlationKey":"P1","messageId":"order-O1","timeToLive":60000,"variables":{"productId":"P1","orderId":"O1","purchasedQuantity":3}}
```

Use a unique updateId for each concurrent update. The producer and administrator complete tasks in Tasklist after assignment. The administrator's checkbox means allow another correction; unchecked means reject. Overselling and unknown products fail the job without altering stock and become incidents after retries, for manual resolution. Repeated orderId with changed purchase details is rejected.

## Checks and remaining evidence

`python -m unittest discover -s tests -p test_inventory.py -v`: 13 checks passed on 22 November 2026. They cover original-node preservation, executable properties, validation, correction limits, notifications, seasonal boundaries, duplicate-job/order handling, stale timer protection and invalid/oversold stock.

`cd tests/camunda-f2; mvn -o -Dtest=ModelValidationTest test`: passed. Camunda's Java BPMN parser and schema validator accepted all three actual executable BPMN files. Web Modeler also displayed the main model with only two informational notices about the separately supplied form and called process; those resources are in the same F2 project. This is model validation, not engine execution evidence.

`cd tests/camunda-f2; mvn -o test`: the three engine tests compiled, but could not start the embedded engine because the execution environment denied its local loopback socket (`Permission denied: connect`). No engine route is recorded as passed. These tests use the actual executable BPMN, with only native user-task markers removed in the in-memory test copy, matching the existing F1 test approach.

Before calling F2 demonstrated, connect the worker, deploy the exact uploaded files, run the routes, and capture Tasklist/Operate outcomes. Required evidence: in-season update; out-of-season update; zero stock; restock; low stock; corrections; third-attempt admin rejection/allowance; 48-hour timeout; season start/end; order decrement and duplicate-order protection. Runtime checks must identify the process version tested.

Rebuild from the untouched source models with `python scripts/build_f2.py`. The script writes only F2 outputs.
