# F2 live validation - 23 November 2026

Environment: UWE Frenchay 2026, cluster `848240b1-573c-4a07-bd52-723bea5b23b7`.
Deployed original operational process: `Process_0g8kz9d`, version 1.
Worker launched by Omar in ordinary PowerShell using `services/inventory-service/start-f2.cmd`.
Authenticated topology request succeeded. Client credentials are outside the repository in Downloads; no secrets are included in this evidence.

Messages were submitted through the signed-in cluster Swagger UI. Completion was checked in Operate and business effects checked in the worker's SQLite catalogue. API acceptance alone was not counted as a pass.

| Case | Main process instance | Observed result |
| --- | --- | --- |
| Valid inventory update | 4503599682076273 | Completed; P1 quantity 20, available |
| Paid order, purchase 17 | 2251799868664055 | Completed; quantity 3, available, low-stock notification recorded |
| Paid order, purchase remaining 3 | 2251799868664206 | Completed; quantity 0, unavailable, out-of-stock notification recorded |
| Update outside season | 4503599682076768 | Completed; quantity 20, future season 2027-01-01 to 2027-02-01, unavailable |
| Paid order outside season | 6755399495759422 | Completed; quantity 19, remained unavailable |
| Zero-stock inventory update | 6755399495759497 | Completed; quantity 0, unavailable |
| Negative quantity then valid correction | 4503599682077093 | Correction request recorded; correlated correction accepted; completed at quantity 4 |
| Three invalid seasonal-date submissions | 4503599682077393 | Reversed dates rejected on each attempt; admin form appeared after third failure; admin rejected; completed without changing valid catalogue data |
| Admin allows further correction | 6755399495760365 | Counter seeded at 2 to isolate approval branch; third failure opened admin form; checked allow-another-correction; valid correlated correction completed |

All nine main process instances had end dates in Operate and none remained active or incidented in the selected process/version filter. The worker recorded 47 handled jobs. Final P1: quantity 20, available true, season 2026-11-01 through 2026-12-31, revision 9, seasonVersion 3.

Review form task keys: rejection `4503599682077730`; approval `6755399495760407`.
Correlation IDs: `f2-live-20261123-correction`, `f2-live-review`, and `f2-live-allow`.
Each repeated correction used a distinct messageId and the same updateId/correlationKey.

## Limits of this evidence

- Notifications are persisted demo records, not delivered email or a separate notification service.
- Seasonal BPMN timer starts were not made to fire in this run. The persistent Python scheduler processed the due demo season start on worker startup, but that is separate from proving the BPMN timer routes.
- The 48-hour review boundary timeout was not awaited or shortened.
- This run does not establish complete branch, concurrency, failure-recovery, or payment-provider integration coverage.
- No BPMN graph or execution settings were changed during testing. F1 and main were not modified.
- This report is repository documentation, not a Camunda project file. Local evidence has not yet been published to GitHub.

