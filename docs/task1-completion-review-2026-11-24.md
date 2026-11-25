> Current F2 status: the Tasklist, message-scheduler and notification-service refinements supersede older F2 instructions in this historical review. Use [the current runbook](../camunda/f2/README.md) and [version-2 live evidence](f2-tasklist-live-validation-2026-11-24.md).

# Task 1 completion review - 24 November 2026

This is an evidence register and demonstration checklist, not a claim that Task 1 is finished. Deadline in the supplied assessment brief: before 14:00 UK time on 10 December 2026. No written report or recorded presentation is required; repository artefacts, live demonstration and individual understanding are assessed.

## Verified integration

Existing runs were inspected in the signed-in UWE Frenchay 2026 Operate UI and compared with the current SQLite catalogue. They were not newly submitted during this review.

| Evidence | Result |
| --- | --- |
| Product `LST-20261124124331893` | Stored with matching listingId, publication timestamp and traceabilityRecord |
| F2 instance `4503599682343002`, update `omar-update-003` | Completed 24 November 13:36:20; validated and saved quantity 40, revision 3, in season and available |
| F2 instance `4503599682344882`, order `omar-order-008` | Completed 24 November 13:40:27; purchasedQuantity 3, quantity 37, revision 4, available |
| SQLite orders and cached jobs | Same order/product/quantity; current product quantity 37, revision 4 |
| Earlier product `LST-20261124112311151` | Low-stock notification recorded at quantity 1; out-of-stock notification recorded at zero |
| Python verification | 32 tests passed on 24 November; temporary/in-memory databases, no live catalogue reset |
| Camunda F2 parser/schema check | `mvn -o -Dtest=ModelValidationTest test` passed on 24 November; one test, zero failures/errors. This validates deployment files, not timed execution |
| Embedded F2 route/timeout rerun | `mvn -o -Dtest=InventoryProcessTest test` failed before process execution on 24 November: all three tests reported engine startup errors caused by `Unable to establish loopback connection` / `Permission denied: connect`. No route/timeout assertion was established |
| Form references | All seven linked formIds resolve to included form files; the additional F2 correction form is standalone and is not a Tasklist task |

The database record supports F1 persistence. A complete live F1 organic/correction/fallback demonstration remains separate from these two F2 runs. Do not use the original installation note's earlier DNS failure as the current integration status.

## Exceptions and honest limits

| Case | Evidence/status | Required next action |
| --- | --- | --- |
| Invalid update, correction and administrator rejection/approval | Nine previous live scenarios documented in `f2-live-validation-2026-11-23.md` | Rehearse with unique messageIds; preserve the distinction between full three-attempt rejection and the approval test seeded at counter 2 |
| Empty productId | Instance `4503599682333827` reached a no-retries-left incident at stock reduction; variables were productId `""`, orderId `LST-20261124124331893`, purchasedQuantity 3 | Treat as invalid demonstration input. Do not retry unchanged or silently change a historical order; submit a new correctly identified test |
| Overselling | Worker raises `Insufficient stock; no negative quantity is permitted`; Python rollback test passes; two live dashboard incidents carry this message | It is an incident, not a low/out-of-stock notification. Reconcile the upstream paid-order contract and agree the business rejection/compensation design before any BPMN change |
| Duplicate order / repeated job | Python tests verify no repeated deduction and reject conflicting order reuse | Still requires a recorded live duplicate-message/recovery demonstration |
| Dynamic seasonal scheduling | Python tests cover date replacement, independent products, zero stock, stale actions and restart recovery | Service-side scheduler updates SQLite; it does not invoke Camunda seasonal routes |
| Seasonal BPMN starts | Fixed dates in executable file: 2026-11-01 and 2027-01-01; single demo product configured by F2_TIMER_PRODUCT_ID | Not dynamically rescheduled. Agree final approach with model author; test in an isolated configuration without creating new model structure or replacing group designs |
| Review timeout | PT48H is configured; existing Java test advances engine clock by 49 hours | No successful engine/live timeout execution established in this review. Do not claim a pass from XML inspection |
| Notifications | SQLite demo records only; outbox has no delivery loop | Do not describe email/SMS as delivered or outbox delivery as implemented |
| Payments | `f2-order-paid` is an integration message | No payment provider or checkout is implemented by this worker; do not enter real payment details for this assessment test |

The worker must remain running and use the same database. A successful message-publication response confirms acceptance only, not process completion. Existing instances retain their deployed version.

## Traceability supplement

