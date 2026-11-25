# F2 executable inventory - current runbook

Current implementation: Tasklist producer forms, persistent message-based seasonal scheduling, and a separate local simulated Notification Service. Supersedes earlier fixed-timer/record-only instructions. Original operational source files are unchanged.

## Start

Stop the previous shared inventory worker with Ctrl+C. From ordinary PowerShell run:

```powershell
& "C:\Users\omarf\Documents\Projects\DaESD\f2-work\services\inventory-service\activate-f2.cmd"
```

This deploys exactly two BPMNs and three forms to the existing UWE cluster, then launches the shared F1/F2 worker and the local notification simulator. Expect DEPLOYED, CONNECTED and NOTIFICATIONS ready. Existing credentials remain outside the repository. Startup does not seed or reset products. Use one worker per catalogue.

For a restart without deployment, run `services/inventory-service/start-f2.cmd`. The launcher starts its own hidden local notification process only if the service is absent, and stops that process when the worker exits. Receipts persist in its separate SQLite file.

## Producer and administrator

In Tasklist > Processes, search `Process_0g8kz9d` and start the process. The worker loads catalogue product choices and generates an update ID. Complete **Update stock and seasonal availability** with a new total quantity and inclusive dates. Invalid dates open **Correct stock and seasonal availability** with errors and submitted values. Three invalid attempts open **Review invalid stock update**. Allow another correction or reject; review has an interrupting PT48H deadline.

Forms are `f2-stock-update`, `f2-stock-correction`, `f2-inventory-review`. All use deployment binding and must be deployed with the BPMNs. Native Tasklist submission/correction and administrator allowance were verified on version 2 on 24 November; see the live report.

Producer submission and correction are in the producer lane; catalogue loading and business logic are in the platform lane. The original black-box Producer participant remains in the operational artefact. This is an explicit executable refinement, not exact diagram identity. Product ownership enforcement remains outside this shared-cluster classroom demo.

## Seasonal scheduling - one mechanism

When F1 publishes a product or F2 changes its dates, `season_schedule` stores its start and end boundaries. End is due the day after inclusive availableUntil, in UTC. Date changes cancel pending/queued old-version entries.

The worker queues due messages in its transactional outbox, publishes `f2-season-start` or `f2-season-end`, and Camunda runs the original seasonal routes. There are no fixed seasonal timeDate values in the executable BPMN and no direct scheduler write to availability. Jobs verify product/version/boundary, recalculate current stock/date availability and record execution. Missed start and end boundaries cannot re-enable an already ended season.

States: pending = not yet due; queued = durable message intent or published message awaiting processing; completed = matching seasonal job applied; cancelled = superseded. Outbox `sent=1` means publication acknowledgement, not process completion.

## Notification service

Correction, low-stock and out-of-stock jobs commit a notification record and an outbox entry together. A dispatcher sends the entry to the separate HTTP simulation at `127.0.0.1:8765/notifications`. Its own SQLite receipts deduplicate event IDs and reject conflicting reuse. Failed requests retain attempts, next retry time and last error; stock changes are not rerun to retry notification delivery.

BPMN send-task completion means **durably queued**. Outbox delivery and service receipts establish the later service acknowledgement. This is simulated notification delivery, not email or SMS and not proof a producer read a message. No external messages are sent to people.

## Other messages and compatibility

| Message | Variables | Purpose |
| --- | --- | --- |
| f2-stock-update | productId, updateId, quantity, availableFrom, availableUntil | Optional external stock-update integration; ordinary producer demo uses Tasklist |
| f2-order-paid | productId, orderId, purchasedQuantity | Paid-order integration; use unique order IDs; no real payment is made here |
| f2-season-start / f2-season-end | productId, seasonVersion, seasonBoundary, seasonDue | Scheduler-controlled seasonal routes |
| f2-stock-corrected | Legacy updateId correlation | Only old version-1 instances still waiting for a correction message |

Overselling currently produces an incident without negative stock; it is not a stock-zero notification. Duplicate orders do not deduct again. Payment reservation/refund/compensation design is an upstream integration responsibility, not implemented by this worker.

## Verification and sources

- `python -m unittest discover -s tests -p 'test_*.py'`: 45 passed after these changes; includes stale seasonal messages, queue/execute separation, restart/retry intent, notification lost-response deduplication, deployment bundle and lane/layout contracts.
- From `tests/camunda-f2`: `mvn -o -Dtest=ModelValidationTest test`: parser/schema validation passed.
- Embedded engine tests remain blocked here by loopback socket restrictions; their job-user-task substitution is not proof of native Tasklist rendering.
- [Live version-2 evidence](../../docs/f2-tasklist-live-validation-2026-11-24.md)
- [Executable mapping](../../docs/f2-tasklist-refinement.md)
- Rebuild execution files using `python scripts/build_f2.py`.

The group must review model consistency and acknowledge AI assistance with executable implementation, supporting code, forms and tests under the assessment brief. Final group artefact authorship, contribution signatures and presentation understanding cannot be supplied by automation.

