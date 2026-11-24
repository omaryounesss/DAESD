# F2 native Tasklist and integration evidence - 24 November 2026

Environment: UWE Frenchay 2026. Deployment `2251799869041810` installed `Process_0g8kz9d` version 2 and `check_product_stock_status` version 2, with all three forms. Omar ran activate-f2.cmd in ordinary PowerShell and supplied DEPLOYED / CONNECTED / NOTIFICATIONS-ready output. Browser actions used the signed-in cluster UI; this session's direct Python network access remains restricted.

## Live runs

| Case | Main instance key | Observed result |
| --- | --- | --- |
| Native submission, invalid dates, correction | 2251799869042170 | Tasklist product choices loaded from SQLite. P1 quantity 3 with reversed dates opened correction with the error/prior values. Valid correction completed 16:31:20; quantity 3, revision 16 |
| Three actual invalid submissions; administrator allows correction | 4503599682365771 | Initial submission and two invalid corrections opened native review. Allow-another-correction returned to the producer. Valid ended-season correction completed 16:35:21; quantity 3, unavailable, revision 17. Counter was not seeded |
| Season-start catch-up | 2251799869044581 | Scheduler message started seasonal route; completed 16:35:26. P1 seasonVersion 7 start audited; ended season remained unavailable |
| Season-end catch-up | 2251799869044656 | Scheduler message started end route; completed 16:35:26. Version 7 end boundary due 24 November audited and completed |
| Zero stock through native form | 6755399496049633 | Completed 16:36:30; quantity zero, revision 18, unavailable; out-of-stock event delivered to separate simulated service |
| Current-season start at zero stock | 2251799869045144 | Completed 16:36:35; version 8 seasonal route did not enable zero stock |
| Native restoration | 2251799869045313 | Completed 16:37:15; quantity 5 and season 1 November to 31 December restored through form |
| Paid order, purchase 2 | 2251799869046749 | Completed 16:39:53; quantity 5 to 3; orderId task1-v2-duplicate-20261124 |
| Same order, different messageId | 2251799869046908 | Completed 16:40:06; quantity stayed 3/revision 20; only one order record |
| Administrator rejection branch | 2251799869049739 | Completed 16:46:08 after native review rejected. This test deliberately started at review with counter=3; it isolates rejection and does not claim another three failed submissions |
| Final restoration through external stock-update integration | 2251799869049982 | Message accepted; final SQLite quantity 5, revision 21, current season and available. Inspect end date separately if UI capture still showed running |

Native task keys: submission `2251799869042194`, correction `2251799869042539`; three-attempt submission `4503599682365786`, corrections `4503599682366351` and `4503599682366470`, administrator `4503599682366808`, post-approval correction `4503599682366996`; zero submission `6755399496049648`; restoration `2251799869045335`; isolated rejection `2251799869049747`.

The ordinary producer journey used forms, not Swagger. Swagger was used for system-integration messages and isolated test setup. API publication acceptance was not counted as process completion.

## Notification and scheduling effects

The separate HTTP simulator persisted receipts in notification-receipts.sqlite3 for correction requests, `notification:P1:16:low-stock` (quantity 3), `notification:P1:17:low-stock`, and `notification:P1:18:out-of-stock` (quantity zero). Correction updates included `UI-32a7c2949c2c4328b0a303c2cd9d2579` and `UI-5117cb00075843c6af718af6d3965846`.

Inspected outbox entries showed sent=1, attempts=1 and no last error. Final inspection found zero pending outbox entries. This is simulated service acceptance, not email/SMS or human receipt. Lost-response retry and receiver deduplication were tested with injected transports/temporary databases; live service outage was not deliberately induced.

P1 version-7 start/end schedules reached completed through the Camunda routes. The old pending version-6 end was cancelled when dates changed. Version-8 start was applied with zero stock and correctly remained unavailable. Catch-up uses the current date, so missed starts cannot re-enable an ended season. No fixed seasonal timeDate remains in the assessed executable.

## Isolated review-timeout test

Fixture: tests/fixtures/f2-review-timeout-test.bpmn. It clones the executable solely for testing with process ID `daesd-f2-review-timeout-test`, a five-second duration, and prefixed message/job types so it cannot consume production F2 work. Forms use existing latest bindings in this fixture only. Deployment `2251799869049340`; definition key `2251799869049341`.

Instance `6755399496053687` started directly at review with test variables and productId `TEST-NO-CATALOGUE-WRITE`. Operate showed start 16:45:26/end 16:45:32, with history: Review invalid stock update -> Review deadline exceeded -> Stock update review timed out. No catalogue product with that test ID was created.

This verifies the timeout route using an accelerated isolated duration, not a real 48-hour wait. The assessed executable remains PT48H. The fixture is not an assessed replacement business model. Its clearly named definition remains as test evidence with no periodic starts; the instance completed.

## Validation and boundaries

- 45 Python tests passed; F2 parser/schema validation passed. Tests cover queue-vs-execution separation, stale messages, retry/reopen, notification deduplication, deployment bundle and lane/layout contracts.
- Embedded engine tests cannot start here because loopback sockets are denied. Their job-user-task approximation is separate from the native Tasklist evidence above.
- Live seasonal testing exercised due/missed-boundary catch-up, not waiting until a future UTC midnight.
- Full live worker-disconnection recovery and an induced HTTP delivery outage remain separate from the local retry/restart tests.
- P1 was restored to quantity 5, available=true, dates 2026-11-01 to 2026-12-31. Revisions/audit history were retained. Existing published products were not reset.
- Earlier F1 persistence evidence remains separate. Organic certification and fallback routes were not retested in this run.
- Main was not merged. Group model-author review, truthful AI disclosure, signed contribution matrix and demonstration rehearsal remain submission responsibilities.

