# F2 seasonal scheduling in the inventory service

Implemented on the separate F2 branch. No BPMN, form, F1 implementation or main branch change is included in this scheduler update.

## Behaviour

The inventory worker's SQLite catalogue stores persistent start and end schedules for each product. Seeding a product creates its schedules. Saving changed season dates cancels the old pending actions and creates a new pair in the same transaction as the catalogue update. Invalid updates leave the schedules untouched. A retry of the same job does not create another schedule.

Schedules have a separate seasonVersion. A stock sale or quantity-only update does not invalidate a seasonal schedule. At execution, the scheduler checks both that version and the current dates again; stale actions are cancelled even if their status was accidentally left pending.

The season starts at UTC midnight on availableFrom and ends at UTC midnight on the day after the inclusive availableUntil. At a due action, availability is recomputed from the current date, current season dates and current stock. Zero stock remains unavailable. If the service was stopped through the entire season, the missed start action does not briefly enable the expired product: both actions evaluate current state.

Completed actions are retained in season_events with product ID, season version, boundary, due date, actual application timestamp, available flag and quantity. Repeated ticks and restarts do not repeat completed actions. Date updates, stock changes and scheduled actions use SQLite write transactions to avoid stale read/write races.

## Running

The normal `python services/inventory-service/worker.py` loop now processes due schedules before polling Camunda jobs and between job-type polls. Scheduling therefore continues on subsequent loop iterations during Camunda connection failures. Actions run when the running service next checks; this is not a hard real-time guarantee. A stopped service catches up after restart.

For a standalone scheduler check with no Camunda connection:

```powershell
python services/inventory-service/worker.py --db f2-catalogue.sqlite3 --scheduler-once
```

Use the same database as the inventory worker. Run one worker process per catalogue for the demonstration. Existing catalogue products are migrated to persistent schedules on startup. Credentials are not required for scheduler-only operation.

## Camunda boundary - still requires a modelling decision

This scheduler currently applies availability changes in the inventory service and records its audit events. It does **not** publish messages, create Camunda process instances, or replace the fixed timer starts in the original operational diagram. Therefore these service tests are not evidence that the seasonal BPMN routes have executed.

Zain's original diagram remains intact. Its existing fixed timer starts are still the separately configured single-product demo; editing producer dates does not reschedule those engine timers. Do not present that limitation as solved in the diagram.

Proposed next agreement with Zain: have the scheduler emit a product-specific due message to each original seasonal route. That would require changing each seasonal timer start to a message start and agreeing message names, productId/seasonVersion data, reliable delivery and duplicate handling. No such modelling change or message transport has been made here. This note is a proposal to discuss; it has not been sent to Zain.

## Validation on 22 November 2026

22 Python checks passed. The eight new scheduler scenarios cover replacing both boundaries; zero stock at season start; sales without schedule cancellation; persistent restart recovery and replay protection; independent products; invalid update rollback; job retries/quantity-only updates; and stale action rejection. The other 14 checks cover the existing inventory rules and original BPMN preservation.

No live Camunda deployment or route execution is claimed by these results.