This supplements the existing `docs/traceability.md`, whose F2 executable column still says planned. It does not change or generate any stakeholder or BPMN model.

| Existing traceability row | Implemented evidence | Remaining qualification |
| --- | --- | --- |
| 1.8 Catalogue and traceability | F1 `Task_PublishListing` uses `f1-publish-product`; worker commits product/traceability/schedule/job result before completion | Include connected F1 resources and shared worker together; do not claim all F1 branches retested |
| 2.1 Accurate availability | `Process_0g8kz9d`; current quantity/date checks and SQLite persistence | Single-worker local demonstration service |
| 2.2 Producer stock data | `f2-stock-update`; validate-quantity and validate-season; correction catch uses updateId; administrator form `f2-inventory-review` | Initial submission/correction uses demonstration messages; no external producer UI is implemented |
| 2.3 Stock alerts | `f2-notify-low` and `f2-notify-zero`; separate persisted records | Recorded alerts, no real notification service delivery |
| 2.4 Seasonal availability | FEEL gateways and worker current-date checks; persistent scheduler; original fixed-date BPMN starts | Dynamic service scheduling and BPMN timer firing are separate mechanisms |
| 2.5 Paid order deduction | `f2-order-paid`, `orderId`, `productId`, `purchasedQuantity`; completed order above | Provider integration remains a Task 2 boundary; overselling currently incidents |

Original F2 graph/nesting/diagram preservation is checked by `ModelTests`. The operational models are group-authored artefacts; final design justification and any model revisions belong to their authors. The assessment prohibits AI-generated models/diagrams. AI assistance used for supporting code, checks and evidence preparation must be disclosed accurately, reviewed by the group and understood by contributors; this note is not a retrospective authorship certification.

## Demonstration rehearsal

1. Start the shared worker; show CONNECTED. Confirm the exact database path. Keep credentials off screen and outside Git.
2. Start a new connected F1 non-organic listing in Tasklist and complete the form with clearly labelled synthetic data. Observe publication completion, productId and cataloguePersisted=true; inspect the saved catalogue entry.
3. Publish a stock update for that exact productId with a unique updateId/messageId. Observe completion and matching persisted quantity.
4. Send an invalid quantity and correct it on the same updateId. Show the waiting process resumes. Explain why the standalone correction form is not a linked Tasklist form.
5. Show the administrator review after three invalid submissions, rejection and allow-another-correction. Count actual attempts honestly.
6. Use distinct order IDs to reach low stock and zero. Show the path, database and recorded notifications; distinguish an oversell incident from reaching zero.
7. Demonstrate duplicate-order protection and worker restart recovery; capture instance keys and before/after quantities. Mark these pending until actually observed.
8. Demonstrate agreed seasonal/timer behaviour and review timeout in a reproducible test environment. Do not change production/group timer settings merely to force a demo.
9. Show the i*  strategic  operational  execution links using group artefacts and this supplement. Explain SQLite transactions, cached jobs, order deduplication and service boundaries in your own words.

## Submission gate

- [ ] Current executable F1 and F2 resources, shared service, launch/setup instructions and tests available on a reviewed repository branch.
- [ ] Group agrees branch integration order; no automatic merge into main. F1 PR #60 is open against docs/operational-bpmn-models as checked on 24 November.
- [ ] Reconcile the stale main/F2 documentation and the new supplement before final submission.
- [ ] Record successful timer/timeout, duplicate/recovery and remaining F1 routes, or explicitly identify the unresolved limitations to the group.
- [ ] Each model author reviews consistency with the submitted implementation. Do not count source-file presence as a complete semantic review.
- [ ] Group confirms module-team agreement for both functionalities and the final demo time; Sprint 3 date in the brief is 23 November, separate from the 10 December repository deadline.
- [ ] Signed contribution matrix agreed and signed by members, with truthful contributions. No signatures or percentages supplied by automation.
- [ ] Individual rehearsal covers model choices, service contracts, data flow, exceptions, limitations and Task 2 reuse.
- [ ] LESP discussion is tied to actual implementation: data minimisation/access to catalogue and credentials; accuracy of organic/allergen/traceability claims; accessibility of forms and correction feedback; truthful audit/contribution/AI records. Support any legal claims with checked authoritative sources; these are prompts for group evaluation, not a legal compliance finding.

The earlier roadmap extending beyond 10 December must not be used for Task 1. Prioritise complete Camunda execution, repository evidence and rehearsal before optional website or email features.

